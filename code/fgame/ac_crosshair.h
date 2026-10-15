/* Shared, side-effect-free crosshair math. No RNG or ballistic state writes. */
#ifndef AC_CROSSHAIR_H
#define AC_CROSSHAIR_H
#include <math.h>

/* Mirror the decay applied immediately before Weapon::Shoot samples spread.
 * In particular, zero amount leaves the stored multiplier untouched. */
static inline float AC_SpreadBeforeShot(float current, float amount, float falloff, float elapsed, float timecap)
{
    if (amount == 0.0f) return current;
    if (elapsed > timecap) return 0.0f;
    const float decayed = current - elapsed * falloff;
    return current <= 0.0f ? fminf(0.0f, decayed) : fmaxf(0.0f, decayed);
}

/* Independent normal offsets: radial CDF = 1-exp(-r*r/2).
 * A circle using the larger sigma is conservative for anisotropic weapons. */
static inline int AC_EncodeSpread95(float sx, float sy, float range)
{
    if (!(range > 0.0f)) return 0;
    const float slope = 2.447746831f * fmaxf(fabsf(sx), fabsf(sy)) / range;
    const float angle = atanf(slope);
    // Keep the encoded angle strictly below pi/2 even for extreme mod values.
    return 1 + (int)fminf(65532.0f, floorf(angle * (65533.0f / 1.570796327f) + 0.5f));
}

static inline float AC_DecodeSpread95(int packed)
{
    const unsigned int value = (unsigned int)packed & 65535u;
    return value ? tanf((value - 1) * (1.570796327f / 65533.0f)) : 0.0f;
}

static inline float AC_SpreadPixels(float slope, float pixels, float fovDegrees)
{
    return slope * pixels * 0.5f / tanf(fovDegrees * (3.141592654f / 360.0f));
}
#endif
