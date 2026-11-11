#include <stdio.h>
#include <string.h>
#include "../../code/qcommon/ac_score.h"

static int check(acScoreStats_t stats,int expected)
{
    acScoreResult_t r;memset(&r,0,sizeof(r));r.stats=stats;AC_ScoreCalculate(&r);
    if(r.total!=expected){printf("expected %d, got %d\n",expected,r.total);return 1;}
    return 0;
}

int main(void)
{
    acScoreStats_t s;int fails=0;memset(&s,0,sizeof(s));
    fails+=check(s,0); // No shots means no accuracy bonus, never division by zero.
    s.kills=1;fails+=check(s,100);
    s.shots=1;s.hits=1;fails+=check(s,150);
    s.heads=1;fails+=check(s,225);
    s.shots=3;fails+=check(s,175); // Exact integer rounding at the final bonus.
    s.friendlyDamage=100;fails+=check(s,0); // Penalty is not reduced by accuracy.
    memset(&s,0,sizeof(s));s.kills=2;s.grenadeKills=2;s.grenadeBonus=200;fails+=check(s,400);
    s.kills=3;s.grenadeKills=3;s.grenadeBonus=600;fails+=check(s,900);
    s.kills=5;s.grenadeKills=5;s.grenadeBonus=800;fails+=check(s,1300); // Separate 2 + 3 groups.
    s.shots=1;s.hits=1;fails+=check(s,1950);
    s.friendlyDamage=25;fails+=check(s,1900);
    memset(&s,0,sizeof(s));s.kills=100000;s.heads=100000;s.grenadeBonus=100204600;
    s.shots=s.hits=1000000;fails+=check(s,172806900); // Widen multiplication before dividing.
    if(!fails)puts("12 score formula cases passed");return fails?1:0;
}
