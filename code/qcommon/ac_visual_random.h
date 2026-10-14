#pragma once
#include <cmath>
// Private visual stream: never call the engine/gameplay RNG.
inline unsigned ACVisualRandom(unsigned& s){s^=s<<13;s^=s>>17;s^=s<<5;return s;}
inline unsigned ACVisualOrientation(unsigned seed,int branch,float& rotation,int& flipU,int& flipV) {
    unsigned initial=seed^(branch?0x85ebca6bu:0xc2b2ae35u),rng=initial?initial:1;
    rotation=(ACVisualRandom(rng)&0xffffff)*(360.f/16777216.f);
    flipU=ACVisualRandom(rng)&1;flipV=ACVisualRandom(rng)&1;return initial;
}
inline void ACVisualRotate(float x,float y,float angle,float& outX,float& outY) {
    float r=angle*(3.14159265358979323846f/180.f),c=std::cos(r),s=std::sin(r);
    outX=c*x+s*y;outY=-s*x+c*y;
}
inline void ACVisualUV(float x,float y,float radius,int flipU,int flipV,float *uv) {
    uv[0]=0.5f+x/(2*radius);uv[1]=0.5f+y/(2*radius);
    if(flipU)uv[0]=1-uv[0];if(flipV)uv[1]=1-uv[1];
}
