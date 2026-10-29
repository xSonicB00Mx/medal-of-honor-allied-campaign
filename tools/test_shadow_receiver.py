"""GPU regression: actual shadow shader on a fixed, sloped receiver plane.

Changing camera scale/shear must not erase shallow contact shadows or admit a
second receiver. No original assets; hidden SDL GL context, isolated outputs.
"""
import argparse, ast, ctypes as C, json, re
from pathlib import Path
import numpy as np

R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('--source',type=Path,default=R/'code/renderergl1/tr_ac_shadows.c');a=ap.parse_args()
assert re.fullmatch('[a-zA-Z0-9-]+',a.run)
out=R/'generated-local/CP09'/a.run;out.mkdir(parents=True,exist_ok=False)
sdl=C.CDLL(str(R/'runtime-local/CP09-r1/SDL2.dll'))
def sf(name,ret,*args):
    f=getattr(sdl,name);f.restype=ret;f.argtypes=args;return f
assert sf('SDL_Init',C.c_int,C.c_uint)(32)==0
window=sf('SDL_CreateWindow',C.c_void_p,C.c_char_p,C.c_int,C.c_int,C.c_int,C.c_int,C.c_uint)(b'Shadow regression',0,0,16,16,10)
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
for name,kind in [('vertexShader',0x8B31),('shadowShader',0x8B30)]:
    body=text.split('static const char *'+name+' =',1)[1].split('\nstatic ',1)[0]
    data=''.join(ast.literal_eval(s) for s in re.findall(r'^\s*("(?:[^"\\]|\\.)*")',body,re.M)).encode()
    sh=shader(kind);s=C.c_char_p(data);source(sh,1,C.byref(s),None);compile_(sh)
    ok=I();get_shader(sh,0x8B81,C.byref(ok));assert ok.value,name
    attach(program,sh)
gl('LinkProgram',None,U)(program)
ok=I();gl('GetProgramiv',None,U,U,C.POINTER(I))(program,0x8B82,C.byref(ok));assert ok.value
gl('UseProgram',None,U)(program)
loc=gl('GetUniformLocation',I,U,C.c_char_p)
def uf(name,value):gl('Uniform1f',None,I,F)(loc(program,name.encode()),value)
def matrix(name,m):
    v=np.ascontiguousarray(m.T,dtype=np.float32)
    gl('UniformMatrix4fv',None,I,I,U,P)(loc(program,name.encode()),1,0,v.ctypes.data)
for name,unit in [('silhouette',0),('receiver',1)]:gl('Uniform1i',None,I,I)(loc(program,name.encode()),unit)
uf('opacity',.4);uf('blurStep',2/1024);uf('fogStart',0);uf('fogEnd',0)
matrix('lightMatrix',np.eye(4))
tex=(U*3)();gl('GenTextures',None,I,C.POINTER(U))(3,tex)
active=gl('ActiveTexture',None,U);bind=gl('BindTexture',None,U,U)
upload=gl('TexImage2D',None,U,I,I,I,I,I,U,U,P)
for i,t in enumerate(tex):
    active(0x84C0+min(i,1));bind(0x0DE1,t)
    for p,v in [(0x2801,0x2600),(0x2800,0x2600),(0x2802,0x812F),(0x2803,0x812F)]:gl('TexParameteri',None,U,U,I)(0x0DE1,p,v)
fbo=U();gl('GenFramebuffers',None,I,C.POINTER(U))(1,C.byref(fbo));gl('BindFramebuffer',None,U,U)(0x8D40,fbo)
bind(0x0DE1,tex[2]);upload(0x0DE1,0,0x8814,256,256,0,0x1908,0x1406,None)
gl('FramebufferTexture2D',None,U,U,U,U,I)(0x8D40,0x8CE0,0x0DE1,tex[2],0)
gl('Viewport',None,I,I,I,I)(0,0,256,256)
begin=gl('Begin',None,U);vertex=gl('Vertex3f',None,F,F,F);end=gl('End',None)
read=gl('ReadPixels',None,I,I,I,I,U,U,P)
uv=np.stack(np.meshgrid((np.arange(1024)+.5)/1024,(np.arange(1024)+.5)/1024),-1)
results=[]
for gradient in [(.3,.2),(.7,-.4)]:
    plane=.5+np.sum((uv-.5)*gradient,axis=-1)
    for case,gap,front_gap,expected in [('contact',.001,0,.4),('clear',-.01,0,0),('coplanar',0,0,0),('blocked',.05,.02,0)]:
        for unit,values in [(0,plane-gap),(1,plane-front_gap)]:
            values=np.ascontiguousarray(values,dtype=np.float32)
            active(0x84C0+unit);bind(0x0DE1,tex[unit]);upload(0x0DE1,0,0x822E,1024,1024,0,0x1903,0x1406,values.ctypes.data)
        values=[]
        for scale,shear,perspective in [(.35,0,0),(.7,.7,0),(1.5,-.6,0),(3,0,0),(.7,.5,.6),(1.5,-.5,-.6)]:
            m=np.eye(4);m[0,0]=scale;m[1,1]=scale;m[0,2]=shear*scale
            m[3,0]=perspective;m[3,1]=perspective*.5
            matrix('mvp',m)
            gl('ClearColor',None,F,F,F,F)(0,0,0,0);gl('Clear',None,U)(0x4000)
            begin(7)
            for x,y in [(-.8,-.8),(.8,-.8),(.8,.8),(-.8,.8)]:vertex(x,y,gradient[0]*x+gradient[1]*y)
            end()
            pixels=np.empty((8,8,4),dtype=np.float32);read(124,124,8,8,0x1908,0x1406,pixels.ctypes.data)
            values.append(float(pixels[:,:,3].mean()))
        results.append(dict(gradient=gradient,case=case,expected=expected,alpha=values))
        assert all(abs(v-expected)<.002 for v in values),results[-1]
assert gl('GetError',U)()==0
(out/'result.json').write_text(json.dumps(results,indent=2)+'\n')
sf('SDL_GL_DeleteContext',None,C.c_void_p)(ctx);sf('SDL_DestroyWindow',None,C.c_void_p)(window);sf('SDL_Quit',None)()
print('PASS: 48 fixed-light receiver cases across camera scales/shears/perspectives')
