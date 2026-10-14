#include "../../code/qcommon/ac_visual_random.h"
#include <cstdio>
#include <cstdlib>
#include <initializer_list>
static void require(bool valid,const char *why){if(!valid){std::fprintf(stderr,"FAIL: %s\n",why);std::exit(1);}}
int main() {
    unsigned combinations[4]={},buckets[12]={};
    for(unsigned seed=0;seed<65536;++seed) {
        float a,b;int u,v,x,y;
        unsigned s=ACVisualOrientation(seed,0,a,u,v);require(s==ACVisualOrientation(seed,0,b,x,y) && a==b && u==x && v==y,"fixed seed reproducibility");
        require(a>=0 && a<360 && u>=0 && u<=1 && v>=0 && v<=1,"orientation range");
        ++combinations[u*2+v];++buckets[(int)(a/30)];
        ACVisualOrientation(seed,1,b,x,y);require(a!=b || u!=x || v!=y,"independent entry/exit subsequences");
    }
    for(unsigned n:combinations)require(n>15500 && n<17300,"all independent mirror combinations near 25 percent");
    for(unsigned n:buckets)require(n>4900 && n<6000,"uniform angular buckets");
    for(float angle:{0.f,90.f,180.f,270.f,359.99f})for(int u=0;u<2;++u)for(int v=0;v<2;++v) {
        float x,y,uv[2];ACVisualRotate(0,0,angle,x,y);ACVisualUV(x,y,3.5f,u,v,uv);require(uv[0]==.5f && uv[1]==.5f,"texture center remains fixed");
        ACVisualRotate(1,0,angle,x,y);require(std::fabs(x*x+y*y-1)<1e-5f,"rotation preserves size");
        ACVisualUV(x,y,1,u,v,uv);require(uv[0]>=0 && uv[0]<=1 && uv[1]>=0 && uv[1]<=1,"all mirrored edge coordinates in bounds");
    }
    std::puts("PASS: 65536 deterministic seeds, independent exit stream, all mirror states and five angles");
}
