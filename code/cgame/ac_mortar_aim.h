namespace {
int acMortarTime=-1000;vec3_t acMortarPoint,acMortarNormal;
void ACMortarQuad(const vec3_t a,const vec3_t b,const vec3_t c,const vec3_t d,byte alpha) {
    polyVert_t v[4]={};const float *points[]={a,b,c,d};
    for(int i=0;i<4;++i){VectorCopy(points[i],v[i].xyz);v[i].modulate[0]=255;v[i].modulate[1]=12;v[i].modulate[2]=8;v[i].modulate[3]=alpha;}
    cgi.R_AddPolyToScene(cgi.R_RegisterShader("ac/mortar_target"),4,v,0);
}
}
extern "C" void CG_ACMortarEvent(void) {
    if(cgi.Argc()!=7)return;
    for(int i=0;i<3;++i){acMortarPoint[i]=atof(cgi.Argv(1+i));acMortarNormal[i]=atof(cgi.Argv(4+i));
        if(!std::isfinite(acMortarPoint[i]) || !std::isfinite(acMortarNormal[i])){acMortarTime=-1000;return;}}
    if(VectorNormalize(acMortarNormal)<0.5f){acMortarTime=-1000;return;}
    acMortarTime=cg.time;
}
extern "C" void CG_ACMortarFrame(void) {
    if(cg.time<acMortarTime || cg.time-acMortarTime>150)return;
    vec3_t center,x,y;VectorMA(acMortarPoint,2,acMortarNormal,center);
    PerpendicularVector(x,acMortarNormal);CrossProduct(acMortarNormal,x,y);
    for(int i=0;i<32;++i) {
        vec3_t p[4];
        for(int j=0;j<4;++j){float angle=(i+(j==1 || j==2))*2*M_PI/32;float radius=j<2?30:25;
            VectorMA(center,cos(angle)*radius,x,p[j]);VectorMA(p[j],sin(angle)*radius,y,p[j]);}
        ACMortarQuad(p[0],p[1],p[2],p[3],220);
    }
    // A vertical luminous column remains visible over uneven ground.
    for(int axis=0;axis<2;++axis)for(int layer=0;layer<2;++layer) {
        vec3_t p[4];for(int j=0;j<4;++j){VectorCopy(center,p[j]);p[j][axis]+=(j==0||j==3?-1:1)*(layer?3:9);if(j>=2)p[j][2]+=120;}
        ACMortarQuad(p[0],p[1],p[2],p[3],layer?230:60);
    }
    cgi.R_AddLightToScene(center,100,1,0.02f,0.01f,0);
}
