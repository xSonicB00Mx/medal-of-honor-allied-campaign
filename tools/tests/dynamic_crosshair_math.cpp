#include "../../code/fgame/ac_crosshair.h"
#include <cstdio>
#include <cstdlib>
#include <random>
#include <cstdint>
static void require(bool ok) { if (!ok) { std::puts("FAIL"); std::exit(1); } }
static float legacy(float value, float amount, float falloff, float elapsed, float cap) {
    if (amount != 0) {
        if (elapsed <= cap) {
            if (value <= 0) { value -= elapsed*falloff; if (value > 0) value=0; }
            else { value -= elapsed*falloff; if (value < 0) value=0; }
        } else value=0;
    }
    return value;
}
int main() {
    int cases=0;
    for (float value : {-2.f, -.01f, 0.f, .01f, 3.f})
    for (float amount : {-.3f,0.f,.7f})
    for (float falloff : {-2.f,0.f,.6f})
    for (float time : {0.f,.1f,.6f,1.f,200.f,201.f}) {
        require(legacy(value,amount,falloff,time,.6f)==AC_SpreadBeforeShot(value,amount,falloff,time,.6f)); ++cases;
    }
    require(AC_EncodeSpread95(20,20,0)==0);
    require(AC_EncodeSpread95(0,0,4000)==1);
    require(AC_DecodeSpread95(0)==0);
    for (float sigma : {0.f,8.f,45.f,140.f,4000.f,10000.f}) {
        int code=AC_EncodeSpread95(sigma,sigma,4000);
        float slope=AC_DecodeSpread95((int16_t)code);
        require(fabsf(atanf(slope)-atanf(2.447746831f*sigma/4000))<.000013f);
    }
    float slope=AC_DecodeSpread95(AC_EncodeSpread95(45,45,4000));
    require(fabsf(AC_SpreadPixels(slope,3840,90)-2*AC_SpreadPixels(slope,1920,90))<.001f);
    require(AC_SpreadPixels(slope,3840,80)>AC_SpreadPixels(slope,3840,90));
    const float fy=2*atanf(tanf(80.f*3.141592654f/360)*2160/3840)*180/3.141592654f;
    require(fabsf(AC_SpreadPixels(slope,3840,80)-AC_SpreadPixels(slope,2160,fy))<.001f);
    std::mt19937 rng(431);std::normal_distribution<float> normal(0,1);
    int contained=0,elliptic=0;
    for(int i=0;i<200000;++i) {
        float x=normal(rng),y=normal(rng);
        if(x*x+y*y<=5.991464547f)++contained;
        if(x*x+.25f*y*y<=5.991464547f)++elliptic;
    }
    require(contained>189000 && contained<191000 && elliptic>contained);
    std::printf("PASS: %d legacy decay cases; signed transport; FOV/aspect/resolution; Gaussian coverage %.4f, anisotropic %.4f\n",cases,contained/200000.f,elliptic/200000.f);
}
