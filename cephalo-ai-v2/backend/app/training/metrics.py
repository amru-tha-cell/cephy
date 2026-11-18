import numpy as np

def localization_metrics(pred, truth, thresholds=(2, 2.5, 3, 4)):
    """Pixel-space mean radial error and SDR, with per-landmark error breakdown."""
    p=np.asarray(pred,dtype=float); t=np.asarray(truth,dtype=float)
    if p.shape != t.shape or p.ndim != 2 or p.shape[1] != 2:
        raise ValueError('Predictions and ground truth must both have shape (N, 2).')
    distances=np.linalg.norm(p-t,axis=-1)
    valid=np.isfinite(distances)
    d=distances[valid]
    per_landmark=[{'index':i,'error_px':float(distances[i]) if np.isfinite(distances[i]) else None} for i in range(len(distances))]
    if not len(d): return {'mre':None,'sd':None,'sdr':{},'count':0,'per_landmark':per_landmark}
    return {'mre':float(d.mean()),'sd':float(d.std()),
            'sdr':{str(x):float((d<=x).mean()*100) for x in thresholds},
            'count':int(len(d)),'per_landmark':per_landmark}
