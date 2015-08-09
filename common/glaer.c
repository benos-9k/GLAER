
/*** GLAER: begin manually authored code ***/

/* we use strcpy and strlen, safely */
#ifndef _CRT_SECURE_NO_WARNINGS
#define _CRT_SECURE_NO_WARNINGS 1
#endif

#define GLAER_NO_GL_ENUMS
#define GLAER_NO_GL_FUNCTYPES
#define GLAER_NO_GL_FUNCTIONS
#include <GLAER/glaer.h>

#include <string.h>

/* pointers to user functions */
static GlaerContextProviderProc glaer_current_context_provider;
static GlaerErrorCallbackProc glaer_error_callback;

static void glaerReportError(const GLchar *msg) {
	if (glaer_error_callback) {
		glaer_error_callback(msg);
	}
}

static int glaerCheckContext(GlaerContext *ctx) {
	if (ctx) return 1;
	glaerReportError("GLAER context is NULL");
	return 0;
}

/* system-specific entrypoint retrieval and error checking */
#if defined(_WIN32)
/* Windows */

#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif

#ifndef NOMINMAX
#define NOMINMAX
#endif

/* prevent redefinition; our definition should be the same as windows.h  */
#undef APIENTRY

#include <windows.h>

#undef far
#undef near

/* https://www.opengl.org/wiki/Load_OpenGL_Functions */

static GlaerPFn glaerGetProcAddressWGL(HMODULE module, const GLchar *procname) {
	void *p;
	p = (void *) wglGetProcAddress(procname);
	if (
		(p == NULL) ||
		(p == (void *) 0x1) ||
		(p == (void *) 0x2) ||
		(p == (void *) 0x3) ||
		(p == (void *) -1)
	){
		p = (void *) GetProcAddress(module, procname);
	}
	return (GlaerPFn) p;
}

static int glaerCheckInitWGL(HMODULE module, GlaerContext *ctx) {
	if (!glaerCheckContext(ctx)) return 0;
	if (!module) {
		GLchar buf[256];
		strcpy(buf, "Failed to load opengl32.dll: ");
		FormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, GetLastError(), MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), buf + 29, 256 - 29, NULL);
		buf[255] = '\0';
		glaerReportError(buf);
		return 0;
	}
	if (!wglGetCurrentContext()) {
		glaerReportError("Current thread has no OpenGL context");
		return 0;
	}
	return 1;
}

#define GLAER_GET_PROC_ADDRESS_DECL HMODULE module;
#define GLAER_GET_PROC_ADDRESS_INIT module = LoadLibraryA("opengl32.dll");
#define glaerGetProcAddress(procname) glaerGetProcAddressWGL(module, procname)
#define glaerCheckInit(ctx) glaerCheckInitWGL(module, ctx)

#elif defined(__APPLE__)
/* Apple */
#include "TargetConditionals.h"

#if TARGET_OS_MAC
/* MacOS */
#include <dlfcn.h>

static GlaerPFn glaerGetProcAddressMac(void *module, const GLchar *procname) {
	void *p;
	p = dlsym(module, procname);
	/* we're expecting some errors, so just clear them */
	if (!p) dlerror();
	return (GlaerPFn) p;
}

static int glaerCheckInitMac(void *module, GlaerContext *ctx) {
	if (!glaerCheckContext(ctx)) return 0;
	if (!module) {
		glaerReportError(dlerror());
		return 0;
	}
	return 1;
}

#define GLAER_GET_PROC_ADDRESS_DECL void *module;
#define GLAER_GET_PROC_ADDRESS_INIT module = dlopen("/System/Library/Frameworks/OpenGL.framework/Versions/A/Libraries/libGL.dylib", RTLD_NOW | RTLD_GLOBAL);
#define glaerGetProcAddress(procname) glaerGetProcAddressMac(module, procname)
#define glaerCheckInit(ctx) glaerCheckInitMac(module, ctx)

#elif TARGET_OS_IPHONE
/* iOS device */
#error iOS is not supported yet

#else
#error unsupported __APPLE__ target
#endif

#elif defined(__ANDROID__)
/* Android */
#error Android is not supported yet

#else
/* Assume GLX (linux etc) */

/*
 * glXGetProcAddress requires GLX 1.4.
 * GLAER requires glXGetProcAddress (or the ARB variant) on GLX.
 * glx.h includes gl.h, whose header guard is already defined by glaer.h,
 * thus preventing its inclusion (and redefinition of GL symbols).
 * glx.h should still compile safely like this.
 */
 
#include <GL/glx.h>

#if defined(GLX_VERSION_1_4)

static GlaerPFn glaerGetProcAddressGLX(const GLchar *procname) {
	return glXGetProcAddress((const GLubyte *)(procname));
}

#elif defined(GLX_ARB_get_proc_address)

static GlaerPFn glaerGetProcAddressGLX(const GLchar *procname) {
	return glXGetProcAddressARB((const GLubyte *)(procname));
}

#else
#error GLX_VERSION_1_4 or GLX_ARB_get_proc_address is required
#endif

static int glaerCheckInitGLX(GlaerContext *ctx) {
	if (!glaerCheckContext(ctx)) return 0;
	if (!glXGetCurrentContext()) {
		glaerReportError("Current thread has no OpenGL context");
		return 0;
	}
	return 1;
}

#define GLAER_GET_PROC_ADDRESS_DECL
#define GLAER_GET_PROC_ADDRESS_INIT
#define glaerGetProcAddress(procname) glaerGetProcAddressGLX(procname)
#define glaerCheckInit(ctx) glaerCheckInitGLX(ctx)

#endif

void APIENTRY glaerSetCurrentContextProvider(GlaerContextProviderProc p) {
	glaer_current_context_provider = p;
}

void APIENTRY glaerSetErrorCallback(GlaerErrorCallbackProc p) {
	glaer_error_callback = p;
}

GlaerContext * APIENTRY glaerGetCurrentContext() {
	return glaer_current_context_provider();
}

/*** GLAER: end manually authored code ***/
