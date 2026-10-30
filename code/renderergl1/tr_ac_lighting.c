/* Allied Campaign lighting extensions. GPL-2.0-or-later.
 * Reuses the map's baked grid; does not rebake or brighten world lightmaps.
 * All state is renderer-owned. No gameplay/savegame or refEntity ABI changes.
 */
#include "tr_local.h"
#include "SDL.h"

cvar_t *r_acModelLighting, *r_acDynamicLighting, *r_acSoftParticles;
static cvar_t *debugLighting;
static int probeBatches, particleBatches, lightTraces, blockedTraces;
static int lastReport;
static const trRefdef_t *brushRefdef;
static int brushFrame=-1, brushScene, brushTime, brushEntityCount, numBrushes;
static const refEntity_t *brushes[1024];
static vec3_t brushBounds[1024][2];
typedef struct {
    unsigned epoch;
    vec3_t light, receiver;
    qboolean visible;
} acLightTrace_t;
static acLightTrace_t visibilityCache[32768];
static unsigned visibilityEpoch;
static void CollectBrushes(const trRefdef_t *refdef) {
    int i,j,k,corner;
    if(brushRefdef==refdef && brushFrame==tr.frameCount && brushScene==tr.sceneCount && brushTime==refdef->time
        && brushEntityCount==refdef->num_entities)return;
    brushRefdef=refdef;brushFrame=tr.frameCount;brushScene=tr.sceneCount;
    brushTime=refdef->time;brushEntityCount=refdef->num_entities;numBrushes=0;
    if(++visibilityEpoch==0){memset(visibilityCache,0,sizeof(visibilityCache));visibilityEpoch=1;}
    for(i=0;i<refdef->num_entities && numBrushes<ARRAY_LEN(brushes);i++){
        const refEntity_t *e=&refdef->entities[i].e;
        if(e->hModel>0 && e->hModel<tr.numModels && tr.models[e->hModel].type==MOD_BRUSH){
            bmodel_t *model=tr.models[e->hModel].d.bmodel;
            ClearBounds(brushBounds[numBrushes][0],brushBounds[numBrushes][1]);
            for(corner=0;corner<8;corner++){
                vec3_t p;VectorCopy(e->origin,p);
                for(j=0;j<3;j++)for(k=0;k<3;k++)p[k]+=model->bounds[(corner>>j)&1][j]*e->axis[j][k];
                AddPointToBounds(p,brushBounds[numBrushes][0],brushBounds[numBrushes][1]);
            }
            brushes[numBrushes++]=e;
        }
    }
}

static float Clamp(float x, float a, float b) { return Q_max(a,Q_min(b,x)); }

qboolean R_ACDynamicLightingActive(const trRefdef_t *refdef)
{
    return r_acDynamicLighting && r_acDynamicLighting->integer && tr.world
        && !(refdef->rdflags & (RDF_NOWORLDMODEL | RDF_FULLBRIGHT));
}

/* World and currently submitted moving brushes. Transform the segment into
 * inline-model space so doors/platforms use their actual current transform.
 * Only trim the receiver end by 0.125 units: a large bias leaks thin walls. */
qboolean R_ACLightVisible(const vec3_t light, const vec3_t receiver, const trRefdef_t *refdef)
{
    trace_t trace;
    vec3_t delta,end;
    float length;
    int i,j;
    unsigned hash=2166136261u,bits;
    acLightTrace_t *cached;
    if (!R_ACDynamicLightingActive(refdef)) return qtrue;
    CollectBrushes(refdef);
    /* Reuse exact duplicate vertices within one scene, never quantized cells
     * or previous frames: thin walls and moving doors retain full precision. */
    for(i=0;i<3;i++){
        memcpy(&bits,&light[i],sizeof(bits));hash=(hash^bits)*16777619u;
        memcpy(&bits,&receiver[i],sizeof(bits));hash=(hash^bits)*16777619u;
    }
    hash^=hash>>16;
    cached=&visibilityCache[hash&(ARRAY_LEN(visibilityCache)-1)];
    if(cached->epoch==visibilityEpoch && !memcmp(cached->light,light,sizeof(vec3_t))
        && !memcmp(cached->receiver,receiver,sizeof(vec3_t)))return cached->visible;
    cached->epoch=visibilityEpoch;VectorCopy(light,cached->light);VectorCopy(receiver,cached->receiver);cached->visible=qtrue;
    VectorSubtract(receiver,light,delta); length=VectorLength(delta);
    if(length<0.25f)return qtrue;
    VectorMA(light,1.0f-0.125f/length,delta,end);
    lightTraces++;
    ri.CM_BoxTrace(&trace,light,end,vec3_origin,vec3_origin,0,CONTENTS_SOLID,0);
    if(debugLighting && debugLighting->integer>1 && lightTraces<8)
        ri.Printf(PRINT_ALL,"AC_LIGHT_TRACE %.2f %.2f %.2f -> %.2f %.2f %.2f fraction=%.6f solid=%d\n",light[0],light[1],light[2],receiver[0],receiver[1],receiver[2],trace.fraction,trace.startsolid);
    if(trace.startsolid || trace.allsolid || (trace.fraction<1.0f && DotProduct(end,trace.plane.normal)-trace.plane.dist < -0.25f)){blockedTraces++;cached->visible=qfalse;return qfalse;}
    for(i=0;i<numBrushes;i++){
        const refEntity_t *e=brushes[i];
        model_t *model;
        vec3_t a,b,da,db;
        int handle;
        /* Reject distant brushes in world space before matrix transforms. */
        for(j=0;j<3;j++)if(Q_min(light[j],end[j])>brushBounds[i][1][j]
            || Q_max(light[j],end[j])<brushBounds[i][0][j])break;
        if(j!=3)continue;
        if(e->hModel<=0 || e->hModel>=tr.numModels)continue;
        model=&tr.models[e->hModel];
        if(model->type!=MOD_BRUSH || model->name[0]!='*')continue;
        handle=atoi(model->name+1);if(handle<=0)continue;
        VectorSubtract(light,e->origin,da);VectorSubtract(end,e->origin,db);
        for(j=0;j<3;j++){a[j]=DotProduct(da,e->axis[j]);b[j]=DotProduct(db,e->axis[j]);}
        /* Cheap segment-AABB rejection before the inline collision trace. */
        for(j=0;j<3;j++)if(Q_min(a[j],b[j])>model->d.bmodel->bounds[1][j]
            || Q_max(a[j],b[j])<model->d.bmodel->bounds[0][j])break;
        if(j!=3)continue;
        ri.CM_BoxTrace(&trace,a,b,vec3_origin,vec3_origin,handle,CONTENTS_SOLID,0);
        if(trace.startsolid || trace.allsolid || (trace.fraction<1.0f && DotProduct(b,trace.plane.normal)-trace.plane.dist < -0.25f)){blockedTraces++;cached->visible=qfalse;return qfalse;}
    }
    return qtrue;
}

void R_ACLightWorldPoint(const vec3_t local, const orientationr_t *ori, vec3_t world)
{
    int j;
    VectorCopy(ori->origin,world);
    for(j=0;j<3;j++)VectorMA(world,local[j],ori->axis[j],world);
}

/* Six local, visibility-clipped samples of the existing trilinear lightgrid.
 * Reconstruct its low-frequency colour gradient on the animated normals.
 * Centre subtraction preserves uniform lighting and avoids adding a second
 * copy of baked/direct light. Attached weapons use their parent's sample. */
void RB_ACModelLighting(unsigned char *colors)
{
    vec3_t centre,base,probe[6];
    trRefEntity_t *e=backEnd.currentEntity,*root;
    float radius,scale;
    int i,j,k,guard=0;
    if(!r_acModelLighting || !r_acModelLighting->integer || !tr.world || !tr.world->lightGridData
        || !e || e==&tr.worldEntity || !e->e.tiki || backEnd.in2D
        || (e->e.renderfx & (RF_FULLBRIGHT | RF_INVISIBLE))
        || (backEnd.refdef.rdflags&(RDF_NOWORLDMODEL|RDF_HUD|RDF_FULLBRIGHT)) || r_light_nolight->integer)return;
    root=e;
    while(root->e.parentEntity>=0 && root->e.parentEntity<backEnd.refdef.num_entities
        && root->e.parentEntity!=ENTITYNUM_NONE && guard++<16){
        trRefEntity_t *p=&backEnd.refdef.entities[root->e.parentEntity];if(p==root)break;root=p;
    }
    VectorCopy(root->e.lightingOrigin,centre);
    radius=Clamp(root->e.radius*0.65f,16.0f,48.0f);
    R_GetLightingGridValue(centre,base);
    for(i=0;i<6;i++){
        trace_t trace;vec3_t p;
        VectorCopy(centre,p);p[i/2]+= (i&1)?-radius:radius;
        ri.CM_BoxTrace(&trace,centre,p,vec3_origin,vec3_origin,0,CONTENTS_SOLID,0);
        if(trace.startsolid || trace.allsolid){VectorCopy(base,probe[i]);continue;}
        if(trace.fraction<1.0f){
            VectorSubtract(p,centre,p);VectorMA(centre,Q_max(0,trace.fraction-0.5f/radius),p,p);
        }
        R_GetLightingGridValue(p,probe[i]);
    }
    scale=0.55f*tr.overbrightMult*r_entlight_scale->value;
    for(i=0;i<tess.numVertexes;i++){
        vec3_t n;float denom=0;
        VectorClear(n);
        for(j=0;j<3;j++)VectorMA(n,tess.normal[i][j],e->e.axis[j],n);
        for(j=0;j<3;j++)denom+=n[j]*n[j];
        if(denom<0.01f)continue;
        for(k=0;k<3;k++){
            float directional=0;
            for(j=0;j<3;j++)directional+=n[j]*n[j]*probe[2*j+(n[j]<0)][k]/denom;
            /* Keep the original scene exposure, including dark SH maps. */
            float limit=Q_max(4.0f,colors[4*i+k]*0.30f);
            float change=Clamp((directional-base[k])*scale,-limit,limit);
            colors[4*i+k]=(byte)Clamp(colors[4*i+k]+change,0,255);
        }
    }
    probeBatches++;
}

/* Preserve MOH's model-light response and influence bounds. A lightmap's
 * 375*(1-d/r)^2 curve is NOT interchangeable with the model inverse-square
 * response: it extinguishes most small muzzle lights. Only visibility is new.
 * Test each actual vertex so a partly exposed model can still receive light. */
void RB_ACDynamicModelLighting(unsigned char *colors, qboolean grid)
{
    int i,j,k;
    float modelScale=1;
    vec3_t centre;
    qboolean isStatic=backEnd.currentStaticModel!=NULL;
    if(!R_ACDynamicLightingActive(&backEnd.refdef) || backEnd.in2D || !backEnd.refdef.num_dlights)return;
    if(isStatic){
        modelScale=backEnd.currentStaticModel->tiki->load_scale*backEnd.currentStaticModel->scale;
        VectorCopy(backEnd.currentStaticModel->origin,centre);
    }
    else if(!backEnd.currentEntity || backEnd.currentEntity==&tr.worldEntity || !backEnd.currentEntity->e.tiki
        || (backEnd.currentEntity->e.renderfx & (RF_FULLBRIGHT | RF_INVISIBLE)))return;
    else VectorCopy(grid?backEnd.currentSphere->traceOrigin:backEnd.currentSphere->worldOrigin,centre);
    for(i=0;i<tess.numVertexes;i++){
        vec3_t local,world,normal={0,0,0},add={0,0,0};
        VectorScale(tess.xyz[i],modelScale,local);R_ACLightWorldPoint(local,&backEnd.ori,world);
        for(k=0;k<3;k++)VectorMA(normal,tess.normal[i][k],backEnd.ori.axis[k],normal);
        VectorNormalize(normal);
        for(j=0;j<backEnd.refdef.num_dlights;j++){
            dlight_t *dl=&backEnd.refdef.dlights[j];vec3_t dir,delta;float distance,lambert,f,centreDistance;
            if(dl->radius<=0)continue;
            VectorSubtract(dl->origin,centre,delta);centreDistance=VectorLength(delta);
            if(centreDistance>dl->radius+(grid?0:(isStatic?dl->radius:backEnd.currentSphere->radius)))continue;
            VectorSubtract(dl->origin,world,dir);distance=VectorNormalize(dir);
            lambert=grid?1.0f:Q_max(0,DotProduct(normal,dir));if(lambert<=0)continue;
            if(!R_ACLightVisible(dl->origin,world,&backEnd.refdef))continue;
            if(grid)f=7500.0f*dl->radius/Q_max(centreDistance*centreDistance,64.0f);
            else if(isStatic)f=7500.0f*dl->radius/Q_max(distance*distance,64.0f);
            else f=r_entlight_scale->value*7500.0f*dl->radius/(Q_max(centreDistance,8.0f)*Q_max(distance,8.0f));
            VectorMA(add,f*lambert*tr.overbrightMult,dl->color,add);
        }
        for(k=0;k<3;k++)colors[4*i+k]=(byte)Clamp(colors[4*i+k]+add[k],0,255);
    }
}

/* Restrict lighting/fade to diffuse clouds; never dim fire, sparks, muzzle
 * flashes, tracers, glass, HUD sprites, solid debris or permanent blood marks. */
static qboolean CloudStage(const shaderStage_t *stage)
{
    const char *name=tess.shader->name;
    unsigned blend=stage->stateBits&(GLS_SRCBLEND_BITS|GLS_DSTBLEND_BITS);
    return !backEnd.in2D && tr.world && !(backEnd.refdef.rdflags&(RDF_NOWORLDMODEL|RDF_HUD))
        && tess.shader->sort>SS_SEE_THROUGH && !(stage->stateBits&GLS_DEPTHMASK_TRUE)
        && blend==(GLS_SRCBLEND_SRC_ALPHA|GLS_DSTBLEND_ONE_MINUS_SRC_ALPHA)
        && (!stage->bundle[1].image[0] || stage->multitextureEnv==GL_MODULATE || stage->multitextureEnv==GL_ADD)
        && (Q_stristr(name,"vsssource") || strstr(name,"puff") || strstr(name,"smoke") || strstr(name,"dust") || strstr(name,"steam")
            || strstr(name,"blood_mist") || strstr(name,"bloodpuff"));
}

void RB_ACParticleColors(const shaderStage_t *stage)
{
    int i,j,l;
    if(!r_acSoftParticles || !r_acSoftParticles->integer || !CloudStage(stage))return;
    /* A sprite's four corners share its centre: moving the camera cannot
     * rotate the lighting samples through a wall or change its colour. */
    for(i=0;i+3<tess.numVertexes;i+=4){
        vec3_t local={0,0,0},point,light;
        if(tess.acParticlePrelit[i] || (backEnd.currentEntity && (backEnd.currentEntity->e.renderfx & RF_AC_PARTICLE_LIT))
            || stage->rgbGen==CGEN_LIGHTING_GRID || stage->rgbGen==CGEN_LIGHTING_SPHERICAL)continue;
        for(j=0;j<4;j++)VectorMA(local,0.25f,tess.xyz[i+j],local);
        R_ACLightWorldPoint(local,&backEnd.ori,point);
        R_GetLightingGridValue(point,light);
        for(j=0;j<3;j++)light[j]=Clamp(light[j]*tr.overbrightMult,24,255);
        for(l=0;l<backEnd.refdef.num_dlights;l++){
            dlight_t *dl=&backEnd.refdef.dlights[l];vec3_t d;float f;
            if(dl->radius<=0)continue;
            VectorSubtract(point,dl->origin,d);f=1.0f-VectorLength(d)/dl->radius;
            if(f<=0 || !R_ACLightVisible(dl->origin,point,&backEnd.refdef))continue;
            VectorMA(light,375.0f*f*f*tr.overbrightMult,dl->color,light);
        }
        for(j=0;j<4;j++)for(l=0;l<3;l++)
            tess.svars.colors[i+j][l]=(byte)Clamp(tess.svars.colors[i+j][l]*Clamp(light[l]/255.0f,0,1.35f),0,255);
    }
    particleBatches++;
}

#define AC_GL(X) \
 X(GLboolean,IsEnabled,(GLenum cap)) \
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
 X(void,DeleteProgram,(GLuint p)) \
 X(void,UseProgram,(GLuint p)) \
 X(GLint,GetUniformLocation,(GLuint p,const char *s)) \
 X(void,Uniform1i,(GLint u,GLint v)) \
 X(void,Uniform2f,(GLint u,GLfloat x,GLfloat y)) \
 X(void,Uniform4f,(GLint u,GLfloat x,GLfloat y,GLfloat z,GLfloat w))
#define DECL(ret,name,args) static ret (APIENTRYP fx##name) args;
AC_GL(DECL)
#undef DECL
static GLuint particleProgram,particleDepth;
static int depthWidth,depthHeight;
static qboolean captured;
static GLint oldProgram,oldTexture;
static int oldUnit;
static const char *particleVertex =
 "#version 120\n"
 "varying vec2 uv,uv2;varying vec4 color;varying float eyeDepth;\n"
 "void main(){vec4 p=gl_ModelViewMatrix*gl_Vertex;eyeDepth=-p.z;gl_Position=gl_ProjectionMatrix*p;uv=gl_MultiTexCoord0.xy;uv2=gl_MultiTexCoord1.xy;color=gl_Color;}\n";
static const char *particleFragment =
 "#version 120\n"
 "uniform sampler2D skin,skin2,sceneDepth;uniform int textureMode;uniform vec4 viewport;uniform vec2 projection;uniform int fogEnabled;\n"
 "varying vec2 uv,uv2;varying vec4 color;varying float eyeDepth;\n"
 "void main(){vec4 c=texture2D(skin,uv)*color; if(textureMode!=0){vec4 b=texture2D(skin2,uv2); if(textureMode==2){c.rgb+=b.rgb;c.a*=b.a;}else c*=b;}\n"
 "float d=texture2D(sceneDepth,(gl_FragCoord.xy-viewport.xy)/viewport.zw).r;\n"
 "float z=projection.y/(d*2.0-1.0+projection.x);\n"
 "float fade=d>=0.9999999?1.0:smoothstep(0.0,6.0,max(0.0,z-eyeDepth));c.a*=fade;\n"
 "if(fogEnabled!=0){float f=clamp((gl_Fog.end-eyeDepth)*gl_Fog.scale,0.0,1.0);c.rgb=mix(gl_Fog.color.rgb,c.rgb,f);}\n"
 "gl_FragColor=c;}\n";

void R_ACLightingShutdown(void)
{
    if(particleProgram)fxDeleteProgram(particleProgram);
    if(particleDepth)qglDeleteTextures(1,&particleDepth);
    particleProgram=particleDepth=0;depthWidth=depthHeight=0;captured=qfalse;brushFrame=-1;brushRefdef=NULL;
}
void R_ACLightingInit(void)
{
    qboolean loaded=qtrue;
    GLuint shaders[2];int i;GLint ok;
    const char *sources[2]={particleVertex,particleFragment};
    r_acModelLighting=ri.Cvar_Get("r_acModelLighting","1",CVAR_ARCHIVE);
    r_acDynamicLighting=ri.Cvar_Get("r_acDynamicLighting","1",CVAR_ARCHIVE);
    r_acSoftParticles=ri.Cvar_Get("r_acSoftParticles","1",CVAR_ARCHIVE);
    debugLighting=ri.Cvar_Get("r_acLightingDebug","0",0);
#define LOAD(ret,name,args) fx##name=(ret(APIENTRYP)args)SDL_GL_GetProcAddress("gl" #name);if(!fx##name)loaded=qfalse;
    AC_GL(LOAD)
#undef LOAD
    if(!loaded || !qglActiveTextureARB || glConfig.numTextureUnits<3)return;
    particleProgram=fxCreateProgram();
    for(i=0;i<2;i++){
        char log[2048];
        shaders[i]=fxCreateShader(i?GL_FRAGMENT_SHADER:GL_VERTEX_SHADER);
        fxShaderSource(shaders[i],1,&sources[i],NULL);fxCompileShader(shaders[i]);
        fxGetShaderiv(shaders[i],GL_COMPILE_STATUS,&ok);
        if(!ok){fxGetShaderInfoLog(shaders[i],sizeof(log),NULL,log);ri.Printf(PRINT_WARNING,"AC lighting shader: %s\n",log);}
        fxAttachShader(particleProgram,shaders[i]);fxDeleteShader(shaders[i]);
    }
    fxLinkProgram(particleProgram);fxGetProgramiv(particleProgram,GL_LINK_STATUS,&ok);
    if(!ok){R_ACLightingShutdown();return;}
    qglGenTextures(1,&particleDepth);
    ri.Printf(PRINT_ALL,"AC lighting ready: local probes, occluded dynamic lights, lit soft clouds.\n");
}
void RB_ACLightingBegin(void)
{
    captured=qfalse;
    if(debugLighting && debugLighting->integer && backEnd.refdef.time-lastReport>1000){
        ri.Printf(PRINT_ALL,"AC_LIGHT probes=%d clouds=%d traces=%d blocked=%d\n",probeBatches,particleBatches,lightTraces,blockedTraces);
        if(debugLighting->integer>1){
            int i;for(i=0;i<backEnd.refdef.num_dlights;i++){
                const dlight_t *d=&backEnd.refdef.dlights[i];
                ri.Printf(PRINT_ALL,"AC_LIGHT_SOURCE %.2f %.2f %.2f radius=%.2f rgb=%.2f %.2f %.2f\n",d->origin[0],d->origin[1],d->origin[2],d->radius,d->color[0],d->color[1],d->color[2]);
            }
        }
        probeBatches=particleBatches=lightTraces=blockedTraces=0;lastReport=backEnd.refdef.time;
    }
}
void RB_ACParticleDepth(void)
{
    GLint binding;
    int w=backEnd.viewParms.viewportWidth,h=backEnd.viewParms.viewportHeight;
    if(captured || !particleProgram || !r_acSoftParticles->integer || !tr.world
        || backEnd.viewParms.isPortal || backEnd.viewParms.isMirror
        || (backEnd.refdef.rdflags&(RDF_NOWORLDMODEL|RDF_HUD)) || w<=0 || h<=0)return;
    GL_SelectTexture(0);qglGetIntegerv(GL_TEXTURE_BINDING_2D,&binding);
    qglBindTexture(GL_TEXTURE_2D,particleDepth);
    if(w!=depthWidth || h!=depthHeight){
        qglTexImage2D(GL_TEXTURE_2D,0,GL_DEPTH_COMPONENT24,w,h,0,GL_DEPTH_COMPONENT,GL_UNSIGNED_INT,NULL);
        qglTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST);
        qglTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST);
        qglTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE);
        qglTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE);
        depthWidth=w;depthHeight=h;
    }
    qglCopyTexSubImage2D(GL_TEXTURE_2D,0,0,0,backEnd.viewParms.viewportX,backEnd.viewParms.viewportY,w,h);
    qglBindTexture(GL_TEXTURE_2D,binding);captured=qtrue;
}
qboolean RB_ACParticleBegin(const shaderStage_t *stage)
{
    if(!captured || !r_acSoftParticles->integer || !CloudStage(stage))return qfalse;
    qglGetIntegerv(GL_CURRENT_PROGRAM,&oldProgram);
    oldUnit=glState.currenttmu;qglActiveTextureARB(GL_TEXTURE2_ARB);qglGetIntegerv(GL_TEXTURE_BINDING_2D,&oldTexture);
    qglBindTexture(GL_TEXTURE_2D,particleDepth);qglActiveTextureARB(GL_TEXTURE0_ARB+oldUnit);
    fxUseProgram(particleProgram);
    fxUniform1i(fxGetUniformLocation(particleProgram,"skin"),0);
    fxUniform1i(fxGetUniformLocation(particleProgram,"sceneDepth"),2);
    fxUniform1i(fxGetUniformLocation(particleProgram,"skin2"),1);
    fxUniform1i(fxGetUniformLocation(particleProgram,"textureMode"),!stage->bundle[1].image[0]?0:(stage->multitextureEnv==GL_ADD?2:1));
    fxUniform1i(fxGetUniformLocation(particleProgram,"fogEnabled"),fxIsEnabled(GL_FOG));
    fxUniform4f(fxGetUniformLocation(particleProgram,"viewport"),backEnd.viewParms.viewportX,backEnd.viewParms.viewportY,depthWidth,depthHeight);
    fxUniform2f(fxGetUniformLocation(particleProgram,"projection"),backEnd.viewParms.projectionMatrix[10],backEnd.viewParms.projectionMatrix[14]);
    return qtrue;
}
void RB_ACParticleEnd(void)
{
    fxUseProgram(oldProgram);qglActiveTextureARB(GL_TEXTURE2_ARB);qglBindTexture(GL_TEXTURE_2D,oldTexture);qglActiveTextureARB(GL_TEXTURE0_ARB+oldUnit);
}
