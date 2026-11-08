/* Allied Campaign weather exposure. GPL-2.0-or-later.
 * A transient scene effect, never a player preference or archived cvar.
 * Normal fog stays intact during thunder. Architectural roof depth separates
 * covered rooms from exposed surfaces independently of the camera, including
 * the exterior seen through a window. Expose before TAA/blur so the scene and
 * its mask are reconstructed together; the HUD is drawn after both passes.
 */
#include "tr_local.h"
#include "SDL.h"

#define LIGHTNING_ROOF_SIZE 4096
#define LT_GL(X) \
 X(void,GenFramebuffers,(GLsizei n,GLuint *p)) \
 X(void,DeleteFramebuffers,(GLsizei n,const GLuint *p)) \
 X(void,BindFramebuffer,(GLenum t,GLuint f)) \
 X(void,FramebufferTexture2D,(GLenum t,GLenum a,GLenum tt,GLuint tex,GLint l)) \
 X(GLenum,CheckFramebufferStatus,(GLenum t)) \
 X(GLuint,CreateShader,(GLenum t)) \
 X(void,ShaderSource,(GLuint s,GLsizei n,const char **text,const GLint *len)) \
 X(void,CompileShader,(GLuint s)) \
 X(void,GetShaderiv,(GLuint s,GLenum p,GLint *v)) \
 X(void,GetShaderInfoLog,(GLuint s,GLsizei n,GLsizei *l,char *log)) \
 X(void,DeleteShader,(GLuint s)) \
 X(GLuint,CreateProgram,(void)) \
 X(void,AttachShader,(GLuint p,GLuint s)) \
 X(void,LinkProgram,(GLuint p)) \
 X(void,GetProgramiv,(GLuint p,GLenum n,GLint *v)) \
 X(void,GetProgramInfoLog,(GLuint p,GLsizei n,GLsizei *l,char *log)) \
 X(void,DeleteProgram,(GLuint p)) \
 X(void,UseProgram,(GLuint p)) \
 X(GLint,GetUniformLocation,(GLuint p,const char *s)) \
 X(void,Uniform1i,(GLint u,GLint v)) \
 X(void,Uniform1f,(GLint u,GLfloat v)) \
 X(void,Uniform2f,(GLint u,GLfloat x,GLfloat y)) \
 X(void,Uniform4f,(GLint u,GLfloat x,GLfloat y,GLfloat z,GLfloat w)) \
 X(void,UniformMatrix4fv,(GLint u,GLsizei n,GLboolean t,const GLfloat *m)) \
 X(void,PushAttrib,(GLbitfield b)) X(void,PopAttrib,(void)) \
 X(void,PushClientAttrib,(GLbitfield b)) X(void,PopClientAttrib,(void)) \
 X(void,ReadBuffer,(GLenum b))
#define DECL(ret,name,args) static ret (APIENTRYP lt##name) args;
LT_GL(DECL)
#undef DECL

static float pendingFlash;
static viewParms_t flashView;
static GLuint framebuffer,sceneDepth,roofDepth,program;
static int depthWidth,depthHeight,framebufferSamples;
static qboolean attempted,ready,dumped;

static const char *lightningVertex=
    "#version 120\n"
    "varying vec2 uv; void main(){gl_Position=gl_Vertex;uv=gl_Vertex.xy*0.5+0.5;}\n";
static const char *lightningFragment=
    "#version 120\n"
    "uniform sampler2D sceneDepth,roofDepth; uniform mat4 inverseView;\n"
    "uniform vec4 projection,roofBounds; uniform vec2 depthPair,roofZ,depthTexel;\n"
    "uniform float exposure,roofResolution,sampleRadius; varying vec2 uv;\n"
    // Reject cross-object edges before deriving an MSAA receiver-plane slope.
    "float neighborStep(vec2 at,float d,float z){\n"
    " float n=texture2D(sceneDepth,at).r;float nz=-depthPair.y/(n*2.0-1.0+depthPair.x);\n"
    " if(n>=1.0 || abs(nz-z)>max(2.0,abs(z)*0.01))return -1.0;return abs(n-d);}\n"
    "float planeStep(float a,float b){if(a<0.0)return max(b,0.0);if(b<0.0)return a;return min(a,b);}\n"
    "vec3 worldAt(vec2 at,float z){\n"
    " vec3 eye=vec3(-(at*2.0-1.0+projection.zw)*z/projection.xy,z);\n"
    " return (inverseView*vec4(eye,1.0)).xyz;}\n"
    // Fragment-quad derivatives can join an indoor wall to a nearer object
    // and invent an outward-facing normal along its silhouette. Choose the
    // closest contiguous depth neighbor on each axis instead. When neither
    // side belongs to this surface, return zero and keep the unoffset query.
    "vec3 surfaceStep(vec2 offset,vec3 world,float z){\n"
    " vec2 a=uv-offset,b=uv+offset;\n"
    " float da=texture2D(sceneDepth,a).r,db=texture2D(sceneDepth,b).r;\n"
    " float za=-depthPair.y/(da*2.0-1.0+depthPair.x),zb=-depthPair.y/(db*2.0-1.0+depthPair.x);\n"
    " float ea=abs(za-z),eb=abs(zb-z),limit=max(2.0,abs(z)*0.01);\n"
    " bool va=da<1.0 && ea<=limit && all(greaterThanEqual(a,vec2(0.0)));\n"
    " bool vb=db<1.0 && eb<=limit && all(lessThanEqual(b,vec2(1.0)));\n"
    " if(va && (!vb || ea<=eb))return world-worldAt(a,za);\n"
    " if(vb)return worldAt(b,zb)-world;return vec3(0.0);}\n"
    // Filter visibility, never raw heights: interpolating roof depth invents
    // sloped roofs between an eave and empty sky. Each of the four neighboring
    // texel centers gets its own receiver-plane comparison before blending.
    "vec2 roofVisibility(vec2 tap,vec2 at,vec3 probe,vec3 normal){\n"
    " float top=texture2D(roofDepth,tap).r;float height=roofZ.x-top*roofZ.y;\n"
    " vec2 delta=(tap-at)/roofBounds.zw;float plane=probe.z;\n"
    // Use the same bounded vertical projection as the ceiling depth pass.
    " if(abs(normal.z)>0.25)plane-=dot(normal.xy,delta)/normal.z;\n"
    // A visible architectural underside is itself cover. Its matching roof
    // plane lies exactly -2/normal.z above the two-unit normal-offset probe.
    // Reconstruct that proven surface continuously at a rasterized roof edge;
    // do not turn its outline into a row of partially covered roof texels.
    // This narrow plane match cannot turn an unrelated actor/leaf into a roof.
    " float ownCover=0.0;\n"
    " if(top<1.0 && normal.z< -0.25 && abs(height-plane+2.0/normal.z)<=0.125)ownCover=1.0;\n"
    " return vec2(float(top>=1.0 || plane+0.5>=height),ownCover);}\n"
    "void main(){\n"
    " float d=texture2D(sceneDepth,uv).r;\n"
    // Use the actual projection, including this frame's TAA jitter.
    " float z=-depthPair.y/(d*2.0-1.0+depthPair.x);\n"
    " vec3 world=worldAt(uv,z);\n"
    " vec3 normal=cross(surfaceStep(vec2(depthTexel.x,0.0),world,z),surfaceStep(vec2(0.0,depthTexel.y),world,z));\n"
    " normal*=inversesqrt(max(dot(normal,normal),1.0e-20));\n"
    " if(dot(normal,inverseView[3].xyz-world)<0.0)normal=-normal;\n"
    // View weapons have artificial 0..0.3 depth: query their player's location,
    // never pretend their reconstructed depth is a real point in the map.
    " if(d<=0.300001){world=inverseView[3].xyz;normal=vec3(0.0);}\n"
    // A facade query moves toward its visible side, outside its own roof.
    // Interior wall queries move INTO the room and remain covered.
    " vec3 probe=world+normal*2.0;\n"
    " vec2 roofUV=(probe.xy-roofBounds.xy)*roofBounds.zw;\n"
    " float outdoor=0.0;\n"
    " if(all(greaterThan(roofUV,vec2(0.0)))&&all(lessThan(roofUV,vec2(1.0)))){\n"
    // One-texel bilinear footprint anti-aliases architectural coverage. A
    // binary nearest sample made a continuous rock overhang's outline turn
    // into regular sawteeth at close range. No screen-space blur or distant
    // probe can carry an exterior flash across an unrelated interior edge.
    "  vec2 grid=roofUV*roofResolution-0.5;vec2 weight=fract(grid);\n"
    "  vec2 base=(floor(grid)+0.5)/roofResolution;float stepUV=1.0/roofResolution;\n"
    "  vec2 a=roofVisibility(base,roofUV,probe,normal);\n"
    "  vec2 b=roofVisibility(base+vec2(stepUV,0.0),roofUV,probe,normal);\n"
    "  vec2 c=roofVisibility(base+vec2(0.0,stepUV),roofUV,probe,normal);\n"
    "  vec2 e=roofVisibility(base+vec2(stepUV),roofUV,probe,normal);\n"
    "  outdoor=mix(mix(a.x,b.x,weight.x),mix(c.x,e.x,weight.x),weight.y);\n"
    "  if(a.y+b.y+c.y+e.y>0.0)outdoor=0.0;\n"
    " }\n"
    " if(d>=1.0)outdoor=1.0;\n"
    // A copied MSAA depth is one sample, not the pixel-center plane. Permit
    // only that plane's subpixel slope (and one depth-quantization step), or a
    // slanted branch lights different numbers of samples in alternating bands.
    // Independent neighbor rejection plus a two-world-unit cap prevents an
    // outside background depth from advancing through a nearby window frame.
    " float guard=1.0/16777215.0;\n"
    " if(d<1.0 && sampleRadius>0.0){\n"
    "  float dx=planeStep(neighborStep(uv-vec2(depthTexel.x,0.0),d,z),neighborStep(uv+vec2(depthTexel.x,0.0),d,z));\n"
    "  float dy=planeStep(neighborStep(uv-vec2(0.0,depthTexel.y),d,z),neighborStep(uv+vec2(0.0,depthTexel.y),d,z));\n"
    "  float distance=max(-z,1.0);float limit=abs(depthPair.y)/(distance*max(distance-2.0,1.0));\n"
    "  guard+=min(sampleRadius*(dx+dy),limit);\n"
    " }\n"
    " gl_FragDepth=d>=1.0?1.0:max(d-guard,0.0);\n"
    " gl_FragColor=vec4(1.0,1.0,1.0,exposure*outdoor);\n"
    "}\n";

static GLuint LightningCompile(GLenum type,const char *source) {
    GLint ok;char log[1024];GLuint shader=ltCreateShader(type);
    ltShaderSource(shader,1,&source,NULL);ltCompileShader(shader);
    ltGetShaderiv(shader,GL_COMPILE_STATUS,&ok);
    if(!ok){ltGetShaderInfoLog(shader,sizeof(log),NULL,log);ri.Printf(PRINT_WARNING,"AC lightning shader: %s\n",log);ltDeleteShader(shader);return 0;}
    return shader;
}
static void LightningInit(void) {
    qboolean loaded=qtrue;GLint ok;GLuint vs,fs;char log[1024];
    if(attempted)return;attempted=qtrue;
#define LOAD(ret,name,args) lt##name=(ret(APIENTRYP)args)SDL_GL_GetProcAddress("gl" #name);if(!lt##name)loaded=qfalse;
    LT_GL(LOAD)
#undef LOAD
    if(!loaded||!qglActiveTextureARB||!qglClientActiveTextureARB||glConfig.numTextureUnits<2
        ||glConfig.maxTextureSize<LIGHTNING_ROOF_SIZE)return;
    vs=LightningCompile(GL_VERTEX_SHADER,lightningVertex);fs=LightningCompile(GL_FRAGMENT_SHADER,lightningFragment);
    if(vs&&fs){
        program=ltCreateProgram();ltAttachShader(program,vs);ltAttachShader(program,fs);ltLinkProgram(program);
        ltGetProgramiv(program,GL_LINK_STATUS,&ok);
        if(!ok){ltGetProgramInfoLog(program,sizeof(log),NULL,log);ri.Printf(PRINT_WARNING,"AC lightning link: %s\n",log);ltDeleteProgram(program);program=0;}
    }
    if(vs)ltDeleteShader(vs);if(fs)ltDeleteShader(fs);
    if(!program)return;
    ltGenFramebuffers(1,&framebuffer);qglGenTextures(1,&sceneDepth);qglGenTextures(1,&roofDepth);
    ready=qtrue;
}
static void LightningTexture(GLuint texture,int width,int height) {
    qglBindTexture(GL_TEXTURE_2D,texture);
    qglTexImage2D(GL_TEXTURE_2D,0,GL_DEPTH_COMPONENT24,width,height,0,GL_DEPTH_COMPONENT,GL_UNSIGNED_INT,NULL);
    qglTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST);
    qglTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST);
    qglTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE);
    qglTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE);
}
/* Allocate on the first normal world frame/resolution change, not during the
 * first strike. Map-independent storage survives map loads, not GL shutdown. */
static void LightningPrepare(void) {
    GLint oldFbo,oldDraw,oldRead;
    LightningInit();
    if(!ready||(depthWidth==flashView.viewportWidth&&depthHeight==flashView.viewportHeight))return;
    qglGetIntegerv(GL_FRAMEBUFFER_BINDING,&oldFbo);
    qglGetIntegerv(GL_DRAW_BUFFER,&oldDraw);qglGetIntegerv(GL_READ_BUFFER,&oldRead);
    qglGetIntegerv(GL_SAMPLES,&framebufferSamples);
    ltPushAttrib(GL_ALL_ATTRIB_BITS);qglActiveTextureARB(GL_TEXTURE0_ARB);
    LightningTexture(sceneDepth,flashView.viewportWidth,flashView.viewportHeight);
    LightningTexture(roofDepth,LIGHTNING_ROOF_SIZE,LIGHTNING_ROOF_SIZE);
    ltBindFramebuffer(GL_FRAMEBUFFER,framebuffer);qglDrawBuffer(GL_NONE);ltReadBuffer(GL_NONE);
    ltFramebufferTexture2D(GL_FRAMEBUFFER,GL_DEPTH_ATTACHMENT,GL_TEXTURE_2D,roofDepth,0);
    if(ltCheckFramebufferStatus(GL_FRAMEBUFFER)!=GL_FRAMEBUFFER_COMPLETE){
        ri.Printf(PRINT_WARNING,"AC lightning roof framebuffer unavailable; sky-only flash enabled.\n");ready=qfalse;
    }
    depthWidth=flashView.viewportWidth;depthHeight=flashView.viewportHeight;
    ltBindFramebuffer(GL_FRAMEBUFFER,oldFbo);qglDrawBuffer(oldDraw);ltReadBuffer(oldRead);ltPopAttrib();
}
void R_ACLightningReset(void) {
    pendingFlash=0;
    if(framebuffer&&ltDeleteFramebuffers)ltDeleteFramebuffers(1,&framebuffer);
    if(sceneDepth)qglDeleteTextures(1,&sceneDepth);
    if(roofDepth)qglDeleteTextures(1,&roofDepth);
    if(program&&ltDeleteProgram)ltDeleteProgram(program);
    framebuffer=sceneDepth=roofDepth=program=0;depthWidth=depthHeight=framebufferSamples=0;attempted=ready=dumped=qfalse;
}
void RB_ACLightningBegin(void) {
    pendingFlash=0;
    if(!tr.world||backEnd.viewParms.isPortal||backEnd.viewParms.isPortalSky
        ||(backEnd.refdef.rdflags&(RDF_NOWORLDMODEL|RDF_HUD))||backEnd.isHyperspace)return;
    pendingFlash=Com_Clamp(0,1,backEnd.refdef.acLightning);
    flashView=backEnd.viewParms;
    if(flashView.viewportWidth>0&&flashView.viewportHeight>0)LightningPrepare();
}
static void LightningInverseView(const float *view,float *inverse) {
    int row,col;memset(inverse,0,16*sizeof(float));
    for(row=0;row<3;row++)for(col=0;col<3;col++)inverse[col*4+row]=view[row*4+col];
    for(row=0;row<3;row++)inverse[12+row]=-(inverse[row]*view[12]+inverse[4+row]*view[13]+inverse[8+row]*view[14]);
    inverse[15]=1;
}
static void LightningRoofMatrix(float *matrix,vec3_t lo,vec3_t hi) {
    int i;
    // A fixed whole-map grid avoids both view-angle changes and moving cascade
    // boundaries. It covers distant exterior visible through any window. 4096
    // texels keep the checked AA/BT maps' roof footprints below four map units.
    for(i=0;i<2;i++){
        lo[i]=floorf((tr.world->nodes->mins[i]-32.0f)/32.0f)*32.0f;
        hi[i]=ceilf((tr.world->nodes->maxs[i]+32.0f)/32.0f)*32.0f;
    }
    lo[2]=fminf(tr.world->nodes->mins[2],flashView.ori.origin[2])-256.0f;
    hi[2]=fmaxf(tr.world->nodes->maxs[2],flashView.ori.origin[2])+256.0f;
    memset(matrix,0,16*sizeof(float));
    matrix[0]=2.0f/(hi[0]-lo[0]);matrix[5]=2.0f/(hi[1]-lo[1]);matrix[10]=-2.0f/(hi[2]-lo[2]);
    matrix[12]=-(hi[0]+lo[0])/(hi[0]-lo[0]);matrix[13]=-(hi[1]+lo[1])/(hi[1]-lo[1]);
    matrix[14]=(hi[2]+lo[2])/(hi[2]-lo[2]);matrix[15]=1;
}
static void LightningQuad(float z) {
    qglBegin(GL_QUADS);
    qglVertex3f(-1,-1,z);qglVertex3f(1,-1,z);qglVertex3f(1,1,z);qglVertex3f(-1,1,z);
    qglEnd();
}
void RB_ACLightningFinish(void) {
    GLint matrixMode,oldProgram=0,oldFbo=0,oldDraw=0,oldRead=0;
    GLenum incomingError=GL_NO_ERROR;float flash=pendingFlash;
    float roofMatrix[16],inverse[16];vec3_t lo,hi;
    int draws=-1,start=0; qboolean spatial=qfalse; cvar_t *debug;
    pendingFlash=0;
    if(!(flash>0)||flashView.viewportWidth<=0||flashView.viewportHeight<=0)return;
    debug=ri.Cvar_Get("r_acLightningDebug","0",0);
    if(debug->integer){incomingError=qglGetError();qglFinish();start=ri.Milliseconds();}
    if(!ltPushAttrib||!ltPopAttrib)return;
    qglGetIntegerv(GL_MATRIX_MODE,&matrixMode);
    if(ltUseProgram){qglGetIntegerv(GL_CURRENT_PROGRAM,&oldProgram);ltUseProgram(0);}
    ltPushAttrib(GL_ALL_ATTRIB_BITS);
    if(ready){
        qglGetIntegerv(GL_FRAMEBUFFER_BINDING,&oldFbo);
        qglGetIntegerv(GL_DRAW_BUFFER,&oldDraw);qglGetIntegerv(GL_READ_BUFFER,&oldRead);
        ltPushClientAttrib(GL_CLIENT_ALL_ATTRIB_BITS);
    }
    qglEnable(GL_SCISSOR_TEST);
    if(qglActiveTextureARB){
        qglActiveTextureARB(GL_TEXTURE1_ARB);qglDisable(GL_TEXTURE_2D);
        qglActiveTextureARB(GL_TEXTURE0_ARB);
    }
    qglDisable(GL_TEXTURE_2D);qglEnable(GL_DEPTH_TEST);qglDepthFunc(GL_LEQUAL);qglDepthRange(0,1);
    qglDisable(GL_STENCIL_TEST);qglDisable(GL_POLYGON_OFFSET_FILL);
    qglDisable(GL_ALPHA_TEST);qglDisable(GL_CULL_FACE);
    qglDisable(GL_FOG);qglDisable(GL_LIGHTING);qglDisable(GL_CLIP_PLANE0);
    qglMatrixMode(GL_PROJECTION);qglPushMatrix();qglLoadIdentity();
    qglMatrixMode(GL_MODELVIEW);qglPushMatrix();qglLoadIdentity();
    if(ready){
        qglBindTexture(GL_TEXTURE_2D,sceneDepth);
        qglCopyTexSubImage2D(GL_TEXTURE_2D,0,0,0,flashView.viewportX,flashView.viewportY,depthWidth,depthHeight);
        if(debug->integer>=3&&!dumped){
            int bytes=depthWidth*depthHeight*sizeof(float);float *pixels=ri.Malloc(bytes);
            qglReadPixels(flashView.viewportX,flashView.viewportY,depthWidth,depthHeight,GL_DEPTH_COMPONENT,GL_FLOAT,pixels);
            ri.FS_WriteFile("lightning-scene.f32",pixels,bytes);ri.Free(pixels);
        }
        LightningRoofMatrix(roofMatrix,lo,hi);
        ltBindFramebuffer(GL_FRAMEBUFFER,framebuffer);qglDrawBuffer(GL_NONE);ltReadBuffer(GL_NONE);
        qglViewport(0,0,LIGHTNING_ROOF_SIZE,LIGHTNING_ROOF_SIZE);qglScissor(0,0,LIGHTNING_ROOF_SIZE,LIGHTNING_ROOF_SIZE);
        qglColorMask(GL_FALSE,GL_FALSE,GL_FALSE,GL_FALSE);qglDepthMask(GL_TRUE);
        qglDepthFunc(GL_LESS);qglDisable(GL_BLEND);qglClearDepth(1);qglClear(GL_DEPTH_BUFFER_BIT);
        draws=RB_ACDrawWorldOccluders(roofMatrix,lo,hi);spatial=draws>=0;
        if(debug->integer>=3&&!dumped){
            int bytes=LIGHTNING_ROOF_SIZE*LIGHTNING_ROOF_SIZE*sizeof(float);float *pixels=ri.Malloc(bytes),meta[38];
            qglReadPixels(0,0,LIGHTNING_ROOF_SIZE,LIGHTNING_ROOF_SIZE,GL_DEPTH_COMPONENT,GL_FLOAT,pixels);
            ri.FS_WriteFile("lightning-roof.f32",pixels,bytes);ri.Free(pixels);
            memcpy(meta,flashView.world.modelMatrix,16*sizeof(float));
            memcpy(meta+16,flashView.projectionMatrix,16*sizeof(float));
            memcpy(meta+32,lo,3*sizeof(float));memcpy(meta+35,hi,3*sizeof(float));
            ri.FS_WriteFile("lightning-meta.f32",meta,sizeof(meta));dumped=qtrue;
        }
        ltBindFramebuffer(GL_FRAMEBUFFER,oldFbo);qglDrawBuffer(oldDraw);ltReadBuffer(oldRead);
        if(spatial){
            ltUseProgram(program);LightningInverseView(flashView.world.modelMatrix,inverse);
            ltUniformMatrix4fv(ltGetUniformLocation(program,"inverseView"),1,GL_FALSE,inverse);
            ltUniform4f(ltGetUniformLocation(program,"projection"),flashView.projectionMatrix[0],flashView.projectionMatrix[5],flashView.projectionMatrix[8],flashView.projectionMatrix[9]);
            ltUniform2f(ltGetUniformLocation(program,"depthPair"),flashView.projectionMatrix[10],flashView.projectionMatrix[14]);
            ltUniform2f(ltGetUniformLocation(program,"depthTexel"),1.0f/depthWidth,1.0f/depthHeight);
            ltUniform1f(ltGetUniformLocation(program,"sampleRadius"),framebufferSamples>1?0.5f:0.0f);
            ltUniform4f(ltGetUniformLocation(program,"roofBounds"),lo[0],lo[1],1.0f/(hi[0]-lo[0]),1.0f/(hi[1]-lo[1]));
            ltUniform2f(ltGetUniformLocation(program,"roofZ"),hi[2],hi[2]-lo[2]);
            ltUniform1f(ltGetUniformLocation(program,"exposure"),.65f*flash);
            ltUniform1f(ltGetUniformLocation(program,"roofResolution"),LIGHTNING_ROOF_SIZE);
            ltUniform1i(ltGetUniformLocation(program,"sceneDepth"),0);ltUniform1i(ltGetUniformLocation(program,"roofDepth"),1);
            qglBindTexture(GL_TEXTURE_2D,sceneDepth);
            qglActiveTextureARB(GL_TEXTURE1_ARB);qglBindTexture(GL_TEXTURE_2D,roofDepth);qglActiveTextureARB(GL_TEXTURE0_ARB);
        }else ltUseProgram(0);
    }
    qglViewport(flashView.viewportX,flashView.viewportY,flashView.viewportWidth,flashView.viewportHeight);
    qglScissor(flashView.viewportX,flashView.viewportY,flashView.viewportWidth,flashView.viewportHeight);
    qglDepthFunc(GL_LEQUAL);qglDepthMask(GL_FALSE);qglColorMask(GL_TRUE,GL_TRUE,GL_TRUE,GL_TRUE);
    qglEnable(GL_BLEND);qglBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);
    // Unsupported programmable hardware still gets a roof-safe sky flash.
    qglColor4f(1,1,1,.65f*flash);LightningQuad(spatial?0.0f:1.0f);
    qglPopMatrix();qglMatrixMode(GL_PROJECTION);qglPopMatrix();qglMatrixMode(matrixMode);
    if(ready)ltPopClientAttrib();
    ltPopAttrib();if(ltUseProgram)ltUseProgram(oldProgram);
    if(debug->integer){
        qglFinish();
        ri.Printf(PRINT_ALL,"AC_LIGHTNING strength=%.4f viewport=%dx%d spatial=%d blockers=%d ms=%d fog=%.4f,%.4f,%.4f gl_error=%d incoming_error=%d\n",
            flash,flashView.viewportWidth,flashView.viewportHeight,spatial,draws,ri.Milliseconds()-start,
            flashView.farplane_color[0],flashView.farplane_color[1],flashView.farplane_color[2],qglGetError(),incomingError);
    }
}
