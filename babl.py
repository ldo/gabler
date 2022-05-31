"""
A pure-Python wrapper for BABL <https://gegl.org/babl/> using ctypes.

For now, I am only providing enough to get the accompanying GEGL
wrapper to work.
"""
#+
# Copyright 2022 Lawrence D'Oliveiro <ldo@geek-central.gen.nz>.
# Licensed under the GNU Lesser General Public License v2.1 or later.
#-

import ctypes as ct

# from babl-0.1/babl/babl-types.h:

BablPtr = ct.c_void_p

class BABL :
    "useful constants and types from include files."

    # from babl-0.1/babl/babl-types.h:

    FuncLinear = ct.CFUNCTYPE(None, BablPtr, ct.c_char_p, ct.c_char_p, ct.c_long, ct.c_void_p)
    FuncPlanar = ct.CFUNCTYPE(None, BablPtr, ct.c_int, ct.POINTER(ct.c_char_p), ct.POINTER(ct.c_int), ct.c_int, ct.POINTER(ct.c_char_p), ct.POINTER(ct.c_int), ct.c_long, ct.c_void_p)

    # from babl-0.1/babl/babl.h:

    IccIntent = ct.c_uint
    # values for IccIntent:
    ICC_INTENT_PERCEPTUAL = 0
    ICC_INTENT_RELATIVE_COLORIMETRIC = 1
    ICC_INTENT_SATURATION = 2
    ICC_INTENT_ABSOLUTE_COLORIMETRIC = 3
    ICC_INTENT_PERFORMANCE = 32

    ModelFlag = ct.c_uint
    # values for ModelFlag:
    MODEL_FLAG_ALPHA = 1 << 1
    MODEL_FLAG_ASSOCIATED = 1 << 2
    MODEL_FLAG_INVERTED = 1 << 3
    MODEL_FLAG_LINEAR = 1 << 10
    MODEL_FLAG_NONLINEAR = 1 << 11
    MODEL_FLAG_PERCEPTUAL = 1 << 12
    MODEL_FLAG_GRAY = 1 << 20
    MODEL_FLAG_RGB = 1 << 21
    # MODEL_FLAG_SPECTRAL = 1 << 22 # NYI
    MODEL_FLAG_CIE = 1 << 23
    MODEL_FLAG_CMYK = 1 << 24
    # MODEL_FLAG_LUZ = 1 << 25 # NYI

    SpaceFlags = ct.c_uint
    # values for SpaceFlags:
    SPACE_FLAG_NONE = 0
    SPACE_FLAG_EQUALIZE = 1

    FishProcess = ct.CFUNCTYPE(None, BablPtr, ct.c_char_p, ct.c_char_p, ct.c_long, ct.c_void_p)

    ALPHA_FLOOR = 1 / 65536

#end BABL

libbabl = ct.cdll.LoadLibrary("libbabl-0.1.so.0")

#+
# Routine arg/result types
#-

libbabl.babl_init.argtypes = ()
libbabl.babl_init.restype = None
libbabl.babl_exit.argtypes = ()
libbabl.babl_exit.restype = None
libbabl.babl_type.argtypes = (ct.c_char_p,)
libbabl.babl_type.restype = BablPtr
libbabl.babl_sampling.argtypes = (ct.c_int, ct.c_int)
libbabl.babl_sampling.restype = BablPtr
libbabl.babl_component.argtypes = (ct.c_char_p,)
libbabl.babl_component.restype = BablPtr
libbabl.babl_model.argtypes = (ct.c_char_p,)
libbabl.babl_model.restype = BablPtr
libbabl.babl_model_with_space.argtypes = (ct.c_char_p, BablPtr)
libbabl.babl_model_with_space.restype = BablPtr
libbabl.babl_space.argtypes = (ct.c_char_p,)
libbabl.babl_space.restype = BablPtr
libbabl.babl_space_from_icc.argtypes = (ct.c_void_p, ct.c_int, BABL.IccIntent, ct.POINTER(ct.c_char_p))
libbabl.babl_space_from_icc.restype = BablPtr
libbabl.babl_space_get_gamma.argtypes = (BablPtr,)
libbabl.babl_space_get_gamma.restype = ct.c_double
# babl_icc_make_space deprecated
libbabl.babl_icc_get_key.argtypes = (ct.c_void_p, ct.c_int, ct.c_char_p, ct.c_char_p, ct.c_char_p)
libbabl.babl_icc_get_key.restype = ct.c_char_p
libbabl.babl_format.argtypes = (ct.c_char_p,)
libbabl.babl_format.restype = BablPtr
libbabl.babl_format_with_space.argtypes = (ct.c_char_p, BablPtr)
libbabl.babl_format_with_space.restype = BablPtr
libbabl.babl_format_exists.argtypes = (ct.c_char_p,)
libbabl.babl_format_exists.restype = ct.c_bool
libbabl.babl_format_get_space.argtypes = (BablPtr,)
libbabl.babl_format_get_space.restype = BablPtr
libbabl.babl_fish.argtypes = (ct.c_void_p, ct.c_void_p)
libbabl.babl_fish.restype = BablPtr
libbabl.babl_fast_fish.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_char_p)
libbabl.babl_fast_fish.restype = BablPtr
libbabl.babl_process.argtypes = (BablPtr, ct.c_void_p, ct.c_void_p, ct.c_long)
libbabl.babl_process.restype = ct.c_long
libbabl.babl_process_rows.argtypes = (BablPtr, ct.c_void_p, ct.c_int, ct.c_void_p, ct.c_int, ct.c_long, ct.c_int)
libbabl.babl_process_rows.restype = ct.c_long
libbabl.babl_get_name.argtypes = (BablPtr,)
libbabl.babl_get_name.restype = ct.c_char_p
libbabl.babl_format_has_alpha.argtypes = (BablPtr,)
libbabl.babl_format_has_alpha.restype = ct.c_bool
libbabl.babl_format_get_bytes_per_pixel.argtypes = (BablPtr,)
libbabl.babl_format_get_bytes_per_pixel.restype = ct.c_int
libbabl.babl_format_get_model.argtypes = (BablPtr,)
libbabl.babl_format_get_model.restype = BablPtr
libbabl.babl_get_model_flags.argtypes = (BablPtr,)
libbabl.babl_get_model_flags.restype = BABL.ModelFlag
libbabl.babl_format_get_n_components.argtypes = (BablPtr,)
libbabl.babl_format_get_n_components.restype = ct.c_int
libbabl.babl_format_get_type.argtypes = (BablPtr, ct.c_int)
libbabl.babl_format_get_type.restype = BablPtr
# babl_model_new, babl_format_new -- use varargs, can’t access
libbabl.babl_format_n.argtypes = (BablPtr, ct.c_int)
libbabl.babl_format_n.restype = BablPtr
libbabl.babl_format_is_format_n.argtypes = (BablPtr,)
libbabl.babl_format_is_format_n.restype = ct.c_bool
# babl_conversion_new -- uses varargs, can’t access
libbabl.babl_conversion_get_source_space.argtypes = (BablPtr,)
libbabl.babl_conversion_get_source_space.restype = BablPtr
libbabl.babl_conversion_get_destination_space.argtypes = (BablPtr,)
libbabl.babl_conversion_get_destination_space.restype = BablPtr
libbabl.babl_new_palette.argtypes = (ct.c_char_p, ct.POINTER(BablPtr), ct.POINTER(BablPtr))
libbabl.babl_new_palette.restype = BablPtr
libbabl.babl_new_palette_with_space.argtypes = (ct.c_char_p, BablPtr, ct.POINTER(BablPtr), ct.POINTER(BablPtr))
libbabl.babl_new_palette_with_space.restype = BablPtr
libbabl.babl_format_is_palette.argtypes = (BablPtr,)
libbabl.babl_format_is_palette.restype = ct.c_bool
libbabl.babl_palette_set_palette.argtypes = (BablPtr, BablPtr, ct.c_void_p, ct.c_int)
libbabl.babl_palette_set_palette.restype = None
libbabl.babl_palette_reset.argtypes = (BablPtr,)
libbabl.babl_palette_reset.restype = None
libbabl.babl_set_user_data.argtypes = (BablPtr, ct.c_void_p)
libbabl.babl_set_user_data.restype = None
libbabl.babl_get_user_data.argtypes = (BablPtr,)
libbabl.babl_get_user_data.restype = ct.c_void_p
libbabl.babl_space_from_chromaticities.argtypes = (ct.c_char_p, ct.c_double, ct.c_double, ct.c_double, ct.c_double, BablPtr, BablPtr, BablPtr, BABL.SpaceFlags)
libbabl.babl_space_from_chromaticities.restype = BablPtr
libbabl.babl_trc_gamma.argtypes = (ct.c_double,)
libbabl.babl_trc_gamma.restype = BablPtr
libbabl.babl_trc.argtypes = (ct.c_char_p,)
libbabl.babl_trc.restype = BablPtr
libbabl.babl_space_with_trc.argtypes = (BablPtr, BablPtr)
libbabl.babl_space_with_trc.restype = BablPtr
libbabl.babl_space_get.argtypes = (BablPtr, ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(BablPtr), ct.POINTER(BablPtr), ct.POINTER(BablPtr))
libbabl.babl_space_get.restype = None
libbabl.babl_space_get_rgb_luminance.argtype = (BablPtr, ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double))
libbabl.babl_space_get_rgb_luminance.restype = None
libbabl.babl_model_is.argtypes = (BablPtr, ct.c_char_p)
libbabl.babl_model_is.restype = ct.c_bool
  # overridden by babl_model_is macro which calls babl_model_with_space instead
libbabl.babl_space_get_icc.argtypes = (BablPtr, ct.POINTER(ct.c_int))
libbabl.babl_space_get_icc.restype = ct.c_char_p
libbabl.babl_space_from_rgbxyz_matrix.argtypes = (ct.c_char_p, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double, BablPtr, BablPtr, BablPtr)
libbabl.babl_space_from_rgbxyz_matrix.restype = BablPtr
libbabl.babl_format_get_encoding.argtypes = (BablPtr,)
libbabl.babl_format_get_encoding = ct.c_char_p
libbabl.babl_space_is_cmyk.argtypes = (BablPtr,)
libbabl.babl_space_is_cmyk.restype = ct.c_bool
libbabl.babl_space_is_gray.argtypes = (BablPtr,)
libbabl.babl_space_is_gray.restype = ct.c_bool
libbabl.babl_fish_get_process.argtypes = (BablPtr,)
libbabl.babl_fish_get_process.restype = BABL.FishProcess
