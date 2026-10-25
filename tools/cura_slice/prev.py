import numpy as np, sys, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
typ=None;x=y=z=0;S=[];W=[]
for l in open(sys.argv[1]):
    if l.startswith(';TYPE:'): typ=l[6:].strip();continue
    if l[:2] in('G0','G1'):
        m={}
        for t in l.split(';')[0].split()[1:]:
            try:m[t[0]]=float(t[1:])
            except:pass
        x=m.get('X',x);y=m.get('Y',y);z=m.get('Z',z)
        if 'E' in m and typ:
            if typ.startswith('SUPPORT'): S.append((x,y,z))
            elif typ=='WALL-OUTER': W.append((x,y,z))
S=np.array(S);W=np.array(W)[::4]
fig=plt.figure(figsize=(14,8))
for i,(el,az) in enumerate([(12,-60),(12,30),(12,120)]):
    ax=fig.add_subplot(1,3,i+1,projection='3d')
    ax.scatter(W[:,0],W[:,1],W[:,2],s=0.08,c='#d33',alpha=0.35,depthshade=False)
    ax.scatter(S[:,0],S[:,1],S[:,2],s=0.15,c='#08a',alpha=0.9,depthshade=False)
    ax.view_init(el,az); ax.set_box_aspect((np.ptp(W[:,0]),np.ptp(W[:,1]),np.ptp(W[:,2]))); ax.set_axis_off()
plt.tight_layout(); plt.savefig(sys.argv[2],dpi=100); print('ok')
