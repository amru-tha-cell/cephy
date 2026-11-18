"""Swin-style window-attention encoder + Attention U-Net decoder.

This is a compact, trainable implementation intended for research prototyping.
It preserves the requested encoder/decoder/head topology; it is not a pretrained
clinical model. The 19 heatmap and 2D offset heads are trained jointly.
"""
import torch
from torch import nn
import torch.nn.functional as F

class WindowAttentionBlock(nn.Module):
    def __init__(self, dim, heads=4, window=8, shift=0, dropout=.1):
        super().__init__(); self.window=window; self.shift=shift
        self.norm1=nn.LayerNorm(dim); self.attn=nn.MultiheadAttention(dim, heads, dropout=dropout, batch_first=True)
        self.norm2=nn.LayerNorm(dim)
        self.mlp=nn.Sequential(nn.Linear(dim,dim*4),nn.GELU(),nn.Dropout(dropout),nn.Linear(dim*4,dim),nn.Dropout(dropout))
        coords=torch.stack(torch.meshgrid(torch.arange(window),torch.arange(window),indexing='ij'))
        flat=coords.flatten(1); rel=flat[:,:,None]-flat[:,None,:]; rel=rel.permute(1,2,0).contiguous()
        rel[:,:,0]+=window-1; rel[:,:,1]+=window-1; rel[:,:,0]*=2*window-1
        self.register_buffer('relative_position_index',rel.sum(-1),persistent=False)
        self.num_heads=heads
        self.relative_position_bias=nn.Parameter(torch.zeros((2*window-1)**2,heads))
        nn.init.trunc_normal_(self.relative_position_bias,std=.02)
    def _shift_mask(self,h,w,device):
        if self.shift==0: return None
        ws=self.window; mask=torch.zeros((1,h,w,1),device=device)
        hs=(slice(0,-ws),slice(-ws,-self.shift),slice(-self.shift,None))
        wslices=(slice(0,-ws),slice(-ws,-self.shift),slice(-self.shift,None))
        count=0
        for hs0 in hs:
            for ws0 in wslices:
                mask[:,hs0,ws0,:]=count; count+=1
        windows=mask.view(1,h//self.window,self.window,w//self.window,self.window,1).permute(0,1,3,2,4,5).reshape(-1,self.window*self.window)
        diff=windows.unsqueeze(1)-windows.unsqueeze(2)
        return diff.masked_fill(diff!=0,-100.0).masked_fill(diff==0,0.0)
    def forward(self,x):
        b,c,h,w=x.shape; ws=self.window
        ph=(ws-h%ws)%ws; pw=(ws-w%ws)%ws
        x=F.pad(x,(0,pw,0,ph)); _,_,hp,wp=x.shape
        if self.shift: x=torch.roll(x,shifts=(-self.shift,-self.shift),dims=(2,3))
        z=x.permute(0,2,3,1).contiguous().view(b,hp//ws,ws,wp//ws,ws,c).permute(0,1,3,2,4,5).reshape(-1,ws*ws,c)
        q=self.norm1(z)
        bias=self.relative_position_bias[self.relative_position_index.reshape(-1)].view(ws*ws,ws*ws,self.num_heads).permute(2,0,1)
        bias=bias.unsqueeze(0).expand(b*(hp//ws)*(wp//ws),-1,-1,-1)
        mask=self._shift_mask(hp,wp,x.device)
        if mask is not None:
            nw=mask.shape[0]; bias=bias.view(b,nw,self.num_heads,ws*ws,ws*ws)
            bias=bias+mask[None,:,None,:,:]
            attn_mask=bias.reshape(-1,ws*ws,ws*ws)
        else: attn_mask=bias.reshape(-1,ws*ws,ws*ws)
        attn,_=self.attn(q,q,q,attn_mask=attn_mask,need_weights=False); z=z+attn; z=z+self.mlp(self.norm2(z))
        z=z.view(b,hp//ws,wp//ws,ws,ws,c).permute(0,1,3,2,4,5).reshape(b,hp,wp,c).permute(0,3,1,2)
        if self.shift: z=torch.roll(z,shifts=(self.shift,self.shift),dims=(2,3))
        return z[:,:,:h,:w]

class PatchEmbed(nn.Module):
    def __init__(self, in_ch=1, dim=64):
        super().__init__(); self.proj=nn.Conv2d(in_ch,dim,4,4)
    def forward(self,x): return self.proj(x)

class SwinEncoder(nn.Module):
    def __init__(self, dims=(64,128,256,512), dropout=.1):
        super().__init__(); self.patch=PatchEmbed(1,dims[0]); self.stages=nn.ModuleList(); self.down=nn.ModuleList()
        for i,d in enumerate(dims):
            self.stages.append(nn.Sequential(WindowAttentionBlock(d,4 if d<512 else 8,8,0,dropout),WindowAttentionBlock(d,4 if d<512 else 8,8,4,dropout)))
            if i<len(dims)-1: self.down.append(nn.Conv2d(d,dims[i+1],2,2))
    def forward(self,x):
        x=self.patch(x); feats=[]
        for i,stage in enumerate(self.stages):
            x=stage(x); feats.append(x)
            if i<len(self.down): x=self.down[i](x)
        return feats

class AttentionGate(nn.Module):
    def __init__(self, gate_ch, skip_ch, inter):
        super().__init__(); self.g=nn.Conv2d(gate_ch,inter,1); self.x=nn.Conv2d(skip_ch,inter,1); self.psi=nn.Sequential(nn.ReLU(inplace=True),nn.Conv2d(inter,1,1),nn.Sigmoid())
    def forward(self,g,x): return x*self.psi(self.g(g)+self.x(x))

class DecoderBlock(nn.Module):
    def __init__(self, in_ch, skip_ch, out_ch, dropout=.1):
        super().__init__(); self.gate=AttentionGate(in_ch,skip_ch,max(out_ch//2,16))
        self.conv=nn.Sequential(nn.Conv2d(in_ch+skip_ch,out_ch,3,padding=1,bias=False),nn.BatchNorm2d(out_ch),nn.ReLU(inplace=True),nn.Dropout2d(dropout),nn.Conv2d(out_ch,out_ch,3,padding=1,bias=False),nn.BatchNorm2d(out_ch),nn.ReLU(inplace=True))
    def forward(self,x,skip):
        x=F.interpolate(x,size=skip.shape[-2:],mode='bilinear',align_corners=False); skip=self.gate(x,skip)
        return self.conv(torch.cat([x,skip],1))

class SwinAttentionUNet(nn.Module):
    def __init__(self,num_landmarks=19,dropout=.15):
        super().__init__(); dims=(64,128,256,512); self.encoder=SwinEncoder(dims,dropout)
        self.bottleneck=nn.Sequential(nn.Conv2d(512,512,3,padding=1),nn.BatchNorm2d(512),nn.GELU(),nn.Dropout2d(dropout))
        self.dec3=DecoderBlock(512,256,256,dropout); self.dec2=DecoderBlock(256,128,128,dropout); self.dec1=DecoderBlock(128,64,64,dropout)
        self.up=nn.Sequential(nn.Upsample(scale_factor=2,mode='bilinear',align_corners=False),nn.Conv2d(64,64,3,padding=1),nn.ReLU(inplace=True),nn.Dropout2d(dropout))
        self.heatmap_head=nn.Conv2d(64,num_landmarks,1); self.offset_head=nn.Conv2d(64,num_landmarks*2,1)
        nn.init.constant_(self.heatmap_head.bias, -6.0)
    def forward(self,x):
        f=self.encoder(x); z=self.bottleneck(f[-1]); z=self.dec3(z,f[2]); z=self.dec2(z,f[1]); z=self.dec1(z,f[0]); z=self.up(z)
        z=F.interpolate(z,size=x.shape[-2:],mode='bilinear',align_corners=False)
        return {'heatmaps':self.heatmap_head(z),'offsets':self.offset_head(z).view(x.shape[0],19,2,*x.shape[-2:])}
