#!/usr/bin/python -B

from string import Template, upper, replace

from ApiUtil import outputCode

cond = { 'wgl' : 'REGAL_SYS_WGL', 'glx' : 'REGAL_SYS_GLX', 'cgl' : 'REGAL_SYS_OSX', 'egl' : 'REGAL_SYS_EGL' }

contextInfoHeaderTemplate = Template( '''${AUTOGENERATED}
${LICENSE}

#ifndef __${HEADER_NAME}_H__
#define __${HEADER_NAME}_H__

#include "RegalUtil.h"

REGAL_GLOBAL_BEGIN

#include <GL/Regal.h>

#include <set>
#include <string>

REGAL_GLOBAL_END

REGAL_NAMESPACE_BEGIN

struct RegalContext;

struct ContextInfo
{
  ContextInfo();
  ~ContextInfo();

  void init(const RegalContext &context);

  // glewGetExtension, glewIsSupported

  bool getExtension(const char *ext) const;
  bool isSupported(const char *ext) const;

  // As reported by OpenGL implementation

  std::string vendor;
  std::string renderer;
  std::string version;
  std::string extensions;

  // As reported by Regal

  std::string regalVendor;
  std::string regalRenderer;
  std::string regalVersion;
  std::string regalExtensions;

  std::set<std::string> regalExtensionsSet;

  // As supported by the OpenGL implementation

${VERSION_DECLARE}

  GLuint maxVertexAttribs;
  GLuint maxVaryings;
};

REGAL_NAMESPACE_END

#endif // __${HEADER_NAME}_H__
''')

contextInfoSourceTemplate = Template( '''${AUTOGENERATED}
${LICENSE}

#include "pch.h" /* For MS precompiled header support */

#include "RegalUtil.h"

REGAL_GLOBAL_BEGIN

#include <GL/Regal.h>

#include <string>
#include <set>
using namespace std;

#include <boost/print/string_list.hpp>
using namespace boost::print;

#include "RegalToken.h"
#include "RegalContext.h"
#include "RegalContextInfo.h"
#include "RegalIff.h"             // For REGAL_MAX_VERTEX_ATTRIBS

REGAL_GLOBAL_END

REGAL_NAMESPACE_BEGIN

using namespace ::REGAL_NAMESPACE_INTERNAL::Logging;
using namespace ::REGAL_NAMESPACE_INTERNAL::Token;

ContextInfo::ContextInfo()
:
${VERSION_INIT}
  maxVertexAttribs(0),
  maxVaryings(0)
{
   Internal("ContextInfo::ContextInfo","()");
}

ContextInfo::~ContextInfo()
{
   Internal("ContextInfo::~ContextInfo","()");
}

inline string getString(const RegalContext &context, const GLenum e)
{
  Internal("getString ",toString(e));
  RegalAssert(context.dispatcher.driver.glGetString);
  const GLubyte *str = context.dispatcher.driver.glGetString(e);
  return str ? string(reinterpret_cast<const char *>(str)) : string();
}

void
ContextInfo::init(const RegalContext &context)
{
  // OpenGL Version.

  vendor     = getString(context, GL_VENDOR);
  renderer   = getString(context, GL_RENDERER);
  version    = getString(context, GL_VERSION);

  Info("OpenGL vendor    : ",vendor);
  Info("OpenGL renderer  : ",renderer);
  Info("OpenGL version   : ",version);

  gl_version_major = 0;
  gl_version_minor = 0;

  gles_version_major = 0;
  gles_version_minor = 0;

  // Detect GL context version

  #if REGAL_SYS_ES1
  es1 = starts_with(version, "OpenGL ES-CM");
  if (es1)
  {
    sscanf(version.c_str(), "OpenGL ES-CM %d.%d", &gles_version_major, &gles_version_minor);
  }
  else
  #endif
  {
    #if REGAL_SYS_ES2
    es2 = starts_with(version,"OpenGL ES ");
    if (es2)
    {
      sscanf(version.c_str(), "OpenGL ES %d.%d", &gles_version_major, &gles_version_minor);
    }
    else
    #endif
    {
      sscanf(version.c_str(), "%d.%d", &gl_version_major, &gl_version_minor);
    }
  }

  // We could get either form of the OpenGL ES string, so confirm version

  #if REGAL_SYS_ES1 || REGAL_SYS_ES2
  if (!es1 && (gles_version_major == 1))
  {
    es1 = GL_TRUE;
    es2 = GL_FALSE;
  }
  else if (!es2 && (gles_version_major == 2))
  {
    es1 = GL_FALSE;
    es2 = GL_TRUE;
  }
  #endif

  #if REGAL_SYS_EMSCRIPTEN
  webgl = starts_with(version, "WebGL");
  #endif

  // For Mesa3D EGL/ES 2.0 on desktop Linux the version string doesn't start with
  // "OpenGL ES" Is that a Mesa3D bug? Perhaps...

  #if REGAL_SYS_ES2 && REGAL_SYS_EGL && !REGAL_SYS_ANDROID && !REGAL_SYS_EMSCRIPTEN
  if (Regal::Config::sysEGL)
  {
    es1 = false;
    es2 = true;
    webgl = false;
    gles_version_major = 2;
    gles_version_minor = 0;
  }
  #endif

  #if REGAL_SYS_ES2 && REGAL_SYS_EGL && REGAL_SYS_EMSCRIPTEN
  {
    es1 = false;
    es2 = true;
    webgl = true;
    gles_version_major = 2;
    gles_version_minor = 0;
  }
  #endif

  // Detect core context

  if (!es1 && !es2 && gl_version_major>=3)
  {
    GLint flags = 0;
    RegalAssert(context.dispatcher.driver.glGetIntegerv);
    context.dispatcher.driver.glGetIntegerv(GL_CONTEXT_PROFILE_MASK, &flags);
    core = flags & GL_CONTEXT_CORE_PROFILE_BIT ? GL_TRUE : GL_FALSE;
  }

  compat = !core && !es1 && !es2 && !webgl;

  if (REGAL_FORCE_CORE_PROFILE || Config::forceCoreProfile)
  {
    compat = false;
    core   = true;
    es1    = false;
    es2    = false;
  }

  #if REGAL_SYS_ES1
  if (REGAL_FORCE_ES1_PROFILE || Config::forceES1Profile)
  {
    compat = false;
    core   = false;
    es1    = true;
    es2    = false;
  }
  #endif

  #if REGAL_SYS_ES2
  if (REGAL_FORCE_ES2_PROFILE || Config::forceES2Profile)
  {
    compat = false;
    core   = false;
    es1    = false;
    es2    = true;
  }
  #endif

  // Detect driver extensions

  string_list<string> driverExtensions;

  if (core)
  {
    RegalAssert(context.dispatcher.driver.glGetStringi);
    RegalAssert(context.dispatcher.driver.glGetIntegerv);

    GLint n = 0;
    context.dispatcher.driver.glGetIntegerv(GL_NUM_EXTENSIONS, &n);

    for (GLint i=0; i<n; ++i)
      driverExtensions.push_back(reinterpret_cast<const char *>(context.dispatcher.driver.glGetStringi(GL_EXTENSIONS,i)));
    extensions = driverExtensions.join(" ");
  }
  else
  {
    extensions = getString(context, GL_EXTENSIONS);
    driverExtensions.split(extensions,' ');
  }

  regalExtensionsSet.insert(driverExtensions.begin(),driverExtensions.end());

  Info("OpenGL extensions: ",extensions);

  // TODO - filter out extensions Regal doesn't support?

#ifdef REGAL_GL_VENDOR
  regalVendor = REGAL_EQUOTE(REGAL_GL_VENDOR);
#else
  regalVendor = vendor;
#endif

#ifdef REGAL_GL_RENDERER
  regalRenderer = REGAL_EQUOTE(REGAL_GL_RENDERER);
#else
  regalRenderer = renderer;
#endif

#ifdef REGAL_GL_VERSION
  regalVersion = REGAL_EQUOTE(REGAL_GL_VERSION);
#else
  regalVersion = version;
#endif

#ifdef REGAL_GL_EXTENSIONS
  {
    string_list<string> extList;
    extList.split(REGAL_EQUOTE(REGAL_GL_EXTENSIONS),' ');
    regalExtensionsSet.clear();
    regalExtensionsSet.insert(extList.begin(),extList.end());
  }
#else
  static const char *ourExtensions[9] = {
    "GL_REGAL_log",
    "GL_REGAL_enable",
    "GL_REGAL_error_string",
    "GL_REGAL_extension_query",
    "GL_REGAL_ES1_0_compatibility",
    "GL_REGAL_ES1_1_compatibility",
    "GL_EXT_debug_marker",
    "GL_GREMEDY_string_marker",
    "GL_GREMEDY_frame_terminator"
  };
  regalExtensionsSet.insert(&ourExtensions[0],&ourExtensions[9]);
#endif

#ifndef REGAL_NO_GETENV
  {
    getEnv("REGAL_GL_VENDOR",   regalVendor);
    getEnv("REGAL_GL_RENDERER", regalRenderer);
    getEnv("REGAL_GL_VERSION",  regalVersion);

    const char *extensionsEnv = getEnv("REGAL_GL_EXTENSIONS");
    if (extensionsEnv)
    {
      string_list<string> extList;
      extList.split(extensionsEnv,' ');
      regalExtensionsSet.clear();
      regalExtensionsSet.insert(extList.begin(),extList.end());
    }
  }
#endif

  // Form Regal extension string from the set

  regalExtensions = ::boost::print::detail::join(regalExtensionsSet,string(" "));

  Info("Regal vendor     : ",regalVendor);
  Info("Regal renderer   : ",regalRenderer);
  Info("Regal version    : ",regalVersion);
  Info("Regal extensions : ",regalExtensions);

${VERSION_DETECT}

  // Driver extensions, etc detected by Regal

  set<string> e;
  e.insert(driverExtensions.begin(),driverExtensions.end());

${EXT_INIT}

  RegalAssert(context.dispatcher.driver.glGetIntegerv);
  if (es1)
  {
    maxVertexAttribs = 8;
    maxVaryings = 0;
  }
  else
  {
    context.dispatcher.driver.glGetIntegerv( GL_MAX_VERTEX_ATTRIBS, reinterpret_cast<GLint *>(&maxVertexAttribs));
    context.dispatcher.driver.glGetIntegerv( es2 ? GL_MAX_VARYING_VECTORS : GL_MAX_VARYING_FLOATS, reinterpret_cast<GLint *>(&maxVaryings));
  }

  Info("OpenGL v attribs : ",maxVertexAttribs);
  Info("OpenGL varyings  : ",maxVaryings);

  if (maxVertexAttribs > REGAL_EMU_IFF_VERTEX_ATTRIBS)
      maxVertexAttribs = REGAL_EMU_IFF_VERTEX_ATTRIBS;

  // Qualcomm fails with float4 attribs with 256 byte stride, so artificially limit to 8 attribs (n*16 is used
  // as the stride in RegalIFF).  WebGL (and Pepper) explicitly disallows stride > 255 as well.

  if (vendor == "Qualcomm" || vendor == "Chromium" || webgl)
    maxVertexAttribs = 8;

  Info("Regal  v attribs : ",maxVertexAttribs);
}

${EXT_CODE}

REGAL_NAMESPACE_END
''')

def traverseContextInfo(apis, args):

  for api in apis:
    if api.name == 'gles':
      api.versions =  [ [2, 0] ]
    if api.name == 'gl':
      api.versions =  [ [4,2], [4, 1], [4, 0] ]
      api.versions += [ [3, 3], [3, 2], [3, 1], [3, 0] ]
      api.versions += [ [2, 1], [2, 0] ]
      api.versions += [ [1, 5], [1, 4], [1, 3], [1, 2], [1, 1], [1, 0] ]
    if api.name == 'glx':
      api.versions = [ [1, 4], [1, 3], [1, 2], [1, 1], [1, 0] ]
    if api.name == 'egl':
      api.versions = [ [1, 2], [1, 1], [1, 0] ]
    c = set()
    c.update([i.category for i in api.functions])
    c.update([i.category for i in api.typedefs])
    c.update([i.category for i in api.enums])
    c.update([i.category for i in api.extensions])

    for i in api.enums:
      c.update([j.category for j in i.enumerants])

    api.categories = [i for i in c if i and len(i) and i.find('_VERSION_')==-1 and i.find('WGL_core')==-1]

    if api.name == 'egl':
      api.categories = [i for i in api.categories if not i.startswith('GL_')]

def versionDeclareCode(apis, args):

  code = ''
  for api in apis:
    name = api.name.lower()

    if name == 'gl':
      code += '  GLboolean compat : 1;\n'
      code += '  GLboolean core   : 1;\n'
      code += '  GLboolean es1    : 1;\n'
      code += '  GLboolean es2    : 1;\n'
      code += '  GLboolean webgl  : 1;\n\n'

    if name in ['gl', 'glx', 'egl']:
      code += '  GLint     %s_version_major;\n' % name
      code += '  GLint     %s_version_minor;\n' % name
      code += '\n'

    if hasattr(api, 'versions'):
      for version in sorted(api.versions):
        code += '  GLboolean %s_version_%d_%d : 1;\n' % (name, version[0], version[1])
      code += '\n'

    if name == 'gl':
      code += '  GLint     gles_version_major;\n'
      code += '  GLint     gles_version_minor;\n'
      code += '\n'
      code += '  GLint     glsl_version_major;\n'
      code += '  GLint     glsl_version_minor;\n'
      code += '\n'

  for api in apis:
    name = api.name.lower()
    if name in cond:
      code += '#if %s\n'%cond[name]
    for c in sorted(api.categories):
      code += '  GLboolean %s : 1;\n' % (c.lower())
    if name in cond:
      code += '#endif\n'
    for ext in api.extensions:
      if len(ext.emulatedBy):
        code += '  GLboolean regal_%s : 1;\n' % (ext.name.lower()[3:])
    code += '\n'

  return code

def versionInitCode(apis, args):

  code = ''
  for api in apis:
    name = api.name.lower()

    if name == 'gl':
      code += '  compat(false),\n'
      code += '  core(false),\n'
      code += '  es1(false),\n'
      code += '  es2(false),\n'
      code += '  webgl(false),\n'

    if name in ['gl', 'glx', 'egl']:
      code += '  %s_version_major(-1),\n' % name
      code += '  %s_version_minor(-1),\n' % name

    if hasattr(api, 'versions'):
      for version in sorted(api.versions):
        code += '  %s_version_%d_%d(false),\n' % (name, version[0], version[1])

    if name == 'gl':
      code += '  gles_version_major(-1),\n'
      code += '  gles_version_minor(-1),\n'
      code += '  glsl_version_major(-1),\n'
      code += '  glsl_version_minor(-1),\n'

  for api in apis:
    name = api.name.lower()
    if name in cond:
      code += '#if %s\n'%cond[name]
    for c in sorted(api.categories):
      code += '  %s(false),\n' % (c.lower())
    if name in cond:
      code += '#endif\n'
    for ext in api.extensions:
      if len(ext.emulatedBy):
        code += '  regal_%s(false),\n' % (ext.name.lower()[3:])

  return code

def versionDetectCode(apis, args):

  code = ''

  for api in apis:
    name = api.name.lower()
    if not hasattr(api, 'versions'):
      continue

    indent = ''
    if api.name=='gl':
      indent = '  '
      code += '  if (!es1 && !es2)\n  {\n'

    for i in range(len(api.versions)):
      version = api.versions[i]
      versionMajor = version[0]
      versionMinor = version[1]

      # Latest version

      if i is 0:
        code += '%s  %s_version_%d_%d = '%(indent, name, versionMajor, versionMinor)
        if versionMinor > 0:
          code += '%s_version_major > %d || (%s_version_major == %d && %s_version_minor >= %d);\n' % (name, versionMajor, name, versionMajor, name, versionMinor)
        else:
          code += '%s_version_major >= %d;\n' % (name, versionMajor)
        continue

      versionLast = api.versions[i-1]

      code += '%s  %s_version_%d_%d = %s_version_%d_%d || '%(indent,name,versionMajor,versionMinor,name,versionLast[0],versionLast[1])
      if versionMinor > 0:
        code += '(%s_version_major == %d && %s_version_minor == %d);\n' % (name, versionMajor, name, versionMinor)
      else:
        code += '%s_version_major == %d;\n' % (name, versionMajor)

    if len(indent):
      code += '  }\n'

    code += '\n'

  return code

def extensionStringCode(apis, args):

  code = ''

  for api in apis:
    name = api.name.lower()
    if name in cond:
      code += '#if %s\n'%cond[name]
    for c in sorted(api.categories):
      code += '  %s = e.find("%s")!=e.end();\n' % (c.lower(),c)
    if name in cond:
      code += '#endif\n'
    code += '\n'

  return code

def getExtensionCode(apis, args):

  code = ''
  code += 'bool\n'
  code += 'ContextInfo::getExtension(const char *ext) const\n'
  code += '{\n'
  code += '  Internal("ContextInfo::getExtension ",boost::print::quote(ext,\'"\'));\n'
  code += '\n'

  for api in apis:
    emulatedExtensions = []

    for extension in api.extensions:
      if len(extension.emulatedBy):
        emulatedExtensions.append(extension.name)

    name = api.name.lower()
    if name in cond:
      code += '#if %s\n'%cond[name]
    for c in sorted(api.categories):
      if c.startswith('GL_REGAL_') or c=='GL_EXT_debug_marker':
        code += '  if (!strcmp(ext,"%s")) return true;\n' % (c)
      elif c in emulatedExtensions:
        code += '  if (!strcmp(ext,"%s")) return regal_%s || %s;\n' % (c,c.lower()[3:],c.lower())
      else:
        code += '  if (!strcmp(ext,"%s")) return %s;\n' % (c,c.lower())
    if name in cond:
      code += '#endif\n'
    code += '\n'

  code += 'return false;\n'
  code += '}\n\n'

  code += 'bool\n'
  code += 'ContextInfo::isSupported(const char *ext) const\n'
  code += '{\n'
  code += '  Internal("ContextInfo::isSupported ",boost::print::quote(ext,\'"\'));\n'
  code += '\n'
  code += '  string_list<string> e;\n'
  code += '  e.split(ext,\' \');\n'
  code += '  for (string_list<string>::const_iterator i=e.begin(); i!=e.end(); ++i)\n'
  code += '    if (i->length() && !getExtension(i->c_str())) return false;\n'
  code += '  return true;\n'
  code += '}\n'

  return code

def generateContextInfoHeader(apis, args):

    substitute = {}
    substitute['LICENSE']         = args.license
    substitute['AUTOGENERATED']   = args.generated
    substitute['COPYRIGHT']       = args.copyright
    substitute['HEADER_NAME']     = "REGAL_CONTEXT_INFO"
    substitute['VERSION_DECLARE'] = versionDeclareCode(apis,args)
    outputCode( '%s/RegalContextInfo.h' % args.srcdir, contextInfoHeaderTemplate.substitute(substitute))

def generateContextInfoSource(apis, args):

    substitute = {}
    substitute['LICENSE']        = args.license
    substitute['AUTOGENERATED']  = args.generated
    substitute['COPYRIGHT']      = args.copyright
    substitute['VERSION_INIT']   = versionInitCode(apis,args)
    substitute['VERSION_DETECT'] = versionDetectCode(apis,args)
    substitute['EXT_INIT']       = extensionStringCode(apis,args)
    substitute['EXT_CODE']       = getExtensionCode(apis,args)
    outputCode( '%s/RegalContextInfo.cpp' % args.srcdir, contextInfoSourceTemplate.substitute(substitute))
