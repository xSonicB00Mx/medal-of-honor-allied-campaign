/*
===========================================================================
Copyright (C) 2025 the OpenMoHAA team

This file is part of OpenMoHAA source code.

OpenMoHAA source code is free software; you can redistribute it
and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of the License,
or (at your option) any later version.

OpenMoHAA source code is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenMoHAA source code; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
===========================================================================
*/

#ifdef USE_INTERNAL_SDL_HEADERS
#    include "SDL.h"
#else
#    include <SDL.h>
#endif

#include "../qcommon/qcommon.h"

static SDL_Cursor *cursor = NULL;
static SDL_Surface *cursor_surface = NULL;
extern SDL_Window *SDL_window;

void IN_GetMousePosition(int *x, int *y) {
    SDL_GetMouseState(x, y);
    SDL_Window *window = SDL_GetMouseFocus();
    if (window) {
        int ww, wh, dw, dh;
        SDL_GetWindowSize(window, &ww, &wh);
        SDL_GL_GetDrawableSize(window, &dw, &dh);
        if (ww > 0 && wh > 0 && dw > 0 && dh > 0) {
            *x = (int)((double)*x * dw / ww);
            *y = (int)((double)*y * dh / wh);
        }
    }
}

qboolean IN_SetCursorFromImage(const byte *pic, int width, int height, pCursorFree cursorFreeFn) {
    SDL_Surface *source;
    int windowWidth = 640, windowHeight = 480;
    int size;
    IN_FreeCursor();
    // Hardware cursors use window pixels rather than drawable pixels. This
    // matches the software cursor's 24/480 height at any resolution or DPI.
    if (SDL_window) SDL_GetWindowSize(SDL_window, &windowWidth, &windowHeight);
    size = Q_max(1, (windowHeight + 10) / 20);
    source = SDL_CreateRGBSurfaceWithFormatFrom((void *)pic, width, height, 32, 4 * width, SDL_PIXELFORMAT_ABGR8888);
    cursor_surface = SDL_CreateRGBSurfaceWithFormat(0, size, size, 32, SDL_PIXELFORMAT_ABGR8888);
    if (!source || !cursor_surface) {
        if (source) SDL_FreeSurface(source);
        cursorFreeFn((byte *)pic);
        IN_FreeCursor();
        return qfalse;
    }
    SDL_SetSurfaceBlendMode(source, SDL_BLENDMODE_NONE);
    const int result = SDL_SoftStretchLinear(source, NULL, cursor_surface, NULL);
    SDL_FreeSurface(source);
    cursorFreeFn((byte *)pic);
    if (result != 0) {
        IN_FreeCursor();
        return qfalse;
    }
    cursor = SDL_CreateColorCursor(cursor_surface, 0, 0);
    if (!cursor) {
        IN_FreeCursor();
        return qfalse;
    }
    SDL_SetCursor(cursor);

    return qtrue;
}

void IN_FreeCursor() {
    if (cursor) {
        SDL_FreeCursor(cursor);
        cursor = NULL;
    }
    if (cursor_surface) {
        SDL_FreeSurface(cursor_surface);
        cursor_surface = NULL;
    }
}

qboolean IN_IsCursorActive()
{
    return SDL_GetRelativeMouseMode() == SDL_TRUE;
}
