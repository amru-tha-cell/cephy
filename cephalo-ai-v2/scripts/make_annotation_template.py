"""Create an empty CSV template for 19-point annotations.
Usage: python scripts/make_annotation_template.py images/ --output annotations_template.csv
Fill x0,y0 ... x18,y18 with pixel coordinates in the original image.
"""
import argparse,csv
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('image_dir');p.add_argument('--output',default='annotations_template.csv');a=p.parse_args()
files=sorted(x.name for x in Path(a.image_dir).iterdir() if x.suffix.lower() in {'.png','.jpg','.jpeg','.tif','.tiff','.bmp'})
with open(a.output,'w',newline='') as f:
 w=csv.writer(f);w.writerow(['image']+[v for i in range(19) for v in (f'x{i}',f'y{i}')]);[w.writerow([name]+['']*38) for name in files]
print(f'Created {a.output} with {len(files)} image rows. Fill in the verified annotation coordinates.')
