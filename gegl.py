"""
A pure-Python wrapper for the GEGL graphics library <https://gegl.org/>
using ctypes.
"""
#+
# Copyright 2022 Lawrence D'Oliveiro <ldo@geek-central.gen.nz>.
# Licensed under the GNU Lesser General Public License v2.1 or later.
#-

import ctypes as ct

from babl import \
    BABL

# from glib-2.0/gobject/gparam.h:

G_PARAM_USER_SHIFT = 8

# from glib-2.0/glib/gtypes.h:

GDestroyNotify = ct.CFUNCTYPE(None, ct.c_void_p)

# from glib-2.0/gobject/gclosure.h:

GCallback = ct.CFUNCTYPE(None) # actually might take args and return result, depending on context

class GEGL :
    "useful constants and types from include files."

    # from gegl-0.4/gegl-buffer-enums.h:

    AbyssPolicy = ct.c_uint
    # values for AbyssPolicy:
    ABYSS_NONE  = 0
    ABYSS_CLAMP = 1
    ABYSS_LOOP  = 2
    ABYSS_BLACK = 3
    ABYSS_WHITE = 4

    BUFFER_FILTER_AUTO = 0
    BUFFER_FILTER_BILINEAR = 16
    BUFFER_FILTER_NEAREST = 32
    BUFFER_FILTER_BOX = 48
    BUFFER_FILTER_ALL = BUFFER_FILTER_BILINEAR | BUFFER_FILTER_NEAREST | BUFFER_FILTER_BOX

    AccessMode = ct.c_uint
    # values for AccessMode:
    ACCESS_READ = 1 << 0
    ACCESS_WRITE = 1 << 1
    ACCESS_READWRITE = ACCESS_READ | ACCESS_WRITE

    SamplerType = ct.c_uint
    # values for SamplerType:
    SAMPLER_NEAREST = 0
    SAMPLER_LINEAR = 1
    SAMPLER_CUBIC = 2
    SAMPLER_NOHALO = 3
    SAMPLER_LOHALO = 4

    # from gegl-0.4/gegl-types.h:

    AUTO_ROWSTRIDE = 0

    PadType = ct.c_uint
    # values for PadType:
    PARAM_PAD_OUTPUT = 1 << G_PARAM_USER_SHIFT
    PARAM_PAD_INPUT = 1 << G_PARAM_USER_SHIFT + 1

    BlitFlags = ct.c_uint
    # values for BlitFlags:
    BLIT_DEFAULT = 0
    BLIT_CACHE = 1 << 0
    BLIT_DIRTY = 1 << 1

    SplitStrategy = ct.c_uint
    # values for SplitStrategy:
    SPLIT_STRATEGY_AUTO = 0
    SPLIT_STRATEGY_HORIZONTAL = 1
    SPLIT_STRATEGY_VERTICAL = 2

    ConfigPtr = ct.c_void_p
    StatsPtr = ct.c_void_p

    CurvePtr = ct.c_void_p
    PathPtr = ct.c_void_p
    ColourPtr = ct.c_void_p
    AudioFragmentPtr = ct.c_void_p
    OperationContextPtr = ct.c_void_p
    OperationPtr = ct.c_void_p
    NodePtr = ct.c_void_p
    ProcessorPtr = ct.c_void_p
    RandomPtr = ct.c_void_p

    # from gegl-0.4/gegl-buffer-matrix2.h:

    class BufferMatrix2(ct.Structure) :
        _fields_ = \
            [
                ("coeff", ct.c_double * 4),
            ]
    #end BufferMatrix2

    # from gegl-0.4/gegl-buffer.h:

    Buffer = ct.c_void_p

    class Rectangle(ct.Structure) :
        _fields_ = \
            [
                ("x", ct.c_int),
                ("y", ct.c_int),
                ("width", ct.c_int),
                ("height", ct.c_int),
            ]
    #end Rectangle

    TileBackendPtr = ct.c_void_p
    BufferPtr = ct.c_void_p
    SamplerPtr = ct.c_void_p

    SamplerGetFun = ct.CFUNCTYPE(None, SamplerPtr, ct.c_double, ct.c_double, ct.POINTER(BufferMatrix2), ct.c_void_p, AbyssPolicy)

#end GEGL

libgegl = ct.cdll.LoadLibrary("libgegl-0.4.so.0")

#+
# Routine arg/result types
#-

# from gegl-0.4/gegl-buffer.h:

libgegl.gegl_buffer_new.argtypes = (ct.POINTER(GEGL.Rectangle), BABL.Ptr)
libgegl.gegl_buffer_new.restype = GEGL.BufferPtr
libgegl.gegl_buffer_new_for_backend.argtypes = (ct.POINTER(GEGL.Rectangle), GEGL.TileBackendPtr)
libgegl.gegl_buffer_new_for_backend.restype = GEGL.BufferPtr
libgegl.gegl_buffer_add_handler.argtypes = (GEGL.BufferPtr, ct.c_void_p)
libgegl.gegl_buffer_add_handler.restype = None
libgegl.gegl_buffer_remove_handler.argtypes = (GEGL.BufferPtr, ct.c_void_p)
libgegl.gegl_buffer_remove_handler.restype = None
libgegl.gegl_buffer_open.argtypes = (ct.c_char_p,)
libgegl.gegl_buffer_open.restype = GEGL.BufferPtr
libgegl.gegl_buffer_save.argtypes = (GEGL.BufferPtr, ct.c_char_p, ct.POINTER(GEGL.Rectangle))
libgegl.gegl_buffer_save.restype = None
libgegl.gegl_buffer_load.argtypes = (ct.c_char_p,)
libgegl.gegl_buffer_load.restype = GEGL.BufferPtr
libgegl.gegl_buffer_flush.argtypes = (GEGL.BufferPtr,)
libgegl.gegl_buffer_flush.restype = None
libgegl.gegl_buffer_create_sub_buffer.argtypes = (GEGL.BufferPtr, ct.POINTER(GEGL.Rectangle))
libgegl.gegl_buffer_create_sub_buffer.restype = GEGL.BufferPtr
libgegl.gegl_buffer_get_extent.argtypes = (GEGL.BufferPtr,)
libgegl.gegl_buffer_get_extent.restype = ct.POINTER(GEGL.Rectangle)
libgegl.gegl_buffer_set_extent.argtypes = (GEGL.BufferPtr, ct.POINTER(GEGL.Rectangle))
libgegl.gegl_buffer_set_extent.restype = ct.c_bool
libgegl.gegl_buffer_set_abyss.argtypes = (GEGL.BufferPtr, ct.POINTER(GEGL.Rectangle))
libgegl.gegl_buffer_set_abyss.restype = ct.c_bool
libgegl.gegl_buffer_get.argtypes = (GEGL.BufferPtr, ct.POINTER(GEGL.Rectangle), ct.c_double, BABL.Ptr, ct.c_void_p, ct.c_int, GEGL.AbyssPolicy)
libgegl.gegl_buffer_get.restype = None
libgegl.gegl_buffer_set.argtypes = (GEGL.BufferPtr, ct.POINTER(GEGL.Rectangle), ct.c_int, BABL.Ptr, ct.c_void_p, ct.c_int)
libgegl.gegl_buffer_set.restype = None
libgegl.gegl_buffer_set_color_from_pixel.argtypes = (GEGL.BufferPtr, ct.POINTER(GEGL.Rectangle), ct.c_void_p, BABL.Ptr)
libgegl.gegl_buffer_set_color_from_pixel.restype = None
libgegl.gegl_buffer_set_pattern.argtypes = (GEGL.BufferPtr, ct.POINTER(GEGL.Rectangle), GEGL.BufferPtr, ct.c_int, ct.c_int)
libgegl.gegl_buffer_set_pattern.restype = None
libgegl.gegl_buffer_get_format.argtypes = (GEGL.BufferPtr,)
libgegl.gegl_buffer_get_format.restype = BABL.Ptr
libgegl.gegl_buffer_set_format.argtypes = (GEGL.BufferPtr, BABL.Ptr)
libgegl.gegl_buffer_set_format.restype = BABL.Ptr
libgegl.gegl_buffer_clear.argtypes = (GEGL.BufferPtr, ct.POINTER(GEGL.Rectangle))
libgegl.gegl_buffer_clear.restype = None
libgegl.gegl_buffer_copy.argtypes = (GEGL.BufferPtr, ct.POINTER(GEGL.Rectangle), GEGL.AbyssPolicy, GEGL.BufferPtr, ct.POINTER(GEGL.Rectangle))
libgegl.gegl_buffer_copy.restype = None
libgegl.gegl_buffer_dup.argtypes = (GEGL.BufferPtr,)
libgegl.gegl_buffer_dup.restype = GEGL.BufferPtr
libgegl.gegl_buffer_sample_at_level.argtypes = (GEGL.BufferPtr, ct.c_double, ct.c_double, ct.POINTER(GEGL.BufferMatrix2), ct.c_void_p, BABL.Ptr, ct.c_int, GEGL.SamplerType, GEGL.AbyssPolicy)
libgegl.gegl_buffer_sample_at_level.restype = None
libgegl.gegl_buffer_sample.argtypes = (GEGL.BufferPtr, ct.c_double, ct.c_double, ct.POINTER(GEGL.BufferMatrix2), ct.c_void_p, BABL.Ptr, GEGL.SamplerType, GEGL.AbyssPolicy)
libgegl.gegl_buffer_sample.restype = None
libgegl.gegl_sampler_get_fun.argtypes = (GEGL.SamplerPtr,)
libgegl.gegl_sampler_get_fun.restype = ct.c_void_p # GEGL.SamplerGetFun
libgegl.gegl_buffer_sampler_new.argtypes = (GEGL.BufferPtr, BABL.Ptr, GEGL.SamplerType)
libgegl.gegl_buffer_sampler_new.restype = GEGL.SamplerPtr
libgegl.gegl_buffer_sampler_new_at_level.argtypes = (GEGL.BufferPtr, BABL.Ptr, GEGL.SamplerType, ct.c_int)
libgegl.gegl_buffer_sampler_new_at_level.restype = GEGL.SamplerPtr
libgegl.gegl_sampler_get.argtypes = (GEGL.SamplerPtr, ct.c_double, ct.c_double, ct.POINTER(GEGL.BufferMatrix2), ct.c_void_p, GEGL.AbyssPolicy)
libgegl.gegl_sampler_get.restype = None
libgegl.gegl_sampler_get_context_rect.argtypes = (GEGL.SamplerPtr,)
libgegl.gegl_sampler_get_context_rect.restype = ct.POINTER(GEGL.Rectangle)
libgegl.gegl_buffer_linear_new.argtypes = (ct.POINTER(GEGL.Rectangle), BABL.Ptr)
libgegl.gegl_buffer_linear_new.restype = GEGL.BufferPtr
libgegl.gegl_buffer_linear_new_from_data.argtypes = (ct.c_void_p, BABL.Ptr, ct.POINTER(GEGL.Rectangle), ct.c_int, GDestroyNotify, ct.c_void_p)
libgegl.gegl_buffer_linear_open.argtypes = (GEGL.BufferPtr, ct.POINTER(GEGL.Rectangle), ct.POINTER(ct.c_int), BABL.Ptr)
libgegl.gegl_buffer_linear_open.restype = ct.c_void_p
libgegl.gegl_buffer_linear_close.argtypes = (GEGL.BufferPtr, ct.c_void_p)
libgegl.gegl_buffer_linear_close.restype = None
libgegl.gegl_buffer_get_abyss.argtypes = (GEGL.BufferPtr,)
libgegl.gegl_buffer_get_abyss.restype = ct.POINTER(GEGL.Rectangle)
libgegl.gegl_buffer_share_storage.argtypes = (GEGL.BufferPtr, GEGL.BufferPtr)
libgegl.gegl_buffer_share_storage.restype = ct.c_bool
libgegl.gegl_buffer_signal_connect.argtypes = (GEGL.BufferPtr, ct.c_char_p, GCallback, ct.c_void_p)
libgegl.gegl_buffer_signal_connect.restype = ct.c_long
libgegl.gegl_buffer_freeze_changed.argtypes = (GEGL.BufferPtr,)
libgegl.gegl_buffer_freeze_changed.restype = None
libgegl.gegl_buffer_thaw_changed.argtypes = (GEGL.BufferPtr,)
libgegl.gegl_buffer_thaw_changed.restype = None
libgegl.gegl_buffer_flush_ext.argtypes = (GEGL.BufferPtr, ct.POINTER(GEGL.Rectangle))
libgegl.gegl_buffer_flush_ext.restype = None
