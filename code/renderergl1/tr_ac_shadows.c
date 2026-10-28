/* Allied Campaign model shadows. GPL-2.0-or-later.
 * Capture the already skinned opaque geometry, then render a depth silhouette
 * from a real map light. A second depth image selects the first receiver, so
 * a model cannot project through a floor onto another floor. World geometry
 * participates in occlusion/receiving only; it never produces a new shadow.
 * All storage is bounded and belongs to the renderer, not the savegame.
 */
#include "tr_local.h"
#include "SDL.h"

#define AC_VERTS 524288
#define AC_BATCHES 8192
#define AC_CASTERS 128
#define AC_MAP_SIZE 1024

typedef struct { float xyz[3], uv[2], normal[3]; } acShadowVertex_t;
typedef struct {
    int first, count, owner;
    GLuint texture;
    float alpha;
    qboolean polygonOffset;
    vec3_t mins, maxs;
} acShadowBatch_t;
typedef struct { int owner; vec3_t mins, maxs; float distance; } acShadowCaster_t;
static acShadowVertex_t vertices[AC_VERTS];
static acShadowBatch_t batches[AC_BATCHES];
static acShadowCaster_t casters[AC_CASTERS];
static int numVertices, numBatches, numCasters;
static qboolean collecting, finished, overflow, ready;
static GLuint framebuffer, maps[2], depthProgram, shadeProgram;
static cvar_t *enabled, *debug;
static float AC_Clamp(float v,float lo,float hi) {return v<lo?lo:v>hi?hi:v;}

/* GL1 deliberately doesn't load the programmable renderer's entry points.
 * Resolve only this pass's functions, without changing GL2's global pointers. */
#define AC_GL_FUNCTIONS(X) \
 X(void, GenFramebuffers, (GLsizei n, GLuint *p)) \
 X(void, DeleteFramebuffers, (GLsizei n, const GLuint *p)) \
 X(void, BindFramebuffer, (GLenum t, GLuint f)) \
 X(void, FramebufferTexture2D, (GLenum t, GLenum a, GLenum tt, GLuint tex, GLint l)) \
 X(GLenum, CheckFramebufferStatus, (GLenum t)) \
 X(GLuint, CreateShader, (GLenum t)) \
 X(void, ShaderSource, (GLuint s, GLsizei n, const char **text, const GLint *len)) \
 X(void, CompileShader, (GLuint s)) \
 X(void, GetShaderiv, (GLuint s, GLenum p, GLint *v)) \
 X(void, GetShaderInfoLog, (GLuint s, GLsizei n, GLsizei *l, char *log)) \
 X(void, DeleteShader, (GLuint s)) \
 X(GLuint, CreateProgram, (void)) \
 X(void, AttachShader, (GLuint p, GLuint s)) \
 X(void, LinkProgram, (GLuint p)) \
 X(void, GetProgramiv, (GLuint p, GLenum n, GLint *v)) \
 X(void, GetProgramInfoLog, (GLuint p, GLsizei n, GLsizei *l, char *log)) \
 X(void, DeleteProgram, (GLuint p)) \
 X(void, UseProgram, (GLuint p)) \
 X(GLint, GetUniformLocation, (GLuint p, const char *s)) \
 X(void, Uniform1i, (GLint u, GLint v)) \
 X(void, Uniform1f, (GLint u, GLfloat v)) \
 X(void, NormalPointer, (GLenum type, GLsizei stride, const GLvoid *pointer)) \
 X(void, UniformMatrix4fv, (GLint u, GLsizei n, GLboolean t, const GLfloat *m)) \
 X(void, PushAttrib, (GLbitfield b)) \
 X(void, PopAttrib, (void)) \
 X(void, PushClientAttrib, (GLbitfield b)) \
 X(void, PopClientAttrib, (void)) \
 X(void, ReadBuffer, (GLenum b))
#define AC_DECLARE(ret, name, args) static ret (APIENTRYP ac##name) args;
AC_GL_FUNCTIONS(AC_DECLARE)
#undef AC_DECLARE

static const char *vertexShader =
    "#version 120\n"
    "uniform mat4 mvp; uniform mat4 lightMatrix; varying vec4 lightPos; varying vec2 uv; varying float eyeDepth;\n"
    "void main(){ gl_Position=mvp*gl_Vertex; eyeDepth=gl_Position.w; lightPos=lightMatrix*gl_Vertex; uv=gl_MultiTexCoord0.xy; }\n";
static const char *depthShader =
    "#version 120\n"
    "uniform sampler2D skin; uniform float alphaCut; varying vec2 uv;\n"
    "void main(){if(alphaCut>=0.0 && texture2D(skin,uv).a<alphaCut)discard; gl_FragColor=vec4(1.0);}\n";
static const char *shadowShader =
    "#version 120\n"
    "uniform sampler2D silhouette; uniform sampler2D receiver; uniform float opacity; uniform float blurStep; uniform float fogStart; uniform float fogEnd;\n"
    "varying vec4 lightPos; varying float eyeDepth;\n"
    "void main(){\n"
    " if(lightPos.w<=0.0)discard; vec3 p=lightPos.xyz/lightPos.w*0.5+0.5;\n"
    " if(any(lessThanEqual(p,vec3(0.002)))||any(greaterThanEqual(p,vec3(0.998))))discard;\n"
    " float slope=min(0.012,2.0*fwidth(p.z));\n"
    " float front=texture2D(receiver,p.xy).r;\n"
    " if(abs(p.z-front)>0.0008+slope)discard;\n"
    " float shade=0.0; float bias=0.00025+0.35*slope;\n"
    " for(int y=-2;y<=2;y++)for(int x=-2;x<=2;x++){\n"
    " float z=texture2D(silhouette,p.xy+vec2(x,y)*blurStep).r;\n"
    " shade+=float(z<p.z-bias && z<0.9999); }\n"
    " float edge=min(min(p.x,1.0-p.x),min(p.y,1.0-p.y));\n"
    " float visibility=fogEnd>fogStart?clamp((fogEnd-eyeDepth)/(fogEnd-fogStart),0.0,1.0):1.0;\n"
    " gl_FragColor=vec4(0.0,0.0,0.0,visibility*opacity*shade/25.0*smoothstep(0.002,0.025,edge));\n"
    "}\n";

static GLuint AC_Compile(GLenum type, const char *source) {
    GLint ok; char log[1024]; GLuint s=acCreateShader(type);
    acShaderSource(s,1,&source,NULL); acCompileShader(s); acGetShaderiv(s,GL_COMPILE_STATUS,&ok);
    if(!ok) { acGetShaderInfoLog(s,sizeof(log),NULL,log); ri.Printf(PRINT_WARNING,"AC shadows shader: %s\n",log); acDeleteShader(s); return 0; }
    return s;
}
static GLuint AC_Program(const char *fragment) {
    GLuint vs=AC_Compile(GL_VERTEX_SHADER,vertexShader),fs=AC_Compile(GL_FRAGMENT_SHADER,fragment),p=0;
    GLint ok; char log[1024];
    if(vs&&fs) { p=acCreateProgram(); acAttachShader(p,vs); acAttachShader(p,fs); acLinkProgram(p);
        acGetProgramiv(p,GL_LINK_STATUS,&ok); if(!ok) {acGetProgramInfoLog(p,sizeof(log),NULL,log);ri.Printf(PRINT_WARNING,"AC shadows link: %s\n",log);acDeleteProgram(p);p=0;} }
    if(vs)acDeleteShader(vs);if(fs)acDeleteShader(fs);return p;
}
void R_ACShadowInit(void) {
    int i; GLint oldTex,oldFbo; qboolean loaded=qtrue;
    enabled=ri.Cvar_Get("r_acModelShadows","1",CVAR_ARCHIVE);
    debug=ri.Cvar_Get("r_acShadowDebug","0",0);
    ri.Cvar_Get("r_acShadowReady","0",CVAR_ROM); ri.Cvar_Set("r_acShadowReady","0");
#define AC_LOAD(ret,name,args) ac##name=(ret (APIENTRYP) args)SDL_GL_GetProcAddress("gl" #name); if(!ac##name)loaded=qfalse;
    AC_GL_FUNCTIONS(AC_LOAD)
#undef AC_LOAD
    if(!loaded || !qglActiveTextureARB || !qglClientActiveTextureARB || glConfig.numTextureUnits<2) {ri.Printf(PRINT_WARNING,"AC model shadows unavailable: OpenGL framebuffer/shader support missing; using legacy shadows.\n");return;}
    depthProgram=AC_Program(depthShader); shadeProgram=AC_Program(shadowShader);
    if(!depthProgram || !shadeProgram) {R_ACShadowShutdown();return;}
    qglGetIntegerv(GL_TEXTURE_BINDING_2D,&oldTex);qglGetIntegerv(GL_FRAMEBUFFER_BINDING,&oldFbo);
    qglGenTextures(2,maps); acGenFramebuffers(1,&framebuffer);acBindFramebuffer(GL_FRAMEBUFFER,framebuffer);
    acPushAttrib(GL_COLOR_BUFFER_BIT|GL_PIXEL_MODE_BIT);
    qglDrawBuffer(GL_NONE);acReadBuffer(GL_NONE);
    for(i=0;i<2;i++) {
        qglBindTexture(GL_TEXTURE_2D,maps[i]);
        qglTexImage2D(GL_TEXTURE_2D,0,GL_DEPTH_COMPONENT24,AC_MAP_SIZE,AC_MAP_SIZE,0,GL_DEPTH_COMPONENT,GL_UNSIGNED_INT,NULL);
        qglTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST);qglTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST);
        qglTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE);qglTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE);
        acFramebufferTexture2D(GL_FRAMEBUFFER,GL_DEPTH_ATTACHMENT,GL_TEXTURE_2D,maps[i],0);
        if(acCheckFramebufferStatus(GL_FRAMEBUFFER)!=GL_FRAMEBUFFER_COMPLETE)loaded=qfalse;
    }
    acBindFramebuffer(GL_FRAMEBUFFER,oldFbo);acPopAttrib();qglBindTexture(GL_TEXTURE_2D,oldTex);
    if(!loaded) {ri.Printf(PRINT_WARNING,"AC shadow framebuffer unsupported; using legacy shadows.\n");R_ACShadowShutdown();return;}
    ready=qtrue; ri.Cvar_Set("r_acShadowReady","1");
    ri.Printf(PRINT_ALL,"AC model shadows ready: NPCs/items, 1024 depth maps, filtered silhouette and first receiver.\n");
}
void R_ACShadowShutdown(void) {
    if(framebuffer&&acDeleteFramebuffers)acDeleteFramebuffers(1,&framebuffer);
    if(maps[0])qglDeleteTextures(2,maps);
    if(depthProgram&&acDeleteProgram)acDeleteProgram(depthProgram);
    if(shadeProgram&&acDeleteProgram)acDeleteProgram(shadeProgram);
    framebuffer=maps[0]=maps[1]=depthProgram=shadeProgram=0;ready=collecting=qfalse;
    ri.Cvar_Set("r_acShadowReady","0");
}
void RB_ACShadowBegin(void) {
    numVertices=numBatches=numCasters=0;overflow=qfalse;finished=qfalse;
    collecting=ready&&(enabled->integer||R_ACAOActive())&&tr.world&&!backEnd.viewParms.isPortal
        &&!(backEnd.refdef.rdflags&(RDF_NOWORLDMODEL|RDF_HUD))&&!backEnd.isHyperspace;
}
static qboolean AC_BoundsOverlap(const vec3_t a, const vec3_t b, const vec3_t c, const vec3_t d) {
    int i;for(i=0;i<3;i++)if(a[i]>d[i]||b[i]<c[i])return qfalse;return qtrue;
}
void RB_ACShadowCapture(void) {
    int i,j,k,owner=-1; acShadowBatch_t *b; shaderStage_t *stage;
    trRefEntity_t *ent=backEnd.currentEntity;
    if(collecting && debug->integer>3 && backEnd.refdef.time%1000<20 && tess.shader && tess.xstages[0])
        ri.Printf(PRINT_ALL,"AC_GEOMETRY %s sort=%.1f bits=%x offset=%d entity=%d vertices=%d\n",tess.shader->name,tess.shader->sort,tess.xstages[0]->stateBits,tess.shader->polygonOffset,ent?ent->e.reType:-1,tess.numIndexes);
    if(!collecting || finished || overflow || !tess.numIndexes || !tess.shader || tess.shader->isSky
        || tess.shader->sort<SS_OPAQUE || tess.shader->sort>SS_SEE_THROUGH)return;
    if(ent && ent!=&tr.worldEntity && ((ent->e.renderfx&(RF_FIRST_PERSON|RF_DEPTHHACK|RF_DONTDRAW|RF_AC_CORPSE_PROXY)) || ent->e.shaderRGBA[3]<250))return;
    stage=tess.xstages[0]; if(!stage)return;
    // Transparent surfaces have no reliable receiver depth. Alpha-tested cutouts do.
    if((stage->stateBits&(GLS_SRCBLEND_BITS|GLS_DSTBLEND_BITS)) && !(stage->stateBits&GLS_DEPTHMASK_TRUE))return;
    if(tess.shader->sort==SS_DECAL && !(stage->stateBits&GLS_DEPTHMASK_TRUE))return;
    if(numBatches==AC_BATCHES || numVertices+tess.numIndexes>AC_VERTS){overflow=qtrue;return;}
    if(ent&&ent!=&tr.worldEntity&&ent->e.acShadowCaster)owner=ent->e.acShadowOwner;
    b=&batches[numBatches++];b->first=numVertices;b->count=tess.numIndexes;b->owner=owner;
    b->polygonOffset=tess.shader->polygonOffset;
    b->texture=stage->bundle[0].image[0]?stage->bundle[0].image[0]->texnum:tr.whiteImage->texnum;
    b->alpha=-1;
    if(stage->stateBits&GLS_ATEST_GE_80)b->alpha=0.5f;
    else if(stage->stateBits&GLS_ATEST_GT_0)b->alpha=0.01f;
    ClearBounds(b->mins,b->maxs);
    for(i=0;i<tess.numIndexes;i++) {
        acShadowVertex_t *v=&vertices[numVertices++];k=tess.indexes[i];
        for(j=0;j<3;j++)v->xyz[j]=backEnd.ori.origin[j]+tess.xyz[k][0]*backEnd.ori.axis[0][j]
            +tess.xyz[k][1]*backEnd.ori.axis[1][j]+tess.xyz[k][2]*backEnd.ori.axis[2][j];
        v->uv[0]=tess.texCoords[k][0][0];v->uv[1]=tess.texCoords[k][0][1];AddPointToBounds(v->xyz,b->mins,b->maxs);
        // Skeletal surfaces always provide skinned normals; unlit BSP/terrain
        // batches may leave tess.normal undefined, so use face derivatives there.
        VectorClear(v->normal);
        if(ent&&ent!=&tr.worldEntity&&ent->e.tiki) {
            for(j=0;j<3;j++)v->normal[j]=tess.normal[k][0]*backEnd.ori.axis[0][j]
                +tess.normal[k][1]*backEnd.ori.axis[1][j]+tess.normal[k][2]*backEnd.ori.axis[2][j];
            VectorNormalize(v->normal);
        }
    }
    if(owner>=0) {
        for(i=0;i<numCasters;i++)if(casters[i].owner==owner)break;
        if(i==numCasters) {if(i==AC_CASTERS)return;numCasters++;casters[i].owner=owner;ClearBounds(casters[i].mins,casters[i].maxs);}
        AddPointToBounds(b->mins,casters[i].mins,casters[i].maxs);AddPointToBounds(b->maxs,casters[i].mins,casters[i].maxs);
    }
}
static void AC_Multiply(const float *a,const float *b,float *out) {
    int row,col,k;for(col=0;col<4;col++)for(row=0;row<4;row++){out[col*4+row]=0;for(k=0;k<4;k++)out[col*4+row]+=a[k*4+row]*b[col*4+k];}
}
/* Shared opaque geometry for AO. The caller owns GL state and the shader;
 * the active server texture unit receives each cutout's skin. */
void RB_ACDrawCapturedScene(GLint alphaCut) {
    int i;
    qglClientActiveTextureARB(GL_TEXTURE0_ARB);
    qglEnableClientState(GL_VERTEX_ARRAY);qglEnableClientState(GL_TEXTURE_COORD_ARRAY);
    qglVertexPointer(3,GL_FLOAT,sizeof(vertices[0]),vertices[0].xyz);
    qglTexCoordPointer(2,GL_FLOAT,sizeof(vertices[0]),vertices[0].uv);
    qglEnableClientState(GL_NORMAL_ARRAY);
    acNormalPointer(GL_FLOAT,sizeof(vertices[0]),vertices[0].normal);
    for(i=0;i<numBatches;i++) {
        if(batches[i].polygonOffset){qglEnable(GL_POLYGON_OFFSET_FILL);qglPolygonOffset(r_offsetFactor->value,r_offsetUnits->value);}
        else qglDisable(GL_POLYGON_OFFSET_FILL);
        qglBindTexture(GL_TEXTURE_2D,batches[i].texture);
        acUniform1f(alphaCut,batches[i].alpha);
        qglDrawArrays(GL_TRIANGLES,batches[i].first,batches[i].count);
    }
}
static void AC_Matrix(GLuint p,const char *name,const float *m) {acUniformMatrix4fv(acGetUniformLocation(p,name),1,GL_FALSE,m);}
static int QDECL AC_SortCaster(const void *a,const void *b) {
    float d=((const acShadowCaster_t*)a)->distance-((const acShadowCaster_t*)b)->distance;return d<0?-1:d>0?1:0;
}
/* Fit a light camera around the animated silhouette. Nearby local lights use
 * perspective; distant sun/moon samples use an orthographic map. */
static qboolean AC_LightMatrix(const acShadowCaster_t *c,float *matrix,vec3_t lo,vec3_t hi,float *opacity,float *blur) {
    vec3_t center,positions[8],intensities[8],forward,right,up,eye,delta,corner;
    float view[16]={0},proj[16]={0},radius,distance,best=0,nearZ,farZ,extent;
    int i,j,n,light=-1;trace_t trace;
    for(i=0;i<3;i++)center[i]=(c->mins[i]+c->maxs[i])*0.5f;
    VectorSubtract(c->maxs,c->mins,delta);radius=AC_Clamp(VectorLength(delta)*0.5f,4.0f,160.0f);
    n=R_GatherLightSources(center,positions,intensities,8);
    if(debug->integer>1 && backEnd.refdef.time%1000<20)ri.Printf(PRINT_ALL,"AC_LIGHT owner=%d center=%.1f %.1f %.1f radius=%.1f n=%d sun=%d\n",c->owner,center[0],center[1],center[2],radius,n,s_sun.exists);
    for(i=0;i<n;i++) {
        float strength=0.2126f*intensities[i][0]+0.7152f*intensities[i][1]+0.0722f*intensities[i][2];
        if(strength<=best)continue;
        ri.CM_BoxTrace(&trace,center,positions[i],vec3_origin,vec3_origin,0,CONTENTS_SOLID,0);
        if(debug->integer>1 && backEnd.refdef.time%1000<20)ri.Printf(PRINT_ALL,"AC_LIGHT sample=%d strength=%.3f solid=%d fraction=%.3f flags=%d\n",i,strength,trace.startsolid,trace.fraction,trace.surfaceFlags);
        if(trace.startsolid || (trace.fraction<0.98f && !(trace.surfaceFlags&SURF_SKY)))continue;
        best=strength;light=i;
    }
    // Moving lights participate too, but short flashes don't erase steady light.
    for(i=0;i<backEnd.refdef.num_dlights;i++) {
        dlight_t *l=&backEnd.refdef.dlights[i];float strength,d;
        VectorSubtract(l->origin,center,delta);d=VectorLength(delta);
        strength=(1.0f-d/fmaxf(l->radius,1.0f))*(l->color[0]+l->color[1]+l->color[2])/3.0f;
        if(strength<=best*1.25f || strength<=0.08f)continue;
        ri.CM_BoxTrace(&trace,center,l->origin,vec3_origin,vec3_origin,0,CONTENTS_SOLID,0);
        if(trace.startsolid||trace.fraction<0.98f)continue;
        VectorCopy(l->origin,eye);light=-2;best=strength;
    }
    // BSP leaf light lists can omit sunlight (notably the original AA maps).
    if(s_sun.exists && n<8) {
        float strength=(s_sun.color[0]+s_sun.color[1]+s_sun.color[2])/1530.0f;
        VectorMA(center,16384,s_sun.direction,positions[n]);
        ri.CM_BoxTrace(&trace,center,positions[n],vec3_origin,vec3_origin,0,CONTENTS_SOLID,0);
        if(!trace.startsolid && (trace.surfaceFlags&SURF_SKY) && strength>best) {light=n;best=strength;}
    }
    // Diffuse-only areas still need contact grounding. An overhead, low-opacity
    // silhouette approximates ambient occlusion; it does not invent a sun angle.
    if(light==-1) {
        if(R_ACAOActive())return qfalse; // GTAO supplies diffuse contact grounding.
        VectorCopy(center,eye);eye[2]+=1024;best=0.32f;light=-3;
    }
    if(light>=0)VectorCopy(positions[light],eye);
    VectorSubtract(center,eye,forward);distance=VectorNormalize(forward);
    if(distance<radius+2)return qfalse;
    PerpendicularVector(right,forward);CrossProduct(right,forward,up);
    if(distance>4096) {distance=512+radius;VectorMA(center,-distance,forward,eye);}
    for(i=0;i<3;i++){view[i*4]=right[i];view[i*4+1]=up[i];view[i*4+2]=-forward[i];}
    view[12]=-DotProduct(right,eye);view[13]=-DotProduct(up,eye);view[14]=DotProduct(forward,eye);view[15]=1;
    nearZ=fmaxf(1,distance-radius-4);farZ=distance+radius+256;
    extent=radius+3;
    if(light==-3 || (light>=0 && Distance(positions[light],center)>4096)) {
        proj[0]=proj[5]=1.0f/extent;proj[10]=-2.0f/(farZ-nearZ);proj[14]=-(farZ+nearZ)/(farZ-nearZ);proj[15]=1;
    } else {
        float tangent=extent/nearZ;proj[0]=proj[5]=1.0f/tangent;proj[10]=-(farZ+nearZ)/(farZ-nearZ);proj[11]=-1;proj[14]=-2*farZ*nearZ/(farZ-nearZ);
    }
    AC_Multiply(proj,view,matrix);
    // Bounds encompass the light and receiver volume (up to 256 units behind).
    ClearBounds(lo,hi);AddPointToBounds(eye,lo,hi);
    for(j=0;j<8;j++){for(i=0;i<3;i++)corner[i]=(j&(1<<i))?c->maxs[i]:c->mins[i];AddPointToBounds(corner,lo,hi);VectorMA(corner,256,forward,corner);AddPointToBounds(corner,lo,hi);}
    for(i=0;i<3;i++){lo[i]-=extent;hi[i]+=extent;}
    *opacity=(light==-3?0.24f:AC_Clamp(0.18f+best*0.4f,0.18f,0.42f))*(1.0f-AC_Clamp((sqrtf(c->distance)-900)/500,0.0f,1.0f));
    *blur=(light==-3?1.5f:0.6f)/(2.0f*extent);
    return *opacity>0;
}
static void AC_DrawBatch(const acShadowBatch_t *b,qboolean depth) {
    if(depth) {qglBindTexture(GL_TEXTURE_2D,b->texture);acUniform1f(acGetUniformLocation(depthProgram,"alphaCut"),b->alpha);}
    qglDrawArrays(GL_TRIANGLES,b->first,b->count);
}
void RB_ACShadowFinish(void) {
    GLint oldFbo,oldProgram,oldDraw,oldRead;int i,j,pass,drawn=0,start=0;float camera[16];
    if(finished)return;finished=qtrue;
    if(collecting&&!overflow&&numVertices&&R_ACAOActive())RB_ACAOApply();
    if(!collecting||overflow||!numCasters||!enabled->integer) {
        if(debug->integer>2 && backEnd.refdef.time%1000<50)
            ri.Printf(PRINT_ALL,"AC_SHADOW_SKIPPED enabled=%d gl_error=%d\n",enabled->integer,qglGetError());
        return;
    }
    collecting=qfalse;
    if(debug->integer>2){GLenum err=qglGetError();qglFinish();start=ri.Milliseconds();if(err && backEnd.refdef.time%1000<50)ri.Printf(PRINT_ALL,"AC_SHADOW_PRIOR_GL_ERROR %d\n",err);}
    for(i=0;i<numCasters;i++){vec3_t center;VectorAdd(casters[i].mins,casters[i].maxs,center);VectorScale(center,0.5f,center);casters[i].distance=DistanceSquared(center,backEnd.viewParms.ori.origin);}
    qsort(casters,numCasters,sizeof(casters[0]),AC_SortCaster);
    qglGetIntegerv(GL_FRAMEBUFFER_BINDING,&oldFbo);qglGetIntegerv(GL_CURRENT_PROGRAM,&oldProgram);
    qglGetIntegerv(GL_DRAW_BUFFER,&oldDraw);qglGetIntegerv(GL_READ_BUFFER,&oldRead);
    acPushAttrib(GL_ALL_ATTRIB_BITS);acPushClientAttrib(GL_CLIENT_ALL_ATTRIB_BITS);
    qglActiveTextureARB(GL_TEXTURE1_ARB);qglDisable(GL_TEXTURE_2D);
    qglActiveTextureARB(GL_TEXTURE0_ARB);qglClientActiveTextureARB(GL_TEXTURE0_ARB);
    qglDisable(GL_FOG);qglDisable(GL_LIGHTING);qglDisable(GL_ALPHA_TEST);qglDisable(GL_STENCIL_TEST);
    qglDisable(GL_CLIP_PLANE0);qglDisable(GL_CULL_FACE);qglEnable(GL_DEPTH_TEST);
    qglDisableClientState(GL_COLOR_ARRAY);qglDisableClientState(GL_NORMAL_ARRAY);
    qglEnableClientState(GL_VERTEX_ARRAY);qglEnableClientState(GL_TEXTURE_COORD_ARRAY);
    qglVertexPointer(3,GL_FLOAT,sizeof(vertices[0]),vertices[0].xyz);qglTexCoordPointer(2,GL_FLOAT,sizeof(vertices[0]),vertices[0].uv);
    AC_Multiply(backEnd.viewParms.projectionMatrix,backEnd.viewParms.world.modelMatrix,camera);
    for(i=0;i<numCasters&&drawn<64;i++) {
        float light[16],opacity,blur;vec3_t lo,hi;acShadowCaster_t *c=&casters[i];
        if(c->distance>1400*1400)break;
        if(!AC_LightMatrix(c,light,lo,hi,&opacity,&blur))continue;
        acBindFramebuffer(GL_FRAMEBUFFER,framebuffer);qglDrawBuffer(GL_NONE);acReadBuffer(GL_NONE);
        qglViewport(0,0,AC_MAP_SIZE,AC_MAP_SIZE);qglScissor(0,0,AC_MAP_SIZE,AC_MAP_SIZE);
        qglColorMask(GL_FALSE,GL_FALSE,GL_FALSE,GL_FALSE);qglDepthMask(GL_TRUE);qglDepthFunc(GL_LESS);qglDepthRange(0,1);
        qglDisable(GL_BLEND);qglDisable(GL_POLYGON_OFFSET_FILL);
        acUseProgram(depthProgram);AC_Matrix(depthProgram,"mvp",light);acUniform1i(acGetUniformLocation(depthProgram,"skin"),0);
        for(pass=0;pass<2;pass++) {
            acFramebufferTexture2D(GL_FRAMEBUFFER,GL_DEPTH_ATTACHMENT,GL_TEXTURE_2D,maps[pass],0);qglClearDepth(1);qglClear(GL_DEPTH_BUFFER_BIT);
            for(j=0;j<numBatches;j++) {
                acShadowBatch_t *b=&batches[j];
                if((pass==0)!=(b->owner==c->owner))continue;
                if(!AC_BoundsOverlap(b->mins,b->maxs,lo,hi))continue;
                AC_DrawBatch(b,qtrue);
            }

        }
        acBindFramebuffer(GL_FRAMEBUFFER,oldFbo);
        // GL1 uses the window framebuffer; restore its buffer before compositing.
        qglDrawBuffer(oldDraw);acReadBuffer(oldRead);
        qglViewport(backEnd.viewParms.viewportX,backEnd.viewParms.viewportY,backEnd.viewParms.viewportWidth,backEnd.viewParms.viewportHeight);
        qglScissor(backEnd.viewParms.viewportX,backEnd.viewParms.viewportY,backEnd.viewParms.viewportWidth,backEnd.viewParms.viewportHeight);
        qglColorMask(GL_TRUE,GL_TRUE,GL_TRUE,GL_TRUE);qglDepthMask(GL_FALSE);qglDepthFunc(GL_LEQUAL);
        qglEnable(GL_POLYGON_OFFSET_FILL);qglPolygonOffset(-1,-1);
        qglEnable(GL_BLEND);qglBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);
        acUseProgram(shadeProgram);AC_Matrix(shadeProgram,"mvp",camera);AC_Matrix(shadeProgram,"lightMatrix",light);
        acUniform1i(acGetUniformLocation(shadeProgram,"silhouette"),0);acUniform1i(acGetUniformLocation(shadeProgram,"receiver"),1);
        acUniform1f(acGetUniformLocation(shadeProgram,"opacity"),opacity);
        acUniform1f(acGetUniformLocation(shadeProgram,"blurStep"),blur);
        acUniform1f(acGetUniformLocation(shadeProgram,"fogStart"),backEnd.viewParms.farplane_bias);
        acUniform1f(acGetUniformLocation(shadeProgram,"fogEnd"),r_farplane_nofog->integer?0:backEnd.viewParms.farplane_distance);
        qglBindTexture(GL_TEXTURE_2D,maps[0]);qglActiveTextureARB(GL_TEXTURE1_ARB);qglBindTexture(GL_TEXTURE_2D,maps[1]);qglActiveTextureARB(GL_TEXTURE0_ARB);
        for(j=0;j<numBatches;j++) {
            acShadowBatch_t *b=&batches[j];if(b->owner==c->owner||!AC_BoundsOverlap(b->mins,b->maxs,lo,hi))continue;
            AC_DrawBatch(b,qfalse);
        }
        drawn++;
    }
    acBindFramebuffer(GL_FRAMEBUFFER,oldFbo);acUseProgram(oldProgram);acPopClientAttrib();acPopAttrib();
    if(debug->integer>2){qglFinish();if(backEnd.refdef.time%1000<50)ri.Printf(PRINT_ALL,"AC_SHADOW_COST ms=%d gl_error=%d\n",ri.Milliseconds()-start,qglGetError());}
    if(debug->integer && backEnd.refdef.time%1000<50)ri.Printf(PRINT_ALL,"AC_SHADOW casters=%d drawn=%d vertices=%d batches=%d\n",numCasters,drawn,numVertices,numBatches);
}
