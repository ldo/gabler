"""
A pure-Python wrapper for the GEGL graphics library <https://gegl.org/>
using ctypes.
"""
#+
# Copyright 2022 Lawrence D'Oliveiro <ldo@geek-central.gen.nz>.
# Licensed under the GNU Lesser General Public License v2.1 or later.
#-

# GLib/GObject 2 and related docs can be found at <https://developer-old.gnome.org/references>.

import enum
import ctypes as ct
from weakref import \
    WeakValueDictionary
import atexit

try :
    import qahirah as qah
except ImportError :
    qah = None
#end try

from babl import \
    BABL, \
    Babl

str_encode = lambda s : s.encode()
str_encode_optional = lambda s : (lambda : None, lambda : s.encode())[s != None]()
str_decode = lambda s : s.decode()

ident = lambda x : x

#+
# Begin consts and types from glib/gobject includes
#-

# from /usr/lib/«arch»/glib-2.0/include/glibconfig.h:

gsize = ct.c_ulong

# from glib-2.0/glib/gtypes.h:

GDestroyNotify = ct.CFUNCTYPE(None, ct.c_void_p)

# from glib-2.0/glib/gslist.h:

class _GSList(ct.Structure) :
    pass
_GSList._fields_ = \
    [
        ("data", ct.c_void_p),
        ("next", ct.POINTER(_GSList)),
    ]
#end _GSList

# from glib-2.0/gobject/glib-types.h:

GType = gsize

# from glib-2.0/gobject/gvaluecollector.h:

class GTypeCValue(ct.Union) :
    _fields_ = \
        [
            ("v_int", ct.c_int),
            ("v_long", ct.c_long),
            ("v_int64", ct.c_int64),
            ("v_double", ct.c_double),
            ("v_pointer", ct.c_void_p),
        ]
#end GTypeCValue

# from glib-2.0/gobject/gvalue.h:

class GValue(ct.Structure) :

    class _data_union(ct.Union) :
        _fields_ = \
            [
                ("v_int", ct.c_int),
                ("v_uint", ct.c_uint),
                ("v_long", ct.c_long),
                ("v_ulong", ct.c_ulong),
                ("v_int64", ct.c_int64),
                ("v_uint64", ct.c_uint64),
                ("v_float", ct.c_float),
                ("v_double", ct.c_double),
                ("v_pointer", ct.c_void_p),
            ]
    #end _data_union

    _fields_ = \
        [
            ("g_type", GType),
            ("data", 2 * _data_union),
        ]

#end GValue

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

class GTypeQuery(ct.Structure) :
    _fields_ = \
        [
            ("type", GType),
            ("type_name", ct.c_char_p),
            ("class_size", ct.c_uint),
            ("instance_size", ct.c_uint),
        ]
#end GTypeQuery

class GTypePlugin(ct.Structure) :
  # placeholder for objects that implement the GTypePlugin interface
  _fields_ = []
#end GTypePlugin

GBaseInitFunc = ct.CFUNCTYPE(None, ct.c_void_p)
GBaseFinalizeFunc = ct.CFUNCTYPE(None, ct.c_void_p)
GClassInitFunc = ct.CFUNCTYPE(None, ct.c_void_p, ct.c_void_p)
GClassFinalizeFunc = ct.CFUNCTYPE(None, ct.c_void_p, ct.c_void_p)
GInstanceInitFunc = ct.CFUNCTYPE(None, ct.c_void_p, ct.c_void_p)
GInterfaceInitFunc = ct.CFUNCTYPE(None, ct.c_void_p, ct.c_void_p)
GInterfaceFinalizeFunc = ct.CFUNCTYPE(None, ct.c_void_p, ct.c_void_p)
GTypeClassCacheFunc = ct.CFUNCTYPE(ct.c_bool, ct.c_void_p, ct.POINTER(GTypeClass))
GTypeInterfaceCheckFunc = ct.CFUNCTYPE(None, ct.c_void_p, ct.c_void_p)

GTypeFundamentalFlags = ct.c_uint
# values for GTypeFundamentalFlags:
G_TYPE_FLAG_CLASSED = 1 << 0
G_TYPE_FLAG_INSTANTIATABLE = 1 << 1
G_TYPE_FLAG_DERIVABLE = 1 << 2
G_TYPE_FLAG_DEEP_DERIVABLE = 1 << 3

GTypeFlags = ct.c_uint
# values for GTypeFlags:
G_TYPE_FLAG_NONE = 0 # since 2.74
G_TYPE_FLAG_ABSTRACT = 1 << 4
G_TYPE_FLAG_VALUE_ABSTRACT = 1 << 5
G_TYPE_FLAG_FINAL = 1 << 6 # since 2.70

class GTypeValueTable(ct.Structure) :
    _fields_ = \
        [
            ("value_init", ct.CFUNCTYPE(None, ct.POINTER(GValue))),
            ("value_free", ct.CFUNCTYPE(None, ct.POINTER(GValue))),
            ("value_copy", ct.CFUNCTYPE(None, ct.POINTER(GValue), ct.POINTER(GValue))),
            # varargs functionality (optional)
            ("value_peek_pointer", ct.CFUNCTYPE(ct.c_void_p, ct.POINTER(GValue))),
            ("collect_format", ct.c_char_p),
            ("collect_value",
                ct.CFUNCTYPE(ct.c_char_p,
                    ct.POINTER(GValue), ct.c_uint, ct.POINTER(GTypeCValue), ct.c_uint)
            ),
            ("lcopy_format", ct.c_char_p),
            ("lcopy_value",
                ct.CFUNCTYPE(ct.c_char_p,
                    ct.POINTER(GValue), ct.c_uint, ct.POINTER(GTypeCValue), ct.c_uint)
            ),
        ]
#end GTypeValueTable

class GTypeInfo(ct.Structure) :
    _fields_ = \
        [
            ("class_size", ct.c_uint16),

            ("base_init", GBaseInitFunc),
            ("base_finalize", GBaseFinalizeFunc),

            ("class_init", GClassInitFunc),
            ("class_finalize", GClassFinalizeFunc),
            ("class_data", ct.c_void_p),

            ("instance_size", ct.c_uint16),
            ("n_preallocs", ct.c_uint16),
            ("instance_init", GInstanceInitFunc),

            ("value_table", ct.POINTER(GTypeValueTable)),
        ]
#end GTypeInfo

class GTypeFundamentalInfo(ct.Structure) :
    _fields_ = \
        [
            ("type_flags", GTypeFundamentalFlags),
        ]
#end GTypeFundamentalInfo

class GInterfaceInfo(ct.Structure) :
    _fields_ = \
        [
            ("interface_init", GInterfaceInitFunc),
            ("interface_finalize", GInterfaceFinalizeFunc),
            ("interface_data", ct.c_void_p),
        ]
#end GInterfaceInfo

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

class GClosure(ct.Structure) :
  _fields_ = []
#end GClosure

GClosureMarshal = ct.CFUNCTYPE(None, ct.POINTER(GClosure), ct.POINTER(GValue), ct.c_uint, ct.POINTER(GValue), ct.c_void_p, ct.c_void_p)

GCallback = ct.CFUNCTYPE(None) # actually might take args and return result, depending on context
GClosureNotify = ct.CFUNCTYPE(None, ct.c_void_p, ct.c_void_p)

# from glib-2.0/glib/gquark.h

GQuark = ct.c_uint32

# from glib-2.0/gobject/gsignal.h:

GSignalFlags = ct.c_uint
# values for GSignalFlags:
G_SIGNAL_RUN_FIRST = 1 << 0
G_SIGNAL_RUN_LAST = 1 << 1
G_SIGNAL_RUN_CLEANUP = 1 << 2
G_SIGNAL_NO_RECURSE = 1 << 3
G_SIGNAL_DETAILED = 1 << 4
G_SIGNAL_ACTION = 1 << 5
G_SIGNAL_NO_HOOKS = 1 << 6
G_SIGNAL_MUST_COLLECT = 1 << 7
G_SIGNAL_DEPRECATED = 1 << 8
G_SIGNAL_ACCUMULATOR_FIRST_RUN = 1 << 17

GConnectFlags = ct.c_uint
# values for GConnectFlags:
G_CONNECT_AFTER = 1 << 0
G_CONNECT_SWAPPED = 1 << 1

GSignalMatchType = ct.c_uint
# values for GSignalMatchType:
G_SIGNAL_MATCH_ID = 1 << 0
G_SIGNAL_MATCH_DETAIL = 1 << 1
G_SIGNAL_MATCH_CLOSURE = 1 << 2
G_SIGNAL_MATCH_FUNC = 1 << 3
G_SIGNAL_MATCH_DATA = 1 << 4
G_SIGNAL_MATCH_UNBLOCKED = 1 << 5

GSignalCMarshaller = GClosureMarshal

class GSignalInvocationHint(ct.Structure) :
    _fields_ = \
        [
            ("signal_id", ct.c_uint),
            ("detail", GQuark),
            ("run_type", GSignalFlags),
        ]
#end GSignalInvocationHint

GSignalAccumulator = ct.CFUNCTYPE(ct.c_bool,
    ct.POINTER(GSignalInvocationHint), ct.POINTER(GValue), ct.POINTER(GValue), ct.c_void_p)

#+
# End of consts and types from glib/gobject includes
#
# Begin consts and types from GEGL-specific includes
#-

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

    # from gegl-0.4/operation/gegl-operation.h:

    class OperationClass(ct.Structure) :
        _fields_ = [] # TODO
    #end OperationClass

#end GEGL

libglib2 = ct.cdll.LoadLibrary("libglib-2.0.so.0")
libgobject2 = ct.cdll.LoadLibrary("libgobject-2.0.so.0")
libgegl = ct.cdll.LoadLibrary("libgegl-0.4.so.0")

#+
# Routine arg/result types, GLib/GObject-specific
#-

# from glib-2.0/glib/gmem.h:

libglib2.g_malloc.argtypes = (gsize,)
libglib2.g_malloc.restype = ct.c_void_p
libglib2.g_free.argtypes = (ct.c_void_p,)
libglib2.g_free.restype = None

def g_new(c_type, nr_elts) :
    "approximate equivalent to g_new() macro in glib-2.0/glib/gmem.h."
    return \
        libglib2.g_malloc(ct.sizeof(c_type * nr_elts))
#end g_new

# from glib-2.0/glib/gstrfuncs.h:

libglib2.g_strfreev.argtypes = (ct.POINTER(ct.c_char_p),)
libglib2.g_strfreev.restype = None

# from glib-2.0/glib/gslist.h:

libglib2.g_slist_free.argtypes = (ct.c_void_p,)
libglib2.g_slist_free.restype = None

# from glib-2.0/gobject/gtype.h:

libgobject2.g_type_register_static.argtypes = (GType, ct.c_char_p, ct.POINTER(GTypeInfo), GTypeFlags)
libgobject2.g_type_register_static.restype = GType
libgobject2.g_type_register_static_simple.argtypes = (GType, ct.c_char_p, ct.c_uint, GClassInitFunc, ct.c_uint, GInstanceInitFunc, GTypeFlags)
libgobject2.g_type_register_static_simple.restype = GType
libgobject2.g_type_register_dynamic.argtypes = (GType, ct.c_char_p, ct.POINTER(GTypePlugin), GTypeFlags)
libgobject2.g_type_register_dynamic.restype = GType
libgobject2.g_type_register_fundamental.argtypes = (GType, ct.c_char_p, ct.POINTER(GTypeInfo), ct.POINTER(GTypeFundamentalInfo), GTypeFlags)
libgobject2.g_type_register_fundamental.restype = GType
libgobject2.g_type_from_name.argtypes = (ct.c_char_p,)
libgobject2.g_type_from_name.restype = GType
libgobject2.g_type_query.argtypes = (GType, ct.POINTER(GTypeQuery))
libgobject2.g_type_query.restype = None
libgobject2.g_type_check_value_holds.argtypes = (ct.POINTER(GValue), GType)
libgobject2.g_type_check_value_holds.restype = ct.c_bool

# from glib-2.0/glib/gvalue.h:

libgobject2.g_value_init.argtypes = (ct.POINTER(GValue), GType)
libgobject2.g_value_init.restype = ct.POINTER(GValue)
libgobject2.g_value_copy.argtypes = (ct.POINTER(GValue), ct.POINTER(GValue))
libgobject2.g_value_copy.restype = None
libgobject2.g_value_reset.argtypes = (ct.POINTER(GValue),)
libgobject2.g_value_reset.restype = ct.POINTER(GValue)
libgobject2.g_value_unset.argtypes = (ct.POINTER(GValue),)
libgobject2.g_value_unset.restype = None
libgobject2.g_value_fits_pointer.argtypes = (ct.POINTER(GValue),)
libgobject2.g_value_fits_pointer.restype = ct.c_bool
libgobject2.g_value_peek_pointer.argtypes = (ct.POINTER(GValue),)
libgobject2.g_value_peek_pointer.restype = ct.c_void_p

# from glib-2.0/glib/gvaluetypes.h:

libgobject2.g_value_set_uchar.argtypes = (ct.POINTER(GValue), ct.c_ubyte)
libgobject2.g_value_set_uchar.restype = None
libgobject2.g_value_get_uchar.argtypes = (ct.POINTER(GValue),)
libgobject2.g_value_get_uchar.restype = ct.c_ubyte
libgobject2.g_value_set_boolean.argtypes = (ct.POINTER(GValue), ct.c_bool)
libgobject2.g_value_set_boolean.restype = None
libgobject2.g_value_get_boolean.argtypes = (ct.POINTER(GValue),)
libgobject2.g_value_get_boolean.restype = ct.c_bool
libgobject2.g_value_set_int.argtypes = (ct.POINTER(GValue), ct.c_int)
libgobject2.g_value_set_int.restype = None
libgobject2.g_value_get_int.argtypes = (ct.POINTER(GValue),)
libgobject2.g_value_get_int.restype = ct.c_int
libgobject2.g_value_set_uint.argtypes = (ct.POINTER(GValue), ct.c_uint)
libgobject2.g_value_set_uint.restype = None
libgobject2.g_value_get_uint.argtypes = (ct.POINTER(GValue),)
libgobject2.g_value_get_uint.restype = ct.c_uint
libgobject2.g_value_set_long.argtypes = (ct.POINTER(GValue), ct.c_long)
libgobject2.g_value_set_long.restype = None
libgobject2.g_value_get_long.argtypes = (ct.POINTER(GValue),)
libgobject2.g_value_get_long.restype = ct.c_long
libgobject2.g_value_set_ulong.argtypes = (ct.POINTER(GValue), ct.c_ulong)
libgobject2.g_value_set_ulong.restype = None
libgobject2.g_value_get_ulong.argtypes = (ct.POINTER(GValue),)
libgobject2.g_value_get_ulong.restype = ct.c_ulong
libgobject2.g_value_set_int64.argtypes = (ct.POINTER(GValue), ct.c_int64)
libgobject2.g_value_set_int64.restype = None
libgobject2.g_value_get_int64.argtypes = (ct.POINTER(GValue),)
libgobject2.g_value_get_int64.restype = ct.c_int64
libgobject2.g_value_set_uint64.argtypes = (ct.POINTER(GValue), ct.c_uint64)
libgobject2.g_value_set_uint64.restype = None
libgobject2.g_value_get_uint64.argtypes = (ct.POINTER(GValue),)
libgobject2.g_value_get_uint64.restype = ct.c_uint64
libgobject2.g_value_set_float.argtypes = (ct.POINTER(GValue), ct.c_float)
libgobject2.g_value_set_float.restype = None
libgobject2.g_value_get_float.argtypes = (ct.POINTER(GValue),)
libgobject2.g_value_get_float.restype = ct.c_float
libgobject2.g_value_set_double.argtypes = (ct.POINTER(GValue), ct.c_double)
libgobject2.g_value_set_double.restype = None
libgobject2.g_value_get_double.argtypes = (ct.POINTER(GValue),)
libgobject2.g_value_get_double.restype = ct.c_double
libgobject2.g_value_set_string.argtypes = (ct.POINTER(GValue), ct.c_char_p)
libgobject2.g_value_set_string.restype = None
libgobject2.g_value_set_static_string.argtypes = (ct.POINTER(GValue), ct.c_char_p)
libgobject2.g_value_set_static_string.restype = None
libgobject2.g_value_set_interned_string.argtypes = (ct.POINTER(GValue), ct.c_char_p)
libgobject2.g_value_set_interned_string.restype = None
libgobject2.g_value_get_string.argtypes = (ct.POINTER(GValue),)
libgobject2.g_value_get_string.restype = ct.c_char_p
libgobject2.g_value_dup_string.argtypes = (ct.POINTER(GValue),)
libgobject2.g_value_dup_string.restype = ct.c_char_p
libgobject2.g_value_set_pointer.argtypes = (ct.POINTER(GValue), ct.c_void_p)
libgobject2.g_value_set_pointer.restype = None
libgobject2.g_value_get_pointer.argtypes = (ct.POINTER(GValue),)
libgobject2.g_value_get_pointer.restype = ct.c_void_p
libgobject2.g_gtype_get_type.argtypes = ()
libgobject2.g_gtype_get_type.restype = GType
libgobject2.g_value_set_gtype.argtypes = (ct.POINTER(GValue), GType)
libgobject2.g_value_set_gtype.restype = None
libgobject2.g_value_get_gtype.argtypes = (ct.POINTER(GValue),)
libgobject2.g_value_get_gtype.restype = GType

# from glib-2.0/gobject/gparam.h:

libgobject2.g_param_spec_ref.argtypes = (ct.POINTER(GParamSpec),)
libgobject2.g_param_spec_ref.restype = ct.POINTER(GParamSpec)
libgobject2.g_param_spec_unref.argtypes = (ct.POINTER(GParamSpec),)
libgobject2.g_param_spec_unref.restype = None

# from glib-2.0/gobject/gobject.h:

libgobject2.g_object_setv.argtypes = (ct.c_void_p, ct.c_uint, ct.POINTER(ct.c_char_p), ct.POINTER(GValue))
libgobject2.g_object_setv.restype = None
libgobject2.g_object_getv.argtypes = (ct.c_void_p, ct.c_uint, ct.POINTER(ct.c_char_p), ct.POINTER(GValue))
libgobject2.g_object_getv.restype = None
libgobject2.g_object_ref.argtypes = (ct.c_void_p,)
libgobject2.g_object_ref.restype = ct.c_void_p
libgobject2.g_object_unref.argtypes = (ct.c_void_p,)
libgobject2.g_object_unref.restype = None
libgobject2.g_object_get_data.argtypes = (ct.c_void_p, ct.c_char_p)
libgobject2.g_object_get_data.restype = ct.c_void_p
libgobject2.g_object_set_data.argtypes = (ct.c_void_p, ct.c_char_p, ct.c_void_p)
libgobject2.g_object_set_data.restype = None
libgobject2.g_object_set_data_full.argtypes = (ct.c_void_p, ct.c_char_p, ct.c_void_p, GDestroyNotify)
libgobject2.g_object_set_data_full.restype = None

# from glib-2.0/gobject/gsignal.h:

libgobject2.g_signal_newv.restype = ct.c_uint
libgobject2.g_signal_newv.argtypes = \
    (ct.c_char_p, GType, GSignalFlags, ct.POINTER(GClosure), GSignalAccumulator,
    ct.c_void_p, GSignalCMarshaller, GType, ct.c_uint, ct.POINTER(GType))
libgobject2.g_signal_connect_data.argtypes = (ct.c_void_p, ct.c_char_p, ct.c_void_p, ct.c_void_p, ct.c_void_p, GConnectFlags)
libgobject2.g_signal_connect_data.restype = ct.c_ulong

#+
# Routine arg/result types, GEGL-specific
#-

# from gegl-0.4/gegl-color.h:

libgegl.gegl_color_new.argtypes = (ct.c_char_p,)
libgegl.gegl_color_new.restype = GEGL.ColourPtr
libgegl.gegl_color_duplicate.argtypes = (GEGL.ColourPtr,)
libgegl.gegl_color_duplicate.restype = GEGL.ColourPtr
libgegl.gegl_color_get_rgba.argtypes = (GEGL.ColourPtr, ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double))
libgegl.gegl_color_get_rgba.restype = None
libgegl.gegl_color_set_rgba.argtypes = (GEGL.ColourPtr, ct.c_double, ct.c_double, ct.c_double, ct.c_double)
libgegl.gegl_color_set_rgba.restype = None
libgegl.gegl_color_set_pixel.argtypes = (GEGL.ColourPtr, BABL.Ptr, ct.c_void_p)
libgegl.gegl_color_set_pixel.restype = None
libgegl.gegl_color_get_pixel.argtypes = (GEGL.ColourPtr, BABL.Ptr, ct.c_void_p)
libgegl.gegl_color_get_pixel.restype = None
libgegl.gegl_param_spec_color.argtypes = (ct.c_char_p, ct.c_char_p, ct.c_char_p, GEGL.ColourPtr, GParamFlags)
libgegl.gegl_param_spec_color.restype = ct.POINTER(GParamSpec)
libgegl.gegl_param_spec_color_from_string.argtypes = (ct.c_char_p, ct.c_char_p, ct.c_char_p, ct.c_char_p, GParamFlags)
libgegl.gegl_param_spec_color_from_string.restype = ct.POINTER(GParamSpec)
libgegl.gegl_param_spec_color_get_default.argtypes = (ct.POINTER(GParamSpec),)
libgegl.gegl_param_spec_color_get_default.restype = GEGL.ColourPtr
libgegl.gegl_color_get_format.argtypes = (GEGL.ColourPtr,)
libgegl.gegl_color_get_format.restype = BABL.Ptr

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
libgegl.gegl_operation_list_property_keys.restype = ct.POINTER(ct.c_char_p)
libgegl.gegl_param_spec_get_property_key.argtypes = (ct.POINTER(GParamSpec), ct.c_char_p)
libgegl.gegl_param_spec_get_property_key.restype = ct.c_char_p
libgegl.gegl_param_spec_set_property_key.argtypes = (ct.POINTER(GParamSpec), ct.c_char_p, ct.c_char_p)
libgegl.gegl_param_spec_set_property_key.restype = None
libgegl.gegl_operation_list_keys.argtypes = (ct.c_char_p, ct.POINTER(ct.c_uint))
libgegl.gegl_operation_list_keys.restype = ct.POINTER(ct.c_char_p)
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

# from gegl-0.4/gegl-node.h:

libgegl.gegl_node_new.argtypes = ()
libgegl.gegl_node_new.restype = ct.c_void_p
libgegl.gegl_node_new_child.argtypes = (ct.c_void_p, ct.c_void_p) # varargs!
libgegl.gegl_node_new_child.restype = ct.c_void_p
libgegl.gegl_node_connect_from.argtypes = (ct.c_void_p, ct.c_char_p, ct.c_void_p, ct.c_char_p)
libgegl.gegl_node_connect_from.restype = ct.c_bool
libgegl.gegl_node_connect_to.argtypes = (ct.c_void_p, ct.c_char_p, ct.c_void_p, ct.c_char_p)
libgegl.gegl_node_connect_to.restype = ct.c_bool
libgegl.gegl_node_link.restype = None
libgegl.gegl_node_link.argtypes = (ct.c_void_p, ct.c_void_p)
libgegl.gegl_node_link_many.restype = None
libgegl.gegl_node_link_many.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_void_p) # varargs!
libgegl.gegl_node_disconnect.restype = ct.c_bool
libgegl.gegl_node_disconnect.argtypes = (ct.c_void_p, ct.c_char_p)
libgegl.gegl_node_set.restype = None
libgegl.gegl_node_set.argtypes = (ct.c_void_p, ct.c_void_p) # varargs!
# don’t try using this
#libgegl.gegl_node_get.restype = None
#libgegl.gegl_node_get.argtypes = (ct.c_void_p, ct.c_void_p) # varargs!
libgegl.gegl_node_blit.restype = None
libgegl.gegl_node_blit.argtypes = (ct.c_void_p, ct.c_double, ct.POINTER(GEGL.Rectangle), BABL.Ptr, ct.c_void_p,  ct.c_int, GEGL.BlitFlags)
libgegl.gegl_node_blit_buffer.restype = None
libgegl.gegl_node_blit_buffer.argtypes = (ct.c_void_p, ct.c_void_p, ct.POINTER(GEGL.Rectangle), ct.c_int, GEGL.AbyssPolicy)
libgegl.gegl_node_process.restype = None
libgegl.gegl_node_process.argtypes = (ct.c_void_p,)
libgegl.gegl_node_add_child.restype = ct.c_void_p
libgegl.gegl_node_add_child.argtypes = (ct.c_void_p, ct.c_void_p)
libgegl.gegl_node_remove_child.restype = ct.c_void_p
libgegl.gegl_node_remove_child.argtypes = (ct.c_void_p, ct.c_void_p)
libgegl.gegl_node_get_parent.restype = ct.c_void_p
libgegl.gegl_node_get_parent.argtypes = (ct.c_void_p,)
libgegl.gegl_node_detect.restype = ct.c_void_p
libgegl.gegl_node_detect.argtypes = (ct.c_void_p, ct.c_int, ct.c_int)
libgegl.gegl_node_find_property.restype = ct.c_void_p # ct.POINTER(GParamSpec)
libgegl.gegl_node_find_property.argtypes = (ct.c_void_p, ct.c_char_p)
libgegl.gegl_node_get_bounding_box.argtypes = (ct.c_void_p,)
libgegl.gegl_node_get_bounding_box.restype = GEGL.Rectangle
libgegl.gegl_node_get_children.restype = ct.c_void_p
libgegl.gegl_node_get_children.argtypes = (ct.c_void_p,)
libgegl.gegl_node_get_consumers.restype = ct.c_int
libgegl.gegl_node_get_consumers.argtypes = (ct.c_void_p, ct.c_char_p, ct.POINTER(ct.POINTER(ct.c_void_p)), ct.POINTER(ct.POINTER(ct.c_char_p)))
libgegl.gegl_node_get_input_proxy.restype = ct.c_void_p
libgegl.gegl_node_get_input_proxy.argtypes = (ct.c_void_p, ct.c_char_p)
libgegl.gegl_node_get_operation.restype = ct.c_char_p
libgegl.gegl_node_get_operation.argtypes = (ct.c_void_p,)
libgegl.gegl_node_get_gegl_operation.restype = ct.c_void_p
libgegl.gegl_node_get_gegl_operation.argtypes = (ct.c_void_p,)
libgegl.gegl_node_get_output_proxy.restype = ct.c_void_p
libgegl.gegl_node_get_output_proxy.argtypes = (ct.c_void_p, ct.c_char_p)
libgegl.gegl_node_get_producer.restype = ct.c_void_p
libgegl.gegl_node_get_producer.argtypes = (ct.c_void_p, ct.c_char_p, ct.POINTER(ct.c_char_p))
libgegl.gegl_node_has_pad.restype = ct.c_bool
libgegl.gegl_node_has_pad.argtypes = (ct.c_void_p, ct.c_char_p)
libgegl.gegl_node_list_input_pads.restype = ct.POINTER(ct.c_char_p)
libgegl.gegl_node_list_input_pads.argtypes = (ct.c_void_p,)
libgegl.gegl_node_list_output_pads.restype = ct.POINTER(ct.c_char_p)
libgegl.gegl_node_list_output_pads.argtypes = (ct.c_void_p,)
libgegl.gegl_node_create_child.restype = ct.c_void_p
libgegl.gegl_node_create_child.argtypes = (ct.c_void_p, ct.c_char_p)
libgegl.gegl_node_get_property.restype = None
libgegl.gegl_node_get_property.argtypes = (ct.c_void_p, ct.c_char_p, ct.POINTER(GValue))
libgegl.gegl_node_set_property.restype = None
libgegl.gegl_node_set_property.argtypes = (ct.c_void_p, ct.c_char_p, ct.POINTER(GValue))
libgegl.gegl_node_new_from_xml.restype = ct.c_void_p
libgegl.gegl_node_new_from_xml.argtypes = (ct.c_char_p, ct.c_char_p)
libgegl.gegl_node_new_from_file.restype = ct.c_void_p
libgegl.gegl_node_new_from_file.argtypes = (ct.c_char_p,)
libgegl.gegl_node_to_xml.restype = ct.c_char_p
libgegl.gegl_node_to_xml.argtypes = (ct.c_void_p, ct.c_char_p)
libgegl.gegl_node_to_xml_full.restype = ct.c_char_p
libgegl.gegl_node_to_xml_full.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_char_p)
libgegl.gegl_node_get_passthrough.restype = ct.c_bool
libgegl.gegl_node_get_passthrough.argtypes = (ct.c_void_p,)
libgegl.gegl_node_set_passthrough.restype = None
libgegl.gegl_node_set_passthrough.argtypes = (ct.c_void_p,)
libgegl.gegl_node_is_graph.restype = ct.c_bool
libgegl.gegl_node_is_graph.argtypes = (ct.c_void_p,)
libgegl.gegl_node_progress.restype = None
libgegl.gegl_node_progress.argtypes = (ct.c_void_p, ct.c_double, ct.c_char_p)
libgegl.gegl_operation_get_op_version.restype = ct.c_char_p
libgegl.gegl_operation_get_op_version.argtypes = (ct.c_char_p,)
# don’t bother with xxx_valist forms

# from gegl-0.4/operation/gegl-operation.h:
libgegl.gegl_operation_get_invalidated_by_change.restype = GEGL.Rectangle
libgegl.gegl_operation_get_invalidated_by_change.argtypes = (ct.c_void_p, ct.c_char_p, ct.POINTER(GEGL.Rectangle))
libgegl.gegl_operation_get_bounding_box.restype = GEGL.Rectangle
libgegl.gegl_operation_get_bounding_box.argtypes = (ct.c_void_p,)
libgegl.gegl_operation_source_get_bounding_box.restype = ct.POINTER(GEGL.Rectangle)
libgegl.gegl_operation_source_get_bounding_box.argtypes = (ct.c_void_p, ct.c_char_p)
libgegl.gegl_operation_get_cached_region.restype = GEGL.Rectangle
libgegl.gegl_operation_get_cached_region.argtypes = (ct.c_void_p, ct.POINTER(GEGL.Rectangle))
libgegl.gegl_operation_get_required_for_output.restype = GEGL.Rectangle
libgegl.gegl_operation_get_required_for_output.argtypes = (ct.c_void_p, ct.c_char_p, ct.POINTER(GEGL.Rectangle))
libgegl.gegl_operation_detect.restype = ct.c_void_p
libgegl.gegl_operation_detect.argtypes = (ct.c_void_p, ct.c_int, ct.c_int)
libgegl.gegl_operation_attach.restype = None
libgegl.gegl_operation_attach.argtypes = (ct.c_void_p, ct.c_void_p)
libgegl.gegl_operation_prepare.restype = None
libgegl.gegl_operation_prepare.argtypes = (ct.c_void_p,)
libgegl.gegl_operation_process.restype = ct.c_bool
libgegl.gegl_operation_process.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_char_p, ct.POINTER(GEGL.Rectangle), ct.c_int)
libgegl.gegl_operation_create_pad.restype = None
libgegl.gegl_operation_create_pad.argtypes = (ct.c_void_p, ct.POINTER(GParamSpec))
libgegl.gegl_operation_set_format.restype = None
libgegl.gegl_operation_set_format.argtypes = (ct.c_void_p, ct.c_char_p, BABL.Ptr)
libgegl.gegl_operation_get_format.restype = BABL.Ptr
libgegl.gegl_operation_get_format.argtypes = (ct.c_void_p, ct.c_char_p)
libgegl.gegl_operation_get_name.restype = ct.c_char_p
libgegl.gegl_operation_get_name.argtypes = (ct.c_void_p,)
libgegl.gegl_operation_get_source_format.restype = BABL.Ptr
libgegl.gegl_operation_get_source_format.argtypes = (ct.c_void_p, ct.c_char_p)
libgegl.gegl_operation_get_source_node.restype = ct.c_void_p
libgegl.gegl_operation_get_source_node.argtypes = (ct.c_void_p, ct.c_char_p)
libgegl.gegl_operation_class_set_key.restype = None
libgegl.gegl_operation_class_set_key.argtypes = (ct.POINTER(GEGL.OperationClass), ct.c_char_p, ct.c_char_p)
libgegl.gegl_operation_class_get_key.restype = ct.c_char_p
libgegl.gegl_operation_class_get_key.argtypes = (ct.POINTER(GEGL.OperationClass), ct.c_char_p)
libgegl.gegl_operation_class_set_keys.restype = None
libgegl.gegl_operation_class_set_keys.argtypes = (ct.POINTER(GEGL.OperationClass), ct.c_void_p) # varargs!
libgegl.gegl_operation_set_key.restype = None
libgegl.gegl_operation_set_key.argtypes = (ct.POINTER(ct.c_char_p), ct.c_char_p, ct.c_char_p)
libgegl.gegl_operation_use_opencl.restype = ct.c_bool
libgegl.gegl_operation_use_opencl.argtypes = (ct.c_void_p,)
libgegl.gegl_operation_use_threading.restype = ct.c_bool
libgegl.gegl_operation_use_threading.argtypes = (ct.c_void_p, ct.POINTER(GEGL.Rectangle))
libgegl.gegl_operation_get_pixels_per_thread.restype = ct.c_double
libgegl.gegl_operation_get_pixels_per_thread.argtypes = (ct.c_void_p,)
libgegl.gegl_operation_invalidate.restype = None
libgegl.gegl_operation_invalidate.argtypes = (ct.c_void_p, ct.POINTER(GEGL.Rectangle), ct.c_bool)
libgegl.gegl_operation_cl_set_kernel_args.restype = ct.c_bool
libgegl.gegl_operation_cl_set_kernel_args.argtypes = (ct.c_void_p, ct.c_void_p, ct.POINTER(ct.c_int), ct.POINTER(ct.c_int))
# gegl_can_do_inplace_processing marked as “should not be used externally”
# gegl_object_set_has_forked, gegl_object_get_has_forked, gegl_temp_buffer
# seem to be for plugin use
libgegl.gegl_operation_progress.restype = None
libgegl.gegl_operation_progress.argtypes = (ct.c_void_p, ct.c_double, ct.c_char_p)
libgegl.gegl_operation_get_source_space.restype = BABL.Ptr
libgegl.gegl_operation_get_source_space.argtypes = (ct.c_void_p, ct.c_char_p)

# from gegl-0.4/operation/gegl-operation-context.h:

libgegl.gegl_operation_context_get_target.restype = ct.c_void_p
libgegl.gegl_operation_context_get_target.argtypes = (ct.c_void_p, ct.c_char_p)
# gegl_operation_context_get_source deprecated
libgegl.gegl_operation_context_dup_object.restype = ct.c_void_p
libgegl.gegl_operation_context_dup_object.argtypes = (ct.c_void_p, ct.c_char_p)
libgegl.gegl_operation_context_get_object.restype = ct.c_void_p
libgegl.gegl_operation_context_get_object.argtypes = (ct.c_void_p, ct.c_char_p)
libgegl.gegl_operation_context_set_object.restype = None
libgegl.gegl_operation_context_set_object.argtypes = (ct.c_void_p, ct.c_char_p, ct.c_void_p)
libgegl.gegl_operation_context_take_object.restype = None
libgegl.gegl_operation_context_take_object.argtypes = (ct.c_void_p, ct.c_char_p, ct.c_void_p)
libgegl.gegl_operation_context_purge.restype = None
libgegl.gegl_operation_context_purge.argtypes = (ct.c_void_p,)
libgegl.gegl_operation_context_get_level.restype = ct.c_int
libgegl.gegl_operation_context_get_level.argtypes = (ct.c_void_p,)
# gegl_operation_context_get_output_maybe_in_place,
# gegl_operation_context_dup_input_maybe_copy, gegl_operation_context_node_get_context
# documented as for internal use only

# from gegl-0.4/gegl-init.h:

libgegl.gegl_init.argtypes = (ct.POINTER(ct.c_int), ct.POINTER(ct.c_char_p))
libgegl.gegl_init.restype = None
libgegl.gegl_exit.argtypes = ()
libgegl.gegl_exit.restype = None

#+
# Higher-level stuff follows
#-

class GTYPE(enum.Enum) :
    "wrapper around some basic GType values with conversions to/from Python."

    # (code, ct_type, ct_conv, gvalue_field)
    CHAR = (G_TYPE_CHAR, ct.c_char, ident, "v_uint")
    UCHAR = (G_TYPE_UCHAR, ct.c_ubyte, ident, "v_uint")
    BOOLEAN = (G_TYPE_BOOLEAN, ct.c_bool, ident, "v_uint")
    INT = (G_TYPE_INT, ct.c_int, ident, "v_int")
    UINT = (G_TYPE_UINT, ct.c_uint, ident, "v_uint")
    LONG = (G_TYPE_LONG, ct.c_long, ident, "v_long")
    ULONG = (G_TYPE_ULONG, ct.c_ulong, ident, "v_ulong")
    INT64 = (G_TYPE_INT64, ct.c_int64, ident, "v_int64")
    UINT64 = (G_TYPE_UINT64, ct.c_uint64, ident, "v_uint64")
    FLOAT = (G_TYPE_FLOAT, ct.c_float, ident, "v_float")
    DOUBLE = (G_TYPE_DOUBLE, ct.c_double, ident, "v_double")
    STRING = (G_TYPE_STRING, ct.c_char_p, str_encode, "v_pointer")
    POINTER = (G_TYPE_POINTER, ct.c_void_p, ident, "v_pointer")

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
        return \
            self.value[2]
    #end ct_conv

    @property
    def gvalue_field(self) :
        return \
            self.value[3]
    #end gvalue_field

    def __repr__(self) :
        return \
            "%s.%s" % (type(self).__name__, self.name)
    #end __repr__

#end GTYPE
GTYPE.from_code = dict((t.code, t) for t in GTYPE)

dynamic_types_by_name = {}
  # filled in by _init_dynamic_types() (below)
dynamic_types_by_id = {}

def _find_dynamic_conv(typeid, parmname) :
    if typeid in dynamic_types_by_id :
        entry = dynamic_types_by_id[typeid]
    else :
        info = GTypeQuery()
        libgobject2.g_type_query(typeid, ct.byref(info))
        if info.type != 0 :
            type_name = str_decode(info.type_name)
            if type_name in dynamic_types_by_name :
                entry = dynamic_types_by_name[type_name]
                entry["typeid"] = typeid
            else :
                entry = {"name" : type_name}
                # no conv, just let caller pass raw pointer
            #end if
            dynamic_types_by_id[typeid] = entry
        else :
            # raise TypeError("unknown type ID %d for param “%s”" % (typeid, parmname))
            entry = {"name" : "?"}
            # again no conv, just let caller pass raw pointer
        #end if
    #end if
    return \
        entry
#end _find_dynamic_conv

def list_operations() :
    nr_operations = ct.c_uint()
    c_ops_list = libgegl.gegl_list_operations(ct.byref(nr_operations))
    result = list(str_decode(s) for s in c_ops_list[:nr_operations.value])
    libglib2.g_free(ct.cast(c_ops_list, ct.c_void_p))
    return \
        result
#end list_operations

def operation_list_properties(opname) :
    nr_props = ct.c_uint()
    c_props_list = libgegl.gegl_operation_list_properties(str_encode(opname), ct.byref(nr_props))
    props = list \
      (
        {
            "name" : str_decode(p.name),
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

def operation_list_keys(opname) :
    nr_keys = ct.c_uint()
    c_keys_list = libgegl.gegl_operation_list_keys(str_encode(opname), ct.byref(nr_keys))
    keys = list(str_decode(k) for k in c_keys_list[:nr_keys.value])
    libglib2.g_free(ct.cast(c_keys_list, ct.c_void_p))
    return \
        keys
#end operation_list_keys

def operation_get_key(opname, keyname) :
    val = libgegl.gegl_operation_get_key(str_encode(opname), str_encode(keyname))
    if val != None :
        try :
            val = str_decode(val)
        except UnicodeDecodeError :
            pass # leave as bytes
            # it seems only the “operation-class” key has this trouble
        #end try
    #end if
    return \
        val
#end operation_get_key

def operation_list_property_keys(opname, propname) :
    nr_keys = ct.c_uint()
    c_keys_list = libgegl.gegl_operation_list_property_keys(str_encode(opname), str_encode(propname), ct.byref(nr_keys))
    keys = list(str_decode(k) for k in c_keys_list[:nr_keys.value])
    libglib2.g_free(ct.cast(c_keys_list, ct.c_void_p))
    return \
        keys
#end operation_list_property_keys

def operation_get_property_key(opname, propname, keyname) :
    val = libgegl.gegl_operation_get_property_key(str_encode(opname), str_encode(propname), str_encode(keyname))
    if val != None :
        val = str_decode(val)
    #end if
    return \
        val
#end operation_get_property_key

def _gegl_op_common(funcname, fixedargs, opname, varargs) :
    "common wrapper to handle calls to the various gegl_xxx_op routines that" \
    " take variable argument lists. In each case, the variable part consists" \
    " of a sequence of name-value pairs terminated by a NULL."
    if varargs != None :
        if isinstance(varargs, dict) :
            if not all(isinstance(k, str) for k in varargs) :
                raise TypeError("varargs keys must be strings")
            #end if
            varargs = tuple((k, v) for k, v in varargs.items())
        elif isinstance(varargs, (tuple, list)) :
            if not all \
              (
                isinstance(a, (tuple, list)) and len(a) == 2 and isinstance(a[0], str)
                for a in varargs
              ) \
            :
                raise TypeError("varargs must be sequence of name/value pairs")
            #end if
        else :
            raise TypeError("varargs must be dict, list, tuple or None")
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
        raise TypeError \
          (
                "expecting %d fixed args, got %d"
            %
                (len(fixedargtypes), len(fixedargs) + 1)
          )
    #end if
    propconvert = dict \
      (
        (prop["name"], prop["value_type"])
        for prop in operation_list_properties(opname)
      )
    all_arg_types = list(fixedargtypes)
    all_args = list(fixedargs) + [str_encode(opname)]
    for propname, value in varargs :
        if propname not in propconvert :
            raise KeyError("operation “%s” has no property “%s”" % (opname, propname))
        #end if
        proptype = propconvert[propname]
        if isinstance(proptype, GTYPE) :
            c_value = proptype.ct_conv(value)
            c_type = proptype.ct_type
        else :
            assert isinstance(proptype, int)
            entry = _find_dynamic_conv(proptype, propname)
            c_value = entry.get("conv", ident)(value)
            c_type = ct.c_void_p
        #end if
        c_propname = str_encode(propname)
        all_args.extend((c_propname, c_value))
        all_arg_types.extend((ct.c_char_p, c_type))
    #end for
    all_arg_types.append(ct.c_void_p) # null to mark end of arg list
    all_args.append(None)
    func.argtypes = tuple(all_arg_types)
    return \
        func(*all_args)
#end _gegl_op_common

def apply_op(buf, opname, args = None) :
    "applies a GEGL operation to a buffer in-place."
    _gegl_op_common("gegl_apply_op", (buf,), opname, args)
#end apply_op

def filter_op(srcbuf, opname, args = None) :
    "applies a GEGL operation on pixels copied from srcbuf to" \
    " a new buffer which is created and returned."
    return \
        _gegl_op_common("gegl_filter_op", (srcbuf,), opname, args)
#end filter_op

def render_op(srcbuf, dstbuf, opname, args = None) :
    "applies a GEGL operation on srcbuf and stores the result in" \
    " the provided dstbuf."
    _gegl_op_common("gegl_render_op", (srcbuf, dstbuf), opname, args)
#end render_op

class Buffer :
    "wrapper around a GEGL buffer object. Do not instantiate directly:" \
    " get from create method."

    __slots__ = ("_geglobj", "__weakref__")

    _instances = WeakValueDictionary()

    def __new__(celf, _geglobj) :
        self = celf._instances.get(_geglobj)
        if self == None :
            self = super().__new__(celf)
            self._geglobj = _geglobj
            celf._instances[_geglobj] = self
        else :
            # don’t need extra reference generated by caller
            libgobject2.g_object_unref(_geglobj)
        #end if
        return \
            self
    #end __new__

    def __del__(self) :
        if self._geglobj != None :
            libgobject2.g_object_unref(self._geglobj)
            self._geglobj = None
        #end if
    #end __del__

    @classmethod
    def create(celf, extent, format) :
        if not isinstance(extent, GEGL.Rectangle) or not isinstance(format, Babl) :
            raise TypeError("extent must be a GEGL.Rectangle and format must be a Babl object")
        #end if
        return \
            celf(libgegl.gegl_buffer_new(ct.byref(extent), format._bablobj))
    #end create

    def apply_op(self, opname, args = None) :
        "applies a GEGL operation to this buffer in-place."
        apply_op(self._geglobj, opname, args)
    #end apply_op

    def filter_op(self, opname, args = None) :
        "applies a GEGL operation on pixels copied from this buffer" \
        " to a new buffer which is created and returned."
        return \
            type(self)(filter_op(self._geglobj, opname, args))
    #end filter_op

    def render_op(self, dstbuf, opname, args = None) :
        if not isinstance(dstbuf, Buffer) :
            raise TypeError("dstbuf must be a Buffer")
        #end if
        render_op(self._geglobj, dstbuf._geglobj, opname, args)
    #end render_op

#end Buffer

class Colour :
    "wrapper around a GEGL colour object. Do not instantiate directly:" \
    " get from create method."

    __slots__ = ("_geglobj", "__weakref__")

    _instances = WeakValueDictionary()

    def __new__(celf, _geglobj) :
        self = celf._instances.get(_geglobj)
        if self == None :
            self = super().__new__(celf)
            self._geglobj = _geglobj
            celf._instances[_geglobj] = self
        else :
            # don’t need extra reference generated by caller
            libgobject2.g_object_unref(_geglobj)
        #end if
        return \
            self
    #end __new__

    def __del__(self) :
        if self._geglobj != None :
            libgobject2.g_object_unref(self._geglobj)
            self._geglobj = None
        #end if
    #end __del__

    @classmethod
    def create(celf, string = None) :
        if string != None :
            c_string = str_encode(string)
        else :
            c_string = None
        #end if
        return \
            celf(libgegl.gegl_color_new(c_string))
    #end create

    if qah != None :

        @classmethod
        def create_from_qah(celf, colour) :
            if not isinstance(colour, qah.Colour) :
                raise TypeError("colour must be a Qahirah Colour")
            #end if
            result = celf.create()
            result.set_rgba(*colour.to_rgba())
            return \
                result
        #end create_from_qah

        def to_qah(self) :
            return \
                qah.Colour.from_rgba(self.rgba)
        #end to_qah

    #end if

    def duplicate(self) :
        return \
            type(self)(libgegl.gegl_color_duplicate(self._geglobj))
    #end duplicate

    @property
    def rgba(self) :
        "returns components in linear space with un-premultiplied alpha."
        red = ct.c_double()
        green = ct.c_double()
        blue = ct.c_double()
        alpha = ct.c_double()
        libgegl.gegl_color_get_rgba(self._geglobj, ct.byref(red), ct.byref(green), ct.byref(blue), ct.byref(alpha))
        return \
            (red.value, green.value, blue.value, alpha.value)
    #end rgba

    def set_rgba(self, red, green, blue, alpha) :
        "expects new components in linear space with un-premultiplied alpha."
        libgegl.gegl_color_set_rgba(self._geglobj, red, green, blue, alpha)
    #end set_rgba

    def set_pixel(self, format : Babl, pixel) :
        "sets the components of this Colour from pixel interpreted according to format."
        if not isinstance(format, Babl) :
            raise TypeError("format must be a Babl object")
        #end if
        libgegl.gegl_color_set_pixel(self._geglobj, format._bablobj, pixel)
    #end set_pixel

    def get_pixel(self, format : Babl, pixel) :
        "sets pixel to this Colour interpreted according to format."
        if not isinstance(format, Babl) :
            raise TypeError("format must be a Babl object")
        #end if
        libgegl.gegl_color_get_pixel(self._geglobj, format._bablobj, pixel)
    #end get_pixel

    # TODO spec_color, get_default

#end Colour

def _conv_node_prop(value, conv_str : bool) :
    "tries to convert a Python value to a suitable GEGL node property type."
    c_save = None
    if isinstance(value, int) :
        value = int(value)
        if value < - 1 << 31 or value >= 1 << 31 :
            # problem with wider ints is that glib has types
            # “long” and “int64”, and I’m not sure which one to use
            raise ValueError("assuming only 32-bit ints for now")
        #end if
        c_value = value
        g_type = GTYPE.INT
    elif isinstance(value, float) :
        c_value = value
        g_type = GTYPE.DOUBLE
    elif isinstance(value, str) :
        c_value = str_encode(value)
        if conv_str :
            c_save = (ct.c_ubyte * (len(c_value) + 1))(*(tuple(c for c in c_value) + (0,)))
            c_value = ct.addressof(c_save)
        #end if
        g_type = GTYPE.STRING
    elif isinstance(value, ct.c_void_p) :
        c_value = value
        g_type = GTYPE.POINTER
    elif hasattr(value, "_geglobj") :
        c_value = value._geglobj
        g_type = GTYPE.POINTER
    else :
        raise TypeError("cannot convert property type %s" % type(value).__name__)
    #end if
    return \
        c_value, g_type, c_save
#end _conv_node_prop

def _gegl_node_props_common(funcname, fixedargs, varargs) :
    "common wrapper to handle calls to the various gegl_node_xxx routines that" \
    " take variable argument lists. In each case, the variable part consists" \
    " of a sequence of name-value pairs terminated by a NULL."
    if varargs != None :
        if isinstance(varargs, dict) :
            if not all(isinstance(k, str) for k in varargs) :
                raise TypeError("varargs keys must be strings")
            #end if
            varargs = tuple((k, v) for k, v in varargs.items())
        elif isinstance(varargs, (tuple, list)) :
            if not all \
              (
                isinstance(a, (tuple, list)) and len(a) == 2 and isinstance(a[0], str)
                for a in varargs
              ) \
            :
                raise TypeError("varargs must be sequence of name/value pairs")
            #end if
        else :
            raise TypeError("varargs must be dict, list, tuple or None")
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
    if len(fixedargs) != len(fixedargtypes) :
        raise TypeError \
          (
                "expecting %d fixed args, got %d"
            %
                (len(fixedargtypes), len(fixedargs))
          )
    #end if
    all_arg_types = list(fixedargtypes)
    all_args = list(fixedargs)
    for propname, value in varargs :
        c_value, g_type, c_save = _conv_node_prop(value, False)
        assert c_save == None
        c_propname = str_encode(propname)
        all_args.extend((c_propname, c_value))
        all_arg_types.extend((ct.c_char_p, g_type.ct_type))
    #end for
    all_arg_types.append(ct.c_void_p) # null to mark end of arg list
    all_args.append(None)
    func.argtypes = tuple(all_arg_types)
    return \
        func(*all_args)
#end _gegl_node_props_common

class Operation :
    "wrapper around a GeglOperation object. Do not instantiate directly;" \
    " get from Node.gegl_operation property."

    __slots__ = ("_geglobj", "__weakref__")

    _instances = WeakValueDictionary()

    def __new__(celf, _geglobj) :
        self = celf._instances.get(_geglobj)
        if self == None :
            self = super().__new__(celf)
            self._geglobj = _geglobj
            celf._instances[_geglobj] = self
        #end if
        # Note I do not manage deletion of these objects
        return \
            self
    #end __new__

    def get_invalidated_by_change(self, input_pad, roi) :
        c_input_pad = str_encode(input_pad)
        if not isinstance(roi, GEGL.Rectangle) :
            raise TypeError("roi must be a GEGL.Rectangle")
        #end if
        return \
            libgegl.gegl_operation_get_invalidated_by_change \
                (self._geglobj, c_input_pad, ct.byref(roi))
    #end get_invalidated_by_change

    @property
    def bounding_box(self) :
        return \
            libgegl.gegl_node_get_bounding_box(self._geglobj)
    #end bounding_box

    def source_get_bounding_box(self, pad_name) :
        c_pad_name = str_encode(pad_name)
        result = libgegl.gegl_operation_source_get_bounding_box(self._geglobj, c_pad_name)
        return \
            result.contents
    #end source_get_bounding_box

    def get_cached_region(self, roi) :
        if not isinstance(roi, GEGL.Rectangle) :
            raise TypeError("roi must be a GEGL.Rectangle")
        #end if
        return \
            libgegl.gegl_operation_get_cached_region(self._geglobj, ct.byref(roi))
    #end get_cached_region

    def get_required_for_output(self, input_pad, roi) :
        if not isinstance(roi, GEGL.Rectangle) :
            raise TypeError("roi must be a GEGL.Rectangle")
        #end if
        c_input_pad = str_encode(input_pad)
        return \
            libgegl.gegl_operation_get_required_for_output \
                (self._geglobj, c_input_pad, ct.byref(roi))
    #end get_required_for_output

    def detect(self, x, y) :
        result = libgegl.gegl_operation_detect(self._geglobj, x, y)
        if result != None :
            result = Node(result)
        #end if
        return \
            result
    #end detect

    def attach(self, node) :
        if not isinstance(node, Node) :
            raise TypeError("node must be a Node")
        #end if
        libgegl.gegl_operation_attach(self._geglobj, node._geglobj)
    #end attach

    def prepare(self) :
        libgegl.gegl_operation_prepare(self._geglobj)
    #end prepare

    def process(self, context, output_pad, roi, level) :
        if not isinstance(context, OperationContext) :
            raise TypeError("context must be an OperationContext")
        #end if
        c_output_pad = str_encode(output_pad)
        if not isinstance(roi, GEGL.Rectangle) :
            raise TypeError("roi must be a GEGL.Rectangle")
        #end if
        ok = libgegl.gegl_operation_process \
            (self._geglobj, context._geglobj, ct.byref(roi), level)
        if not ok :
            raise RuntimeError("operation process failed")
        #end if
    #end process

    def create_pad(self, param_spec) :
        if not isinstance(param_spec, GParamSpec) :
            # fixme: does using this type make sense?
            raise TypeError("param_spec must be an GParamSpec")
        #end if
        libgegl.gegl_operation_create_pad(self._geglobj, ct.byref(param_spec))
    #end create_pad

    def set_format(self, pad_name, format) :
        if not isinstance(format, Babl) :
            raise TypeError("format must be a Babl object")
        #end if
        c_pad_name = str_encode(pad_name)
        libgegl.gegl_operation_set_format(self._geglobj, c_pad_name, format._bablobj)
    #end set_format

    def get_format(self, pad_name) :
        c_pad_name = str_encode(pad_name)
        result = libgegl.gegl_operation_get_format(self._geglobj, c_pad_name)
        if result != None :
            result = Babl(result)
        #end if
        return \
            result
    #end get_format

    @property
    def name(self) :
        return \
            str_decode(libgegl.gegl_operation_get_name(self._geglobj))
    #end name

    def get_source_format(self, pad_name) :
        c_pad_name = str_encode(pad_name)
        result = libgegl.gegl_operation_get_source_format(self._geglobj, c_pad_name)
        if result != None :
            result = Babl(result)
        #end if
        return \
            result
    #end get_source_format

    def get_source_node(self, pad_name) :
        c_pad_name = str_encode(pad_name)
        result = libgegl.gegl_operation_get_source_node(self._geglobj, c_pad_name)
        if result != None :
            result = Node(result)
        #end if
        return \
            result
    #end get_source_node

    # TODO where to put GeglOperationClass methods?
    # gegl_operation_class_set_key, gegl_operation_class_get_key,
    # gegl_operation_class_set_keys, gegl_operation_set_key

    @property
    def use_opencl(self) :
        return \
            libgegl.gegl_operation_use_opencl(self._geglobj)
    #end use_opencl

    def use_threading(self, roi) :
        if not isinstance(roi, GEGL.Rectangle) :
            raise TypeError("roi must be a GEGL.Rectangle")
        #end if
        return \
            libgegl.gegl_operation_use_threading(self._geglobj, ct.byref(roi))
    #end use_threading

    @property
    def pixels_per_thread(self) :
        return \
            libgegl.gegl_operation_get_pixels_per_thread(self._geglobj)
    #end pixels_per_thread

    def invalidate(self, roi, clear_cache) :
        if not isinstance(roi, GEGL.Rectangle) :
            raise TypeError("roi must be a GEGL.Rectangle")
        #end if
        libgegl.gegl_operation_invalidate(self._geglobj, ct.byref(roi), clear_cache)
    #end invalidate

    # cl_set_kernel_args NYI

    def progress(self, progress, message) :
        c_message = str_encode(message)
        libgegl.gegl_operation_progress(self._geglobj, progress, c_message)
    #end progress

    def get_source_space(self, in_pad) :
        c_in_pad = str_encode(in_pad)
        result = libgegl.gegl_operation_get_source_space(self._geglobj, c_in_pad)
        if result != None :
            result = Babl(result)
        #end if
        return \
            result
    #end get_source_space

#end Operation

class OperationContext :

    __slots__ = ("_geglobj", "__weakref__")

    _instances = WeakValueDictionary()

    def __new__(celf, _geglobj) :
        self = celf._instances.get(_geglobj)
        if self == None :
            self = super().__new__(celf)
            self._geglobj = _geglobj
            celf._instances[_geglobj] = self
        #end if
        # Note I do not manage deletion of these objects
        return \
            self
    #end __new__

    def get_target(self, padname) :
        c_padname = str_encode(padname)
        result = libgegl.gegl_operation_context_get_target(self._geglobj, c_padname)
        if result != None :
            result = Buffer(result)
        #end if
        return \
            result
    #end get_target

    # TODO: dup_object, get_object, set_object, take_object

    def purge(self) :
        libgegl.gegl_operation_context_purge(self._geglobj)
    #end purge

    def get_level(self) :
        return \
            libgegl.gegl_operation_context_get_level(self._geglobj)
    #end get_level

#end OperationContext

class Node :
    "wrapper around a GEGL node object. Do not instantiate directly:" \
    " get from create methods."

    __slots__ = ("_geglobj", "__weakref__", "_prop_save")

    _instances = WeakValueDictionary()

    def __new__(celf, _geglobj) :
        self = celf._instances.get(_geglobj)
        if self == None :
            self = super().__new__(celf)
            self._geglobj = _geglobj
            self._prop_save = {}
              # warning: if caller loses reference to this wrapper Node object
              # while _geglobj remains allocated, then references kept in
              # _prop_save will be lost as well, which might cause GEGL to crash.
            celf._instances[_geglobj] = self
        else :
            # don’t need extra reference generated by caller
            libgobject2.g_object_unref(_geglobj)
        #end if
        return \
            self
    #end __new__

    def __del__(self) :
        if self._geglobj != None :
            libgobject2.g_object_unref(self._geglobj)
            self._geglobj = None
        #end if
    #end __del__

    @classmethod
    def create(celf, props = None) :
        if props != None :
            result = _gegl_node_props_common("gegl_node_new_child", (None,), props)
        else :
            result = libgegl.gegl_node_new()
        #end if
        return \
            celf(result)
    #end create

    @classmethod
    def create_from_xml(celf, xmldata, path_root) :
        c_xmldata = str_encode(xmldata)
        c_path_root = str_encode(path_root)
        result = libgegl.gegl_node_new_from_xml(c_xmldata, c_path_root)
        if result == None :
            raise RuntimeError("failed to create node from XML file")
        #end if
        return \
            celf(result)
    #end create_from_xml

    @classmethod
    def create_from_file(celf, path) :
        c_path = str_encode(path)
        result = libgegl.gegl_node_new_from_file(c_path)
        if result == None :
            raise RuntimeError("failed to create node from file")
        #end if
        return \
            celf(result)
    #end create_from_file

    def new_child(self, props) :
        return \
            type(self)(_gegl_node_props_common("gegl_node_new_child", (self._geglobj,), props))
    #end new_child

    def connect_from(sink, input_pad_name, source, output_pad_name) :
        if not isinstance(source, Node) :
            raise TypeError("source must be a Node")
        #end if
        if not libgegl.gegl_node_connect_from \
          (
            sink._geglobj, str_encode(input_pad_name),
            source._geglobj, str_encode(output_pad_name)
          ) :
            raise RuntimeError \
              (
                "could not connect their %s to my %s" % (output_pad_name, input_pad_name)
              )
        #end if
    #end connect_from

    def connect_to(source, output_pad_name, sink, input_pad_name) :
        if not isinstance(sink, Node) :
            raise TypeError("sink must be a Node")
        #end if
        if not libgegl.gegl_node_connect_to \
          (
            source._geglobj, str_encode(output_pad_name),
            sink._geglobj, str_encode(input_pad_name)
          ) :
            raise RuntimeError \
              (
                "could not connect my %s to their %s" % (output_pad_name, input_pad_name)
              )
        #end if
    #end connect_to

    def link(self, *args) :
        "does a gegl_node_link or a gegl_node_link_many call, depending on how" \
        " many args are passed."
        if len(args) == 0 :
            raise TypeError("must specify at least one other node in chain")
        #end if
        if not all(isinstance(s, Node) for s in args) :
            raise TypeError("sinks must all be Node objects")
        #end if
        if len(args) > 1 :
            basefunc = libgegl.gegl_node_link_many
            func = type(basefunc).from_address(ct.addressof(basefunc))
            func.restype = basefunc.restype
            func.argtypes = (ct.c_void_p,) * (len(args) + 2)
            all_args = (self._geglobj,) + tuple(a._geglobj for a in args) + (None,)
            func(*all_args)
        else :
            libgegl.gegl_node_link(self._geglobj, args[0]._geglobj)
        #end if
    #end link

    def disconnect(self, input_pad) :
        return \
            libgegl.gegl_node_disconnect(self._geglobj, str_encode(input_pad))
    #end disconnect

    def set(self, props) :
        _gegl_node_props_common("gegl_node_set", (self._geglobj,), props)
    #end set

    def get(self, propnames) :
        return \
            dict \
              (
                (propname, self[propname])
                for propname in propnames
              )
    #end get

    def __setitem__(self, propname, propvalue) :
        "allows setting property values via «node»[«propname»] = «propvalue»"
        c_value, g_type, c_save = _conv_node_prop(propvalue, True)
        gval = GValue()
        gval.g_type = g_type.code
        setattr(gval.data[0], g_type.gvalue_field, c_value)
        c_propname = str_encode(propname)
        libgegl.gegl_node_set_property(self._geglobj, c_propname, ct.byref(gval))
        if c_save != None :
            self._prop_save[propname] = c_save
              # GEGL is not expecting us to lose object it is referencing
        else :
            self._prop_save.pop(propname, None)
        #end if
        #libgobject2.g_value_unset(ct.byref(gval))
          # don’t do this: triggers abort with “free(): invalid pointer”
    #end __setitem__

    def __getitem__(self, propname) :
        "allows retrieving property values via «node»[«propname»]"
        gval = GValue()
        libgegl.gegl_node_get_property(self._geglobj, str_encode(propname), ct.byref(gval))
        if gval.g_type not in GTYPE.from_code :
            raise TypeError("cannot convert property %s of type %d" % (propname, gval.g_type))
        #end if
        valtype = GTYPE.from_code[gval.g_type]
        value = getattr(gval.data[0], valtype.gvalue_field)
        if valtype == GTYPE.STRING :
            value = str_decode(ct.cast(value, ct.c_char_p).value)
        #end if
        libgobject2.g_value_unset(ct.byref(gval)) # need to free any memory?
        return \
            value
    #end __getitem__

    def blit(self, scale : float, roi : GEGL.Rectangle, format : Babl, destination_buf : Buffer, rowstride : int, flags : GEGL.BlitFlags) :
        if not isinstance(format, Babl) :
            raise TypeError("format must be a Babl object")
        #end if
        if destination_buf != None and not isinstance(destination_buf, Buffer) :
            raise TypeError("destination_buf must be a Buffer object")
        #end if
        libgegl.gegl_node_blit.restype \
          (
            self._geglobj,
            scale, roi,
            format._bablobj,
            (lambda : None, lambda : destination_buf._geglobj)[destination_buf != None](),
            rowstride, flags
          )
    #end blit

    def blit_buffer(self, buffer, roi : GEGL.Rectangle, level : int, absyss_policy : GEGL.AbyssPolicy) :
        if not isinstance(buffer, Buffer) :
            raise TypeError("buffer must be a Buffer object")
        #end if
        libgegl.gegl_node_blit_buffer(self._geglobj, buffer._geglobj, roi, level, abyss_policy)
    #end blit_buffer

    def process(self) :
        libgegl.gegl_node_process(self._geglobj)
    #end process

    def add_child(self, child) :
        if not isinstance(child, Node) :
            raise TypeError("child must be a Node")
        #end if
        libgegl.gegl_node_add_child(self._geglobj, child._geglobj)
    #end add_child

    def remove_child(self, child) :
        if not isinstance(child, Node) :
            raise TypeError("child must be a Node")
        #end if
        libgegl.gegl_node_remove_child(self._geglobj, child._geglobj)
    #end remove_child

    @property
    def parent(self) :
        result = libgegl.gegl_node_get_parent(self._geglobj)
        if result != None :
            result = type(self)(result)
        #end if
        return \
            result
    #end parent

    def detect(self, x : int, y : int) :
        result = libgegl.gegl_node_detect(self._geglobj, x, y)
        if result != None :
            result = type(self)(result)
        #end if
        return \
            result
    #end detect

    def find_property(self, property_name) :
        c_propname = str_encode(property_name)
        c_result = libgegl.gegl_node_find_property(self._geglobj, c_propname)
        if c_result != None :
            c_result = ct.cast(c_result, ct.POINTER(GParamSpec)).contents
            result = dict \
              (
                (k, getattr(c_result, k))
                for k in ("g_type_instance", "flags", "value_type", "owner_type")
              )
            result["name"] = str_decode(c_result.name)
        else :
            result = None
        #end if
        return \
            result
    #end find_property

    @property
    def bounding_box(self) :
        return \
           libgegl.gegl_node_get_bounding_box(self._geglobj)
    #end bounding_box

    @property
    def children(self) :
        c_result = libgegl.gegl_node_get_children(self._geglobj)
        celf = type(self)
        result = []
        elt = c_result
        while elt != None :
            elt = elt.contents
            result.append(celf(elt.data))
            elt = elt.next
        #end while
        libglib2.g_slist_free(c_result)
        return \
            result
    #end children

    def get_nr_consumers(self, output_pad) :
        c_output_pad = str_encode(output_pad)
        return \
            libgegl.gegl_node_get_consumers(self._geglobj, c_output_pad, None, None)
    #end get_nr_consumers

    def get_consumers(self, output_pad) :
        c_output_pad = str_encode(output_pad)
        c_nodes = ct.POINTER(ct.c_void_p)()
        c_pads = ct.POINTER(ct.c_char_p)()
        nr_consumers = libgegl.gegl_node_get_consumers \
            (self._geglobj, c_output_pad, ct.byref(c_nodes), ct.byref(c_pads))
        nodes = []
        pads = []
        celf = type(self)
        for i in range(nr_consumers) :
            nodes.append(celf(c_nodes[i]))
            pads.append(str_decode(c_pads[i]))
        #end for
        libglib2.g_free(ct.cast(c_nodes, ct.c_void_p))
        libglib2.g_free(ct.cast(c_pads, ct.c_void_p))
        return \
            nodes, pads
    #end get_consumers

    def get_input_proxy(self, pad_name) :
        c_pad_name = str_encode(pad_name)
        return \
            type(self)(libgegl.gegl_node_get_input_proxy(self._geglobj, c_pad_name))
    #end get_input_proxy

    @property
    def operation(self) :
        result = libgegl.gegl_node_get_operation(self._geglobj)
        if result != None :
            result = str_decode(result)
        #end if
        return \
            result
    #end operation

    @property
    def gegl_operation(self) :
        result = libgegl.gegl_node_get_gegl_operation(self._geglobj)
        if result != None :
            result = Operation(result)
        #end if
        return \
            result
    #end gegl_operation

    def get_output_proxy(self, pad_name) :
        c_pad_name = str_encode(pad_name)
        return \
            type(self)(libgegl.gegl_node_get_output_proxy(self._geglobj, c_pad_name))
    #end get_output_proxy

    def get_producer(self, input_pad_name) :
        c_input_pad_name = str_encode(input_pad_name)
        c_output_pad_name = ct.POINTER(ct.c_char_p)()
        c_prod = libgegl.gegl_node_get_producer(self._geglobj, c_input_pad_name, ct.byref(c_output_pad_name))
        if c_prod != None :
            result = (type(self)(c_prod), str_decode(c_output_pad_name[0]))
        else :
            result = (None, None)
        #end if
        return \
            result
    #end get_producer

    def has_pad(self, pad_name) :
        c_pad_name = str_encode(pad_name)
        return \
            libgegl.gegl_node_has_pad(self._geglobj, c_pad_name)
    #end has_pad

    @property
    def input_pads(self) :
        c_result = libgegl.gegl_node_list_input_pads(self._geglobj)
        c_result = ct.cast(c_result, ct.c_void_p).value
        result = []
        if c_result != None :
            p_elt = c_result
            while True :
                elt = ct.cast(p_elt, ct.c_void_p).value
                if elt == None :
                    break
                result.append(str_decode(ct.cast(elt, ct.c_char_p).contents.value))
                p_elt += ct.sizeof(ct.c_void_p)
            #end while
            libglib2.g_strfreev(c_result)
        #end if
        return \
            result
    #end input_pads

    @property
    def output_pads(self) :
        c_result = libgegl.gegl_node_list_output_pads(self._geglobj)
        c_result = ct.cast(c_result, ct.c_void_p).value
        result = []
        if c_result != None :
            p_elt = c_result
            while True :
                elt = ct.cast(p_elt, ct.c_void_p).value
                if elt == None :
                    break
                result.append(str_decode(ct.cast(elt, ct.c_char_p).contents.value))
                p_elt += ct.sizeof(ct.c_void_p)
            #end while
            libglib2.g_strfreev(c_result)
        #end if
        return \
            result
    #end output_pads

    def create_child(self, operation) :
        c_operation = str_encode(operation)
        return \
            type(self)(libgegl.gegl_node_create_child(self._geglobj, c_operation))
    #end create_child

    def to_xml(self, path_root) :
        c_path_root = str_encode(path_root)
        xml = libgegl.gegl_node_to_xml(self._geglobj, c_path_root)
        return \
            str_decode(xml)
    #end to_xml

    def to_xml_full(self, tail, path_root) :
        if tail != None :
            if not isinstance(tail, Node) :
                raise TypeError("tail must be a Node")
            #end if
            c_tail = tail._geglobj
        else :
            c_tail = None
        #end if
        c_path_root = str_encode(path_root)
        xml = libgegl.gegl_node_to_xml_full(self._geglobj, c_tail, c_path_root)
        return \
            str_decode(xml)
    #end to_xml_full

    @property
    def passthrough(self) :
        return \
            libgegl.gegl_node_get_passthrough(self._geglobj)
    #end passthrough

    @passthrough.setter
    def passthrough(self, passthrough : bool) :
        libgegl.gegl_node_set_passthrough(self._geglobj. passthrough)
    #end passthrough

    @property
    def is_graph(self) :
        return \
            libgegl.gegl_node_is_graph(self._geglobj)
    #end is_graph

    def progress(self, progress : float, message) :
        c_message = str_encode(message)
        libgegl.gegl_node_progress(self._geglobj, progress, c_message)
    #end progress

#end Node

def get_op_version(op_name) :
    c_op_name = str_encode(op_name)
    result = libgegl.gegl_operation_get_op_version(c_op_name)
    if not bool(result) :
        raise RuntimeError("failed to get version for op %s" % op_name)
    #end if
    return \
        str_decode(result)
#end get_op_version

def _init_dynamic_types() :

    def def_expect_gegl_wrapper(wrapper_type) :

        def conv(val) :
            if not isinstance(val, wrapper_type) :
                raise TypeError("value must be of type %s" % wrapper_type.__name__)
            #end if
            return \
                val._geglobj
        #end conv

    #begin def_expect_gegl_wrapper
        conv.__name__ = "conv_%s" % wrapper_type.__name__
        return \
            conv
    #end def_expect_gegl_wrapper

#begin _init_dynamic_types
    for type_name, conv in \
        (
            ("GeglBuffer", def_expect_gegl_wrapper(Buffer)),
            ("GeglColor", def_expect_gegl_wrapper(Colour)),
        ) \
    :
        dynamic_types_by_name[type_name] = \
            {
                "name" : type_name,
                "conv" : conv,
            }
    #end for
#end _init_dynamic_types
_init_dynamic_types()
del _init_dynamic_types

#+
# Overall
#-

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
        c_argv[i] = str_encode(argv[i])
    #end for
    c_argv[len(argv)] = None
    libgegl.gegl_init(c_argc, c_argv)
    return \
        list(str_decode(v) for v in c_argv[:c_argc.value])
#end init

def exit() :
    "cleanup after finishing with GEGL. Note that you must have freed all" \
    " allocated buffers before this point, or you will see complaints" \
    " about leaks."
    libgegl.gegl_exit()
#end exit

def _atexit() :
    # disable all __del__ methods at process termination to avoid segfaults
    for cłass in GObject, Buffer, Colour, Node :
        delattr(cłass, "__del__")
    #end for
#end _atexit
atexit.register(_atexit)
del _atexit
