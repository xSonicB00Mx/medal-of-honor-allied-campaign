#ifndef AC_SCORE_H
#define AC_SCORE_H

/* Version 1 rules. Scores are local records, not an online anti-cheat system. */
enum { AC_SCORE_SHOT, AC_SCORE_KILL, AC_SCORE_GRENADE_KILL, AC_SCORE_FRIENDLY, AC_SCORE_DEATH };
typedef struct {
    int kills, heads, shots, hits, grenadeKills, grenadeBonus, bestGrenade;
    int friendlyHits, friendlyDamage;
} acScoreStats_t;
typedef struct { int played[3], best[3], last, lastSkill, hasLast; } acScoreRecord_t;
typedef struct {
    acScoreStats_t stats;
    int level, skill, base, accuracyBonus, penalty, total, previous, newBest, saved, valid;
} acScoreResult_t;

/* Integer arithmetic makes displayed totals and saved records exactly reproducible.
   Accuracy counts one successful firearm discharge, even through multiple targets. */
static void AC_ScoreCalculate(acScoreResult_t *r)
{
    long long base=100LL*r->stats.kills+50LL*r->stats.heads+r->stats.grenadeBonus;
    long long bonus=r->stats.shots?base*r->stats.hits/(2LL*r->stats.shots):0;
    long long penalty=2LL*r->stats.friendlyDamage;
    long long total=base+bonus-penalty;
    r->base=(int)base;r->accuracyBonus=(int)bonus;r->penalty=(int)penalty;
    r->total=total<0?0:total>2000000000?2000000000:(int)total;
}

#endif
