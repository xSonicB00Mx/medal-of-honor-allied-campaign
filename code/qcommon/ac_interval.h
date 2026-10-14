#pragma once
// Sorted ray contacts. A closed thin/grazing interval must never borrow a later exit.
struct ACIntervalContact {float distance,facing;};
inline void ACSelectInterval(const ACIntervalContact *p,int count,int& entry,int& exit) {
    entry=exit=-1;
    for(int i=0;i<count;++i) {
        if(entry<0){if(p[i].facing<-.12f)entry=i;continue;}
        const float thickness=p[i].distance-p[entry].distance;
        if(p[i].facing>.12f) {
            if(thickness>.25f && thickness<80.f)exit=i;
            return;
        }
        if(thickness>=80.f)return;
    }
}
