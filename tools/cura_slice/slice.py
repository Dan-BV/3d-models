import numpy as np, sys, subprocess, zipfile, re, os, time
S=os.path.dirname(os.path.abspath(__file__))
CURA=r'C:\Program Files\UltiMaker Cura 5.13.0'
R=CURA+r'\share\cura\resources'
prof, tag = sys.argv[1], sys.argv[2]
over = dict(a.split('=',1) for a in sys.argv[3:])
# translated STL centred on bed (110,110)
stl=S+'/naruto_c.stl'
if not os.path.exists(stl):
    P=np.fromfile(S+'/nodes.bin','<f8').reshape(-1,3)*10
    T=np.fromfile(S+'/tris.bin','<i4').reshape(-1,3)
    V=P[T].astype('<f4')
    nrm=np.cross(V[:,1]-V[:,0],V[:,2]-V[:,0]); nrm/=np.maximum(np.linalg.norm(nrm,axis=1,keepdims=True),1e-12)
    rec=np.zeros(len(T),dtype=[('n','<f4',3),('v','<f4',(3,3)),('a','<u2')]); rec['n']=nrm; rec['v']=V
    with open(stl,'wb') as f: f.write(b'\0'*80); f.write(np.uint32(len(T)).tobytes()); f.write(rec.tobytes())
vals={}
z=zipfile.ZipFile(prof)
for n in z.namelist():
    sec=z.read(n).decode().split('[values]')[1]
    for l in sec.strip().splitlines():
        k,v=[s.strip() for s in l.split('=',1)]; vals[k]=v
vals.pop('adhesion_z_offset',None)
vals.update(over); vals['center_object']='false'
out=S+f'/{tag}.gcode'
sys.path.insert(0,S); import curaeval
gv,ev=curaeval.resolve(vals)
import json
def wr(name,inh,vals):
    p=S+'/'+name+'.def.json'
    json.dump({"version":2,"name":name,"inherits":inh,"metadata":{},"overrides":{k:{"default_value":v} for k,v in vals.items() if v is not None}},open(p,'w'))
    return p
gj=wr('g_'+tag,'creality_ender3pro',gv); ej=wr('e_'+tag,'creality_base_extruder_0',ev)
cmd=[CURA+r'\CuraEngine.exe','slice','-j',gj,'-e0','-j',ej]
cmd+=['-l',stl,'-o',out]
t=time.time(); p=subprocess.run(cmd,capture_output=True,text=True,env=dict(os.environ,CURA_ENGINE_SEARCH_PATH=R+r'\definitions;'+R+r'\extruders'))
print('engine rc',p.returncode,'%.0fs'%(time.time()-t))
if p.returncode: print(p.stdout[-2000:], p.stderr[-3000:]); sys.exit(1)
# parse support extrusion points
typ=None; zc=0; x=y=0; pts=[]; W=[]
for l in open(out):
    if l.startswith(';TYPE:'): typ=l[6:].strip(); continue
    if l.startswith('G1') or l.startswith('G0'):
        m={}
        for t in l.split(';')[0].split()[1:]:
            if t[0] in 'XYZE':
                try: m[t[0]]=float(t[1:])
                except ValueError: pass
        x=m.get('X',x); y=m.get('Y',y); zc=m.get('Z',zc)
        if 'E' in m and typ and typ.startswith('SUPPORT'): pts.append((x,y,zc))
        if 'E' in m and typ=='WALL-OUTER': W.append((x,y))
pts=np.array(pts) if pts else np.zeros((0,3))
W=np.array(W); ox=(W[:,0].min()+W[:,0].max())/2; oy=(W[:,1].min()+W[:,1].max())/2
if len(pts): pts[:,0]-=ox; pts[:,1]-=oy
print('offset',ox,oy)
print('support points',len(pts))
for tx,ty,tz in [(25.2,10.1,57.1),(24.2,7.8,54.1),(20.9,7.6,47.1),(18.4,11.9,46.1)]:
    m=(np.hypot(pts[:,0]-tx,pts[:,1]-ty)<3)&(pts[:,2]<tz)&(pts[:,2]>tz-3) if len(pts) else np.array([])
    print(f' ribbon tip ({tx},{ty}) z={tz}: support below -> {"YES" if m.sum() else "NO"} ({int(m.sum())})')
for line in open(out):
    if line.startswith(';TIME:') or line.startswith(';Filament used'): print(line.strip())
