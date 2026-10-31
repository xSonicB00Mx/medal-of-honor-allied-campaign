/* Offline level-lighting pilot. GPL-2.0-or-later.
 * No ray tests in the game, no BSP/save mutations. Default disabled.
 * Export contains licensed map geometry/textures: local bake input ONLY.
 */
#include "tr_local.h"
#include "SDL.h"

static unsigned sourceHash;
static qboolean loaded;
static float   *gridFactors;
static int      gridBounds[3];
static vec3_t   gridOrigin;
static float    gridStep;

void R_ACRelightClear(void)
{
    loaded      = qfalse;
    gridFactors = NULL;
}

static unsigned Hash(const byte *p, int n)
{
    unsigned h = 2166136261u;
    while (n--) {
        h = (h ^ *p++) * 16777619u;
    }
    return h;
}

void R_ACRelightLoad(gamelump_t *l, const char *map)
{
    void           *buffer = NULL;
    const unsigned *h;
    int             n;
    char            path[MAX_QPATH];
    qboolean        enabled = ri.Cvar_Get("r_acLevelRelight", "0", CVAR_ARCHIVE)->integer != 0;
    R_ACRelightClear();
    sourceHash = 0;
    if (!enabled && !ri.Cvar_Get("r_acRelightExport", "0", 0)->integer) {
        return;
    }
    sourceHash = Hash(l->buffer, l->length);
    if (!enabled) {
        return;
    }
    COM_StripExtension(COM_SkipPath(map), path, sizeof(path));
    n = ri.FS_ReadFileEx(va("maps/ac_relight/%s.aclm", path), &buffer, qtrue);
    if (n <= 0) {
        return;
    }
    h = buffer;
    if (n < 16 || h[0] != 0x314c4341u || h[1] != sourceHash || h[2] != (unsigned)l->length || h[3] != 1u
        || n != 16 + l->length) {
        ri.Printf(PRINT_WARNING, "AC_RELIGHT_REJECT lightmap source/size/version mismatch\n");
    } else {
        memcpy(l->buffer, (byte *)buffer + 16, l->length);
        loaded = qtrue;
        ri.Printf(PRINT_ALL, "AC_RELIGHT_APPLIED %s bytes=%d\n", path, l->length);
    }
    ri.FS_FreeFile(buffer);
}

void R_ACRelightGridLoad(void)
{
    void       *buffer = NULL;
    const byte *p;
    int         n, i, count;
    unsigned    h[4];
    float       origin[3], step;
    int         bounds[3];
    if (!loaded || !tr.world) {
        return;
    }
    n = ri.FS_ReadFileEx(va("maps/ac_relight/%s.acgrid", tr.world->baseName), &buffer, qtrue);
    if (n <= 0) {
        return;
    }
    p = buffer;
    if (n < 44) {
        goto reject;
    }
    memcpy(h, p, 16);
    memcpy(origin, p + 16, 12);
    memcpy(&step, p + 28, 4);
    memcpy(bounds, p + 32, 12);
    if (h[0] != 0x31474341u || h[1] != sourceHash || h[2] != 1 || h[3] != 3 || !isfinite(step) || step < 16
        || step > 512) {
        goto reject;
    }
    count = 1;
    for (i = 0; i < 3; i++) {
        if (!isfinite(origin[i]) || bounds[i] < 2 || bounds[i] > 512 || count > 4000000 / bounds[i]) {
            goto reject;
        }
        count *= bounds[i];
    }
    if (n != 44 + count * 12) {
        goto reject;
    }
    for (i = 0; i < count * 3; i++) {
        float f;
        memcpy(&f, p + 44 + 4 * i, 4);
        if (!isfinite(f) || f < .05f || f > 3) {
            goto reject;
        }
    }
    gridFactors = ri.Hunk_Alloc(count * 12, h_low);
    memcpy(gridFactors, p + 44, count * 12);
    VectorCopy(origin, gridOrigin);
    memcpy(gridBounds, bounds, 12);
    gridStep = step;
    ri.Printf(PRINT_ALL, "AC_RELIGHT_GRID %dx%dx%d step=%.1f\n", bounds[0], bounds[1], bounds[2], step);
    ri.FS_FreeFile(buffer);
    return;
reject:
    ri.Printf(PRINT_WARNING, "AC_RELIGHT_REJECT invalid grid\n");
    ri.FS_FreeFile(buffer);
}

void R_ACRelightGrid(const vec3_t pos, vec3_t color)
{
    int   p[3], i, c, x, y, z;
    float f[3], factor[3] = {0, 0, 0};
    if (!gridFactors) {
        return;
    }
    for (i = 0; i < 3; i++) {
        float v = (pos[i] - gridOrigin[i]) / gridStep;
        if (!isfinite(v) || v < 0 || v >= gridBounds[i] - 1) {
            return;
        }
        p[i] = (int)v;
        f[i] = v - p[i];
    }
    for (z = 0; z < 2; z++) {
        for (y = 0; y < 2; y++) {
            for (x = 0; x < 2; x++) {
                int   index = ((p[2] + z) * gridBounds[1] + p[1] + y) * gridBounds[0] + p[0] + x;
                float w     = (x ? f[0] : 1 - f[0]) * (y ? f[1] : 1 - f[1]) * (z ? f[2] : 1 - f[2]);
                for (c = 0; c < 3; c++) {
                    factor[c] += w * gridFactors[3 * index + c];
                }
            }
        }
    }
    for (c = 0; c < 3; c++) {
        color[c] *= factor[c];
    }
}

/* Static props use baked vertex colors instead of the entity light grid.
 * Correct each instance's colors once at load, never per rendered triangle. */
void R_ACRelightStaticModels(void)
{
    int i, mesh, j, n, d, offset;
    if (!gridFactors || !tr.world || !tr.world->staticModelData) {
        return;
    }
    for (i = 0; i < tr.world->numStaticModels; i++) {
        const cStaticModelUnpacked_t *sm   = &tr.world->staticModels[i];
        const dtiki_t                *tiki = sm->tiki;
        if (!tiki) {
            continue;
        }
        offset = sm->firstVertexData;
        for (mesh = 0; mesh < tiki->numMeshes; mesh++) {
            const skelHeaderGame_t  *skel = ri.TIKI_GetSkel(tiki->mesh[mesh]);
            const skelSurfaceGame_t *s;
            if (!skel) {
                continue;
            }
            for (j = 0, s = skel->pSurfaces; j < skel->numSurfaces; j++, s = s->pNext) {
                for (n = 0; n < s->numVerts; n++, offset += 4) {
                    vec3_t pos, color;
                    byte  *p;
                    if (!s->pStaticXyz || offset < 0 || offset > tr.world->numStaticModelData * 4 - 4) {
                        continue;
                    }
                    VectorCopy(sm->origin, pos);
                    for (d = 0; d < 3; d++) {
                        VectorMA(pos, s->pStaticXyz[n][d] * sm->scale * tiki->load_scale, sm->axis[d], pos);
                    }
                    p = tr.world->staticModelData + offset;
                    for (d = 0; d < 3; d++) {
                        color[d] = p[d];
                    }
                    R_ACRelightGrid(pos, color);
                    for (d = 0; d < 3; d++) {
                        p[d] = (byte)Q_clamp_int((int)(color[d] + .5f), 0, 255);
                    }
                }
            }
        }
    }
}

typedef struct {
    float p[3], n[3], uv[2], lm[2];
} exportVert;

typedef struct {
    exportVert v[3];
    int        material, lightmap, chart, flags;
} exportTri;

static fileHandle_t output;
static int          triangles, materials;
static shader_t    *materialShaders[4096];

static int Material(shader_t *s)
{
    int i;
    for (i = 0; i < materials; i++) {
        if (materialShaders[i] == s) {
            return i;
        }
    }
    if (materials == 4096) {
        return -1;
    }
    materialShaders[materials] = s;
    return materials++;
}

static qboolean Usable(shader_t *s)
{
    return s && (s->isSky || (!(s->surfaceFlags & SURF_NODRAW) && s->sort <= SS_SEE_THROUGH));
}

static void Emit(exportVert *v, int a, int b, int c, shader_t *s, int chart)
{
    exportTri t;
    int       i;
    vec3_t    ab, ac, n;
    if (!Usable(s)) {
        return;
    }
    t.v[0] = v[a];
    t.v[1] = v[b];
    t.v[2] = v[c];
    VectorSubtract(t.v[1].p, t.v[0].p, ab);
    VectorSubtract(t.v[2].p, t.v[0].p, ac);
    CrossProduct(ab, ac, n);
    if (VectorNormalize(n) < .001f) {
        return;
    }
    for (i = 0; i < 3; i++) {
        if (VectorNormalize(t.v[i].n) < .01f) {
            VectorCopy(n, t.v[i].n);
        }
    }
    t.material = Material(s);
    if (t.material < 0) {
        return;
    }
    t.lightmap = s->lightmapIndex;
    t.chart    = chart;
    t.flags    = s->isSky ? 1 : 0;
    if (chart < 0) {
        t.lightmap = -1;
    }
    ri.FS_Write(&t, sizeof(t), output);
    triangles++;
}

static void Surface(const msurface_t *s, int chart)
{
    exportVert     *v;
    int             i, j, count;
    const unsigned *indices;
    if (!Usable(s->shader)) {
        return;
    }
    if (*s->data == SF_FACE) {
        const srfSurfaceFace_t *f = (void *)s->data;
        count                     = f->numPoints;
        v                         = ri.Malloc(count * sizeof(*v));
        for (i = 0; i < count; i++) {
            VectorCopy(f->points[i], v[i].p);
            VectorCopy(f->plane.normal, v[i].n);
            memcpy(v[i].uv, f->points[i] + 3, 8);
            memcpy(v[i].lm, f->points[i] + 5, 8);
        }
        indices = (void *)((byte *)f + f->ofsIndices);
        for (i = 0; i < f->numIndices; i += 3) {
            Emit(v, indices[i], indices[i + 1], indices[i + 2], s->shader, chart);
        }
    } else if (*s->data == SF_GRID) {
        const srfGridMesh_t *g = (void *)s->data;
        count                  = g->width * g->height;
        v                      = ri.Malloc(count * sizeof(*v));
        for (i = 0; i < count; i++) {
            VectorCopy(g->verts[i].xyz, v[i].p);
            VectorCopy(g->verts[i].normal, v[i].n);
            memcpy(v[i].uv, g->verts[i].st, 8);
            memcpy(v[i].lm, g->verts[i].lightmap, 8);
        }
        for (j = 0; j < g->height - 1; j++) {
            for (i = 0; i < g->width - 1; i++) {
                int a = j * g->width + i;
                Emit(v, a, a + g->width, a + 1, s->shader, chart);
                Emit(v, a + 1, a + g->width, a + g->width + 1, s->shader, chart);
            }
        }
    } else {
        return;
    }
    ri.Free(v);
}

void R_ACRelightExport(void)
{
    int          i, j, k, mesh;
    unsigned     header[4] = {0x31584541u, 0, 0, 0};
    fileHandle_t texfile;
    GLint        binding;
    void(APIENTRYP readTexture)(GLenum, GLint, GLenum, GLenum, void *);
    if (!tr.world || !ri.Cvar_Get("r_acRelightExport", "0", 0)->integer) {
        return;
    }
    readTexture = (void(APIENTRYP)(GLenum, GLint, GLenum, GLenum, void *))SDL_GL_GetProcAddress("glGetTexImage");
    if (!readTexture) {
        return;
    }
    ri.Cvar_Set("r_acRelightExport", "0");
    triangles = materials = 0;
    output                = ri.FS_OpenFileWrite("relight/scene.bin");
    if (!output) {
        return;
    }
    ri.FS_Write(header, 16, output);
    for (i = 0; i < tr.world->bmodels[0].numSurfaces; i++) {
        Surface(tr.world->bmodels[0].firstSurface + i, i);
    }
    for (i = 0; i < tr.world->numTerraPatches; i++) {
        const cTerraPatchUnpacked_t *p = &tr.world->terraPatches[i];
        exportVert                   v[81];
        float                        span = (p->drawinfo.lmapSize - 1) / 128.0f;
        for (j = 0; j < 9; j++) {
            for (k = 0; k < 9; k++) {
                exportVert *a = &v[j * 9 + k];
                float       u = k / 8.0f, w = j / 8.0f;
                int         d;
                a->p[0] = p->x0 + k * 64;
                a->p[1] = p->y0 + j * 64;
                a->p[2] = p->z0 + 2 * p->heightmap[j * 9 + k];
                a->n[0] = -(p->heightmap[j * 9 + Q_min(k + 1, 8)] - p->heightmap[j * 9 + Q_max(k - 1, 0)]) * 2.0f
                        / (k == 0 || k == 8 ? 64 : 128);
                a->n[1] = -(p->heightmap[Q_min(j + 1, 8) * 9 + k] - p->heightmap[Q_max(j - 1, 0) * 9 + k]) * 2.0f
                        / (j == 0 || j == 8 ? 64 : 128);
                a->n[2] = 1;
                for (d = 0; d < 2; d++) {
                    a->uv[d] = (1 - u) * (1 - w) * p->texCoord[0][0][d] + (1 - u) * w * p->texCoord[0][1][d]
                             + u * (1 - w) * p->texCoord[1][0][d] + u * w * p->texCoord[1][1][d];
                }
                a->lm[0] = p->s + u * span;
                a->lm[1] = p->t + w * span;
            }
        }
        for (j = 0; j < 8; j++) {
            for (k = 0; k < 8; k++) {
                int a = j * 9 + k;
                Emit(v, a, a + 1, a + 9, p->shader, 100000 + i);
                Emit(v, a + 1, a + 10, a + 9, p->shader, 100000 + i);
            }
        }
    }
    for (i = 0; i < tr.world->numStaticModels; i++) {
        const cStaticModelUnpacked_t *sm   = &tr.world->staticModels[i];
        const dtiki_t                *tiki = sm->tiki;
        dtikisurface_t               *ds;
        if (!tiki) {
            continue;
        }
        ds = tiki->surfaces;
        for (mesh = 0; mesh < tiki->numMeshes; mesh++) {
            const skelHeaderGame_t  *skel = ri.TIKI_GetSkel(tiki->mesh[mesh]);
            const skelSurfaceGame_t *s;
            if (!skel) {
                continue;
            }
            for (j = 0, s = skel->pSurfaces; j < skel->numSurfaces; j++, s = s->pNext, ds++) {
                exportVert *v;
                shader_t   *shader = tr.shaders[ds->hShader[0]];
                int         n, d;
                if (!s->pStaticXyz || !s->pStaticNormal || !s->pStaticTexCoords || !Usable(shader)) {
                    continue;
                }
                v = ri.Malloc(s->numVerts * sizeof(*v));
                for (n = 0; n < s->numVerts; n++) {
                    VectorCopy(sm->origin, v[n].p);
                    VectorClear(v[n].n);
                    for (d = 0; d < 3; d++) {
                        VectorMA(v[n].p, s->pStaticXyz[n][d] * sm->scale * tiki->load_scale, sm->axis[d], v[n].p);
                        VectorMA(v[n].n, s->pStaticNormal[n][d], sm->axis[d], v[n].n);
                    }
                    memcpy(v[n].uv, s->pStaticTexCoords[n][0], 8);
                    v[n].lm[0] = v[n].lm[1] = 0;
                }
                for (n = 0; n < s->numTriangles * 3; n += 3) {
                    Emit(v, s->pTriangles[n], s->pTriangles[n + 1], s->pTriangles[n + 2], shader, -1 - i);
                }
                ri.Free(v);
            }
        }
    }
    header[1] = triangles;
    header[2] = materials;
    header[3] = sourceHash;
    ri.FS_Seek(output, 0, FS_SEEK_SET);
    ri.FS_Write(header, 16, output);
    ri.FS_CloseFile(output);
    texfile = ri.FS_OpenFileWrite("relight/materials.bin");
    ri.FS_Write(header, 16, texfile);
    GL_SelectTexture(0);
    qglGetIntegerv(GL_TEXTURE_BINDING_2D, &binding);
    for (i = 0; i < materials; i++) {
        shader_t *s     = materialShaders[i];
        image_t  *im    = NULL;
        float     alpha = -1;
        int       d[3];
        byte     *p;
        for (j = 0; j < MAX_SHADER_STAGES; j++) {
            const shaderStage_t *st = s->unfoggedStages[j];
            if (!st) {
                break;
            }
            if (st->stateBits & GLS_ATEST_GE_80) {
                alpha = .5f;
            } else if (st->stateBits & GLS_ATEST_GT_0) {
                alpha = .01f;
            }
            for (k = 0; k < 2; k++) {
                if (!st->bundle[k].isLightmap && st->bundle[k].image[0] && st->bundle[k].image[0] != tr.whiteImage
                    && !im) {
                    im = st->bundle[k].image[0];
                }
            }
        }
        if (!im) {
            im = tr.whiteImage;
        }
        d[0] = im->uploadWidth;
        d[1] = im->uploadHeight;
        d[2] = s->isSky ? 1 : 0;
        p    = ri.Malloc(d[0] * d[1] * 4);
        qglBindTexture(GL_TEXTURE_2D, im->texnum);
        readTexture(GL_TEXTURE_2D, 0, GL_RGBA, GL_UNSIGNED_BYTE, p);
        ri.FS_Write(s->name, MAX_QPATH, texfile);
        ri.FS_Write(d, 12, texfile);
        ri.FS_Write(&alpha, 4, texfile);
        ri.FS_Write(p, d[0] * d[1] * 4, texfile);
        ri.Free(p);
    }
    qglBindTexture(GL_TEXTURE_2D, binding);
    ri.FS_CloseFile(texfile);
    ri.Printf(PRINT_ALL, "AC_RELIGHT_EXPORT triangles=%d materials=%d hash=%u\n", triangles, materials, sourceHash);
}
