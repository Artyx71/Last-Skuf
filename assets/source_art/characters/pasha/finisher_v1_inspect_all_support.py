from pathlib import Path
from PIL import Image
from collections import deque
import json,hashlib,sys,shutil
r=Path(__file__).resolve().parents[4];w=r/'.autopilot/worktrees/P06';d=Path(__file__).parent;raw=d/'finisher_master_v1.png';replacement=d.parent/'action-left-fire-v2/left_fire_master_v2.png';im=Image.open(raw).convert('RGBA');mask=im.getchannel('A').point(lambda a:255 if a>=128 else 0);data=bytes(mask.get_flattened_data());width,height=im.size;assert (width,height)==(1536,1024);seen=bytearray(width*height);components=[];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Analysis finds complete rectangles only. NO silhouette/component masks are
# pasted or edited; contaminated rectangle LEFT7 is explicitly NOT reused.
for start,alpha in enumerate(data):
 if not alpha or seen[start]:continue
 q=deque([start]);seen[start]=1;x0=x1=start%width;y0=y1=start//width;area=0
 while q:
  i=q.popleft();x=i%width;y=i//width;area+=1;x0=min(x0,x);x1=max(x1,x);y0=min(y0,y);y1=max(y1,y)
  for j in ([i-1] if x else [])+([i+1] if x+1<width else [])+([i-width] if y else [])+([i+width] if y+1<height else []):
   if data[j] and not seen[j]:seen[j]=1;q.append(j)
 components.append({'area':area,'box':[x0,y0,x1+1,y1+1]})

print(sorted(components,key=lambda c:c["area"]))
