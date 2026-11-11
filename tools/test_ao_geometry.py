"""Run the actual GL1 AO shaders against analytic geometry, without game assets.

Hidden SDL/OpenGL context; outputs stay under generated-local. The ground plane
must not occlude itself, and a convex box must not acquire a dark outline on its
exposed faces. Fixed world-space contact probes are compared across camera views.
This is a numerical regression, not a substitute for native visual inspection.
"""
import argparse
import ast
import ctypes as C
import json
from pathlib import Path
import re
import numpy as np
from PIL import Image

R = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument('run')
ap.add_argument('--source', type=Path, default=R/'code/renderergl1/tr_ac_ao.c')
a = ap.parse_args()
assert re.fullmatch('[a-zA-Z0-9-]+', a.run)
out = R/'generated-local/CP09'/a.run
out.mkdir(parents=True, exist_ok=False)
sdl = C.CDLL(str(R/'runtime-local/CP09-r1/SDL2.dll'))
def sf(name, ret, *args):
    fn = getattr(sdl, name); fn.restype = ret; fn.argtypes = args; return fn
assert sf('SDL_Init', C.c_int, C.c_uint)(32) == 0
window = sf('SDL_CreateWindow', C.c_void_p, C.c_char_p, C.c_int, C.c_int, C.c_int, C.c_int, C.c_uint)(b'AO regression', 0, 0, 16, 16, 10)
context = sf('SDL_GL_CreateContext', C.c_void_p, C.c_void_p)(window)
assert context
get = sf('SDL_GL_GetProcAddress', C.c_void_p, C.c_char_p)
def gl(name, ret, *args):
    ptr = get(('gl'+name).encode()); assert ptr, name
    return C.WINFUNCTYPE(ret, *args)(ptr)
U, I, F, P = C.c_uint, C.c_int, C.c_float, C.c_void_p
shader = gl('CreateShader', U, U)
source = gl('ShaderSource', None, U, I, C.POINTER(C.c_char_p), P)
compile_ = gl('CompileShader', None, U)
get_shader = gl('GetShaderiv', None, U, U, C.POINTER(I))
create_program = gl('CreateProgram', U)
attach = gl('AttachShader', None, U, U)
link = gl('LinkProgram', None, U)
use = gl('UseProgram', None, U)
loc = gl('GetUniformLocation', I, U, C.c_char_p)
uniform1i = gl('Uniform1i', None, I, I)
uniform1f = gl('Uniform1f', None, I, F)
uniform2f = gl('Uniform2f', None, I, F, F)
gen_tex = gl('GenTextures', None, I, C.POINTER(U))
bind_tex = gl('BindTexture', None, U, U)
tex_image = gl('TexImage2D', None, U, I, I, I, I, I, U, U, P)
tex_param = gl('TexParameteri', None, U, U, I)
gen_fbo = gl('GenFramebuffers', None, I, C.POINTER(U))
bind_fbo = gl('BindFramebuffer', None, U, U)
attach_tex = gl('FramebufferTexture2D', None, U, U, U, U, I)
active = gl('ActiveTexture', None, U)
viewport = gl('Viewport', None, I, I, I, I)
begin = gl('Begin', None, U); end = gl('End', None)
vertex = gl('Vertex3f', None, F, F, F)
read = gl('ReadPixels', None, I, I, I, I, U, U, P)
get_error = gl('GetError', U)
enable = gl('Enable', None, U)
disable = gl('Disable', None, U)
depth_func = gl('DepthFunc', None, U)
clear_color = gl('ClearColor', None, F, F, F, F)
clear = gl('Clear', None, U)

text = a.source.read_text()
def program(fragment):
    p = create_program()
    for name, kind in [('screenVertex', 0x8B31), (fragment, 0x8B30)]:
        body = text.split('static const char *'+name+' =', 1)[1].split('\nstatic ', 1)[0]
        strings = re.findall(r'^\s*("(?:[^"\\]|\\.)*")', body, re.M)
        data = ''.join(ast.literal_eval(s) for s in strings).encode()
        sh = shader(kind); src = C.c_char_p(data)
        source(sh, 1, C.byref(src), None); compile_(sh)
        ok = I(); get_shader(sh, 0x8B81, C.byref(ok)); assert ok.value, name
        attach(p, sh)
    link(p)
    return p
horizon, filter_, composite = program('horizonFragment'), program('filterFragment'), program('compositeFragment')
W, H = 640, 480
scale = np.array([1.0, W/H])
uv = np.stack(np.meshgrid((np.arange(W)+.5)/W, (np.arange(H)+.5)/H), -1)
rays_view = np.concatenate([(uv*2-1)/scale, -np.ones((H,W,1))], -1)
tex = (U*3)(); gen_tex(3, tex)
for t in tex:
    bind_tex(0x0DE1, t)
    for name, value in [(0x2801,0x2600),(0x2800,0x2600),(0x2802,0x812F),(0x2803,0x812F)]:
        tex_param(0x0DE1, name, value)
    tex_image(0x0DE1, 0, 0x8814, W, H, 0, 0x1908, 0x1406, None)
fbo = U(); gen_fbo(1, C.byref(fbo)); bind_fbo(0x8D40, fbo)
viewport(0,0,W,H)

def render(g):
    active(0x84C0); bind_tex(0x0DE1, tex[0])
    tex_image(0x0DE1,0,0x8814,W,H,0,0x1908,0x1406,g.ctypes.data)
    for p, dst, src, direction in [(horizon,1,0,None),(filter_,2,1,(1,0)),(filter_,1,2,(0,1))]:
        attach_tex(0x8D40,0x8CE0,0x0DE1,tex[dst],0)
        use(p); uniform1i(loc(p,b'scene'),0)
        uniform2f(loc(p,b'size'),W,H); uniform2f(loc(p,b'projectionScale'),*scale)
        if direction:
            active(0x84C1); bind_tex(0x0DE1,tex[src]); active(0x84C0)
            uniform1i(loc(p,b'ao'),1); uniform2f(loc(p,b'direction'),*direction)
        begin(7)
        for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]: vertex(x,y,0)
        end()
    result = np.empty((H,W,4),np.float32)
    read(0,0,W,H,0x1908,0x1406,result.ctypes.data)
    assert get_error()==0
    return result[:,:,0]

def scene(eye, box, turn=0):
    eye=np.array(eye, float); target=np.array([0,0,8.])
    forward=target-eye; forward/=np.linalg.norm(forward)
    turn=np.deg2rad(turn)
    forward=np.array([[np.cos(turn),-np.sin(turn),0],[np.sin(turn),np.cos(turn),0],[0,0,1]])@forward
    right=np.cross(forward,[0,0,1]); right/=np.linalg.norm(right)
    up=np.cross(right,forward); basis=np.array([right,up,-forward])
    rays=rays_view@basis
    with np.errstate(divide='ignore',invalid='ignore'):
        depth=-eye[2]/rays[:,:,2]
    depth=np.where(depth>0,depth,np.inf)
    normals=np.zeros((H,W,3)); normals[:,:,2]=1
    if box:
        lo=np.array([-10,-10,0.]); hi=np.array([10,10,30.])
        with np.errstate(divide='ignore',invalid='ignore'):
            t0=(lo-eye)/rays; t1=(hi-eye)/rays
        near=np.minimum(t0,t1); far=np.maximum(t0,t1)
        enter=near.max(2); leave=far.min(2)
        hit=(enter>0)&(enter<leave)&(enter<depth)
        axis=np.argmax(near,axis=2)
        box_normals=np.eye(3)[axis]*(-np.sign(rays))
        normals[hit]=box_normals[hit]; depth[hit]=enter[hit]
    valid=np.isfinite(depth)
    positions=eye+rays*np.where(valid,depth,0)[:,:,None]
    g=np.zeros((H,W,4),np.float32)
    g[:,:,:3]=normals@basis.T; g[:,:,3]=np.where(valid,depth,0)
    return g,positions,normals,valid

rows=[]
for pitch in [15,35,60]:
    for yaw in [0,30,60]:
        angle=np.deg2rad(yaw); elevation=np.deg2rad(pitch)
        eye=[120*np.cos(angle)*np.cos(elevation),120*np.sin(angle)*np.cos(elevation),120*np.sin(elevation)+8]
        for box in [False,True]:
            g,pos,n,valid=scene(eye,box); ao=render(g)
            # Exposed top / distant flat floor have no blocking geometry.
            free=valid & ((pos[:,:,2]>29.9) | ((pos[:,:,2]<.01)&(np.linalg.norm(pos[:,:,:2],axis=2)>50)))
            if not box: free=valid
            contact=valid & (pos[:,:,2]<.01) & (np.abs(pos[:,:,0]-14)<2) & (np.abs(pos[:,:,1])<8)
            row=dict(pitch=pitch,yaw=yaw,box=box,free_min=float(ao[free].min()),free_mean=float(ao[free].mean()),
                     contact_mean=float(ao[contact].mean()) if contact.any() else None)
            rows.append(row)
            Image.fromarray(np.uint8(np.clip(ao[::-1],0,1)*255)).save(out/f'{pitch}-{yaw}-{int(box)}.png')
for turn in [-30,-15,0,15,30]:
    g,pos,n,valid=scene([100,0,70],True,turn)
    ao=render(g)
    contact=valid & (pos[:,:,2]<.01) & (np.abs(pos[:,:,0]-14)<2) & (np.abs(pos[:,:,1])<4)
    rows.append(dict(turn=turn,contact_mean=float(ao[contact].mean()),pixels=int(contact.sum())))
# Retreat continuously from the same 20x20x30 prop. Integrate the full local
# floor contact, normalized by projected area: it must not disappear at a fixed
# camera distance. Pixel coverage is necessarily finite for a tiny distant
# object; this test checks retention, not perfect sub-pixel motion stability.
distance_rows=[]
for distance in [120,240,480,720,960,1200,1440,1680,1920,2160,2400,2640,2880]:
    g,pos,n,valid=scene([distance,0,distance*.6+8],True)
    ao=render(g)
    floor=valid & (pos[:,:,2]<.01) & (np.linalg.norm(pos[:,:,:2],axis=2)<50)
    mass=float((1-ao[floor]).sum()*distance*distance/(W*H))
    distance_rows.append(dict(distance=distance,contact_mass=mass,contact_pixels=int(floor.sum())))
    if distance in [120,960,1920,2880]:
        Image.fromarray(np.uint8(np.clip(ao[::-1],0,1)*255)).save(out/f'distance-{distance}.png')
(out/'distance.json').write_text(json.dumps(distance_rows,indent=2)+'\n')
assert all(r['contact_mass']>.05 for r in distance_rows), 'Distant contact AO disappeared'
# At a depth discontinuity, the old dFdx-based compositor bias pulled a hidden
# background surface onto a foreground pixel. A flat surface just behind the
# window depth must stay hidden, including the last column at its silhouette.
window_depth=U(); gen_tex(1,C.byref(window_depth))
bind_tex(0x0DE1,window_depth)
z=np.full((H,W),.8,np.float32)
tex_image(0x0DE1,0,0x81A6,W,H,0,0x1902,0x1406,z.ctypes.data)
attach_tex(0x8D40,0x8D00,0x0DE1,window_depth,0)
edge=W//2+1
source_depth=np.full((H,W,4),.8,np.float32); source_depth[:,:edge]=.80005
active(0x84C1); bind_tex(0x0DE1,tex[0])
tex_image(0x0DE1,0,0x8814,W,H,0,0x1908,0x1406,source_depth.ctypes.data)
active(0x84C0); bind_tex(0x0DE1,tex[1])
zero=np.zeros((H,W,4),np.float32)
tex_image(0x0DE1,0,0x8814,W,H,0,0x1908,0x1406,zero.ctypes.data)
attach_tex(0x8D40,0x8CE0,0x0DE1,tex[2],0)
clear_color(1,1,1,1); clear(0x4000); enable(0x0B71); depth_func(0x0203)
use(composite); uniform1i(loc(composite,b'ao'),0); uniform1i(loc(composite,b'sceneDepth'),1)
uniform2f(loc(composite,b'size'),W,H); uniform2f(loc(composite,b'depthReconstruct'),-1,-8)
uniform1f(loc(composite,b'diagnostic'),1); uniform1f(loc(composite,b'fogEnd'),0)
begin(7)
for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]: vertex(x,y,0)
end()
result=np.empty((H,W,4),np.float32)
read(0,0,W,H,0x1908,0x1406,result.ctypes.data)
assert get_error()==0
rows.append(dict(composite_hidden_edge_min=float(result[:,:edge,0].min()),
                 composite_visible_mean=float(result[:,edge:,0].mean())))
Image.fromarray(np.uint8(np.clip(result[::-1,:,:3],0,1)*255)).save(out/'depth-discontinuity.png')
print(json.dumps(rows,indent=2))
(out/'result.json').write_text(json.dumps(rows,indent=2)+'\n')
# Test the real temporal shader separately: retained distant contacts, correct
# camera reprojection, disocclusion/normal rejection, history reset, and a bound
# on ghosting when the occluder leaves a receiver whose depth did not change.
temporal=program('temporalFragment')
uniform_matrix=gl('UniformMatrix4fv',None,I,I,C.c_ubyte,P)
hist=(U*5)();gen_tex(5,hist)
for t in hist:
    bind_tex(0x0DE1,t)
    for name,value in [(0x2801,0x2600),(0x2800,0x2600),(0x2802,0x812F),(0x2803,0x812F)]:tex_param(0x0DE1,name,value)
    tex_image(0x0DE1,0,0x8814,W,H,0,0x1908,0x1406,None)
attach_tex(0x8D40,0x8CE0,0x0DE1,hist[4],0)
disable(0x0B71)
g=np.zeros((H,W,4),np.float32);g[:,:,2]=1;g[:,:,3]=100
identity=np.eye(4,dtype=np.float32)
projection=np.zeros((4,4),np.float32)
projection[0,0]=scale[0];projection[1,1]=scale[1];projection[2,2]=-1;projection[2,3]=-8;projection[3,2]=-1
def temporal_render(current,old_ao,old_g=None,retention=.8,transform=identity):
    for unit,data in enumerate([g,current,g if old_g is None else old_g,old_ao]):
        active(0x84C0+unit);bind_tex(0x0DE1,hist[unit]);data=np.ascontiguousarray(data,dtype=np.float32)
        tex_image(0x0DE1,0,0x8814,W,H,0,0x1908,0x1406,data.ctypes.data)
    use(temporal)
    for i,name in enumerate([b'scene',b'ao',b'oldScene',b'oldAO']):uniform1i(loc(temporal,name),i)
    uniform1f(loc(temporal,b'retention'),retention)
    uniform2f(loc(temporal,b'size'),W,H);uniform2f(loc(temporal,b'projectionScale'),*scale)
    for name,matrix in [(b'previousFromCurrent',transform),(b'previousProjection',projection)]:
        matrix=np.ascontiguousarray(matrix.T);uniform_matrix(loc(temporal,name),1,0,matrix.ctypes.data)
    begin(7)
    for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]:vertex(x,y,0)
    end()
    result=np.empty((H,W,4),np.float32);read(0,0,W,H,0x1908,0x1406,result.ctypes.data)
    assert get_error()==0
    return result
old=np.full_like(g,.8);values=[];raw=[]
for frame in range(30):
    value=.77 if frame%2 else .83
    old=temporal_render(np.full_like(g,value),old)
    values.append(float(old[H//2,W//2,0]));raw.append(value)
ratio=float(np.std(values[10:])/np.std(raw[10:]))
assert ratio<.2,('Unstable distant AO',ratio)
current=np.full_like(g,.9);old=np.full_like(g,.3)
wrong_depth=g.copy();wrong_depth[:,:,3]=120
wrong_normal=g.copy();wrong_normal[:,:,:3]=[0,1,0]
checks={}
for name,old_g,retention in [('depth',wrong_depth,.8),('normal',wrong_normal,.8),('reset',g,0)]:
    result=temporal_render(current,old,old_g,retention)
    checks[name]=float(np.max(np.abs(result[:,:,:3]-.9)))
    assert checks[name]<1e-6,('History leaked',name)
released=temporal_render(np.ones_like(g),np.full_like(g,.3))
assert released[:,:,0].min()>=.935, 'Trailing shadow exceeds clipping bound'
gradient=np.broadcast_to(np.linspace(.3,.7,W,dtype=np.float32)[None,:,None],(H,W,4)).copy()
transform=identity.copy();transform[0,3]=400/W
reprojected=temporal_render(gradient,gradient,transform=transform)
expected=.2*gradient[H//2,W//2,0]+.8*gradient[H//2,W//2+2,0]
assert abs(reprojected[H//2,W//2,0]-expected)<1e-6,'Wrong camera reprojection'
(out/'temporal.json').write_text(json.dumps(dict(variation_ratio=ratio,rejection_errors=checks,
    release_min=float(released[:,:,0].min()),camera_reprojection=True),indent=2)+'\n')
sf('SDL_GL_DeleteContext',None,C.c_void_p)(context)
sf('SDL_DestroyWindow',None,C.c_void_p)(window)
sf('SDL_Quit',None)()
assert all(r.get('free_min',1)>.999 for r in rows), 'False AO on unoccluded analytic surfaces'
turns=[r['contact_mean'] for r in rows if 'turn' in r]
assert max(turns)-min(turns)<.006, 'AO changes with camera yaw at fixed position'
assert rows[-1]['composite_hidden_edge_min']>.99, 'AO leaks across foreground silhouette'
assert .44<rows[-1]['composite_visible_mean']<.46, 'Visible AO was lost'
