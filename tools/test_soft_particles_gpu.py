"""GPU regression of the actual soft-particle shader: depth, FOV, viewport and texture layers."""
import argparse, ast, ctypes as C, json, re
from pathlib import Path
import numpy as np

R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('--source',type=Path,default=R/'code/renderergl1/tr_ac_lighting.c');a=ap.parse_args()
assert re.fullmatch('[a-zA-Z0-9-]+',a.run)
out=R/'generated-local/CP09'/a.run;out.mkdir(parents=True,exist_ok=False)
sdl=C.CDLL(str(R/'runtime-local/CP09-r1/SDL2.dll'))
def sf(name,ret,*args):
    f=getattr(sdl,name);f.restype=ret;f.argtypes=args;return f
assert sf('SDL_Init',C.c_int,C.c_uint)(32)==0
window=sf('SDL_CreateWindow',C.c_void_p,C.c_char_p,C.c_int,C.c_int,C.c_int,C.c_int,C.c_uint)(b'Particle regression',0,0,16,16,10)
ctx=sf('SDL_GL_CreateContext',C.c_void_p,C.c_void_p)(window);assert ctx
get=sf('SDL_GL_GetProcAddress',C.c_void_p,C.c_char_p)
U,I,F,P=C.c_uint,C.c_int,C.c_float,C.c_void_p
def gl(name,ret,*args):
    ptr=get(('gl'+name).encode());assert ptr,name
    return C.WINFUNCTYPE(ret,*args)(ptr)
shader=gl('CreateShader',U,U);source=gl('ShaderSource',None,U,I,C.POINTER(C.c_char_p),P)
compile_=gl('CompileShader',None,U);get_shader=gl('GetShaderiv',None,U,U,C.POINTER(I))
program=gl('CreateProgram',U)();attach=gl('AttachShader',None,U,U)
text=a.source.read_text()
for name,kind in [('particleVertex',0x8B31),('particleFragment',0x8B30)]:
 body=text.split('static const char *'+name+' =',1)[1].split(';\n',1)[0]
 data=''.join(ast.literal_eval(s) for s in re.findall(r'^\s*("(?:[^"\\]|\\.)*")',body,re.M)).encode()
 sh=shader(kind);v=C.c_char_p(data);source(sh,1,C.byref(v),None);compile_(sh)
 ok=I();get_shader(sh,0x8B81,C.byref(ok));assert ok.value,(name,data)
 attach(program,sh)
gl('LinkProgram',None,U)(program);ok=I();gl('GetProgramiv',None,U,U,C.POINTER(I))(program,0x8B82,C.byref(ok));assert ok.value
gl('UseProgram',None,U)(program)
loc=gl('GetUniformLocation',I,U,C.c_char_p)
def ui(n,v):gl('Uniform1i',None,I,I)(loc(program,n.encode()),v)
ui('skin',0);ui('skin2',1);ui('sceneDepth',2);ui('fogEnabled',0)
active=gl('ActiveTexture',None,U);bind=gl('BindTexture',None,U,U)
tex=(U*4)();gl('GenTextures',None,I,C.POINTER(U))(4,tex)
upload=gl('TexImage2D',None,U,I,I,I,I,I,U,U,P)
for i,t in enumerate(tex):
 active(0x84C0+min(i,2));bind(0x0DE1,t)
 for k,v in [(0x2801,0x2600),(0x2800,0x2600),(0x2802,0x812F),(0x2803,0x812F)]:gl('TexParameteri',None,U,U,I)(0x0DE1,k,v)
 if i<2:
  data=np.array([[[.5,.4,.3,.8] if i==0 else [.8,.7,.6,.5]]],np.float32)
  upload(0x0DE1,0,0x8814,1,1,0,0x1908,0x1406,data.ctypes.data)
fbo=U();gl('GenFramebuffers',None,I,C.POINTER(U))(1,C.byref(fbo));gl('BindFramebuffer',None,U,U)(0x8D40,fbo)
bind(0x0DE1,tex[3]);upload(0x0DE1,0,0x8814,512,512,0,0x1908,0x1406,None)
gl('FramebufferTexture2D',None,U,U,U,U,I)(0x8D40,0x8CE0,0x0DE1,tex[3],0)
begin=gl('Begin',None,U);vertex=gl('Vertex3f',None,F,F,F);end=gl('End',None)
mode=gl('MatrixMode',None,U);identity=gl('LoadIdentity',None);load=gl('LoadMatrixf',None,P)
mode(0x1700);identity();gl('Color4f',None,F,F,F,F)(1,1,1,1)
results=[]
for near,far,fov in [(4,4096,80),(1,8192,110),(8,40000,60)]:
 cot=1/np.tan(np.deg2rad(fov)*.5);A=-(far+near)/(far-near);B=-2*far*near/(far-near)
 proj=np.array([[cot,0,0,0],[0,cot,0,0],[0,0,A,B],[0,0,-1,0]],np.float32).T.copy()
 mode(0x1701);load(proj.ctypes.data)
 gl('Uniform2f',None,I,F,F)(loc(program,b'projection'),A,B)
 for x,y,w,h in [(0,0,256,256),(17,11,320,240)]:
  gl('Viewport',None,I,I,I,I)(x,y,w,h)
  gl('Uniform4f',None,I,F,F,F,F)(loc(program,b'viewport'),x,y,w,h)
  for texture_mode in [0,1,2]:
   ui('textureMode',texture_mode)
   for gap in [-1,0,1,3,6,30]:
    for distance in [50,500,2000]:
     scene=distance+gap;d=(-A+B/scene+1)*.5
     data=np.full((h,w),d,np.float32);active(0x84C2);bind(0x0DE1,tex[2]);upload(0x0DE1,0,0x822E,w,h,0,0x1903,0x1406,data.ctypes.data)
     active(0x84C0);bind(0x0DE1,tex[0]);active(0x84C1);bind(0x0DE1,tex[1]);active(0x84C0)
     gl('Clear',None,U)(0x4000)
     begin(7)
     for vx,vy in [(-1,-1),(1,-1),(1,1),(-1,1)]:vertex(vx*distance,vy*distance,-distance)
     end()
     pixel=np.zeros(4,np.float32);gl('ReadPixels',None,I,I,I,I,U,U,P)(x+w//2,y+h//2,1,1,0x1908,0x1406,pixel.ctypes.data)
     t=np.clip(gap/6,0,1);fade=t*t*(3-2*t);expected=.8*(.5 if texture_mode else 1)*fade
     assert abs(pixel[3]-expected)<.035,(near,far,gap,distance,texture_mode,pixel,expected)
     rgb=np.array([.5,.4,.3]);b=np.array([.8,.7,.6]);rgb=rgb if texture_mode==0 else rgb*b if texture_mode==1 else rgb+b
     assert np.max(abs(pixel[:3]-rgb))<.002,(pixel,rgb)
     results.append(dict(near=near,far=far,gap=gap,distance=distance,mode=texture_mode,alpha=float(pixel[3])))
fog_color=np.array([.1,.2,.3,1],np.float32)
gl('Fogfv',None,U,P)(0x0B66,fog_color.ctypes.data)
gl('Fogf',None,U,F)(0x0B63,100)
gl('Fogf',None,U,F)(0x0B64,1000)
ui('textureMode',0);ui('fogEnabled',1)
data=np.ones((h,w),np.float32)
active(0x84C2);bind(0x0DE1,tex[2]);upload(0x0DE1,0,0x822E,w,h,0,0x1903,0x1406,data.ctypes.data)
active(0x84C0)
for distance in [50,100,400,1000,2000]:
 gl('Clear',None,U)(0x4000);begin(7)
 for vx,vy in [(-1,-1),(1,-1),(1,1),(-1,1)]:vertex(vx*distance,vy*distance,-distance)
 end();pixel=np.zeros(4,np.float32)
 gl('ReadPixels',None,I,I,I,I,U,U,P)(x+w//2,y+h//2,1,1,0x1908,0x1406,pixel.ctypes.data)
 f=np.clip((1000-distance)/900,0,1)
 assert np.max(abs(pixel[:3]-(fog_color[:3]*(1-f)+np.array([.5,.4,.3])*f)))<.002,pixel
 assert abs(pixel[3]-.8)<.002,('Background depth must not fade particles',pixel)
assert gl('GetError',U)()==0
(out/'result.json').write_text(json.dumps(dict(cases=len(results),fog_background_cases=5,results=results),indent=2))
print('PASS actual particle GLSL',len(results),'depth / projection / viewport / texture cases')
sf('SDL_GL_DeleteContext',None,P)(ctx);sf('SDL_DestroyWindow',None,P)(window);sf('SDL_Quit',None)()
