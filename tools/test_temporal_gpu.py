"""Exercise the shipped GLSL on a real compatibility GL context, without game assets.

Tests camera/object separation, animated vertex reprojection, occlusion, reset,
disocclusion, clipping, blur footprint, static-image invariance and TAA edge quality.
"""
import argparse, ast, ctypes as C, json, re
from pathlib import Path
import numpy as np

R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('run');a=ap.parse_args()
assert re.fullmatch('[a-zA-Z0-9-]+',a.run)
out=R/'generated-local/CP09'/a.run;out.mkdir(parents=True,exist_ok=False)
sdl=C.CDLL(str(R/'runtime-local/CP09-r1/SDL2.dll'))
def sf(n,r,*args):
    f=getattr(sdl,n);f.restype=r;f.argtypes=args;return f
U,I,F,P=C.c_uint,C.c_int,C.c_float,C.c_void_p
assert sf('SDL_Init',I,U)(32)==0
window=sf('SDL_CreateWindow',P,C.c_char_p,I,I,I,I,U)(b'Temporal regression',0,0,32,32,10)
ctx=sf('SDL_GL_CreateContext',P,P)(window);assert ctx
get=sf('SDL_GL_GetProcAddress',P,C.c_char_p)
def gl(n,r,*args):
    ptr=get(('gl'+n).encode());assert ptr,n
    return C.WINFUNCTYPE(r,*args)(ptr)
source=(R/'code/renderergl1/tr_ac_temporal_shaders.h').read_text()
programs={}
def shader_text(n):
    body=source.split('static const char *'+n+' =',1)[1].split(';\n',1)[0]
    return ''.join(ast.literal_eval(s) for s in re.findall(r'^\s*("(?:[^"\\]|\\.)*")',body,re.M)).encode()
for name,vs,fs in [('camera','tmScreenVertex','tmCameraFragment'),('object','tmObjectVertex','tmObjectFragment'),('resolve','tmScreenVertex','tmResolveFragment'),('blur','tmScreenVertex','tmBlurFragment'),('copy','tmScreenVertex','tmCopyFragment')]:
    p=gl('CreateProgram',U)()
    for n,kind in [(vs,0x8B31),(fs,0x8B30)]:
        s=gl('CreateShader',U,U)(kind);v=C.c_char_p(shader_text(n))
        gl('ShaderSource',None,U,I,C.POINTER(C.c_char_p),P)(s,1,C.byref(v),None);gl('CompileShader',None,U)(s)
        ok=I();gl('GetShaderiv',None,U,U,C.POINTER(I))(s,0x8B81,C.byref(ok))
        log=C.create_string_buffer(4096);gl('GetShaderInfoLog',None,U,I,P,P)(s,4096,None,log)
        assert ok.value,(n,log.value)
        gl('AttachShader',None,U,U)(p,s)
    gl('LinkProgram',None,U)(p);ok=I();gl('GetProgramiv',None,U,U,C.POINTER(I))(p,0x8B82,C.byref(ok));assert ok.value,name
    programs[name]=p
loc=gl('GetUniformLocation',I,U,C.c_char_p)
def use(n):
    global program
    program=programs[n];gl('UseProgram',None,U)(program)
def ui(n,v):gl('Uniform1i',None,I,I)(loc(program,n.encode()),v)
def uf(n,v):gl('Uniform1f',None,I,F)(loc(program,n.encode()),v)
def uv(n,x,y):gl('Uniform2f',None,I,F,F)(loc(program,n.encode()),x,y)
def um(n,v):
    v=np.asarray(v,np.float32).T.copy();gl('UniformMatrix4fv',None,I,I,U,P)(loc(program,n.encode()),1,0,v.ctypes.data)
tex=[]
def texture(data,linear=False):
    data=np.asarray(data,np.float32);t=U();gl('GenTextures',None,I,C.POINTER(U))(1,C.byref(t));bind(0,t.value)
    for k,v in [(0x2801,0x2601 if linear else 0x2600),(0x2800,0x2601 if linear else 0x2600),(0x2802,0x812F),(0x2803,0x812F)]:gl('TexParameteri',None,U,U,I)(0xDE1,k,v)
    gl('TexImage2D',None,U,I,I,I,I,I,U,U,P)(0xDE1,0,0x8814,data.shape[1],data.shape[0],0,0x1908,0x1406,data.ctypes.data)
    tex.append(t.value);return t.value
def bind(unit,t):gl('ActiveTexture',None,U)(0x84C0+unit);gl('BindTexture',None,U,U)(0xDE1,t)
W=H=96
target=texture(np.zeros((H,W,4),np.float32))
fbo=U();gl('GenFramebuffers',None,I,C.POINTER(U))(1,C.byref(fbo));gl('BindFramebuffer',None,U,U)(0x8D40,fbo)
gl('FramebufferTexture2D',None,U,U,U,U,I)(0x8D40,0x8CE0,0xDE1,target,0)
gl('Viewport',None,I,I,I,I)(0,0,W,H)
begin=gl('Begin',None,U);vertex=gl('Vertex3f',None,F,F,F);end=gl('End',None);mt=gl('MultiTexCoord3f',None,U,F,F,F)
def screen(*render_size):
    uv('size',*(render_size or (W,H)));begin(7)
    for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]:vertex(x,y,0)
    end();return read()
def read():
    data=np.zeros((H,W,4),np.float32);gl('ReadPixels',None,I,I,I,I,U,U,P)(0,0,W,H,0x1908,0x1406,data.ctypes.data)
    assert np.isfinite(data).all();error=gl('GetError',U)();assert error==0,hex(error)
    return data
def rgba(rgb):
    x=np.zeros((H,W,4),np.float32);x[...,:3]=rgb;x[...,3]=1;return x
def projection(near=4,far=4096,fov=80):
    c=1/np.tan(np.deg2rad(fov)/2);return np.array([[c,0,0,0],[0,c,0,0],[0,0,-(far+near)/(far-near),-2*far*near/(far-near)],[0,0,-1,0]],np.float32)
def depth(z,p):return (-p[2,2]+p[2,3]/z+1)*.5
cases=[]
assert gl('GetError',U)()==0,'setup'
# Object pass: camera changes, object does not. The residual motion must be zero.
for fov in [60,80,110]:
    p=projection(fov=fov)
    for camera_x,object_x,weapon in [(0,0,0),(20,0,0),(20,5,0),(0,5,0),(20,0,1)]:
        current=np.eye(4,dtype=np.float32);current[0,3]=-camera_x
        old=np.eye(4,dtype=np.float32)
        use('object');um('currentMVP',p@current);um('previousMVP',p@old);um('currentViewPrevious',p@current);um('weaponPrevious',p@old)
        uv('size',W,H);ui('skin',0);ui('depthTexture',1);ui('objectPass',1);ui('weapon',weapon);ui('reactive',0);uf('alphaCut',-1);uf('identity',7);uf('valid',1)
        bind(0,texture(np.ones((1,1,4),np.float32)))
        d=depth(100,p)*(.3 if weapon else 1);bind(1,texture(rgba(d)))
        gl('DepthRange',None,C.c_double,C.c_double)(0,.3 if weapon else 1)
        gl('ClearColor',None,F,F,F,F)(0,0,0,0);gl('Clear',None,U)(0x4000)
        begin(7)
        for x,y in [(-40,-40),(40,-40),(40,40),(-40,40)]:
            # Weapon remains fixed relative to camera; model vertices translated
            # by camera_x are NOT object animation.
            mt(0x84C1,x,y,-100)
            vertex(x+object_x+(camera_x if weapon else 0),y,-100)
        end();result=read();mask=result[...,3]==7;assert mask.any()
        expected=p[0,0]*object_x/200
        assert abs(np.median(result[...,0][mask])-expected)<2e-6,(fov,camera_x,object_x,weapon,result[H//2,W//2],expected)
        cases.append(dict(kind='object_camera_separation',fov=fov,camera=camera_x,object=object_x,weapon=weapon))
        # Same object behind a wall must write no motion.
        bind(1,texture(rgba(depth(50,p)*(.3 if weapon else 1))))
        gl('Clear',None,U)(0x4000);begin(7)
        for x,y in [(-40,-40),(40,-40),(40,40),(-40,40)]:vertex(x,y,-100)
        end();assert not np.any(read()[...,3])
gl('DepthRange',None,C.c_double,C.c_double)(0,1)
# A deforming surface has different per-vertex motion, not a single rigid
# entity transform. Interpolated velocity must vary continuously with its pose.
p=projection();use('object');um('currentMVP',p);um('previousMVP',p);um('currentViewPrevious',p);um('weaponPrevious',p)
uv('size',W,H);ui('skin',0);ui('depthTexture',1);ui('objectPass',1);ui('weapon',0);ui('reactive',0);uf('alphaCut',-1);uf('identity',7);uf('valid',1)
skin=texture(np.ones((1,1,4),np.float32));dep=texture(rgba(depth(100,p)));bind(0,skin);bind(1,dep)
gl('Clear',None,U)(0x4000);begin(7)
for x,y in [(-40,-40),(40,-40),(40,40),(-40,40)]:
    mt(0x84C1,x-.2*y,y,-100);vertex(x,y,-100)
end();r=read();mask=r[...,3]==7;expected=np.broadcast_to(.1*(2*(np.arange(H)+.5)/H-1)[:,None],(H,W))
# Rasterizer interpolation has subpixel fixed-point precision; allow less than
# 0.0005 pixel error at this resolution, independently of the shader's floats.
assert np.max(abs(r[...,0][mask]-expected[mask]))*W<.0005
cases.append(dict(kind='deformed_vertex_motion'))
# MSAA depth may resolve an off-center sample on a sloping triangle. It must
# match the visible triangle without admitting a genuinely occluded object.
xx=2*(np.arange(W)+.5)/W-1
plane=(-p[2,2]+p[2,3]*(1+.4*xx/p[0,0])/100+1)*.5
slope=p[2,3]*.5*.4/p[0,0]/100*2/W
sampled=np.broadcast_to(plane[None,:]+.375*slope,(H,W))
dep=texture(rgba(sampled[...,None]));bind(0,skin);bind(1,dep)
def sloped_quad():
    gl('Clear',None,U)(0x4000);begin(7)
    for x,y in [(-40,-40),(40,-40),(40,40),(-40,40)]:
        mt(0x84C1,x-5,y,-100+.4*x);vertex(x,y,-100+.4*x)
    end();return read()
uf('sampleRadius',0);assert np.sum(sloped_quad()[...,3]>0)<10
uf('sampleRadius',.5);assert np.sum(sloped_quad()[...,3]>0)>1500
dep=texture(rgba(depth(50,p)));bind(0,skin);bind(1,dep)
assert not np.any(sloped_quad()[...,3])
uf('sampleRadius',0)
cases.append(dict(kind='MSAA_sloped_depth_and_wall_occlusion'))
# Camera reconstruction with jitter and camera translation.
for fov in [60,110]:
    p=projection(fov=fov);p[0,2]=.3/W;p[1,2]=-.7/H
    relative=np.eye(4,dtype=np.float32);relative[0,3]=8
    use('camera');ui('depthTexture',0);ui('objectPass',0);um('previousFromCurrent',relative);um('previousProjection',projection(fov=fov))
    uv('projectionScale',p[0,0],p[1,1]);uv('projectionOffset',p[0,2],p[1,2]);uv('depthReconstruct',p[2,2],p[2,3]);bind(0,texture(rgba(depth(100,p))))
    r=screen();xx=(np.arange(W)+.5)/W;yy=(np.arange(H)+.5)/H
    assert np.max(abs(r[...,0]-(xx[None,:]+p[0,2]*.5+8*p[0,0]/200)))<2e-5
    assert np.max(abs(r[...,1]-(yy[:,None]+p[1,2]*.5)))<2e-5
    cases.append(dict(kind='camera_reprojection',fov=fov))
grid=np.stack(np.meshgrid((np.arange(W)+.5)/W,(np.arange(H)+.5)/H),-1)
motion=np.zeros((H,W,4),np.float32);motion[...,:2]=grid;motion[...,2]=.8;motion[...,3]=1
data=np.zeros_like(motion);data[...,2]=.8
checker=((np.indices((H,W)).sum(axis=0)//4)%2).astype(np.float32)
current=rgba(checker[...,None]);old=rgba(1-checker[...,None])
def resolve(cur,prev,retention=.9,meta=data,prior=data,m=motion,j=(0,0),pj=(0,0)):
    use('resolve');uf('retention',retention);uv('currentJitter',*j);uv('previousJitter',*pj)
    prior=prior.copy();prior[...,:2]=prior[...,2:4]
    for i,(n,x) in enumerate([('currentColor',cur),('oldColor',prev),('motion',m),('objectData',meta),('oldData',prior)]):
        t=texture(x,linear=n in ['currentColor','oldColor']);bind(i,t);ui(n,i)
    # texture() uses unit zero; restore all sampler bindings after allocations.
    for i,t in enumerate(tex[-5:]):bind(i,t)
    return screen()
assert np.max(abs(resolve(current,old,0)-current))<1e-6
occluded=data.copy();occluded[...,2]=.2
assert np.max(abs(resolve(current,old,prior=occluded)-current))<1e-6
different=data.copy();different[...,3]=3
assert np.max(abs(resolve(current,old,prior=different)-current))<1e-6
reactive=data.copy();reactive[...,3]=-1
assert np.max(abs(resolve(current,old,meta=reactive)-current))<1e-6
flat=rgba(.37);assert np.max(abs(resolve(flat,rgba(1))-flat))<.0002
cases.extend([dict(kind=n) for n in ['reset','disocclusion','identity_change','reactive_transparency','neighborhood_clip']])
# An oblique binary edge sampled at Halton offsets. Compare to an 8x8 ground
# truth and require real improvement over unfiltered jittered frames.
def halton(i,b):
    f=1;r=0
    while i:f/=b;r+=f*(i%b);i//=b
    return r
y,x=np.mgrid[:H,:W];reference=np.zeros((H,W))
for sy in range(8):
    for sx in range(8):reference+=((x+(sx+.5)/8)*.63-(y+(sy+.5)/8)+19>0)/64
prev=rgba(0);err=[];raw=[];oldjx=oldjy=0
for frame in range(1,49):
    jx=halton((frame-1)%16+1,2)-.5;jy=halton((frame-1)%16+1,3)-.5
    cur=rgba((((x+.5+jx)*.63-(y+.5+jy)+19)>0)[...,None])
    m=motion.copy();m[...,0]+=(jx-oldjx)/W;m[...,1]+=(jy-oldjy)/H
    prev=resolve(cur,prev,0 if frame==1 else .9,m=m,j=(jx/W,jy/H),pj=(oldjx/W,oldjy/H))
    if frame>16:err.append(float(np.mean(abs(prev[...,0]-reference))));raw.append(float(np.mean(abs(cur[...,0]-reference))))
    oldjx,oldjy=jx,jy
assert np.mean(err)<np.mean(raw)*.85,(np.mean(err),np.mean(raw))
cases.append(dict(kind='TAA_subpixel_edge',taa_error=float(np.mean(err)),raw_error=float(np.mean(raw))))
# Pure camera motion must leave arbitrary image pixels EXACTLY unchanged by MB.
def blur_image(img,obj,strength=1,render_size=()):
    use('blur');uf('shutter',strength);uf('diagnostic',0);ui('image',0);ui('objectData',1)
    a=texture(img,True);b=texture(obj);bind(0,a);bind(1,b);return screen(*render_size)
assert np.max(abs(blur_image(current,data)-current))<1e-6
img=rgba(0);img[20:76,40:56,:3]=1
obj=data.copy();obj[20:76,40:56,0]=20/W;obj[20:76,40:56,2]=.4;obj[20:76,40:56,3]=7
r=blur_image(img,obj)
assert 0.02<r[48,38,0]<r[48,48,0] and r[48,48,0]>.6 and r[48,28,0]<.001, r[48,20:60,0].tolist()
assert np.max(abs(blur_image(img,obj,0)-img))<1e-6
wall=obj.copy();wall[:,0:40,2]=.2
rw=blur_image(img,wall);assert np.max(abs(rw[:,0:40,:3]-img[:,0:40,:3]))<1e-6
cases.extend([dict(kind=n) for n in ['no_camera_blur','moving_silhouette','blur_off','foreground_wall_occlusion']])
# Equal exposure produces the same footprint at 30/60/120 fps.
for ratio in [.5,2.0]:
    scaled=obj.copy();scaled[...,:2]*=ratio
    assert np.max(abs(blur_image(img,scaled,1/ratio)-r))<1e-5
cases.append(dict(kind='frame_rate_independent_exposure'))
# A long blur must occupy the same fraction of the screen at 1080p and UHD,
# rather than being clamped to the same 32 physical pixels at every resolution.
fast=obj.copy();fast[20:76,40:56,0]=.25
hd=blur_image(img,fast,1,(1920,1080));uhd=blur_image(img,fast,1,(3840,2160))
assert np.max(abs(hd-uhd))<1e-5
cases.append(dict(kind='resolution_independent_blur_limit'))

(out/'result.json').write_text(json.dumps(dict(cases=cases),indent=2))
print('PASS',len(cases),'temporal GPU cases',cases[-5:])
sf('SDL_GL_DeleteContext',None,P)(ctx);sf('SDL_DestroyWindow',None,P)(window);sf('SDL_Quit',None)()
