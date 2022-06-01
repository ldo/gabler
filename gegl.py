"""
A pure-Python wrapper for the GEGL graphics library <https://gegl.org/>
using ctypes.
"""
#+
# Copyright 2022 Lawrence D'Oliveiro <ldo@geek-central.gen.nz>.
# Licensed under the GNU Lesser General Public License v2.1 or later.
#-

import enum
import ctypes as ct

from babl import \
    BABL

# from glib-2.0/glib/gtypes.h:

GDestroyNotify = ct.CFUNCTYPE(None, ct.c_void_p)

# from glib-2.0/gobject/glib-types.h:

GType = ct.c_size_t

# from glib-2.0/gobject/gtype.h:

G_TYPE_FUNDAMENTAL_SHIFT = 2
G_TYPE_MAKE_FUNDAMENTAL = lambda t : t << G_TYPE_FUNDAMENTAL_SHIFT
G_TYPE_FUNDAMENTAL_MAX = 255 << G_TYPE_FUNDAMENTAL_SHIFT

G_TYPE_INVALID = G_TYPE_MAKE_FUNDAMENTAL(0)
G_TYPE_NONE = G_TYPE_MAKE_FUNDAMENTAL(1)
G_TYPE_INTERFACE = G_TYPE_MAKE_FUNDAMENTAL(2)
G_TYPE_CHAR = G_TYPE_MAKE_FUNDAMENTAL(3)
G_TYPE_UCHAR = G_TYPE_MAKE_FUNDAMENTAL(4)
G_TYPE_BOOLEAN = G_TYPE_MAKE_FUNDAMENTAL(5)
G_TYPE_INT = G_TYPE_MAKE_FUNDAMENTAL(6)
G_TYPE_UINT = G_TYPE_MAKE_FUNDAMENTAL(7)
G_TYPE_LONG = G_TYPE_MAKE_FUNDAMENTAL(8)
G_TYPE_ULONG = G_TYPE_MAKE_FUNDAMENTAL(9)
G_TYPE_INT64 = G_TYPE_MAKE_FUNDAMENTAL(10)
G_TYPE_UINT64 = G_TYPE_MAKE_FUNDAMENTAL(11)
G_TYPE_ENUM = G_TYPE_MAKE_FUNDAMENTAL(12)
G_TYPE_FLAGS = G_TYPE_MAKE_FUNDAMENTAL(13)
G_TYPE_FLOAT = G_TYPE_MAKE_FUNDAMENTAL(14)
G_TYPE_DOUBLE = G_TYPE_MAKE_FUNDAMENTAL(15)
G_TYPE_STRING = G_TYPE_MAKE_FUNDAMENTAL(16) # nul-terminated C strings
G_TYPE_POINTER = G_TYPE_MAKE_FUNDAMENTAL(17)
G_TYPE_BOXED = G_TYPE_MAKE_FUNDAMENTAL(18)
G_TYPE_PARAM = G_TYPE_MAKE_FUNDAMENTAL(19)
G_TYPE_OBJECT = G_TYPE_MAKE_FUNDAMENTAL(20)
G_TYPE_VARIANT = G_TYPE_MAKE_FUNDAMENTAL(21)

class GTypeClass(ct.Structure) :
    _fields_ = \
        [
            ("g_type", GType),
        ]
#end GTypeClass

class GTypeInstance(ct.Structure) :
    _fields_ = \
        [
            ("g_class", ct.POINTER(GTypeClass)),
        ]
#end GTypeInstance

class GTypeInterface(ct.Structure) :
    _fields_ = \
        [
            ("g_type", GType),
            ("g_instance_type", GType),
        ]
#end GTypeInterface

# from glib-2.0/gobject/gparam.h:

GParamFlags = ct.c_uint
# values for GParamFlags:
G_PARAM_READABLE = 1 << 0
G_PARAM_WRITABLE = 1 << 1
G_PARAM_READWRITE = G_PARAM_READABLE | G_PARAM_WRITABLE
G_PARAM_CONSTRUCT = 1 << 2
G_PARAM_CONSTRUCT_ONLY = 1 << 3
G_PARAM_LAX_VALIDATION = 1 << 4
G_PARAM_STATIC_NAME = 1 << 5
# GLIB_DEPRECATED_ENUMERATOR_IN_2_26 = G_PARAM_STATIC_NAME
G_PARAM_STATIC_NICK = 1 << 6
G_PARAM_STATIC_BLURB = 1 << 7
G_PARAM_EXPLICIT_NOTIFY = 1 << 30
G_PARAM_DEPRECATED = 1 << 31

G_PARAM_USER_SHIFT = 8

class GParamSpec(ct.Structure) :
    _fields_ = \
        [
            ("g_type_instance", ct.POINTER(GTypeInstance)),
            ("name", ct.c_char_p),
            ("flags", GParamFlags),
            ("value_type", GType),
            ("owner_type", GType),
            # private:
            ("nick", ct.c_char_p),
            ("blurb", ct.c_char_p),
            ("qdata", ct.c_void_p),
            ("ref_count", ct.c_uint),
            ("param_id", ct.c_uint),
        ]
#end GParamSpec

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

libglib2 = ct.cdll.LoadLibrary("libglib-2.0.so.0")
libgobject2 = ct.cdll.LoadLibrary("libgobject-2.0.so.0")
libgegl = ct.cdll.LoadLibrary("libgegl-0.4.so.0")

#+
# Routine arg/result types
#-

# from glib-2.0/glib/gmem.h:

libglib2.g_malloc.argtypes = (ct.c_size_t,)
libglib2.g_malloc.restype = ct.c_void_p
libglib2.g_free.argtypes = (ct.c_void_p,)
libglib2.g_free.restype = None

def g_new(c_type, nr_elts) :
    "approximate equivalent to g_new() macro in glib-2.0/glib/gmem.h."
    return \
        libglib2.g_malloc(ct.sizeof(c_type * nr_elts))
#end g_new

# from glib-2.0/gobject/gobject.h:

libgobject2.g_object_unref.argtypes = (ct.c_void_p,)
libgobject2.g_object_unref.restype = None

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

# from gegl-0.4/gegl-operations-util.h:

libgegl.gegl_list_operations.argtypes = (ct.POINTER(ct.c_uint),)
libgegl.gegl_list_operations.restype = ct.POINTER(ct.c_char_p)
libgegl.gegl_has_operation.argtypes = (ct.c_char_p,)
libgegl.gegl_has_operation.restype = ct.c_bool
libgegl.gegl_operation_list_properties.argtypes = (ct.c_char_p, ct.POINTER(ct.c_uint))
libgegl.gegl_operation_list_properties.restype = ct.POINTER(ct.POINTER(GParamSpec))
libgegl.gegl_operation_find_property.argtypes = (ct.c_char_p, ct.c_char_p)
libgegl.gegl_operation_find_property.restype = ct.c_void_p # ct.POINTER(GParamSpec)
libgegl.gegl_operation_get_property_key.argtypes = (ct.c_char_p, ct.c_char_p, ct.c_char_p)
libgegl.gegl_operation_get_property_key.restype = ct.c_char_p
libgegl.gegl_operation_list_property_keys.argtypes = (ct.c_char_p, ct.c_char_p, ct.POINTER(ct.c_uint))
libgegl.gegl_operation_list_property_keys.restype = ct.c_void_p # ct.POINTER(ct.c_char_p)
libgegl.gegl_param_spec_get_property_key.argtypes = (ct.POINTER(GParamSpec), ct.c_char_p)
libgegl.gegl_param_spec_get_property_key.restype = ct.c_char_p
libgegl.gegl_param_spec_set_property_key.argtypes = (ct.POINTER(GParamSpec), ct.c_char_p, ct.c_char_p)
libgegl.gegl_param_spec_set_property_key.restype = None
libgegl.gegl_operation_list_keys.argtypes = (ct.c_char_p, ct.POINTER(ct.c_uint))
libgegl.gegl_operation_list_keys = ct.c_void_p # ct.POINTER(ct.c_char_p)
libgegl.gegl_operation_get_key.argtypes = (ct.c_char_p, ct.c_char_p)
libgegl.gegl_operation_get_key.restype = ct.c_char_p

# from gegl-0.4/gegl-apply.h:

libgegl.gegl_apply_op.argtypes = (GEGL.BufferPtr, ct.c_char_p, ct.c_void_p) # varargs!
libgegl.gegl_apply_op.restype = None
libgegl.gegl_filter_op.argtypes = (GEGL.BufferPtr, ct.c_char_p, ct.c_void_p) # varargs!
libgegl.gegl_filter_op.restype = GEGL.BufferPtr
libgegl.gegl_render_op.argtypes = (GEGL.BufferPtr, GEGL.BufferPtr, ct.c_char_p, ct.c_void_p) # varargs!
libgegl.gegl_render_op.restype = None
# don’t bother with xxx_valist forms

# from gegl-0.4/gegl-init.h:

libgegl.gegl_init.argtypes = (ct.POINTER(ct.c_int), ct.POINTER(ct.c_char_p))
libgegl.gegl_init.restype = None
libgegl.gegl_exit.argtypes = ()
libgegl.gegl_exit.restype = None

#+
# Higher-level stuff follows
#-

class GTYPE(enum.Enum) :
    "wrapper around some basic GType values with conversions from Python."

    # (code, ct_type)
    CHAR = (G_TYPE_CHAR, ct.c_char)
    UCHAR = (G_TYPE_UCHAR, ct.c_ubyte)
    BOOLEAN = (G_TYPE_BOOLEAN, ct.c_bool)
    INT = (G_TYPE_INT, ct.c_int)
    UINT = (G_TYPE_UINT, ct.c_uint)
    LONG = (G_TYPE_LONG, ct.c_long)
    ULONG = (G_TYPE_ULONG, ct.c_ulong)
    INT64 = (G_TYPE_INT64, ct.c_int64)
    UINT64 = (G_TYPE_UINT64, ct.c_uint64)
    FLOAT = (G_TYPE_FLOAT, ct.c_float)
    DOUBLE = (G_TYPE_DOUBLE, ct.c_double)
    POINTER = (G_TYPE_POINTER, ct.c_void_p)

    @property
    def code(self) :
        return \
            self.value[0]
    #end code

    @property
    def ct_type(self) :
        return \
            self.value[1]
    #end ct_type

    @property
    def ct_conv(self) :
        # value returned unchanged for all currently-supported types
        return \
            lambda x : x
    #end ct_conv

    def __repr__(self) :
        return \
            "%s.%s" % (type(self).__name__, self.name)
    #end __repr__

#end GTYPE
GTYPE.from_code = dict((t.code, t) for t in GTYPE)

def list_operations() :
    nr_operations = ct.c_uint()
    c_ops_list = libgegl.gegl_list_operations(ct.byref(nr_operations))
    result = list(s.decode() for s in c_ops_list[:nr_operations.value])
    libglib2.g_free(ct.cast(c_ops_list, ct.c_void_p))
    return \
        result
#end list_operations

def operation_list_properties(opname) :
    nr_props = ct.c_uint()
    c_props_list = libgegl.gegl_operation_list_properties(opname.encode(), ct.byref(nr_props))
    props = list \
      (
        {
            "name" : p.name.decode(),
            "flags" : p.flags,
            "value_type" :
                (lambda : p.value_type, lambda : GTYPE.from_code[p.value_type])
                    [p.value_type in GTYPE.from_code](),
        }
        for pp in c_props_list[:nr_props.value]
        for p in (pp.contents,)
      )
    libglib2.g_free(ct.cast(c_props_list, ct.c_void_p))
    return \
        props
#end operation_list_properties

def _gegl_op_common(funcname, fixedargs, opname, varargs) :
    "common wrapper to handle calls to the various gegl_xxx_op routines that" \
    " take variable argument lists. In each case, the variable part consists" \
    " of a sequence of name-value pairs terminated by a NULL."
    if varargs != None :
        if not isinstance(varargs, (tuple, list)) :
            raise TypeError("varargs must be list, tuple or None")
        #end if
        if (
                len(varargs) % 2 != 0
            or
                not all(i % 2 != 0 or isinstance(varargs[i], str) for i in range(len(varargs)))
        ) :
            raise TypeError("varargs must be sequence of name/value pairs")
        #end if
    else :
        varargs = ()
    #end if
    basefunc = getattr(libgegl, funcname)
      # fixed part of type info already set up
    func = type(basefunc).from_address(ct.addressof(basefunc))
      # same entry point, but can have entirely different arg/result types
    func.restype = basefunc.restype
    fixedargtypes = basefunc.argtypes
    fixedargtypes = fixedargtypes[:-1] # drop trailing null-pointer arg, re-added below
    if len(fixedargs) + 1 != len(fixedargtypes) :
        raise TypeError("expecting %d fixed args, got %d" % (len(fixedargtypes), len(fixedargs) + 1))
    #end if
    propconvert = dict \
      (
        (prop["name"], prop["value_type"])
        for prop in operation_list_properties(opname)
      )
    all_arg_types = list(fixedargtypes)
    all_args = list(fixedargs) + [opname.encode()]
    for i in range(0, len(varargs), 2) :
        propname, value = varargs[i : i + 2]
        if propname not in propconvert :
            raise KeyError("operation “%s” has no property “%s”" % (opname, propname))
        #end if
        proptype = propconvert[propname]
        if not instance(proptype, GTYPE) :
            raise TypeError("unsupported param type %d for param “%s”" % (proptype, propname))
        #end if
        c_propname = propname.encode()
        c_value = proptype.ct_conv(value)
        all_arg_types.extend(ct.c_char_p, proptype.ct_type)
        all_args.extend(c_propname, c_value)
    #end for
    all_arg_types.append(ct.c_void_p) # null to mark end of arg list
    all_args.append(None)
    func.argtypes = tuple(all_arg_types)
    return \
        func(*all_args)
#end _gegl_op_common

def apply_op(buf, opname, args = None) :
    _gegl_op_common("gegl_apply_op", (buf,), opname, args)
#end apply_op

def filter_op(srcbuf, opname, args = None) :
    return \
        _gegl_op_common("gegl_filter_op", (srcbuf,), opname, args)
#end filter_op

def render_op(srcbuf, dstbuf, opname, args = None) :
    _gegl_op_common("gegl_render_op", (srcbuf, dstbuf), opname, args)
#end render_op

def init(argv = None) :
    "wrapper around gegl_init() which lets you control what args are passed." \
    " You can pass sys.argv, or make up your own. The adjusted argument list" \
    " is returned."
    if argv == None :
        argv = ()
    #end if
    c_argc = ct.c_int(len(argv))
    c_argv = (ct.c_char_p * (len(argv) + 1))()
    for i in range(len(argv)) :
        c_argv[i] = argv[i].encode()
    #end for
    c_argv[len(argv)] = None
    libgegl.gegl_init(c_argc, c_argv)
    return \
        list(v.decode() for v in c_argv[:c_argc.value])
#end init
