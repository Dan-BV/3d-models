import json, math, os, re
R=r'C:\Program Files\UltiMaker Cura 5.13.0\share\cura\resources'
def load(path):
    d=json.load(open(path,encoding='utf-8'))
    chain=[d]
    while 'inherits' in chain[-1]:
        base=chain[-1]['inherits']
        for sub in ('definitions','extruders'):
            p=os.path.join(R,sub,base+'.def.json')
            if os.path.exists(p): chain.append(json.load(open(p,encoding='utf-8'))); break
    return chain[::-1]
def flatten(settings,out):
    for k,v in settings.items():
        out[k]={kk:vv for kk,vv in v.items() if kk!='children'}
        if 'children' in v: flatten(v['children'],out)
def build(chain):
    defs={}
    for d in chain:
        if 'settings' in d:
            for cat in d['settings'].values():
                flatten(cat.get('children',{}),defs)
    for d in chain:
        for k,ov in d.get('overrides',{}).items():
            defs.setdefault(k,{}).update(ov)
    return defs
class Stack:
    def __init__(self,defs,user,parent=None):
        self.defs=defs;self.user=user;self.parent=parent;self.cache={}
    def get(self,k):
        if k in self.cache: return self.cache[k]
        if k in self.user: v=self.user[k]
        else:
            d=self.defs.get(k)
            if d is None:
                if self.parent: return self.parent.get(k)
                raise KeyError(k)
            if 'value' in d: v=self.ev(d['value'])
            else: v=d.get('default_value')
        self.cache[k]=v; return v
    def ev(self,expr):
        s=self
        class NS(dict):
            def __missing__(_,key):
                if key in g: return g[key]
                try: return s.get(key)
                except KeyError:
                    raise NameError(key)
        g={'math':math,'extruderValue':lambda e,k: EXT.get(k),'extruderValues':lambda k:[EXT.get(k)],
           'resolveOrValue':lambda k:s.get(k),'defaultExtruderPosition':lambda:'0','valueFromContainer':lambda *a:0,
           'anyExtruderWithMaterial':lambda k:'0','anyExtruderNrWithOrDefault':lambda k:'0','extruderValueFromContainer':lambda e,k,c:EXT.get(k),
           'max':max,'min':min,'round':round,'int':int,'float':float,'sum':sum,'len':len,'any':any,'all':all,'map':map,'abs':abs,'str':str,'list':list,'sorted':sorted,'True':True,'False':False,'None':None}
        if isinstance(expr,str):
            return eval(expr,g,NS())
        return expr
def norm(v):
    if isinstance(v,str):
        try: return json.loads(v.replace("'",'"')) if v.strip().startswith('[') else (float(v) if re.fullmatch(r'-?\d+(\.\d+)?',v.strip()) else ({'True':True,'False':False}.get(v,v)))
        except Exception: return v
    return v
FAIL=[]
def resolve(user):
    global EXT
    u={k:norm(v) for k,v in user.items()}
    gdefs=build(load(os.path.join(R,'definitions','creality_ender3pro.def.json')))
    edefs_chain=load(os.path.join(R,'extruders','creality_base_extruder_0.def.json'))
    edefs=dict(gdefs); 
    for k,v in build(edefs_chain).items(): edefs.setdefault(k,{}).update(v)
    G=Stack(gdefs,u); EXT=Stack(edefs,u,G)
    gv={};ev={}
    for name,st,out in (('g',G,gv),('e',EXT,ev)):
        for k,d in (gdefs if name=='g' else edefs).items():
            if d.get('type') in ('category',None) : continue
            try: out[k]=st.get(k)
            except Exception as ex: FAIL.append((name,k,repr(ex)[:80]))
    return gv,ev
def fmt(v):
    if isinstance(v,bool): return 'true' if v else 'false'
    if isinstance(v,float): return repr(round(v,6))
    if isinstance(v,(list,dict)): return json.dumps(v)
    return str(v)
