/* Allied Campaign near-field GTAO. GPL-2.0-or-later.
 * Cosine-weighted horizon integration (Jimenez et al., GTAO, 2016), with
 * full-resolution geometric normals and depth/normal-aware spatial filtering.
 * This is a GL1 implementation, not a port of XeGTAO or ray-traced lighting.
 * Screen-space visibility is deliberately local (32 world units). The replay
 * against the original depth buffer excludes the weapon, sky, HUD and particles.
 * Reprojected renderer-only history stabilizes sub-pixel distant contacts;
 * depth/normal validation rejects disocclusions. No savegame-owned state.
 */
#include "tr_local.h"
#include "SDL.h"

#define AO_FUNCTIONS(X) \
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
 X(void,UniformMatrix4fv,(GLint u,GLsizei n,GLboolean t,const GLfloat *m)) \
 X(void,PushAttrib,(GLbitfield b)) \
 X(void,PopAttrib,(void)) \
 X(void,PushClientAttrib,(GLbitfield b)) \
 X(void,PopClientAttrib,(void)) \
 X(void,ReadBuffer,(GLenum b))
#define DECL(ret,name,args) static ret (APIENTRYP ao##name) args;
AO_FUNCTIONS(DECL)
#undef DECL

static GLuint fbo, geometry, depth, visibility[2], geometryProgram, horizonProgram, filterProgram, compositeProgram;
static GLuint previousGeometry, previousVisibility, temporalProgram;
static float previousView[16],previousProjection[16];
static world_t *previousWorld;
static int previousTime;
static qboolean historyValid;
static int width,height;
static qboolean ready;
static cvar_t *enabled,*debug;

static const char *sceneVertex =
 "#version 120\n"
 "uniform mat4 projection,view; varying vec3 position,normal; varying vec2 uv;\n"
 "void main(){vec4 p=view*gl_Vertex; position=p.xyz;normal=mat3(view)*gl_Normal; uv=gl_MultiTexCoord0.xy; gl_Position=projection*p;}\n";
static const char *screenVertex =
 "#version 120\n"
 "varying vec2 uv; void main(){uv=gl_Vertex.xy*0.5+0.5;gl_Position=gl_Vertex;}\n";
static const char *geometryFragment =
 "#version 120\n"
 "uniform sampler2D skin;uniform float alphaCut;varying vec3 position,normal;varying vec2 uv;\n"
 "void main(){\n"
 " vec3 face=cross(dFdx(position),dFdy(position));vec3 n=normalize(dot(normal,normal)>0.25?normal:face); if(dot(n,-position)<0.0)n=-n;\n"
 " if(alphaCut>=0.0 && texture2D(skin,uv).a<alphaCut)discard;\n"
 " gl_FragColor=vec4(n,-position.z);}\n";
static const char *horizonFragment =
 "#version 120\n"
 "uniform sampler2D scene;uniform vec2 size,projectionScale,projectionOffset; varying vec2 uv;\n"
 "vec3 reconstruct(vec2 t,float z){return vec3((t*2.0-1.0+projectionOffset)*z/projectionScale,-z);}\n"
 "float integral(float h,float n,float c){return (c+2.0*h*sin(n)-cos(2.0*h-n))*0.25;}\n"
 "void main(){\n"
 " vec4 g=texture2D(scene,uv);if(g.a<=0.0){gl_FragColor=vec4(1.0);return;}\n"
 " vec3 p=reconstruct(uv,g.a),v=normalize(-p),N=normalize(g.xyz);\n"
 " float radius=32.0; vec2 screenRadius=0.5*size*projectionScale*radius/g.a;\n"
 // Stable spatial rotation; there is deliberately no per-frame jitter.
 " float phase=fract(52.9829189*fract(dot(gl_FragCoord.xy,vec2(0.06711056,0.00583715))));\n"
 // Integrate uniformly around the actual pixel view ray, not the camera's Z
 // axis. Screen-plane slices cluster at wide-FOV edges and change their solid
 // angle when the camera turns, even when the visible geometry is unchanged.
 " vec3 tangent=normalize(cross(vec3(0.0,1.0,0.0),v)),bitangent=cross(v,tangent);float sum=0.0;\n"
 " for(int slice=0;slice<6;slice++){\n"
 "  float phi=(float(slice)+phase)*3.14159265/6.0;vec2 direction=vec2(cos(phi),sin(phi));\n"
 "  vec3 d=tangent*direction.x+bitangent*direction.y;vec3 ortho=d;\n"
 "  vec2 projected=d.xy-v.xy*d.z/v.z;\n"
 "  vec3 axis=normalize(cross(ortho,v));vec3 np=N-axis*dot(N,axis);float plen=length(np);\n"
 "  float c=clamp(dot(np,v)/max(plen,0.0001),0.0,1.0);\n"
 "  float n=sign(dot(ortho,np))*acos(c);\n"
 "  vec2 low=cos(vec2(n+1.57079633,n-1.57079633));vec2 horizon=low;\n"
 "  for(int tap=1;tap<=4;tap++){\n"
 "   float t=(float(tap)-0.35)/4.0;t*=t;\n"
 // Preserve the slice's projected direction, including at sub-pixel radii.
 "   vec2 delta=projected*screenRadius*t;delta*=max(1.0,1.0/max(length(delta),0.0001));\n"
 "   for(int side=0;side<2;side++){\n"
 "    vec2 st=(floor(gl_FragCoord.xy+delta*(side==0?1.0:-1.0))+0.5)/size;\n"
 "    if(any(lessThan(st,vec2(0.0)))||any(greaterThan(st,vec2(1.0))))continue;\n"
 "    float z=texture2D(scene,st).a;if(z<=0.0)continue;\n"
 "    vec3 offset=reconstruct(st,z)-p;float dist=length(offset);if(dist<0.05)continue;\n"
 // A spherical world-space radius must stay spherical when the camera turns.
 // Stretching view-space Z as a thickness heuristic caused moving dark edges.
 // The surface-normal rejection still prevents planar self-occlusion.
 "    float weight=clamp((radius-dist)/(radius*0.7),0.0,1.0);\n"
 "    if(dot(offset,N)<0.08)weight=0.0;\n"
 "    float h=dot(offset/dist,v);\n"
 "    if(side==0)horizon.x=max(horizon.x,mix(low.x,h,weight));\n"
 "    else horizon.y=max(horizon.y,mix(low.y,h,weight));\n"
 "   }\n"
 "  }\n"
 "  float h0=-acos(clamp(horizon.y,-1.0,1.0)),h1=acos(clamp(horizon.x,-1.0,1.0));\n"
 "  float base=integral(n-1.57079633,n,c)+integral(n+1.57079633,n,c);\n"
 // Integrate blocked irradiance with the projected normal's length. Dividing
 // each slice by its own baseline instead gives grazing slices too much weight.
 // Subtract from analytic visibility 1 so a free plane stays exactly unoccluded
 // even with the finite angular quadrature (including at grazing angles).
 "  sum+=plen*max(0.0,base-integral(h0,n,c)-integral(h1,n,c));\n"
 " }\n"
 " gl_FragColor=vec4(clamp(1.0-sum/6.0,0.0,1.0));}\n";
static const char *filterFragment =
 "#version 120\n"
 "uniform sampler2D scene,ao;uniform vec2 size,projectionScale,projectionOffset,direction;varying vec2 uv;\n"
 "vec3 reconstruct(vec2 t,float z){return vec3((t*2.0-1.0+projectionOffset)*z/projectionScale,-z);}\n"
 "void main(){vec4 g=texture2D(scene,uv);if(g.a<=0.0){gl_FragColor=vec4(1.0);return;}\n"
 " vec3 p=reconstruct(uv,g.a);float sum=0.0,total=0.0;\n"
 " for(int i=-4;i<=4;i++){vec2 t=uv+direction*float(i)/size;vec4 q=texture2D(scene,t);\n"
 "  vec3 delta=reconstruct(t,q.a)-p;\n"
 "  float plane=max(abs(dot(delta,g.xyz)),abs(dot(delta,q.xyz)));\n"
 "  float w=exp(-float(i*i)/8.0)*pow(max(dot(g.xyz,q.xyz),0.0),16.0)*exp(-plane*plane*2.0);\n"
 "  if(q.a<=0.0 || abs(q.a-g.a)>max(2.0,g.a*0.025))w=0.0;\n"
 "  sum+=texture2D(ao,t).r*w;total+=w;\n"
 " } gl_FragColor=vec4(sum/max(total,0.0001));}\n";
static const char *temporalFragment =
 "#version 120\n"
 "uniform sampler2D scene,ao,oldScene,oldAO;uniform vec2 size,projectionScale,projectionOffset;\n"
 "uniform mat4 previousFromCurrent,previousProjection;uniform float retention;varying vec2 uv;\n"
 "void main(){float current=texture2D(ao,uv).r;vec4 g=texture2D(scene,uv);\n"
 " if(retention<=0.0||g.a<=0.0){gl_FragColor=vec4(current);return;}\n"
 " vec4 p=previousFromCurrent*vec4((uv*2.0-1.0+projectionOffset)*g.a/projectionScale,-g.a,1.0);\n"
 " vec4 clip=previousProjection*p;vec2 oldUV=clip.xy/clip.w*0.5+0.5;\n"
 " if(clip.w<=0.0||any(lessThan(oldUV,vec2(0.0)))||any(greaterThan(oldUV,vec2(1.0)))){gl_FragColor=vec4(current);return;}\n"
 " vec4 old=texture2D(oldScene,oldUV);vec3 N=normalize(mat3(previousFromCurrent)*g.xyz);\n"
 " float tolerance=max(0.25,abs(p.z)*0.001);\n"
 " if(old.a<=0.0||abs(old.a+p.z)>tolerance||dot(N,old.xyz)<0.95){gl_FragColor=vec4(current);return;}\n"
 // Clip history to the current local visibility range, with a small allowance
 // for gradual changes. This bounds trails when an occluder moves while its
 // receiver (e.g. floor) keeps the same depth and normal.
 " float low=current,high=current;\n"
 " for(int y=-1;y<=1;y++)for(int x=-1;x<=1;x++){\n"
 "  vec2 t=uv+vec2(float(x),float(y))/size;vec4 q=texture2D(scene,t);\n"
 "  if(abs(q.a-g.a)<=max(0.5,g.a*0.002)&&dot(q.xyz,g.xyz)>0.95){\n"
 "   float a=texture2D(ao,t).r;low=min(low,a);high=max(high,a);}}\n"
 " float history=clamp(texture2D(oldAO,oldUV).r,low-0.08,high+0.08);\n"
 " gl_FragColor=vec4(clamp(mix(current,history,retention),0.0,1.0));}\n";
static const char *compositeFragment =
 "#version 120\n"
 "uniform sampler2D ao,sceneDepth;uniform vec2 size,depthReconstruct;uniform float fogStart,fogEnd,diagnostic;\n"
 "varying vec2 uv;\n"
 "void main(){float z=texture2D(sceneDepth,uv).r;if(z>=1.0)discard;\n"
 // Use actual per-pixel scene depth, not a quad at the near plane. First-person
 // depthhack geometry in the window buffer remains in front and fails the test.
 // Compositing once also avoids double darkening of overlapping opaque layers.
 // A derivative crossing a silhouette is not a surface slope. Use the closer
 // depth on each axis so a background edge cannot bias AO onto the foreground.
 " vec2 pixel=1.0/size;\n"
 " float dx=min(abs(z-texture2D(sceneDepth,uv-vec2(pixel.x,0.0)).r),abs(z-texture2D(sceneDepth,uv+vec2(pixel.x,0.0)).r));\n"
 " float dy=min(abs(z-texture2D(sceneDepth,uv-vec2(0.0,pixel.y)).r),abs(z-texture2D(sceneDepth,uv+vec2(0.0,pixel.y)).r));\n"
 " float bias=min(0.0001,0.0000003+max(dx,dy));\n"
 " gl_FragDepth=max(0.0,z-bias);float eyeDepth=depthReconstruct.y/(2.0*z-1.0+depthReconstruct.x);\n"
 " float a=texture2D(ao,uv).r;\n"
 " float fog=fogEnd>fogStart?clamp((fogEnd-eyeDepth)/(fogEnd-fogStart),0.0,1.0):1.0;\n"
 " float occlusion=min((1.0-a)*0.7,0.55)*fog;\n"
 " gl_FragColor=diagnostic>0.5?vec4(vec3(1.0-occlusion),1.0):vec4(0.0,0.0,0.0,occlusion);}\n";

static GLuint Compile(GLenum type,const char *text) {
 GLint ok;char log[2048];GLuint s=aoCreateShader(type);
 aoShaderSource(s,1,&text,NULL);aoCompileShader(s);aoGetShaderiv(s,GL_COMPILE_STATUS,&ok);
 if(!ok){aoGetShaderInfoLog(s,sizeof(log),NULL,log);ri.Printf(PRINT_WARNING,"AC AO shader: %s\n",log);aoDeleteShader(s);return 0;}return s;
}
static GLuint Program(const char *vertex,const char *fragment) {
 GLuint v=Compile(GL_VERTEX_SHADER,vertex),f=Compile(GL_FRAGMENT_SHADER,fragment),p=0;GLint ok;char log[2048];
 if(v&&f){p=aoCreateProgram();aoAttachShader(p,v);aoAttachShader(p,f);aoLinkProgram(p);aoGetProgramiv(p,GL_LINK_STATUS,&ok);
  if(!ok){aoGetProgramInfoLog(p,sizeof(log),NULL,log);ri.Printf(PRINT_WARNING,"AC AO link: %s\n",log);aoDeleteProgram(p);p=0;}}
 if(v)aoDeleteShader(v);if(f)aoDeleteShader(f);return p;
}
static void I(GLuint p,const char *n,int v){aoUniform1i(aoGetUniformLocation(p,n),v);}
static void F(GLuint p,const char *n,float v){aoUniform1f(aoGetUniformLocation(p,n),v);}
static void V(GLuint p,const char *n,float x,float y){aoUniform2f(aoGetUniformLocation(p,n),x,y);}
static void Multiply(const float *a,const float *b,float *out){
 int r,c,k;for(c=0;c<4;c++)for(r=0;r<4;r++){out[c*4+r]=0;for(k=0;k<4;k++)out[c*4+r]+=a[k*4+r]*b[c*4+k];}
}
static void PreviousFromCurrent(float *out){
 const float *view=backEnd.viewParms.world.modelMatrix;float inverse[16]={0};int r,c;
 // The world view is rigid: transpose its rotation and invert translation.
 for(r=0;r<3;r++)for(c=0;c<3;c++)inverse[c*4+r]=view[r*4+c];
 for(r=0;r<3;r++)inverse[12+r]=-(inverse[r]*view[12]+inverse[4+r]*view[13]+inverse[8+r]*view[14]);
 inverse[15]=1;Multiply(previousView,inverse,out);
}
static void Camera(GLuint p){
 aoUniformMatrix4fv(aoGetUniformLocation(p,"projection"),1,GL_FALSE,backEnd.viewParms.projectionMatrix);
 aoUniformMatrix4fv(aoGetUniformLocation(p,"view"),1,GL_FALSE,backEnd.viewParms.world.modelMatrix);
}
static void Screen(GLuint p){
 static const GLfloat quad[12]={-1,-1,0, 1,-1,0, 1,1,0, -1,1,0};
 aoUseProgram(p);V(p,"size",width,height);V(p,"projectionScale",backEnd.viewParms.projectionMatrix[0],backEnd.viewParms.projectionMatrix[5]);
 V(p,"projectionOffset",backEnd.viewParms.projectionMatrix[8],backEnd.viewParms.projectionMatrix[9]);
 qglDisableClientState(GL_TEXTURE_COORD_ARRAY);qglDisableClientState(GL_NORMAL_ARRAY);
 qglVertexPointer(3,GL_FLOAT,0,quad);qglDrawArrays(GL_QUADS,0,4);
}
static void Texture(GLuint tex,GLint format,GLenum external,GLenum type){
 qglBindTexture(GL_TEXTURE_2D,tex);qglTexImage2D(GL_TEXTURE_2D,0,format,width,height,0,external,type,NULL);
 qglTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST);qglTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST);
 qglTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE);qglTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE);
}
static qboolean Resize(void){
 int w=backEnd.viewParms.viewportWidth,h=backEnd.viewParms.viewportHeight;
 if(w==width&&h==height)return qtrue;
 width=w;height=h;historyValid=qfalse;
 // RGBA32F avoids half-float depth quantization on far, shallow-angle surfaces.
 Texture(geometry,GL_RGBA32F,GL_RGBA,GL_FLOAT);Texture(depth,GL_DEPTH_COMPONENT24,GL_DEPTH_COMPONENT,GL_UNSIGNED_INT);
 Texture(visibility[0],GL_RGBA8,GL_RGBA,GL_UNSIGNED_BYTE);Texture(visibility[1],GL_RGBA8,GL_RGBA,GL_UNSIGNED_BYTE);
 Texture(previousGeometry,GL_RGBA32F,GL_RGBA,GL_FLOAT);Texture(previousVisibility,GL_RGBA8,GL_RGBA,GL_UNSIGNED_BYTE);
 aoFramebufferTexture2D(GL_FRAMEBUFFER,GL_DEPTH_ATTACHMENT,GL_TEXTURE_2D,depth,0);
 aoFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,geometry,0);
 if(aoCheckFramebufferStatus(GL_FRAMEBUFFER)!=GL_FRAMEBUFFER_COMPLETE){
  ri.Printf(PRINT_WARNING,"AC AO framebuffer unsupported; ambient occlusion disabled.\n");ready=qfalse;ri.Cvar_Set("r_acAOReady","0");return qfalse;}
 return qtrue;
}
void R_ACAOInit(void){
 qboolean loaded=qtrue;
 enabled=ri.Cvar_Get("r_acAmbientOcclusion","1",CVAR_ARCHIVE);debug=ri.Cvar_Get("r_acAODebug","0",0);
 ri.Cvar_Get("r_acAOReady","0",CVAR_ROM);ri.Cvar_Set("r_acAOReady","0");
#define LOAD(ret,name,args) ao##name=(ret (APIENTRYP) args)SDL_GL_GetProcAddress("gl" #name);if(!ao##name)loaded=qfalse;
 AO_FUNCTIONS(LOAD)
#undef LOAD
 if(!loaded||!qglActiveTextureARB||!qglClientActiveTextureARB||glConfig.numTextureUnits<4||!ri.Cvar_VariableIntegerValue("r_acShadowReady"))return;
 geometryProgram=Program(sceneVertex,geometryFragment);horizonProgram=Program(screenVertex,horizonFragment);
 filterProgram=Program(screenVertex,filterFragment);compositeProgram=Program(screenVertex,compositeFragment);
 temporalProgram=Program(screenVertex,temporalFragment);
 if(!geometryProgram||!horizonProgram||!filterProgram||!compositeProgram||!temporalProgram){R_ACAOShutdown();return;}
 aoGenFramebuffers(1,&fbo);qglGenTextures(1,&geometry);qglGenTextures(1,&depth);qglGenTextures(2,visibility);
 qglGenTextures(1,&previousGeometry);qglGenTextures(1,&previousVisibility);historyValid=qfalse;
 ready=qtrue;ri.Cvar_Set("r_acAOReady","1");ri.Printf(PRINT_ALL,"AC GTAO ready: full-resolution geometry, 48 horizon samples, bilateral filter, validated reprojection.\n");
}
void R_ACAOShutdown(void){
 if(fbo&&aoDeleteFramebuffers)aoDeleteFramebuffers(1,&fbo);
 if(geometry)qglDeleteTextures(1,&geometry);if(depth)qglDeleteTextures(1,&depth);if(visibility[0])qglDeleteTextures(2,visibility);
 if(previousGeometry)qglDeleteTextures(1,&previousGeometry);if(previousVisibility)qglDeleteTextures(1,&previousVisibility);
 if(geometryProgram)aoDeleteProgram(geometryProgram);if(horizonProgram)aoDeleteProgram(horizonProgram);
 if(filterProgram)aoDeleteProgram(filterProgram);if(compositeProgram)aoDeleteProgram(compositeProgram);
 if(temporalProgram)aoDeleteProgram(temporalProgram);
 fbo=geometry=depth=visibility[0]=visibility[1]=geometryProgram=horizonProgram=filterProgram=compositeProgram=0;
 width=height=0;ready=qfalse;ri.Cvar_Set("r_acAOReady","0");
 previousGeometry=previousVisibility=temporalProgram=0;historyValid=qfalse;previousWorld=NULL;
}
qboolean R_ACAOActive(void){qboolean active=ready&&enabled&&enabled->integer;if(!active)historyValid=qfalse;return active;}
void RB_ACAOApply(void){
 GLint oldFbo,oldProgram,oldDraw,oldRead;int pass,start=0;GLenum error;GLuint swap;
 if(!R_ACAOActive())return;
 if(debug->integer>1){error=qglGetError();qglFinish();start=ri.Milliseconds();if(error&&backEnd.refdef.time%1000<50)ri.Printf(PRINT_ALL,"AC_AO_PRIOR_GL_ERROR %d\n",error);}
 qglGetIntegerv(GL_FRAMEBUFFER_BINDING,&oldFbo);qglGetIntegerv(GL_CURRENT_PROGRAM,&oldProgram);
 qglGetIntegerv(GL_DRAW_BUFFER,&oldDraw);qglGetIntegerv(GL_READ_BUFFER,&oldRead);
 aoPushAttrib(GL_ALL_ATTRIB_BITS);aoPushClientAttrib(GL_CLIENT_ALL_ATTRIB_BITS);
 qglActiveTextureARB(GL_TEXTURE0_ARB);qglClientActiveTextureARB(GL_TEXTURE0_ARB);
 aoBindFramebuffer(GL_FRAMEBUFFER,fbo);qglDrawBuffer(GL_COLOR_ATTACHMENT0);aoReadBuffer(GL_COLOR_ATTACHMENT0);
 if(!Resize())goto restore;
 qglViewport(0,0,width,height);qglScissor(0,0,width,height);
 qglDisable(GL_FOG);qglDisable(GL_LIGHTING);qglDisable(GL_ALPHA_TEST);qglDisable(GL_STENCIL_TEST);qglDisable(GL_CLIP_PLANE0);
 qglDisable(GL_CULL_FACE);qglDisable(GL_BLEND);qglDisable(GL_POLYGON_OFFSET_FILL);
 qglDisableClientState(GL_COLOR_ARRAY);qglDisableClientState(GL_NORMAL_ARRAY);
 qglEnable(GL_DEPTH_TEST);qglDepthMask(GL_TRUE);qglDepthFunc(GL_LESS);qglDepthRange(0,1);qglColorMask(GL_TRUE,GL_TRUE,GL_TRUE,GL_TRUE);
 aoFramebufferTexture2D(GL_FRAMEBUFFER,GL_DEPTH_ATTACHMENT,GL_TEXTURE_2D,depth,0);
 aoFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,geometry,0);
 qglClearColor(0,0,0,0);qglClearDepth(1);qglClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT);
 aoUseProgram(geometryProgram);Camera(geometryProgram);I(geometryProgram,"skin",0);
 RB_ACDrawCapturedScene(aoGetUniformLocation(geometryProgram,"alphaCut"));
 if(debug->integer==3){
  int bytes=width*height*4*sizeof(float);float *pixels=ri.Malloc(bytes);
  qglReadPixels(0,0,width,height,GL_RGBA,GL_FLOAT,pixels);
  ri.FS_WriteFile("ao-geometry.f32",pixels,bytes);ri.Free(pixels);
  // Independent reference for alignment tests: the actual fixed-function scene
  // depth, before AO composition, including the original model transforms/LOD.
  bytes=width*height*sizeof(float);pixels=ri.Malloc(bytes);
  aoBindFramebuffer(GL_FRAMEBUFFER,oldFbo);
  qglReadPixels(backEnd.viewParms.viewportX,backEnd.viewParms.viewportY,width,height,GL_DEPTH_COMPONENT,GL_FLOAT,pixels);
  ri.FS_WriteFile("ao-window-depth.f32",pixels,bytes);ri.Free(pixels);
  aoBindFramebuffer(GL_FRAMEBUFFER,fbo);
  ri.Printf(PRINT_ALL,"AC_AO_GEOMETRY width=%d height=%d projection=%f %f depth=%f %f\n",width,height,backEnd.viewParms.projectionMatrix[0],backEnd.viewParms.projectionMatrix[5],backEnd.viewParms.projectionMatrix[10],backEnd.viewParms.projectionMatrix[14]);
  ri.Cvar_Set("r_acAODebug","2");
 }
 aoFramebufferTexture2D(GL_FRAMEBUFFER,GL_DEPTH_ATTACHMENT,GL_TEXTURE_2D,0,0);
 aoFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,visibility[0],0);
 qglDisable(GL_DEPTH_TEST);qglDepthMask(GL_FALSE);qglBindTexture(GL_TEXTURE_2D,geometry);
 aoUseProgram(horizonProgram);I(horizonProgram,"scene",0);Screen(horizonProgram);
 for(pass=0;pass<2;pass++){
  aoFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,visibility[1-pass],0);
  qglActiveTextureARB(GL_TEXTURE1_ARB);qglBindTexture(GL_TEXTURE_2D,visibility[pass]);qglActiveTextureARB(GL_TEXTURE0_ARB);
  aoUseProgram(filterProgram);I(filterProgram,"scene",0);I(filterProgram,"ao",1);V(filterProgram,"direction",pass==0?1:0,pass==1?1:0);Screen(filterProgram);
 }
 {
  float transform[16],retention=0;int elapsed=backEnd.refdef.time-previousTime;
  if(historyValid&&previousWorld==tr.world&&elapsed>=0&&elapsed<250){
   PreviousFromCurrent(transform);
   // Camera cuts and teleports must not carry old contacts into a new view.
   if(transform[12]*transform[12]+transform[13]*transform[13]+transform[14]*transform[14]<128*128
      &&transform[0]+transform[5]+transform[10]>1.0f)
    retention=expf(-fmaxf(elapsed,8)/75.0f);
  }else{memset(transform,0,sizeof(transform));transform[0]=transform[5]=transform[10]=transform[15]=1;}
  aoFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,visibility[1],0);
  qglActiveTextureARB(GL_TEXTURE3_ARB);qglBindTexture(GL_TEXTURE_2D,previousVisibility);
  qglActiveTextureARB(GL_TEXTURE2_ARB);qglBindTexture(GL_TEXTURE_2D,previousGeometry);
  qglActiveTextureARB(GL_TEXTURE1_ARB);qglBindTexture(GL_TEXTURE_2D,visibility[0]);
  qglActiveTextureARB(GL_TEXTURE0_ARB);qglBindTexture(GL_TEXTURE_2D,geometry);
  aoUseProgram(temporalProgram);I(temporalProgram,"scene",0);I(temporalProgram,"ao",1);
  I(temporalProgram,"oldScene",2);I(temporalProgram,"oldAO",3);F(temporalProgram,"retention",retention);
  aoUniformMatrix4fv(aoGetUniformLocation(temporalProgram,"previousFromCurrent"),1,GL_FALSE,transform);
  aoUniformMatrix4fv(aoGetUniformLocation(temporalProgram,"previousProjection"),1,GL_FALSE,previousProjection);
  Screen(temporalProgram);
  swap=previousVisibility;previousVisibility=visibility[1];visibility[1]=swap;
  swap=previousGeometry;previousGeometry=geometry;geometry=swap;
  memcpy(previousView,backEnd.viewParms.world.modelMatrix,sizeof(previousView));
  memcpy(previousProjection,backEnd.viewParms.projectionMatrix,sizeof(previousProjection));
  previousTime=backEnd.refdef.time;previousWorld=tr.world;historyValid=qtrue;
 }
 aoBindFramebuffer(GL_FRAMEBUFFER,oldFbo);qglDrawBuffer(oldDraw);aoReadBuffer(oldRead);
 qglViewport(backEnd.viewParms.viewportX,backEnd.viewParms.viewportY,width,height);qglScissor(backEnd.viewParms.viewportX,backEnd.viewParms.viewportY,width,height);
 qglEnable(GL_DEPTH_TEST);qglDepthFunc(GL_LEQUAL);qglDisable(GL_POLYGON_OFFSET_FILL);
 qglEnable(GL_BLEND);qglBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);
 aoUseProgram(compositeProgram);I(compositeProgram,"ao",0);I(compositeProgram,"sceneDepth",1);
 V(compositeProgram,"depthReconstruct",backEnd.viewParms.projectionMatrix[10],backEnd.viewParms.projectionMatrix[14]);
 F(compositeProgram,"fogStart",backEnd.viewParms.farplane_bias);F(compositeProgram,"fogEnd",r_farplane_nofog->integer?0:backEnd.viewParms.farplane_distance);
 F(compositeProgram,"diagnostic",debug->integer==1?1.0f:0.0f);
 qglBindTexture(GL_TEXTURE_2D,previousVisibility);qglActiveTextureARB(GL_TEXTURE1_ARB);qglBindTexture(GL_TEXTURE_2D,depth);qglActiveTextureARB(GL_TEXTURE0_ARB);
 Screen(compositeProgram);
restore:
 aoBindFramebuffer(GL_FRAMEBUFFER,oldFbo);qglDrawBuffer(oldDraw);aoReadBuffer(oldRead);aoUseProgram(oldProgram);aoPopClientAttrib();aoPopAttrib();
 if(debug->integer>1){qglFinish();error=qglGetError();if(backEnd.refdef.time%1000<50)ri.Printf(PRINT_ALL,"AC_AO_COST ms=%d gl_error=%d size=%dx%d\n",ri.Milliseconds()-start,error,width,height);}
}
