import numpy as np, json, math
from shapely.geometry import Polygon, Point, LineString, MultiPoint
from shapely.ops import unary_union
from shapely import affinity
FIT=0.05          # pocket offset per side, mm
C=(-2.9,-4.0); R_LOW=42; R_UP=37
EMB_C=(-2.9,-29.0); EMB_S=1.0
feet=[Polygon(p).buffer(FIT,join_style=2) for p in json.load(open('feet_outline.json'))]
# Konoha emblem (unit design ~ radius 8), tip toward +45 deg
def emblem():
    body=MultiPoint([(8*math.cos(t),8*math.sin(t)) for t in np.linspace(0,2*math.pi,180)]+[(14.5*math.cos(math.radians(50)),14.5*math.sin(math.radians(50)))]).convex_hull
    a1,a2,ap=math.radians(170),math.radians(225),math.radians(198)
    tri=Polygon([(7.6*math.cos(a1),7.6*math.sin(a1)),(12.5*math.cos(ap),12.5*math.sin(ap)),(7.6*math.cos(a2),7.6*math.sin(a2))])
    plate=unary_union([body,tri])
    # spiral groove
    th=np.linspace(0,2.6*2*math.pi,400); r=0.6+5.6*th/th[-1]
    ang=th+math.radians(50)-th[-1]  # end of spiral heads toward tip
    sp=LineString(np.c_[r*np.cos(ang),r*np.sin(ang)])
    # extend spiral end out to the tip
    end=np.array(sp.coords[-1]); tipdir=np.array([math.cos(math.radians(50)),math.sin(math.radians(50))])
    groove=unary_union([sp.buffer(0.55,cap_style=1), LineString([end,end+tipdir*5.5]).buffer(0.55,cap_style=1)]).intersection(plate.buffer(-1.0))
    return plate, groove
plate,groove=emblem()
plate=affinity.translate(affinity.scale(plate,EMB_S,EMB_S,origin=(0,0)),*EMB_C)
groove=affinity.translate(affinity.scale(groove,EMB_S,EMB_S,origin=(0,0)),*EMB_C)
if __name__=='__main__':
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(7,7))
    def draw(g,**k):
        gs=getattr(g,'geoms',[g])
        for q in gs: x,y=q.exterior.xy; ax.fill(x,y,**k)
    draw(Point(C).buffer(R_LOW),fc='#ddd',ec='k')
    draw(Point(C).buffer(R_UP),fc='#eee',ec='k')
    draw(plate,fc='#f90',ec='k'); draw(groove,fc='#333')
    for f in feet: draw(f,fc='#48c',ec='k')
    print('emblem bounds',np.round(plate.bounds,1),'min gap emblem-feet',round(min(plate.distance(f) for f in feet),2),'emblem inside upper tier margin',round(R_UP-max(Point(C).distance(Point(p)) for p in plate.exterior.coords),2))
    ax.set_aspect('equal'); plt.savefig('stand2d.png',dpi=80)
