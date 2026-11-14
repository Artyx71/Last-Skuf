#!/usr/bin/env python3
"""Palette-assisted clothing anchor candidates, no edits to any character pixels.

A source/layout SHA binds each candidate. ART must inspect the diagnostic and
actual clothing overlay; opaque pixels alone do not establish anatomical quality.
"""
import argparse, hashlib, json
from collections import deque
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[3]
# Gabar's maroon garment candidates. Palette overlap with hair is checked visually;
# explicit metadata overrides below correct the one ambiguous component.
GABAR_SHIRT={tuple(bytes.fromhex(h)) for h in ['4e202c','67243b','963450','994a63','8b3146','bc6573','c04b66','6d354b']}
OLEZHKA_SHIRT={tuple(bytes.fromhex(h)) for h in ['4c3c56','352b3d']}

def anchor(frame, palette=GABAR_SHIRT):
    remaining={(x,y) for y in range(64) for x in range(48)
               if frame.getpixel((x,y))[3] and frame.getpixel((x,y))[:3] in palette}
    components=[]
    while remaining:
        first=remaining.pop();queue=deque([first]);component=[first]
        while queue:
            x,y=queue.popleft()
            for p in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
                if p in remaining:
                    remaining.remove(p);queue.append(p);component.append(p)
        components.append(component)
    assert components,'No authored garment component'
    component=max(components,key=lambda c:(len(c),-min(y for x,y in c),-min(x for x,y in c)))
    center=tuple(sum(p[a] for p in component)/len(component) for a in [0,1])
    chosen=min(component,key=lambda p:((p[0]-center[0])**2+(p[1]-center[1])**2,p[1],p[0]))
    return chosen,len(component)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('actor',choices=['gabar','olezhka']);parser.add_argument('--output',default='reports/phases/P06/author-checks/socket-candidates-01');args=parser.parse_args()
    folder=ROOT/'game/assets/art/characters'/args.actor
    diagnostics=(ROOT/args.output).resolve();assert diagnostics.is_relative_to(ROOT/'reports/phases/P06');assert not diagnostics.exists();diagnostics.mkdir()
    for kind in ['world','action','finisher']:
        target=folder/(kind+'.sockets.json');assert not target.exists(),'Preserve annotations; use an explicit reviewed revision'
        layout=json.loads((folder/(kind+'.json')).read_text());source=folder/(kind+'_sheet.png')
        assert hashlib.sha256(source.read_bytes()).hexdigest()==layout['sha256']
        image=Image.open(source).convert('RGBA');board=Image.new('RGBA',image.size,(36,48,44,255));board.alpha_composite(image);draw=ImageDraw.Draw(board)
        entries=[]
        for i in range(32):
            x,y=i%8*48,i//8*64
            frame=image.crop((x,y,x+48,y+64));point,pixels=anchor(frame,GABAR_SHIRT if args.actor=='gabar' else OLEZHKA_SHIRT)
            entries.append({'index':i,'clothing':list(point),'garment_component_pixels':pixels,'source_frame_rgba_sha256':hashlib.sha256(frame.tobytes()).hexdigest()})
            px,py=x+point[0],y+point[1]
            draw.line((px-2,py,px+2,py),fill='#7bd2df');draw.line((px,py-2,px,py+2),fill='#7bd2df')
        if args.actor=='gabar' and kind=='finisher':
            entry=entries[19];entry['palette_candidate_clothing']=entry['clothing'];entry['clothing']=[20,32]
            entry['annotation_note']='Manual torso correction after inspecting the diagnostic: palette shared with hair made the automatic component choose the head.'
        data={'schema':1,'actor_id':args.actor,'kind':kind,'sheet_sha256':layout['sha256'],'status':'CANDIDATE_REQUIRES_ACTUAL_OVERLAY_ART_REVIEW','method':'largest connected authored garment palette component, nearest opaque garment pixel to centroid; metadata only, no bitmap changes','garment_palette':[list(color) for color in sorted(GABAR_SHIRT if args.actor=='gabar' else OLEZHKA_SHIRT)],'frames':entries}
        if args.actor=='gabar' and kind=='finisher': data['manual_overrides']={'19':{'from':[21,18],'to':[20,32],'reason':'visible maroon torso, not hair'}}
        target.write_text(json.dumps(data,indent=2)+'\n')
        board.resize((1536,1024),Image.Resampling.NEAREST).save(diagnostics/(kind+'_anchors_4x.png'))
        print(kind,[(e['index'],e['clothing']) for e in entries])
if __name__=='__main__':main()
