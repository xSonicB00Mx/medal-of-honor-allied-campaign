/* Allied Campaign temporal rendering. GPL-2.0-or-later.
 * Renderer-owned history; no persistent game/save state. Animated surfaces keep
 * their actual deformed vertices, keyed by entity/model/surface/material and
 * validated topology. Motion blur uses OBJECT displacement in the CURRENT
 * camera, never the camera velocity used by TAA reprojection.
 */
#include "tr_local.h"
#include "SDL.h"
#include <stdint.h>

#define TM_GL(X) \
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
 X(void,PushAttrib,(GLbitfield b)) X(void,PopAttrib,(void)) \
 X(void,PushClientAttrib,(GLbitfield b)) X(void,PopClientAttrib,(void)) \
 X(void,ReadBuffer,(GLenum b))
#define DECL(ret,name,args) static ret (APIENTRYP tm##name) args;
TM_GL(DECL)
#undef DECL

#define TM_VERTS 524288
#define TM_CACHE_VERTS 262144
#define TM_BATCHES 8192
#define TM_SLOTS 16384
typedef struct {float xyz[3],old[3],uv[2];} tmVertex;
typedef struct {int first,count;GLuint skin;float alpha,id,valid;int weapon,reactive;cullType_t cull;} tmBatch;
typedef struct {uintptr_t surface,model,shader;int owner,parent,weapon;unsigned generation;} tmKey;
typedef struct {tmKey key;unsigned topology;int first,count,occupied;} tmEntry;
typedef struct {tmEntry entries[TM_SLOTS];vec3_t positions[TM_CACHE_VERTS];int count;} tmCache;
static tmCache caches[2];
static tmVertex vertices[TM_VERTS];
static tmBatch batches[TM_BATCHES];
static int cacheIndex,numVertices,numBatches;
static const void *surfaceKey;
static GLuint fbo,color,sceneDepth,velocity,objects,history[2],metadata[2],resolved;
static GLuint cameraProgram,objectProgram,resolveProgram,blurProgram,copyProgram;
static cvar_t *taa,*blur,*debug;
static qboolean ready,pending,historyValid,overflow;
static int width,height,historyIndex,previousTime,previousFrame,previousTAA,framebufferSamples;
static world_t *previousWorld;
static float previousView[16],previousProjection[16];
static float previousLightning;
static viewParms_t sceneView;
static trRefdef_t sceneRefdef;

#include "tr_ac_temporal_shaders.h"

static void I(GLuint p,const char*n,int v){tmUniform1i(tmGetUniformLocation(p,n),v);}
static void F(GLuint p,const char*n,float v){tmUniform1f(tmGetUniformLocation(p,n),v);}
static void V(GLuint p,const char*n,float x,float y){tmUniform2f(tmGetUniformLocation(p,n),x,y);}
static void M(GLuint p,const char*n,const float*m){tmUniformMatrix4fv(tmGetUniformLocation(p,n),1,GL_FALSE,m);}
static void Multiply(const float*a,const float*b,float*out){int r,c,k;for(c=0;c<4;c++)for(r=0;r<4;r++){out[c*4+r]=0;for(k=0;k<4;k++)out[c*4+r]+=a[k*4+r]*b[c*4+k];}}
static void InverseView(const float*v,float*out){int r,c;memset(out,0,16*sizeof(float));for(r=0;r<3;r++)for(c=0;c<3;c++)out[c*4+r]=v[r*4+c];for(r=0;r<3;r++)out[12+r]=-(out[r]*v[12]+out[4+r]*v[13]+out[8+r]*v[14]);out[15]=1;}
static float Halton(int i,int base){float f=1,r=0;while(i){f/=base;r+=f*(i%base);i/=base;}return r;}
static qboolean Active(void){return ready&&(taa->integer||blur->value>0);}
void R_ACTemporalReset(void){historyValid=pending=qfalse;previousWorld=NULL;memset(caches,0,sizeof(caches));}
void R_ACTemporalJitter(void){
 int phase=(tr.frameCount%16)+1;
 if(!Active()||!taa->integer||!tr.world||tr.viewParms.isPortal||tr.viewParms.isPortalSky
    ||(tr.refdef.rdflags&(RDF_NOWORLDMODEL|RDF_HUD))||tr.viewParms.viewportWidth<1||tr.viewParms.viewportHeight<1)return;
 tr.viewParms.projectionMatrix[8]+=2*(Halton(phase,2)-.5f)/tr.viewParms.viewportWidth;
 tr.viewParms.projectionMatrix[9]+=2*(Halton(phase,3)-.5f)/tr.viewParms.viewportHeight;
}
static GLuint Compile(GLenum type,const char*text){
 GLuint s=tmCreateShader(type);GLint ok;char log[2048];tmShaderSource(s,1,&text,NULL);tmCompileShader(s);tmGetShaderiv(s,GL_COMPILE_STATUS,&ok);
 if(!ok){tmGetShaderInfoLog(s,sizeof(log),NULL,log);ri.Printf(PRINT_WARNING,"AC temporal shader: %s\n",log);tmDeleteShader(s);return 0;}return s;
}
static GLuint Program(const char*v,const char*f){
 GLuint vs=Compile(GL_VERTEX_SHADER,v),fs=Compile(GL_FRAGMENT_SHADER,f),p=0;GLint ok;char log[2048];
 if(vs&&fs){p=tmCreateProgram();tmAttachShader(p,vs);tmAttachShader(p,fs);tmLinkProgram(p);tmGetProgramiv(p,GL_LINK_STATUS,&ok);if(!ok){tmGetProgramInfoLog(p,sizeof(log),NULL,log);ri.Printf(PRINT_WARNING,"AC temporal link: %s\n",log);tmDeleteProgram(p);p=0;}}
 if(vs)tmDeleteShader(vs);if(fs)tmDeleteShader(fs);return p;
}
void R_ACTemporalShutdown(void){
 GLuint tex[9]={color,sceneDepth,velocity,objects,history[0],history[1],metadata[0],metadata[1],resolved};
 GLuint programs[5]={cameraProgram,objectProgram,resolveProgram,blurProgram,copyProgram};int i;
 if(fbo&&tmDeleteFramebuffers)tmDeleteFramebuffers(1,&fbo);
 for(i=0;i<9;i++)if(tex[i])qglDeleteTextures(1,&tex[i]);
 for(i=0;i<5;i++)if(programs[i]&&tmDeleteProgram)tmDeleteProgram(programs[i]);
 fbo=color=sceneDepth=velocity=objects=resolved=0;history[0]=history[1]=metadata[0]=metadata[1]=0;
 cameraProgram=objectProgram=resolveProgram=blurProgram=copyProgram=0;
 width=height=0;ready=pending=historyValid=qfalse;previousWorld=NULL;memset(caches,0,sizeof(caches));
 ri.Cvar_Set("r_acTemporalReady","0");
}
void R_ACTemporalInit(void){
 qboolean loaded=qtrue;GLint units=0;
 taa=ri.Cvar_Get("r_acTAA","1",CVAR_ARCHIVE);blur=ri.Cvar_Get("r_acObjectMotionBlur","0",CVAR_ARCHIVE);debug=ri.Cvar_Get("r_acTemporalDebug","0",0);
 ri.Cvar_Get("r_acTemporalReady","0",CVAR_ROM);ri.Cvar_Set("r_acTemporalReady","0");
#define LOAD(ret,name,args) tm##name=(ret(APIENTRYP)args)SDL_GL_GetProcAddress("gl" #name);if(!tm##name)loaded=qfalse;
 TM_GL(LOAD)
#undef LOAD
 if(!loaded||!qglActiveTextureARB||!qglClientActiveTextureARB)return;
 qglGetIntegerv(GL_MAX_TEXTURE_IMAGE_UNITS,&units);if(units<6)return;
 cameraProgram=Program(tmScreenVertex,tmCameraFragment);objectProgram=Program(tmObjectVertex,tmObjectFragment);
 resolveProgram=Program(tmScreenVertex,tmResolveFragment);blurProgram=Program(tmScreenVertex,tmBlurFragment);copyProgram=Program(tmScreenVertex,tmCopyFragment);
 if(!cameraProgram||!objectProgram||!resolveProgram||!blurProgram||!copyProgram){R_ACTemporalShutdown();return;}
 tmGenFramebuffers(1,&fbo);qglGenTextures(1,&color);qglGenTextures(1,&sceneDepth);qglGenTextures(1,&velocity);qglGenTextures(1,&objects);
 qglGenTextures(2,history);qglGenTextures(2,metadata);qglGenTextures(1,&resolved);
 qglGetIntegerv(GL_SAMPLES,&framebufferSamples);ri.Printf(PRINT_ALL,"AC temporal framebuffer samples: %d\n",framebufferSamples);
 ready=qtrue;ri.Cvar_Set("r_acTemporalReady","1");ri.Printf(PRINT_ALL,"AC temporal ready: jittered TAA, deformed object history, camera-independent object motion blur.\n");
}
void RB_ACTemporalBegin(void){
 pending=Active()&&tr.world&&!backEnd.viewParms.isPortal&&!backEnd.viewParms.isPortalSky
  &&!(backEnd.refdef.rdflags&(RDF_NOWORLDMODEL|RDF_HUD))&&!backEnd.isHyperspace;
 if(!pending){if(!Active())historyValid=qfalse;return;}
 sceneView=backEnd.viewParms;sceneRefdef=backEnd.refdef;numVertices=numBatches=0;overflow=qfalse;surfaceKey=NULL;
 /* The original weather fog changes with each flash as well. Never blend
  * its bright state into the next dark frame (or delay the flash onset). */
 if(historyValid&&fabsf(previousLightning-sceneRefdef.acLightning)>.001f)historyValid=qfalse;
 memset(caches[cacheIndex].entries,0,sizeof(caches[cacheIndex].entries));caches[cacheIndex].count=0;
 if(previousWorld!=tr.world||sceneView.frameCount!=previousFrame+1||sceneRefdef.time<previousTime||sceneRefdef.time-previousTime>200||previousTAA!=taa->integer
  ||fabsf(previousProjection[0]-sceneView.projectionMatrix[0])>.01f||fabsf(previousProjection[5]-sceneView.projectionMatrix[5])>.01f)historyValid=qfalse;
 if(historyValid){float relative[16],inverse[16];InverseView(sceneView.world.modelMatrix,inverse);Multiply(previousView,inverse,relative);
  if(relative[0]+relative[5]+relative[10]<2.5f||relative[12]*relative[12]+relative[13]*relative[13]+relative[14]*relative[14]>128*128)historyValid=qfalse;}
}
/* Isolate only dynamic surfaces; world batching remains untouched. */
qboolean RB_ACTemporalSurface(const void*surface){
 if(!pending||!backEnd.currentEntity||backEnd.currentEntity==&tr.worldEntity||backEnd.currentStaticModel)return qfalse;
 if(tess.numIndexes){RB_EndSurface();RB_BeginSurface(tess.shader);}
 surfaceKey=surface;return qtrue;
}
void RB_ACTemporalSurfaceEnd(qboolean isolated){if(isolated){RB_EndSurface();RB_BeginSurface(tess.shader);surfaceKey=NULL;}}
static unsigned HashKey(const tmKey*k){
 uintptr_t v=k->surface^(k->model>>3)^(k->shader<<3);unsigned h=(unsigned)(v^(v>>16));
 return (h^(unsigned)k->owner*2654435761u^(unsigned)k->parent*97u^(unsigned)k->weapon*31u^k->generation*2246822519u);
}
static tmEntry*Entry(tmCache*c,const tmKey*k,qboolean insert){
 unsigned h=HashKey(k)&(TM_SLOTS-1),i;for(i=0;i<TM_SLOTS;i++,h=(h+1)&(TM_SLOTS-1)){
  tmEntry*e=&c->entries[h];if(!e->occupied){if(insert){e->occupied=1;e->key=*k;}return insert?e:NULL;}
  if(!memcmp(&e->key,k,sizeof(*k)))return e;
 }return NULL;
}
void RB_ACTemporalCapture(void){
 const trRefEntity_t*ent=backEnd.currentEntity;shaderStage_t*stage;tmBatch*b;tmEntry*old=NULL,*now=NULL;
 tmKey key;unsigned topology=2166136261u;int i,j,k;float scale=1; qboolean reactive,valid=qfalse;
 if(!pending||overflow||!tess.numIndexes||!tess.shader||tess.shader->isSky)return;
 stage=tess.xstages[0];if(!stage)return;
 reactive=tess.shader->sort>SS_SEE_THROUGH||((stage->stateBits&(GLS_SRCBLEND_BITS|GLS_DSTBLEND_BITS))&&!(stage->stateBits&GLS_DEPTHMASK_TRUE));
 /* Texture animation has no geometric velocity. Reject temporal accumulation
  * on those pixels instead of dragging fire/water/video textures behind. */
 if(stage->bundle[0].numImageAnimations>1||stage->bundle[0].numTexMods||stage->bundle[0].isVideoMap
    ||(!surfaceKey&&tess.shader->numDeforms))reactive=qtrue;
 if(!surfaceKey&&!reactive)return;
 if(numBatches>=TM_BATCHES||numVertices+tess.numIndexes>TM_VERTS){overflow=qtrue;return;}
 b=&batches[numBatches++];memset(b,0,sizeof(*b));b->first=numVertices;b->count=tess.numIndexes;b->reactive=reactive;b->cull=tess.shader->cullType;
 b->skin=stage->bundle[0].image[0]?stage->bundle[0].image[0]->texnum:tr.whiteImage->texnum;
 b->alpha=(stage->stateBits&GLS_ATEST_GE_80)?.5f:(stage->stateBits&GLS_ATEST_GT_0)?.01f:-1;
 b->weapon=ent&&ent!=&tr.worldEntity&&(ent->e.renderfx&RF_DEPTHHACK);
 if(b->weapon&&ent&&(ent->e.renderfx&RF_FIRST_PERSON)&&b->cull==CT_FRONT_SIDED)b->cull=CT_TWO_SIDED;
 if(backEnd.currentStaticModel)scale=backEnd.currentStaticModel->tiki->load_scale*backEnd.currentStaticModel->scale;
 if(!reactive&&surfaceKey&&ent){
  memset(&key,0,sizeof(key));key.surface=(uintptr_t)surfaceKey;key.model=(uintptr_t)ent->e.tiki^(uintptr_t)ent->e.hModel;
  key.shader=(uintptr_t)tess.shader;key.owner=ent->e.acMotionId?ENTITYNUM_NONE+ent->e.acMotionId:ent->e.entityNumber;
  key.generation=ent->e.acMotionGeneration;
  key.parent=ent->e.parentEntity>=0&&ent->e.parentEntity<backEnd.refdef.num_entities?backEnd.refdef.entities[ent->e.parentEntity].e.entityNumber:ENTITYNUM_NONE;
  key.weapon=b->weapon;
  for(i=0;i<tess.numIndexes;i++)topology=(topology^(unsigned)tess.indexes[i])*16777619u;
  old=Entry(&caches[1-cacheIndex],&key,qfalse);now=Entry(&caches[cacheIndex],&key,qtrue);
  if(now&&now->count){
   /* Temporary models can share ENTITYNUM_NONE and the same mesh. Never
    * match those by draw order: invalidate just their surfaces, not the world.
    * Also invalidate the first occurrence already queued this frame. */
   float id=(float)((HashKey(&key)&0x7fffff)+1);
   if(debug->integer&&sceneRefdef.time%1000<20)ri.Printf(PRINT_DEVELOPER,"AC_TEMPORAL_AMBIGUOUS owner=%d material=%s\n",key.owner,tess.shader->name);
   for(i=0;i<numBatches-1;i++)if(batches[i].id==id)batches[i].valid=0;
   now->count=-abs(now->count);now=NULL;old=NULL;
  }
  if(!now||caches[cacheIndex].count+tess.numVertexes>TM_CACHE_VERTS){
   /* Explicit invalid history is safe for untrackable or excessive objects. */
   b->id=0;
  }else{
  now->first=caches[cacheIndex].count;now->count=tess.numVertexes;now->topology=topology;caches[cacheIndex].count+=now->count;
  valid=historyValid&&old&&old->count==now->count&&old->topology==topology;
  b->id=(float)((HashKey(&key)&0x7fffff)+1);
  for(i=0;i<tess.numVertexes;i++){
   float*p=caches[cacheIndex].positions[now->first+i];
   for(j=0;j<3;j++)p[j]=backEnd.ori.origin[j]+scale*(tess.xyz[i][0]*backEnd.ori.axis[0][j]+tess.xyz[i][1]*backEnd.ori.axis[1][j]+tess.xyz[i][2]*backEnd.ori.axis[2][j]);
   if(valid&&DistanceSquared(p,caches[1-cacheIndex].positions[old->first+i])>128*128)valid=qfalse;
  }
  }
 }
 b->valid=valid?1:0;
 for(i=0;i<tess.numIndexes;i++){
  tmVertex*v=&vertices[numVertices++];k=tess.indexes[i];
  for(j=0;j<3;j++)v->xyz[j]=backEnd.ori.origin[j]+scale*(tess.xyz[k][0]*backEnd.ori.axis[0][j]+tess.xyz[k][1]*backEnd.ori.axis[1][j]+tess.xyz[k][2]*backEnd.ori.axis[2][j]);
  VectorCopy(valid?caches[1-cacheIndex].positions[old->first+k]:v->xyz,v->old);
  v->uv[0]=tess.texCoords[k][0][0];v->uv[1]=tess.texCoords[k][0][1];
 }
}
static void Texture(GLuint t,GLint format,GLenum external,GLenum type,GLint filter){
 qglBindTexture(GL_TEXTURE_2D,t);qglTexImage2D(GL_TEXTURE_2D,0,format,width,height,0,external,type,NULL);
 qglTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,filter);qglTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,filter);
 qglTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE);qglTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE);
}
static void Bind(int unit,GLuint t){qglActiveTextureARB(GL_TEXTURE0_ARB+unit);qglBindTexture(GL_TEXTURE_2D,t);}
static void Target(GLuint t){tmFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,t,0);}
static void Screen(GLuint p){
 static const float quad[12]={-1,-1,0,1,-1,0,1,1,0,-1,1,0};
 tmUseProgram(p);V(p,"size",width,height);qglClientActiveTextureARB(GL_TEXTURE0_ARB);qglDisableClientState(GL_TEXTURE_COORD_ARRAY);qglDisableClientState(GL_NORMAL_ARRAY);
 qglVertexPointer(3,GL_FLOAT,0,quad);qglDrawArrays(GL_QUADS,0,4);
}
static qboolean Resize(void){
 GLuint targets[7]={velocity,objects,resolved,history[0],history[1],metadata[0],metadata[1]};
 int i;if(width==sceneView.viewportWidth&&height==sceneView.viewportHeight)return qtrue;
 width=sceneView.viewportWidth;height=sceneView.viewportHeight;historyValid=qfalse;
 Texture(color,GL_RGBA8,GL_RGBA,GL_UNSIGNED_BYTE,GL_LINEAR);Texture(sceneDepth,GL_DEPTH_COMPONENT24,GL_DEPTH_COMPONENT,GL_UNSIGNED_INT,GL_NEAREST);
 Texture(velocity,GL_RGBA32F,GL_RGBA,GL_FLOAT,GL_NEAREST);Texture(objects,GL_RGBA32F,GL_RGBA,GL_FLOAT,GL_NEAREST);
 Texture(resolved,GL_RGBA16F,GL_RGBA,GL_FLOAT,GL_LINEAR);
 for(i=0;i<2;i++){Texture(history[i],GL_RGBA16F,GL_RGBA,GL_FLOAT,GL_LINEAR);Texture(metadata[i],GL_RG32F,GL_RG,GL_FLOAT,GL_NEAREST);}
 for(i=0;i<7;i++){
  Target(targets[i]);if(tmCheckFramebufferStatus(GL_FRAMEBUFFER)!=GL_FRAMEBUFFER_COMPLETE){ri.Printf(PRINT_WARNING,"AC temporal framebuffer unavailable; effects disabled.\n");ready=qfalse;ri.Cvar_Set("r_acTemporalReady","0");return qfalse;}
 }return qtrue;
}
/* The full slider range intentionally reaches a strong 1/15s exposure.
 * Normalize by frame duration, not a fixed per-frame multiplier. */
static float Shutter(int elapsed){
 return historyValid&&elapsed>0&&blur->value>0?fminf(blur->value,100)*.01f*66.6667f/fmaxf(elapsed,1):0;
}
void RB_ACTemporalFinish(void){
 GLint oldFbo,oldProgram,oldDraw,oldRead;int pass,i,elapsed,start=0;float inverse[16],relative[16],currentMVP[16],previousMVP[16],weaponPrevious[16];
 qboolean compare;static int comparisonIndex;
 GLenum error;
 if(!pending)return;pending=qfalse;surfaceKey=NULL;
 compare=debug->integer==4;
 if(debug->integer){qglGetError();qglFinish();start=ri.Milliseconds();}
 qglGetIntegerv(GL_FRAMEBUFFER_BINDING,&oldFbo);qglGetIntegerv(GL_CURRENT_PROGRAM,&oldProgram);qglGetIntegerv(GL_DRAW_BUFFER,&oldDraw);qglGetIntegerv(GL_READ_BUFFER,&oldRead);
 tmPushAttrib(GL_ALL_ATTRIB_BITS);tmPushClientAttrib(GL_CLIENT_ALL_ATTRIB_BITS);qglActiveTextureARB(GL_TEXTURE0_ARB);qglClientActiveTextureARB(GL_TEXTURE0_ARB);
 tmBindFramebuffer(GL_FRAMEBUFFER,fbo);qglDrawBuffer(GL_COLOR_ATTACHMENT0);tmReadBuffer(GL_COLOR_ATTACHMENT0);
 if(!Resize())goto restore;
 tmBindFramebuffer(GL_FRAMEBUFFER,oldFbo);tmReadBuffer(oldRead);
 qglBindTexture(GL_TEXTURE_2D,color);qglCopyTexSubImage2D(GL_TEXTURE_2D,0,0,0,sceneView.viewportX,sceneView.viewportY,width,height);
 qglBindTexture(GL_TEXTURE_2D,sceneDepth);qglCopyTexSubImage2D(GL_TEXTURE_2D,0,0,0,sceneView.viewportX,sceneView.viewportY,width,height);
 tmBindFramebuffer(GL_FRAMEBUFFER,fbo);qglDrawBuffer(GL_COLOR_ATTACHMENT0);tmReadBuffer(GL_COLOR_ATTACHMENT0);
 qglViewport(0,0,width,height);qglScissor(0,0,width,height);qglDisable(GL_DEPTH_TEST);qglDepthMask(GL_FALSE);qglDisable(GL_FOG);qglDisable(GL_LIGHTING);
 qglDisable(GL_ALPHA_TEST);qglDisable(GL_STENCIL_TEST);qglDisable(GL_CLIP_PLANE0);qglDisable(GL_CULL_FACE);qglDisable(GL_BLEND);qglDisable(GL_POLYGON_OFFSET_FILL);
 qglColorMask(GL_TRUE,GL_TRUE,GL_TRUE,GL_TRUE);qglDisableClientState(GL_COLOR_ARRAY);qglEnableClientState(GL_VERTEX_ARRAY);qglDepthRange(0,1);
 InverseView(sceneView.world.modelMatrix,inverse);Multiply(previousView,inverse,relative);
 Multiply(sceneView.projectionMatrix,sceneView.world.modelMatrix,currentMVP);Multiply(previousProjection,previousView,previousMVP);
 /* View weapons move with the camera: measure animation in camera space. */
 Multiply(sceneView.projectionMatrix,previousView,weaponPrevious);
 elapsed=sceneRefdef.time-previousTime;
 if(overflow)historyValid=qfalse;
 for(pass=0;pass<2;pass++){
  Target(pass?objects:velocity);Bind(0,sceneDepth);tmUseProgram(cameraProgram);I(cameraProgram,"depthTexture",0);I(cameraProgram,"objectPass",pass);
  M(cameraProgram,"previousFromCurrent",relative);M(cameraProgram,"previousProjection",previousProjection);
  V(cameraProgram,"projectionScale",sceneView.projectionMatrix[0],sceneView.projectionMatrix[5]);V(cameraProgram,"projectionOffset",sceneView.projectionMatrix[8],sceneView.projectionMatrix[9]);
  V(cameraProgram,"depthReconstruct",sceneView.projectionMatrix[10],sceneView.projectionMatrix[14]);Screen(cameraProgram);
  if(overflow)continue;
  tmUseProgram(objectProgram);M(objectProgram,"currentMVP",currentMVP);M(objectProgram,"previousMVP",previousMVP);M(objectProgram,"currentViewPrevious",currentMVP);M(objectProgram,"weaponPrevious",weaponPrevious);
  V(objectProgram,"size",width,height);I(objectProgram,"depthTexture",1);I(objectProgram,"skin",0);I(objectProgram,"objectPass",pass);
  F(objectProgram,"sampleRadius",framebufferSamples>1?.5f:0);Bind(1,sceneDepth);qglActiveTextureARB(GL_TEXTURE0_ARB);
  qglClientActiveTextureARB(GL_TEXTURE0_ARB);qglEnableClientState(GL_TEXTURE_COORD_ARRAY);qglTexCoordPointer(2,GL_FLOAT,sizeof(tmVertex),vertices[0].uv);
  qglClientActiveTextureARB(GL_TEXTURE1_ARB);qglEnableClientState(GL_TEXTURE_COORD_ARRAY);qglTexCoordPointer(3,GL_FLOAT,sizeof(tmVertex),vertices[0].old);
  qglClientActiveTextureARB(GL_TEXTURE0_ARB);qglVertexPointer(3,GL_FLOAT,sizeof(tmVertex),vertices[0].xyz);
  for(i=0;i<numBatches;i++){
   tmBatch*b=&batches[i];qglBindTexture(GL_TEXTURE_2D,b->skin);F(objectProgram,"alphaCut",b->alpha);F(objectProgram,"identity",b->id);F(objectProgram,"valid",b->valid);
   I(objectProgram,"weapon",b->weapon);I(objectProgram,"reactive",b->reactive);
   if(b->cull==CT_TWO_SIDED)qglDisable(GL_CULL_FACE);else{qglEnable(GL_CULL_FACE);qglCullFace((b->cull==CT_BACK_SIDED)!=sceneView.isMirror?GL_BACK:GL_FRONT);}
   qglDepthRange(0,b->weapon?.3:1);qglDrawArrays(GL_TRIANGLES,b->first,b->count);
  }
  qglDisable(GL_CULL_FACE);qglDepthRange(0,1);qglClientActiveTextureARB(GL_TEXTURE1_ARB);qglDisableClientState(GL_TEXTURE_COORD_ARRAY);qglClientActiveTextureARB(GL_TEXTURE0_ARB);
 }
 if(debug->integer==3||compare){
  int bytes=width*height*4*sizeof(float);float *pixels=ri.Malloc(bytes);
  Target(objects);qglReadPixels(0,0,width,height,GL_RGBA,GL_FLOAT,pixels);ri.FS_WriteFile("temporal-objects.f32",pixels,bytes);
  if(compare)ri.FS_WriteFile(va("temporal-%03d-objects.f32",comparisonIndex),pixels,bytes);
  Target(velocity);qglReadPixels(0,0,width,height,GL_RGBA,GL_FLOAT,pixels);ri.FS_WriteFile("temporal-motion.f32",pixels,bytes);
  ri.Free(pixels);ri.Cvar_Set("r_acTemporalDebug","1");
 }
 Target(resolved);Bind(0,color);tmUseProgram(copyProgram);I(copyProgram,"image",0);I(copyProgram,"linearize",1);Screen(copyProgram);
 Target(history[historyIndex]);tmUseProgram(resolveProgram);
 Bind(0,resolved);Bind(1,history[1-historyIndex]);Bind(2,velocity);Bind(3,objects);Bind(4,metadata[1-historyIndex]);
 I(resolveProgram,"currentColor",0);I(resolveProgram,"oldColor",1);I(resolveProgram,"motion",2);I(resolveProgram,"objectData",3);I(resolveProgram,"oldData",4);
 V(resolveProgram,"currentJitter",sceneView.projectionMatrix[8]*.5f,sceneView.projectionMatrix[9]*.5f);V(resolveProgram,"previousJitter",previousProjection[8]*.5f,previousProjection[9]*.5f);
 F(resolveProgram,"retention",taa->integer&&historyValid?powf(.9f,fmaxf(elapsed,1)/16.6667f):0);Screen(resolveProgram);
 Target(metadata[historyIndex]);Bind(0,objects);tmUseProgram(copyProgram);I(copyProgram,"image",0);I(copyProgram,"linearize",2);Screen(copyProgram);
 /* The history is pre-blur: a blurred silhouette can never feed back into TAA. */
 tmBindFramebuffer(GL_FRAMEBUFFER,oldFbo);qglDrawBuffer(oldDraw);tmReadBuffer(oldRead);qglViewport(sceneView.viewportX,sceneView.viewportY,width,height);qglScissor(sceneView.viewportX,sceneView.viewportY,width,height);
 Bind(0,history[historyIndex]);Bind(1,objects);tmUseProgram(blurProgram);I(blurProgram,"image",0);I(blurProgram,"objectData",1);
 F(blurProgram,"shutter",Shutter(elapsed));
 V(blurProgram,"currentJitter",sceneView.projectionMatrix[8]*.5f,sceneView.projectionMatrix[9]*.5f);
 F(blurProgram,"diagnostic",debug->integer==2?1:0);
 if(compare){
  int bytes=width*height*4;byte*pixels=ri.Malloc(bytes);
  F(blurProgram,"shutter",0);Screen(blurProgram);tmReadBuffer(oldDraw);
  qglReadPixels(sceneView.viewportX,sceneView.viewportY,width,height,GL_RGBA,GL_UNSIGNED_BYTE,pixels);
  ri.FS_WriteFile(va("temporal-%03d-sharp.rgba",comparisonIndex),pixels,bytes);
  F(blurProgram,"shutter",Shutter(elapsed));Screen(blurProgram);
  qglReadPixels(sceneView.viewportX,sceneView.viewportY,width,height,GL_RGBA,GL_UNSIGNED_BYTE,pixels);
  ri.FS_WriteFile(va("temporal-%03d-blur.rgba",comparisonIndex),pixels,bytes);ri.Free(pixels);
  ri.Printf(PRINT_ALL,"AC_TEMPORAL_COMPARE index=%d size=%dx%d elapsed=%d strength=%g history=%d\n",comparisonIndex++,width,height,elapsed,blur->value,historyValid);
 }else Screen(blurProgram);
 memcpy(previousView,sceneView.world.modelMatrix,sizeof(previousView));memcpy(previousProjection,sceneView.projectionMatrix,sizeof(previousProjection));
 previousTime=sceneRefdef.time;previousFrame=sceneView.frameCount;previousWorld=tr.world;previousTAA=taa->integer;
 previousLightning=sceneRefdef.acLightning;
 historyValid=!overflow;historyIndex=1-historyIndex;cacheIndex=1-cacheIndex;
restore:
 tmBindFramebuffer(GL_FRAMEBUFFER,oldFbo);qglDrawBuffer(oldDraw);tmReadBuffer(oldRead);tmUseProgram(oldProgram);tmPopClientAttrib();tmPopAttrib();
 if(debug->integer){qglFinish();error=qglGetError();if(sceneRefdef.time%1000<80)ri.Printf(PRINT_ALL,"AC_TEMPORAL batches=%d vertices=%d valid=%d overflow=%d ms=%d gl_error=%d\n",numBatches,numVertices,historyValid,overflow,ri.Milliseconds()-start,error);}
}
