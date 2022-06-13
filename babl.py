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
from weakref import \
    WeakValueDictionary

class BABL :
    "useful constants and types from include files."

    # from babl-0.1/babl/babl-types.h:

    Ptr = ct.c_void_p

    FuncLinear = ct.CFUNCTYPE(None, Ptr, ct.c_char_p, ct.c_char_p, ct.c_long, ct.c_void_p)
    FuncPlanar = ct.CFUNCTYPE(None, Ptr, ct.c_int, ct.POINTER(ct.c_char_p), ct.POINTER(ct.c_int), ct.c_int, ct.POINTER(ct.c_char_p), ct.POINTER(ct.c_int), ct.c_long, ct.c_void_p)

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

    FishProcess = ct.CFUNCTYPE(None, Ptr, ct.c_char_p, ct.c_char_p, ct.c_long, ct.c_void_p)

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
libbabl.babl_type.restype = BABL.Ptr
libbabl.babl_sampling.argtypes = (ct.c_int, ct.c_int)
libbabl.babl_sampling.restype = BABL.Ptr
libbabl.babl_component.argtypes = (ct.c_char_p,)
libbabl.babl_component.restype = BABL.Ptr
libbabl.babl_model.argtypes = (ct.c_char_p,)
libbabl.babl_model.restype = BABL.Ptr
libbabl.babl_model_with_space.argtypes = (ct.c_char_p, BABL.Ptr)
libbabl.babl_model_with_space.restype = BABL.Ptr
libbabl.babl_space.argtypes = (ct.c_char_p,)
libbabl.babl_space.restype = BABL.Ptr
libbabl.babl_space_from_icc.argtypes = (ct.c_void_p, ct.c_int, BABL.IccIntent, ct.POINTER(ct.c_char_p))
libbabl.babl_space_from_icc.restype = BABL.Ptr
libbabl.babl_space_get_gamma.argtypes = (BABL.Ptr,)
libbabl.babl_space_get_gamma.restype = ct.c_double
# babl_icc_make_space deprecated
libbabl.babl_icc_get_key.argtypes = (ct.c_void_p, ct.c_int, ct.c_char_p, ct.c_char_p, ct.c_char_p)
libbabl.babl_icc_get_key.restype = ct.c_char_p
libbabl.babl_format.argtypes = (ct.c_char_p,)
libbabl.babl_format.restype = BABL.Ptr
libbabl.babl_format_with_space.argtypes = (ct.c_char_p, BABL.Ptr)
libbabl.babl_format_with_space.restype = BABL.Ptr
libbabl.babl_format_exists.argtypes = (ct.c_char_p,)
libbabl.babl_format_exists.restype = ct.c_bool
libbabl.babl_format_get_space.argtypes = (BABL.Ptr,)
libbabl.babl_format_get_space.restype = BABL.Ptr
libbabl.babl_fish.argtypes = (ct.c_void_p, ct.c_void_p)
libbabl.babl_fish.restype = BABL.Ptr
libbabl.babl_fast_fish.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_char_p)
libbabl.babl_fast_fish.restype = BABL.Ptr
libbabl.babl_process.argtypes = (BABL.Ptr, ct.c_void_p, ct.c_void_p, ct.c_long)
libbabl.babl_process.restype = ct.c_long
libbabl.babl_process_rows.argtypes = (BABL.Ptr, ct.c_void_p, ct.c_int, ct.c_void_p, ct.c_int, ct.c_long, ct.c_int)
libbabl.babl_process_rows.restype = ct.c_long
libbabl.babl_get_name.argtypes = (BABL.Ptr,)
libbabl.babl_get_name.restype = ct.c_char_p
libbabl.babl_format_has_alpha.argtypes = (BABL.Ptr,)
libbabl.babl_format_has_alpha.restype = ct.c_bool
libbabl.babl_format_get_bytes_per_pixel.argtypes = (BABL.Ptr,)
libbabl.babl_format_get_bytes_per_pixel.restype = ct.c_int
libbabl.babl_format_get_model.argtypes = (BABL.Ptr,)
libbabl.babl_format_get_model.restype = BABL.Ptr
libbabl.babl_get_model_flags.argtypes = (BABL.Ptr,)
libbabl.babl_get_model_flags.restype = BABL.ModelFlag
libbabl.babl_format_get_n_components.argtypes = (BABL.Ptr,)
libbabl.babl_format_get_n_components.restype = ct.c_int
libbabl.babl_format_get_type.argtypes = (BABL.Ptr, ct.c_int)
libbabl.babl_format_get_type.restype = BABL.Ptr
libbabl.babl_type_new.argtypes = (ct.c_void_p,) # varargs!
libbabl.babl_type_new.restype = ct.c_void_p
libbabl.babl_component_new.argtypes = (ct.c_void_p,) # varargs!
libbabl.babl_component_new.restype = ct.c_void_p
libbabl.babl_model_new.argtypes = (ct.c_void_p,) # varargs!
libbabl.babl_model_new.restype = ct.c_void_p
libbabl.babl_format_new.argtypes = (ct.c_void_p,) # varargs!
libbabl.babl_format_new.restype = ct.c_void_p
libbabl.babl_format_n.argtypes = (BABL.Ptr, ct.c_int)
libbabl.babl_format_n.restype = BABL.Ptr
libbabl.babl_format_is_format_n.argtypes = (BABL.Ptr,)
libbabl.babl_format_is_format_n.restype = ct.c_bool
libbabl.babl_conversion_new.argtypes = (ct.c_void_p,) # varargs!
libbabl.babl_conversion_new.restype = ct.c_void_p
libbabl.babl_conversion_get_source_space.argtypes = (BABL.Ptr,)
libbabl.babl_conversion_get_source_space.restype = BABL.Ptr
libbabl.babl_conversion_get_destination_space.argtypes = (BABL.Ptr,)
libbabl.babl_conversion_get_destination_space.restype = BABL.Ptr
libbabl.babl_new_palette.argtypes = (ct.c_char_p, ct.POINTER(BABL.Ptr), ct.POINTER(BABL.Ptr))
libbabl.babl_new_palette.restype = BABL.Ptr
libbabl.babl_new_palette_with_space.argtypes = (ct.c_char_p, BABL.Ptr, ct.POINTER(BABL.Ptr), ct.POINTER(BABL.Ptr))
libbabl.babl_new_palette_with_space.restype = BABL.Ptr
libbabl.babl_format_is_palette.argtypes = (BABL.Ptr,)
libbabl.babl_format_is_palette.restype = ct.c_bool
libbabl.babl_palette_set_palette.argtypes = (BABL.Ptr, BABL.Ptr, ct.c_void_p, ct.c_int)
libbabl.babl_palette_set_palette.restype = None
libbabl.babl_palette_reset.argtypes = (BABL.Ptr,)
libbabl.babl_palette_reset.restype = None
libbabl.babl_set_user_data.argtypes = (BABL.Ptr, ct.c_void_p)
libbabl.babl_set_user_data.restype = None
libbabl.babl_get_user_data.argtypes = (BABL.Ptr,)
libbabl.babl_get_user_data.restype = ct.c_void_p
libbabl.babl_space_from_chromaticities.argtypes = (ct.c_char_p, ct.c_double, ct.c_double, ct.c_double, ct.c_double, BABL.Ptr, BABL.Ptr, BABL.Ptr, BABL.SpaceFlags)
libbabl.babl_space_from_chromaticities.restype = BABL.Ptr
libbabl.babl_trc_gamma.argtypes = (ct.c_double,)
libbabl.babl_trc_gamma.restype = BABL.Ptr
libbabl.babl_trc.argtypes = (ct.c_char_p,)
libbabl.babl_trc.restype = BABL.Ptr
libbabl.babl_space_with_trc.argtypes = (BABL.Ptr, BABL.Ptr)
libbabl.babl_space_with_trc.restype = BABL.Ptr
libbabl.babl_space_get.argtypes = (BABL.Ptr, ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(BABL.Ptr), ct.POINTER(BABL.Ptr), ct.POINTER(BABL.Ptr))
libbabl.babl_space_get.restype = None
libbabl.babl_space_get_rgb_luminance.argtype = (BABL.Ptr, ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double))
libbabl.babl_space_get_rgb_luminance.restype = None
libbabl.babl_model_is.argtypes = (BABL.Ptr, ct.c_char_p)
libbabl.babl_model_is.restype = ct.c_bool
  # overridden by babl_model_is macro which calls babl_model_with_space instead
libbabl.babl_space_get_icc.argtypes = (BABL.Ptr, ct.POINTER(ct.c_int))
libbabl.babl_space_get_icc.restype = ct.c_char_p
libbabl.babl_space_from_rgbxyz_matrix.argtypes = (ct.c_char_p, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double, BABL.Ptr, BABL.Ptr, BABL.Ptr)
libbabl.babl_space_from_rgbxyz_matrix.restype = BABL.Ptr
libbabl.babl_format_get_encoding.argtypes = (BABL.Ptr,)
libbabl.babl_format_get_encoding = ct.c_char_p
libbabl.babl_space_is_cmyk.argtypes = (BABL.Ptr,)
libbabl.babl_space_is_cmyk.restype = ct.c_bool
libbabl.babl_space_is_gray.argtypes = (BABL.Ptr,)
libbabl.babl_space_is_gray.restype = ct.c_bool
libbabl.babl_fish_get_process.argtypes = (BABL.Ptr,)
libbabl.babl_fish_get_process.restype = BABL.FishProcess

#+
# Higher-level stuff
#-

class Component :

    __slots__ = ("_bablobj", "__weakref__")

    _instances = WeakValueDictionary()

    def __new__(celf, _bablobj) :
        self = celf._instances.get(_bablobj)
        if self == None :
            self = super().__new__(celf)
            self._bablobj = _bablobj
            celf._instances[_bablobj] = self
        #end if
        return \
            self
    #end __new__

    # no need for __del__ -- babl manages its own storage?

    @classmethod
    def with_name(celf, name) :
        result = libbabl.babl_component(name.encode())
        if result != None :
            result = celf(name)
        #end if
        return \
            result
    #end with_name

    @classmethod
    def new(celf, name, id = None, doc = None, luma = False, chroma = False, alpha = False) :
        func = getattr(libbabl, "babl_component_new")
        func = type(func).from_address(ct.addressof(func))
          # new copy with same entry point
        argtypes = [ct.c_char_p]
        args = [name.encode()]
        if id != None :
            argtypes.extend([ct.c_char_p, ct.c_int])
            args.extend(["id".encode(), id])
        #end if
        if doc != None :
            argtypes.extend([ct.c_char_p, ct.c_char_p])
            args.extend(["doc".encode(), doc.encode()])
        #end if
        for keyword, value in \
            (
                ("luma", luma),
                ("chroma", chroma),
                ("alpha", alpha),
            ) \
        :
            if value :
                argtypes.extend([ct.c_char_p])
                args.extend([keyword.encode()])
            #end if
        #end for
        argtypes.append(ct.c_void_p) # null to mark end of arg list
        args.append(None)
        func.argtypes = tuple(argtypes)
        return \
            celf(func(*args))
    #end new

#end Component

class Babl :
    "wrapper around a Babl object. Do not instantiate directly: use the" \
    " format_xxx methods."

    __slots__ = ("_bablobj", "__weakref__")

    _instances = WeakValueDictionary()

    def __new__(celf, _bablobj) :
        self = celf._instances.get(_bablobj)
        if self == None :
            self = super().__new__(celf)
            self._bablobj = _bablobj
            celf._instances[_bablobj] = self
        #end if
        return \
            self
    #end __new__

    # no need for __del__ -- babl manages its own storage?

    @classmethod
    def format(celf, encoding) :
        return \
            celf(libbabl.babl_format(encoding.encode()))
    #end format

    @classmethod
    def format_with_space(celf, encoding, space) :
        if not isinstance(space, celf) :
            raise TypeError("space must be a %s" % celf.__name__)
        #end if
        return \
            celf(libbabl.babl_format_with_space(encoding.encode()), space._bablobj)
    #end format

    @property
    def name(self) :
        return \
            libbabl.babl_get_name(self._bablobj).decode()
    #end name

    @property
    def bytes_per_pixel(self) :
        return \
            libbabl.babl_format_get_bytes_per_pixel(self._bablobj)
    #end bytes_per_pixel

    @property
    def model(self) :
        return \
            type(self)(libbabl.babl_format_get_model(self._bablobj))
    #end model

    @property
    def model_flags(self) :
        return \
            libbabl.babl_get_model_flags(self._bablobj)
    #end model_flags

    @property
    def n_components(self) :
        return \
            libbabl.babl_format_get_n_components(self._bablobj)
    #end n_components

    def get_type(self, component_index) :
        return \
            type(self)(libbabl.babl_format_get_type(self._bablobj, component_index))
    #end get_type

    def __repr__(self) :
        return \
            "<Babl %s>" % repr(self.name)
    #end __repr__

#end Babl

def init() :
    libbabl.babl_init()
#end init

def exit() :
    libbabl.babl_exit()
#end exit
