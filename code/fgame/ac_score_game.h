#ifndef AC_SCORE_GAME_H
#define AC_SCORE_GAME_H
#include "../qcommon/ac_score.h"

extern bool *acScoreBulletHit;
// One BulletAttack is one discharge (including all shotgun pellets). Nested
// attacks restore the outer scope; enemies behind a body cannot inflate accuracy.
class ACScoreShot {
    bool hit, player;
    bool *previous;
public:
    explicit ACScoreShot(Entity *owner):hit(false),player(owner && owner->IsSubclassOfPlayer()),previous(acScoreBulletHit)
    { acScoreBulletHit=player?&hit:NULL; }
    ~ACScoreShot()
    { if(player)gi.AC_ScoreEvent(AC_SCORE_SHOT,hit?1:0);acScoreBulletHit=previous; }
};
#endif
