/* Allied Campaign weather exposure. GPL-2.0-or-later.
 * A transient scene effect, never a player preference or archived cvar.
 * Normal fog stays intact during thunder. Directional sky visibility separates
 * enclosed rooms from exposed surfaces independently of the camera, including
 * the exterior seen through a window. Expose before TAA/blur so the scene and
 * its mask are reconstructed together; the HUD is drawn after both passes.
 */
#include "tr_local.h"
#include "SDL.h"

#define LIGHTNING_TILE_SIZE 2048
#define LIGHTNING_ATLAS_SIZE (3 * atlasTileSize)
#define LIGHTNING_DIRECTIONS 9
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
static GLuint framebuffer,sceneDepth,roofDepth,staticDepth,program;
static int depthWidth,depthHeight,framebufferSamples;
static int atlasTileSize=LIGHTNING_TILE_SIZE;
static qboolean attempted,ready,dumped,pendingWorld,staticValid,atlasValid;
static unsigned long long brushFingerprint;
static float skyMatrices[LIGHTNING_DIRECTIONS][16];

static const char *lightningVertex=
    "#version 120\n"
    "varying vec2 uv; void main(){gl_Position=gl_Vertex;uv=gl_Vertex.xy*0.5+0.5;}\n";
static const char *lightningFragment=
    "#version 120\n"
    "uniform sampler2D sceneDepth,roofDepth; uniform mat4 inverseView;\n"
    "uniform vec4 projection; uniform vec2 depthPair,depthTexel;\n"
    "uniform mat4 skyMatrices[9];\n"
    "uniform float exposure,tileResolution,sampleRadius; varying vec2 uv;\n"
    // Projected depth is affine on a plane. Validate each side independently
    // with a second neighbor: a triangle edge can have a different slope on
    // the other side, while a true object jump fails extrapolation to center.
    "float depthError(vec2 at,float d1,float d){\n"
    " vec2 second=uv+2.0*(at-uv);float d2=texture2D(sceneDepth,second).r;\n"
    " if(d1>=1.0 || d2>=1.0 || any(lessThan(second,vec2(0.0))) || any(greaterThan(second,vec2(1.0))))return 1.0;\n"
    " return abs(2.0*d1-d2-d); }\n"
    "bool depthNeighbor(vec2 at,float d1,float d){return depthError(at,d1,d)<=3.0/16777215.0+0.02*abs(d1-d); }\n"
    // Across a curved terrain crease neither side need be exactly planar.
    // Four monotonic, comparably sized gradients prove continuity; an object
    // edge instead has a jump next to flat samples and fails this bounded test.
    "bool depthCurve(vec2 a,vec2 b,float da,float db,float d){\n"
    " vec2 aa=uv+2.0*(a-uv),bb=uv+2.0*(b-uv);\n"
    " if(any(lessThan(aa,vec2(0.0)))||any(greaterThan(aa,vec2(1.0)))||any(lessThan(bb,vec2(0.0)))||any(greaterThan(bb,vec2(1.0))))return false;\n"
    " float daa=texture2D(sceneDepth,aa).r,dbb=texture2D(sceneDepth,bb).r;\n"
    " if(max(max(da,db),max(daa,dbb))>=1.0)return false;\n"
    " vec4 g=vec4(da-daa,d-da,db-d,dbb-db);\n"
    " bool monotonic=all(greaterThan(g,vec4(0.0)))||all(lessThan(g,vec4(0.0)));g=abs(g);\n"
    " return monotonic && min(min(g.x,g.y),min(g.z,g.w))>=0.5*max(max(g.x,g.y),max(g.z,g.w)); }\n"
    "float neighborStep(vec2 at,float d,float z){\n"
    " float n=texture2D(sceneDepth,at).r;float nz=-depthPair.y/(n*2.0-1.0+depthPair.x);\n"
    " vec2 opposite=2.0*uv-at;float other=texture2D(sceneDepth,opposite).r;\n"
    " if(n>=1.0 || (abs(nz-z)>max(2.0,abs(z)*0.01) && !depthNeighbor(at,n,d) && !depthCurve(at,opposite,n,other,d)))return -1.0;return abs(n-d); }\n"
    "float planeStep(float a,float b){if(a<0.0)return max(b,0.0);if(b<0.0)return a;return min(a,b);}\n"
    "vec3 worldAt(vec2 at,float z){\n"
    " vec3 eye=vec3(-(at*2.0-1.0+projection.zw)*z/projection.xy,z);\n"
    " return (inverseView*vec4(eye,1.0)).xyz;}\n"
    // Fragment-quad derivatives can join an indoor wall to a nearer object
    // and invent an outward-facing normal along its silhouette. Choose the
    // closest contiguous depth neighbor on each axis instead. When neither
    // side belongs to this surface, return zero and keep the unoffset query.
    "vec3 surfaceStep(vec2 offset,vec3 world,float z,float d){\n"
    " vec2 a=uv-offset,b=uv+offset;\n"
    " float da=texture2D(sceneDepth,a).r,db=texture2D(sceneDepth,b).r;\n"
    " float za=-depthPair.y/(da*2.0-1.0+depthPair.x),zb=-depthPair.y/(db*2.0-1.0+depthPair.x);\n"
    " float ea=abs(za-z),eb=abs(zb-z),limit=max(2.0,abs(z)*0.01);\n"
    " bool va=da<1.0 && ea<=limit && all(greaterThanEqual(a,vec2(0.0)));\n"
    " bool vb=db<1.0 && eb<=limit && all(lessThanEqual(b,vec2(1.0)));\n"
    // Prefer the side that reconstructs this pixel's plane, even when both
    // neighbors are close in eye depth. At a wall/ceiling crease the nearest
    // neighbor alone can invent a diagonal normal into the adjacent room.
    " float pa=depthError(a,da,d),pb=depthError(b,db,d);\n"
    " bool ca=pa<=3.0/16777215.0+0.02*abs(da-d),cb=pb<=3.0/16777215.0+0.02*abs(db-d);\n"
    " if(ca && (!cb || pa<=pb))return world-worldAt(a,za);\n"
    " if(cb)return worldAt(b,zb)-world;\n"
    " if(depthCurve(a,b,da,db,d))return pa<=pb?world-worldAt(a,za):worldAt(b,zb)-world;\n"
    " if(va && (!vb || ea<=eb))return world-worldAt(a,za);\n"
    " if(vb)return worldAt(b,zb)-world;return vec3(0.0);}\n"
    // Hemisphere visibility uses complete walls/roofs from nine fixed sky
    // directions. A shallow eave blocks the zenith but not the lateral sky.
    // Sample comparison results, not interpolated depths, and correct each
    // PCF tap for the receiver plane without moving a probe through a wall.
    "vec2 skyTap(vec2 tap,vec2 center,vec2 tile,float depth,vec2 slope,vec3 worldScale,vec3 worldZ){\n"
    " tap=clamp(tap,vec2(0.5/tileResolution),vec2(1.0-0.5/tileResolution));float blocker=texture2D(roofDepth,(tile+tap)/3.0).r;\n"
    " float visible=float(blocker>=1.0 || depth+dot(tap-center,slope)-1.0/16777215.0<=blocker);\n"
    " float radius=clamp(3.0*max(worldScale.x,worldScale.y)/tileResolution,8.0,32.0);\n"
    " vec3 delta=vec3(tap-center,blocker-depth)*worldScale;float distance=length(delta);\n"
    // A nearby steep terrain triangle or ground below a model is not a
    // ceiling. Reconstruct the blocker's slope only for a nearby opaque tap
    // above this receiver; all other taps keep the original filtered result.
    // Scene and atlas depth quantization can put a ceiling less than .01
    // world units below its receiver at the shared edge (measured: .007).
    // Tolerate only that comparison error; do not move either depth query.
    " if(visible>0.5 || distance>=2.0*radius || dot(delta,worldZ)<-0.01)return vec2(visible,0.0);\n"
    " float stepUV=1.0/tileResolution,lo=0.5*stepUV,hi=1.0-lo;\n"
    " vec2 left=tap-vec2(stepUV,0.0),right=tap+vec2(stepUV,0.0),down=tap-vec2(0.0,stepUV),up=tap+vec2(0.0,stepUV);\n"
    " float dl=texture2D(roofDepth,(tile+clamp(left,vec2(lo),vec2(hi)))/3.0).r;\n"
    " float dr=texture2D(roofDepth,(tile+clamp(right,vec2(lo),vec2(hi)))/3.0).r;\n"
    " float dd=texture2D(roofDepth,(tile+clamp(down,vec2(lo),vec2(hi)))/3.0).r;\n"
    " float du=texture2D(roofDepth,(tile+clamp(up,vec2(lo),vec2(hi)))/3.0).r;\n"
    // Reject out-of-tile and sky neighbors instead of treating clamped copies
    // of the center or sky depth as flat, artificial ceiling normals.
    " bool vl=left.x>=lo && dl<1.0,vr=right.x<=hi && dr<1.0,vd=down.y>=lo && dd<1.0,vu=up.y<=hi && du<1.0;\n"
    " if((!vl && !vr)||(!vd && !vu))return vec2(visible,0.0);\n"
    " float dx=vl && (!vr || abs(blocker-dl)<=abs(dr-blocker))?blocker-dl:dr-blocker;\n"
    " float dy=vd && (!vu || abs(blocker-dd)<=abs(du-blocker))?blocker-dd:du-blocker;\n"
    " vec3 normal=cross(vec3(stepUV*worldScale.x,0.0,dx*worldScale.z),vec3(0.0,stepUV*worldScale.y,dy*worldScale.z));\n"
    " normal*=inversesqrt(max(dot(normal,normal),1.0e-20));\n"
    " if(abs(dot(normal,worldZ))<=0.5)return vec2(visible,0.0);\n"
    " return vec2(visible,1.0-smoothstep(radius,2.0*radius,distance)); }\n"
    "vec2 skyVisibility(int i,vec3 probe,vec3 normal){\n"
    " mat4 m=skyMatrices[i];vec3 p=(m*vec4(probe,1.0)).xyz*0.5+0.5;\n"
    " vec3 x=vec3(m[0][0],m[1][0],m[2][0]);\n"
    " vec3 y=vec3(m[0][1],m[1][1],m[2][1]);\n"
    " vec3 z=vec3(m[0][2],m[1][2],m[2][2]);\n"
    // A small diffuse wrap includes back-facing foliage, while the actual
    // surface orientation keeps inward-facing window frames sheltered.
    " float facing=max(dot(normal,-normalize(z)),0.10);\n"
    " if(dot(normal,normal)<0.5)facing=1.0;\n"
    " if(any(lessThanEqual(p,vec3(0.0)))||any(greaterThanEqual(p,vec3(1.0))))return vec2(facing);\n"
    " vec3 worldScale=2.0/vec3(length(x),length(y),length(z));\n"
    " vec3 worldZ=vec3(normalize(x).z,normalize(y).z,normalize(z).z);\n"
    " vec3 plane=vec3(dot(normal,x)/dot(x,x),dot(normal,y)/dot(y,y),dot(normal,z)/dot(z,z));\n"
    " vec2 slope=abs(dot(normal,normalize(z)))>0.15?-plane.xy/plane.z:vec2(0.0);\n"
    " vec2 grid=p.xy*tileResolution-0.5,weight=fract(grid);\n"
    " vec2 base=(floor(grid)+0.5)/tileResolution;float stepUV=1.0/tileResolution;\n"
    " vec2 tile=vec2(mod(float(i),3.0),floor(float(i)/3.0));\n"
    " vec2 a=skyTap(base,p.xy,tile,p.z,slope,worldScale,worldZ);\n"
    " vec2 b=skyTap(base+vec2(stepUV,0.0),p.xy,tile,p.z,slope,worldScale,worldZ);\n"
    " vec2 c=skyTap(base+vec2(0.0,stepUV),p.xy,tile,p.z,slope,worldScale,worldZ);\n"
    " vec2 e=skyTap(base+vec2(stepUV),p.xy,tile,p.z,slope,worldScale,worldZ);\n"
    // At wall/ceiling contacts, one texel footprint can cross the roof edge.
    // Conservatively retain nearby ceilings instead of averaging in sky from
    // the other side. Distant occluders retain soft PCF edges; the contact
    // weight falls off smoothly in world space. Upward terrain keeps its result
    // so adjacent curved terrain triangles cannot cast a false contact strip.
    " float filtered=mix(mix(a.x,b.x,weight.x),mix(c.x,e.x,weight.x),weight.y);\n"
    " float cover=min(min(a.x,b.x),min(c.x,e.x)),contact=max(max(a.y,b.y),max(c.y,e.y));\n"
    " if(normal.z<0.5){\n"
    "  vec2 nearest=(floor(p.xy*tileResolution)+0.5)/tileResolution;\n"
    "  for(int sy=-1;sy<=1;sy++)for(int sx=-1;sx<=1;sx++)\n"
    "   {vec2 t=skyTap(nearest+vec2(float(sx),float(sy))*stepUV,p.xy,tile,p.z,slope,worldScale,worldZ);cover=min(cover,t.x);contact=max(contact,t.y);}\n"
    " }\n"
    " float visible=mix(filtered,cover,contact*(1.0-smoothstep(0.25,0.5,normal.z)));\n"
    " return vec2(visible*facing,facing); }\n"
    "void main(){\n"
    " float d=texture2D(sceneDepth,uv).r;\n"
    // Use the actual projection, including this frame's TAA jitter.
    " float z=-depthPair.y/(d*2.0-1.0+depthPair.x);\n"
    " vec3 world=worldAt(uv,z);\n"
    " vec3 normal=cross(surfaceStep(vec2(depthTexel.x,0.0),world,z,d),surfaceStep(vec2(0.0,depthTexel.y),world,z,d));\n"
    " normal*=inversesqrt(max(dot(normal,normal),1.0e-20));\n"
    " if(dot(normal,inverseView[3].xyz-world)<0.0)normal=-normal;\n"
    // View weapons have artificial 0..0.3 depth: query their player's location,
    // never pretend their reconstructed depth is a real point in the map.
    " if(d<=0.300001){world=inverseView[3].xyz;normal=vec3(0.0);}\n"
    " float outdoor=1.0;\n"
    " if(d<1.0){\n"
    "  vec3 probe=world+normal*2.0;vec2 sky=vec2(0.0);\n"
    "  for(int i=0;i<9;i++)sky+=skyVisibility(i,probe,normal);\n"
    "  outdoor=smoothstep(0.12,0.60,sky.x/max(sky.y,0.1));\n"
    " }\n"
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
        ||glConfig.maxTextureSize<3072)return;
    atlasTileSize=glConfig.maxTextureSize>=3*LIGHTNING_TILE_SIZE?LIGHTNING_TILE_SIZE:1024;
    vs=LightningCompile(GL_VERTEX_SHADER,lightningVertex);fs=LightningCompile(GL_FRAGMENT_SHADER,lightningFragment);
    if(vs&&fs){
        program=ltCreateProgram();ltAttachShader(program,vs);ltAttachShader(program,fs);ltLinkProgram(program);
        ltGetProgramiv(program,GL_LINK_STATUS,&ok);
        if(!ok){ltGetProgramInfoLog(program,sizeof(log),NULL,log);ri.Printf(PRINT_WARNING,"AC lightning link: %s\n",log);ltDeleteProgram(program);program=0;}
    }
    if(vs)ltDeleteShader(vs);if(fs)ltDeleteShader(fs);
    if(!program)return;
    ltGenFramebuffers(1,&framebuffer);qglGenTextures(1,&sceneDepth);qglGenTextures(1,&roofDepth);qglGenTextures(1,&staticDepth);
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
    GLint oldFbo,oldDraw,oldRead;int i;GLuint attachments[3];qboolean valid=qtrue;
    LightningInit();
    if(!ready||(depthWidth==flashView.viewportWidth&&depthHeight==flashView.viewportHeight))return;
    qglGetIntegerv(GL_FRAMEBUFFER_BINDING,&oldFbo);
    qglGetIntegerv(GL_DRAW_BUFFER,&oldDraw);qglGetIntegerv(GL_READ_BUFFER,&oldRead);
    qglGetIntegerv(GL_SAMPLES,&framebufferSamples);
    ltPushAttrib(GL_ALL_ATTRIB_BITS);qglActiveTextureARB(GL_TEXTURE0_ARB);
    LightningTexture(sceneDepth,flashView.viewportWidth,flashView.viewportHeight);
    LightningTexture(roofDepth,LIGHTNING_ATLAS_SIZE,LIGHTNING_ATLAS_SIZE);
    LightningTexture(staticDepth,LIGHTNING_ATLAS_SIZE,LIGHTNING_ATLAS_SIZE);
    staticValid=atlasValid=qfalse;
    ltBindFramebuffer(GL_FRAMEBUFFER,framebuffer);qglDrawBuffer(GL_NONE);ltReadBuffer(GL_NONE);
    // All allocations must be renderable, including the second large atlas.
    // Checking only the combined atlas could accept an out-of-memory static
    // attachment and reuse undefined depth as if it were valid architecture.
    attachments[0]=sceneDepth;attachments[1]=roofDepth;attachments[2]=staticDepth;
    for(i=0;i<3;i++) {
        ltFramebufferTexture2D(GL_FRAMEBUFFER,GL_DEPTH_ATTACHMENT,GL_TEXTURE_2D,attachments[i],0);
        if(ltCheckFramebufferStatus(GL_FRAMEBUFFER)!=GL_FRAMEBUFFER_COMPLETE)valid=qfalse;
    }
    if(!valid){
        ri.Printf(PRINT_WARNING,"AC lightning depth storage unavailable; sky-only flash enabled.\n");ready=qfalse;
    }
    ltFramebufferTexture2D(GL_FRAMEBUFFER,GL_DEPTH_ATTACHMENT,GL_TEXTURE_2D,roofDepth,0);
    depthWidth=flashView.viewportWidth;depthHeight=flashView.viewportHeight;
    ltBindFramebuffer(GL_FRAMEBUFFER,oldFbo);qglDrawBuffer(oldDraw);ltReadBuffer(oldRead);ltPopAttrib();
}
void R_ACLightningReset(void) {
    pendingFlash=0;
    if(framebuffer&&ltDeleteFramebuffers)ltDeleteFramebuffers(1,&framebuffer);
    if(sceneDepth)qglDeleteTextures(1,&sceneDepth);
    if(roofDepth)qglDeleteTextures(1,&roofDepth);
    if(staticDepth)qglDeleteTextures(1,&staticDepth);
    if(program&&ltDeleteProgram)ltDeleteProgram(program);
    framebuffer=sceneDepth=roofDepth=staticDepth=program=0;
    staticValid=atlasValid=pendingWorld=qfalse;depthWidth=depthHeight=framebufferSamples=0;attempted=ready=dumped=qfalse;
}
void R_ACLightningWorldChanged(void) {
    staticValid=atlasValid=pendingWorld=qfalse;dumped=qfalse;
}
void RB_ACLightningBegin(void) {
    pendingFlash=0;pendingWorld=qfalse;
    if(!tr.world||backEnd.viewParms.isPortal||backEnd.viewParms.isPortalSky
        ||(backEnd.refdef.rdflags&(RDF_NOWORLDMODEL|RDF_HUD))||backEnd.isHyperspace)return;
    pendingWorld=qtrue;pendingFlash=Com_Clamp(0,1,backEnd.refdef.acLightning);
    flashView=backEnd.viewParms;
    if(flashView.viewportWidth>0&&flashView.viewportHeight>0)LightningPrepare();
}
static void LightningInverseView(const float *view,float *inverse) {
    int row,col;memset(inverse,0,16*sizeof(float));
    for(row=0;row<3;row++)for(col=0;col<3;col++)inverse[col*4+row]=view[row*4+col];
    for(row=0;row<3;row++)inverse[12+row]=-(inverse[row]*view[12]+inverse[4+row]*view[13]+inverse[8+row]*view[14]);
    inverse[15]=1;
}
static void LightningSkyMatrices(vec3_t lo,vec3_t hi) {
    int i,j,k;vec3_t corner;
    // Stable whole-map projections, never centered on the camera. Include
    // complete architectural walls as blockers for the lateral directions.
    for(j=0;j<3;j++){lo[j]=tr.world->nodes->mins[j]-64;hi[j]=tr.world->nodes->maxs[j]+64;}
    for(i=0;i<LIGHTNING_DIRECTIONS;i++) {
        vec3_t direction,right,up,low,high;float *m=skyMatrices[i];
        if(i==0)VectorSet(direction,0,0,1);
        else {float a=(i-1)*M_PI/4.0f;VectorSet(direction,cosf(a)*0.8660254f,sinf(a)*0.8660254f,0.5f);}
        if(i==0)VectorSet(right,1,0,0);
        else {VectorSet(right,-direction[1],direction[0],0);VectorNormalize(right);}
        CrossProduct(direction,right,up);ClearBounds(low,high);
        for(k=0;k<8;k++) {
            vec3_t p;
            for(j=0;j<3;j++)corner[j]=(k&(1<<j))?hi[j]:lo[j];
            VectorSet(p,DotProduct(corner,right),DotProduct(corner,up),DotProduct(corner,direction));
            AddPointToBounds(p,low,high);
        }
        memset(m,0,16*sizeof(float));
        for(j=0;j<3;j++) {
            m[j*4]=2*right[j]/(high[0]-low[0]);
            m[j*4+1]=2*up[j]/(high[1]-low[1]);
            m[j*4+2]=-2*direction[j]/(high[2]-low[2]);
        }
        m[12]=-(high[0]+low[0])/(high[0]-low[0]);
        m[13]=-(high[1]+low[1])/(high[1]-low[1]);
        m[14]=(high[2]+low[2])/(high[2]-low[2]);m[15]=1;
    }
}
static void LightningQuad(float z) {
    qglBegin(GL_QUADS);
    qglVertex3f(-1,-1,z);qglVertex3f(1,-1,z);qglVertex3f(1,1,z);qglVertex3f(-1,1,z);
    qglEnd();
}
static unsigned long long LightningHashBytes(unsigned long long h,const void *data,int bytes) {
    const byte *p=data;int i;for(i=0;i<bytes;i++)h=(h^p[i])*1099511628211ULL;return h;
}
static unsigned long long LightningBrushFingerprint(int *brushes) {
    unsigned long long sum=0,other=0;int i,count=0;
    for(i=0;i<backEnd.refdef.num_entities;i++) {
        const refEntity_t *e=&backEnd.refdef.entities[i].e;model_t *model;
        unsigned long long h=1469598103934665603ULL;
        if(e->reType!=RT_MODEL||e->shaderRGBA[3]<250
            ||(e->renderfx&(RF_DONTDRAW|RF_FIRST_PERSON|RF_DEPTHHACK)))continue;
        model=R_GetModelByHandle(e->hModel);if(!model||model->type!=MOD_BRUSH)continue;
        h=LightningHashBytes(h,&e->hModel,sizeof(e->hModel));
        h=LightningHashBytes(h,e->origin,sizeof(e->origin));
        h=LightningHashBytes(h,e->axis,sizeof(e->axis));
        sum+=h;other^=h*0x9e3779b97f4a7c15ULL;count++;
    }
    *brushes=count;return sum^(other<<1)^((unsigned long long)count<<32);
}
static int LightningDrawAtlas(const vec3_t lo,const vec3_t hi,int parts) {
    int i,draws=0;
    for(i=0;i<LIGHTNING_DIRECTIONS;i++) {
        int count;
        qglViewport((i%3)*atlasTileSize,(i/3)*atlasTileSize,atlasTileSize,atlasTileSize);
        qglScissor((i%3)*atlasTileSize,(i/3)*atlasTileSize,atlasTileSize,atlasTileSize);
        count=RB_ACDrawWorldOccluders(skyMatrices[i],lo,hi,parts);
        if(count<0)return -1;draws+=count;
    }
    return draws;
}
void RB_ACLightningFinish(void) {
    GLint matrixMode,oldProgram=0,oldFbo=0,oldDraw=0,oldRead=0;
    GLenum incomingError=GL_NO_ERROR;float flash=pendingFlash;
    float inverse[16];vec3_t lo,hi;
    int draws=0,start=0,brushes=0,staticRebuilt=0,dynamicRebuilt=0; qboolean spatial=qfalse,rebuild; cvar_t *debug;
    unsigned long long fingerprint;
    pendingFlash=0;
    if(!pendingWorld||flashView.viewportWidth<=0||flashView.viewportHeight<=0)return;
    pendingWorld=qfalse;
    // Prepare immutable geometry once, but rotating shutters must not copy
    // the large atlas or redraw doors between strikes. The next active flash
    // fingerprints the current pose and refreshes any stale dynamic coverage.
    if(!(flash>0)&&(!ready||staticValid))return;
    fingerprint=LightningBrushFingerprint(&brushes);
    rebuild=ready&&(!atlasValid||brushFingerprint!=fingerprint);
    if(!(flash>0)&&!rebuild)return;
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
        if(flash>0)qglCopyTexSubImage2D(GL_TEXTURE_2D,0,0,0,flashView.viewportX,flashView.viewportY,depthWidth,depthHeight);
        if(flash>0&&debug->integer>=3&&!dumped){
            int bytes=depthWidth*depthHeight*sizeof(float);float *pixels=ri.Malloc(bytes);
            qglReadPixels(flashView.viewportX,flashView.viewportY,depthWidth,depthHeight,GL_DEPTH_COMPONENT,GL_FLOAT,pixels);
            ri.FS_WriteFile("lightning-scene.f32",pixels,bytes);ri.Free(pixels);
        }
        if(rebuild) {
            LightningSkyMatrices(lo,hi);
            ltBindFramebuffer(GL_FRAMEBUFFER,framebuffer);qglDrawBuffer(GL_NONE);ltReadBuffer(GL_NONE);
            qglColorMask(GL_FALSE,GL_FALSE,GL_FALSE,GL_FALSE);qglDepthMask(GL_TRUE);
            qglDepthFunc(GL_LESS);qglDisable(GL_BLEND);qglClearDepth(1);
            if(!staticValid) {
                staticRebuilt=1;
                ltFramebufferTexture2D(GL_FRAMEBUFFER,GL_DEPTH_ATTACHMENT,GL_TEXTURE_2D,staticDepth,0);
                qglScissor(0,0,LIGHTNING_ATLAS_SIZE,LIGHTNING_ATLAS_SIZE);qglClear(GL_DEPTH_BUFFER_BIT);
                draws=LightningDrawAtlas(lo,hi,1);staticValid=draws>=0;
            }
            if(staticValid) {
                int count;
                // Copy immutable architecture on the GPU, then overlay current
                // brush doors/platforms. Moving doors never redraw the BSP nine
                // times; unchanged scenes reuse the complete atlas directly.
                ltFramebufferTexture2D(GL_FRAMEBUFFER,GL_DEPTH_ATTACHMENT,GL_TEXTURE_2D,staticDepth,0);
                qglBindTexture(GL_TEXTURE_2D,roofDepth);
                qglCopyTexSubImage2D(GL_TEXTURE_2D,0,0,0,0,0,LIGHTNING_ATLAS_SIZE,LIGHTNING_ATLAS_SIZE);
                ltFramebufferTexture2D(GL_FRAMEBUFFER,GL_DEPTH_ATTACHMENT,GL_TEXTURE_2D,roofDepth,0);
                dynamicRebuilt=1;count=LightningDrawAtlas(lo,hi,2);
                atlasValid=count>=0;draws+=count;
                if(atlasValid)brushFingerprint=fingerprint;
            }
        }
        spatial=atlasValid;
        if(flash>0&&debug->integer>=3&&!dumped){
            int bytes=LIGHTNING_ATLAS_SIZE*LIGHTNING_ATLAS_SIZE*sizeof(float);float *pixels=ri.Malloc(bytes),meta[32+16*LIGHTNING_DIRECTIONS];
            ltBindFramebuffer(GL_FRAMEBUFFER,framebuffer);qglDrawBuffer(GL_NONE);ltReadBuffer(GL_NONE);
            ltFramebufferTexture2D(GL_FRAMEBUFFER,GL_DEPTH_ATTACHMENT,GL_TEXTURE_2D,roofDepth,0);
            qglReadPixels(0,0,LIGHTNING_ATLAS_SIZE,LIGHTNING_ATLAS_SIZE,GL_DEPTH_COMPONENT,GL_FLOAT,pixels);
            ri.FS_WriteFile("lightning-roof.f32",pixels,bytes);ri.Free(pixels);
            memcpy(meta,flashView.world.modelMatrix,16*sizeof(float));
            memcpy(meta+16,flashView.projectionMatrix,16*sizeof(float));
            memcpy(meta+32,skyMatrices,sizeof(skyMatrices));
            ri.FS_WriteFile("lightning-meta.f32",meta,sizeof(meta));dumped=qtrue;
        }
        ltBindFramebuffer(GL_FRAMEBUFFER,oldFbo);qglDrawBuffer(oldDraw);ltReadBuffer(oldRead);
        if(spatial&&flash>0){
            ltUseProgram(program);LightningInverseView(flashView.world.modelMatrix,inverse);
            ltUniformMatrix4fv(ltGetUniformLocation(program,"inverseView"),1,GL_FALSE,inverse);
            ltUniform4f(ltGetUniformLocation(program,"projection"),flashView.projectionMatrix[0],flashView.projectionMatrix[5],flashView.projectionMatrix[8],flashView.projectionMatrix[9]);
            ltUniform2f(ltGetUniformLocation(program,"depthPair"),flashView.projectionMatrix[10],flashView.projectionMatrix[14]);
            ltUniform2f(ltGetUniformLocation(program,"depthTexel"),1.0f/depthWidth,1.0f/depthHeight);
            ltUniform1f(ltGetUniformLocation(program,"sampleRadius"),framebufferSamples>1?0.5f:0.0f);
            ltUniformMatrix4fv(ltGetUniformLocation(program,"skyMatrices"),LIGHTNING_DIRECTIONS,GL_FALSE,&skyMatrices[0][0]);
            ltUniform1f(ltGetUniformLocation(program,"exposure"),.65f*flash);
            ltUniform1f(ltGetUniformLocation(program,"tileResolution"),atlasTileSize);
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
    if(flash>0){qglColor4f(1,1,1,.65f*flash);LightningQuad(spatial?0.0f:1.0f);}
    qglPopMatrix();qglMatrixMode(GL_PROJECTION);qglPopMatrix();qglMatrixMode(matrixMode);
    if(ready)ltPopClientAttrib();
    ltPopAttrib();if(ltUseProgram)ltUseProgram(oldProgram);
    if(debug->integer){
        qglFinish();
        ri.Printf(PRINT_ALL,"AC_LIGHTNING strength=%.4f viewport=%dx%d spatial=%d blockers=%d ms=%d fog=%.4f,%.4f,%.4f gl_error=%d incoming_error=%d static_rebuilt=%d dynamic_rebuilt=%d brushes=%d\n",
            flash,flashView.viewportWidth,flashView.viewportHeight,spatial,draws,ri.Milliseconds()-start,
            flashView.farplane_color[0],flashView.farplane_color[1],flashView.farplane_color[2],qglGetError(),incomingError,staticRebuilt,dynamicRebuilt,brushes);
    }
}
