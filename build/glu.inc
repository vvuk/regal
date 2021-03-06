# glu.inc
#
# Generic gnumake .inc for building GLU
#

# Sources

GLU.C += src/glu/libtess/dict.c
GLU.C += src/glu/libtess/geom.c
GLU.C += src/glu/libtess/memalloc.c
GLU.C += src/glu/libtess/mesh.c
GLU.C += src/glu/libtess/normal.c
#GLU.C += src/glu/libtess/priorityq-heap.c
GLU.C += src/glu/libtess/priorityq.c
GLU.C += src/glu/libtess/render.c
GLU.C += src/glu/libtess/sweep.c
GLU.C += src/glu/libtess/tess.c
GLU.C += src/glu/libtess/tessmono.c
GLU.C += src/glu/libutil/error.c
GLU.C += src/glu/libutil/glue.c
GLU.C += src/glu/libutil/mipmap.c
GLU.C += src/glu/libutil/project.c
GLU.C += src/glu/libutil/quad.c
GLU.C += src/glu/libutil/registry.c

GLU.CXX += src/glu/libnurbs/interface/bezierEval.cc
GLU.CXX += src/glu/libnurbs/interface/bezierPatch.cc
GLU.CXX += src/glu/libnurbs/interface/bezierPatchMesh.cc
GLU.CXX += src/glu/libnurbs/interface/glcurveval.cc
GLU.CXX += src/glu/libnurbs/interface/glinterface.cc
GLU.CXX += src/glu/libnurbs/interface/glrenderer.cc
GLU.CXX += src/glu/libnurbs/interface/glsurfeval.cc
GLU.CXX += src/glu/libnurbs/interface/incurveeval.cc
GLU.CXX += src/glu/libnurbs/interface/insurfeval.cc
GLU.CXX += src/glu/libnurbs/internals/arc.cc
GLU.CXX += src/glu/libnurbs/internals/arcsorter.cc
GLU.CXX += src/glu/libnurbs/internals/arctess.cc
GLU.CXX += src/glu/libnurbs/internals/backend.cc
GLU.CXX += src/glu/libnurbs/internals/basiccrveval.cc
GLU.CXX += src/glu/libnurbs/internals/basicsurfeval.cc
GLU.CXX += src/glu/libnurbs/internals/bin.cc
GLU.CXX += src/glu/libnurbs/internals/bufpool.cc
GLU.CXX += src/glu/libnurbs/internals/cachingeval.cc
GLU.CXX += src/glu/libnurbs/internals/ccw.cc
GLU.CXX += src/glu/libnurbs/internals/coveandtiler.cc
GLU.CXX += src/glu/libnurbs/internals/curve.cc
GLU.CXX += src/glu/libnurbs/internals/curvelist.cc
GLU.CXX += src/glu/libnurbs/internals/curvesub.cc
GLU.CXX += src/glu/libnurbs/internals/dataTransform.cc
GLU.CXX += src/glu/libnurbs/internals/displaylist.cc
GLU.CXX += src/glu/libnurbs/internals/flist.cc
GLU.CXX += src/glu/libnurbs/internals/flistsorter.cc
GLU.CXX += src/glu/libnurbs/internals/hull.cc
GLU.CXX += src/glu/libnurbs/internals/intersect.cc
GLU.CXX += src/glu/libnurbs/internals/knotvector.cc
GLU.CXX += src/glu/libnurbs/internals/mapdesc.cc
GLU.CXX += src/glu/libnurbs/internals/mapdescv.cc
GLU.CXX += src/glu/libnurbs/internals/maplist.cc
GLU.CXX += src/glu/libnurbs/internals/mesher.cc
GLU.CXX += src/glu/libnurbs/internals/monotonizer.cc
GLU.CXX += src/glu/libnurbs/internals/monoTriangulationBackend.cc
GLU.CXX += src/glu/libnurbs/internals/mycode.cc
GLU.CXX += src/glu/libnurbs/internals/nurbsinterfac.cc
GLU.CXX += src/glu/libnurbs/internals/nurbstess.cc
GLU.CXX += src/glu/libnurbs/internals/patch.cc
GLU.CXX += src/glu/libnurbs/internals/patchlist.cc
GLU.CXX += src/glu/libnurbs/internals/quilt.cc
GLU.CXX += src/glu/libnurbs/internals/reader.cc
GLU.CXX += src/glu/libnurbs/internals/renderhints.cc
GLU.CXX += src/glu/libnurbs/internals/slicer.cc
GLU.CXX += src/glu/libnurbs/internals/sorter.cc
GLU.CXX += src/glu/libnurbs/internals/splitarcs.cc
GLU.CXX += src/glu/libnurbs/internals/subdivider.cc
GLU.CXX += src/glu/libnurbs/internals/tobezier.cc
GLU.CXX += src/glu/libnurbs/internals/trimline.cc
GLU.CXX += src/glu/libnurbs/internals/trimregion.cc
GLU.CXX += src/glu/libnurbs/internals/trimvertpool.cc
GLU.CXX += src/glu/libnurbs/internals/uarray.cc
GLU.CXX += src/glu/libnurbs/internals/varray.cc
GLU.CXX += src/glu/libnurbs/nurbtess/directedLine.cc
GLU.CXX += src/glu/libnurbs/nurbtess/gridWrap.cc
GLU.CXX += src/glu/libnurbs/nurbtess/monoChain.cc
GLU.CXX += src/glu/libnurbs/nurbtess/monoPolyPart.cc
GLU.CXX += src/glu/libnurbs/nurbtess/monoTriangulation.cc
GLU.CXX += src/glu/libnurbs/nurbtess/partitionX.cc
GLU.CXX += src/glu/libnurbs/nurbtess/partitionY.cc
GLU.CXX += src/glu/libnurbs/nurbtess/polyDBG.cc
GLU.CXX += src/glu/libnurbs/nurbtess/polyUtil.cc
GLU.CXX += src/glu/libnurbs/nurbtess/primitiveStream.cc
GLU.CXX += src/glu/libnurbs/nurbtess/quicksort.cc
GLU.CXX += src/glu/libnurbs/nurbtess/rectBlock.cc
GLU.CXX += src/glu/libnurbs/nurbtess/sampleComp.cc
GLU.CXX += src/glu/libnurbs/nurbtess/sampleCompBot.cc
GLU.CXX += src/glu/libnurbs/nurbtess/sampleCompRight.cc
GLU.CXX += src/glu/libnurbs/nurbtess/sampleCompTop.cc
GLU.CXX += src/glu/libnurbs/nurbtess/sampledLine.cc
GLU.CXX += src/glu/libnurbs/nurbtess/sampleMonoPoly.cc
GLU.CXX += src/glu/libnurbs/nurbtess/searchTree.cc

#

GLU.CFLAGS     := -Isrc/glu/include -Isrc/glu/libnurbs/interface -Isrc/glu/libnurbs/internals -Isrc/glu/libnurbs/nurbtess
GLU.CFLAGS     += -DLIBRARYBUILD

GLU.SHARED     := libRegalGLU.so
GLU.STATIC     := libRegalGLUlib.a

ifneq ($(filter darwin%,$(SYSTEM)),)
GLU.SHARED     := libRegalGLU.dylib
endif
