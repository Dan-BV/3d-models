import numpy as np, pyvista as pv, sys
pv.OFF_SCREEN=True
P=np.fromfile('nodes.bin','<f8').reshape(-1,3)*10; T=np.fromfile('tris.bin','<i4').reshape(-1,3)
FIG=pv.PolyData(P,np.c_[np.full(len(T),3),T].ravel())
parts=[('Ground','#c9b48a'),('Log1','#c9b48a'),('Log2','#c9b48a'),('Log3','#c9b48a'),('Kunai1','#c9b48a'),('Kunai2','#c9b48a')]
def shot(fn,vec,zoom=1.3,fig=True,color=False,size=(1000,1000)):
    pl=pv.Plotter(off_screen=True,window_size=size); pl.set_background('#f4f1ec',top='#ffffff')
    if fig: pl.add_mesh(FIG,color='#efd9b4',smooth_shading=True,specular=0.15)
    for n,c in parts:
        m=pv.read(f'tg_{n}.stl')
        if color: c={'Ground':'#7da34a','Log1':'#8b5a2b','Log2':'#8b5a2b','Log3':'#8b5a2b','Kunai1':'#5d6670','Kunai2':'#5d6670'}[n]
        pl.add_mesh(m,color=c,smooth_shading=False,specular=0.2)
    pl.view_vector(vec,viewup=(0,0,1)); pl.reset_camera(); pl.camera.zoom(zoom)
    pl.screenshot(fn); pl.close()
out=sys.argv[1]
shot(out+'/training_iso.png',(0.55,-1,0.5),color=False)
shot(out+'/training_painted.png',(-0.6,-1,0.45),color=True)
shot(out+'/training_base_top.png',(0.35,-0.8,1.0),fig=False,zoom=1.35)
print('ok')
