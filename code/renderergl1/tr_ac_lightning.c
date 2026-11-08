/* Allied Campaign weather exposure. GPL-2.0-or-later.
 * A transient scene effect, never a player preference or archived cvar.
 * Resolve after TAA/blur but before HUD so short thunder pulses neither smear
 * into temporal history nor turn the interface white. Sky/cloud detail remains.
 */
#include "tr_local.h"
#include "SDL.h"

static float pendingFlash;
static int flashViewport[4];

void R_ACLightningReset(void) { pendingFlash = 0; }

void RB_ACLightningBegin(void)
{
    pendingFlash = 0;
    if (!tr.world || backEnd.viewParms.isPortal || backEnd.viewParms.isPortalSky
        || (backEnd.refdef.rdflags & (RDF_NOWORLDMODEL | RDF_HUD)) || backEnd.isHyperspace)
        return;
    pendingFlash = Com_Clamp(0, 1, backEnd.refdef.acLightning);
    flashViewport[0] = backEnd.viewParms.viewportX;
    flashViewport[1] = backEnd.viewParms.viewportY;
    flashViewport[2] = backEnd.viewParms.viewportWidth;
    flashViewport[3] = backEnd.viewParms.viewportHeight;
}

void RB_ACLightningFinish(void)
{
    void (APIENTRYP pushAttrib)(GLbitfield);
    void (APIENTRYP popAttrib)(void);
    void (APIENTRYP useProgram)(GLuint);
    GLint matrixMode, program = 0;
    GLenum incomingError = GL_NO_ERROR;
    float flash = pendingFlash;
    cvar_t *debug;
    pendingFlash = 0;
    if (!(flash > 0) || flashViewport[2] <= 0 || flashViewport[3] <= 0) return;
    debug = ri.Cvar_Get("r_acLightningDebug", "0", 0);
    if (debug->integer) incomingError = qglGetError();

    // Resolve per context; compatible with the fixed-function renderer, with or
    // without the optional temporal GLSL pipeline. Raw GL restores keep the
    // renderer's cached state and the actual driver state in agreement.
    pushAttrib = (void (APIENTRYP)(GLbitfield))SDL_GL_GetProcAddress("glPushAttrib");
    popAttrib = (void (APIENTRYP)(void))SDL_GL_GetProcAddress("glPopAttrib");
    useProgram = (void (APIENTRYP)(GLuint))SDL_GL_GetProcAddress("glUseProgram");
    if (!pushAttrib || !popAttrib) return;
    qglGetIntegerv(GL_MATRIX_MODE, &matrixMode);
    if (useProgram) { qglGetIntegerv(GL_CURRENT_PROGRAM, &program); useProgram(0); }
    pushAttrib(GL_ALL_ATTRIB_BITS);
    qglViewport(flashViewport[0], flashViewport[1], flashViewport[2], flashViewport[3]);
    qglScissor(flashViewport[0], flashViewport[1], flashViewport[2], flashViewport[3]);
    qglEnable(GL_SCISSOR_TEST);
    if (qglActiveTextureARB) {
        qglActiveTextureARB(GL_TEXTURE1_ARB); qglDisable(GL_TEXTURE_2D);
        qglActiveTextureARB(GL_TEXTURE0_ARB);
    }
    qglDisable(GL_TEXTURE_2D);
    qglDisable(GL_DEPTH_TEST); qglDisable(GL_STENCIL_TEST);
    qglDisable(GL_ALPHA_TEST); qglDisable(GL_CULL_FACE);
    qglDisable(GL_FOG); qglDisable(GL_LIGHTING); qglDisable(GL_CLIP_PLANE0);
    qglDepthMask(GL_FALSE); qglColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE);
    qglEnable(GL_BLEND); qglBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    qglMatrixMode(GL_PROJECTION); qglPushMatrix(); qglLoadIdentity();
    qglMatrixMode(GL_MODELVIEW); qglPushMatrix(); qglLoadIdentity();
    // White screen blend lifts the scene without clipping away cloud detail.
    qglColor4f(1, 1, 1, .65f * flash);
    qglBegin(GL_QUADS);
    qglVertex2f(-1,-1); qglVertex2f(1,-1); qglVertex2f(1,1); qglVertex2f(-1,1);
    qglEnd();
    qglPopMatrix(); qglMatrixMode(GL_PROJECTION); qglPopMatrix();
    qglMatrixMode(matrixMode);
    popAttrib();
    if (useProgram) useProgram(program);
    if (debug->integer)
        ri.Printf(PRINT_ALL, "AC_LIGHTNING strength=%.4f viewport=%dx%d gl_error=%d incoming_error=%d\n",
                  flash, flashViewport[2], flashViewport[3], qglGetError(), incomingError);
}
