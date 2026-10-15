import numpy as np, json
from shapely.geometry import LineString, Polygon, MultiPolygon
from shapely.ops import polygonize, unary_union
P=np.fromfile('nodes.bin','<f8').reshape(-1,3)*10
T=np.fromfile('tris.bin','<i4').reshape(-1,3)
V=P[T]; zs=V[:,:,2]
def section(z):
    m=(zs.min(1)<z)&(zs.max(1)>z); segs=[]
    for t in V[m]:
        pts=[]
        for i in range(3):
            a,b=t[i],t[(i+1)%3]
            if (a[2]-z)*(b[2]-z)<0:
                s=(z-a[2])/(b[2]-a[2]); pts.append(tuple(np.round(a[:2]+s*(b[:2]-a[:2]),5)))
        if len(pts)==2: segs.append(LineString(pts))
    polys=list(polygonize(unary_union(segs)))
    return unary_union([Polygon(p.exterior) for p in polys])
U=unary_union([section(z) for z in np.arange(0.3,2.6,0.2)])
U=U.buffer(0.3).buffer(-0.3)  # close tiny notches
geoms=list(U.geoms) if isinstance(U,MultiPolygon) else [U]
geoms=[Polygon(g.exterior) for g in geoms if g.area>20]
out=[]
for g in sorted(geoms,key=lambda g:g.centroid.x):
    s=g.simplify(0.03)
    c=np.array(s.exterior.coords)
    print('foot centroid %.2f %.2f area %.1f bounds %s pts %d'%(g.centroid.x,g.centroid.y,g.area,np.round(g.bounds,2),len(c)))
    out.append(c.tolist())
json.dump(out,open('feet_outline.json','w'))
# max outline also up to 3.0 for clearance check
U3=unary_union([section(z) for z in np.arange(2.6,3.2,0.2)])
print('z2.6-3.0 inside z0.3-2.5 outline?', U3.difference(U.buffer(0.01)).area)
