#!/usr/bin/python3

from __future__ import print_function
import os
import time
import ctypes
import ctypes.util
from ctypes import sizeof

try:
    import ctypes.c_ssize_t
except ImportError:
    if sizeof(ctypes.c_uint) == sizeof(ctypes.c_void_p):
        setattr(ctypes, 'c_ssize_t', ctypes.c_int)
    elif sizeof(ctypes.c_ulong) == sizeof(ctypes.c_void_p):
        setattr(ctypes, 'c_ssize_t', ctypes.c_long)
    elif sizeof(ctypes.c_ulonglong) == sizeof(ctypes.c_void_p):
        setattr(ctypes, 'c_ssize_t', ctypes.c_longlong)

so_file_name = ctypes.util.find_library("gfapi")
api = ctypes.CDLL(so_file_name, ctypes.RTLD_GLOBAL, use_errno=True)


# api.glfs_set_volfile_server.argtypes = [ctypes.c_void_p,
#                                  ctypes.c_char_p,
#                                  ctypes.c_char_p,
#                                  ctypes.c_int]
# api.glfs_set_volfile_server.restype = ctypes.c_int


def gfapi_prototype(method_name, restype, *argtypes):
    """
    Create a named foreign function belonging to gfapi

    :param method_name: Name of the foreign function
    :param restype: resulting type
    :param argtypes: arguments that represent argument types
    :returns: foreign function of gfapi library
    """
    # use_errno=True ensures that errno is exposed by ctypes.get_errno()
    return ctypes.CFUNCTYPE(restype, *argtypes, use_errno=True)(
        (method_name, api)
    )


def decode_to_bytes(text):
    """
    Decode unicode object to bytes
    or return original object if already bytes
    """

    string_types = (str,)

    if isinstance(text, string_types):
        return text.encode('utf-8')
    elif isinstance(text, bytes):
        return text
    else:
        raise ValueError('Cannot convert object with type %s' % type(text))


def do_func(func, args: tuple, restype, *argtypes):
    ret = gfapi_prototype(func, restype, *argtypes)(*args)
    if issubclass(restype, ctypes.c_int) and ret != 0 or (not issubclass(restype, ctypes.c_int) and not ret):
        err = ctypes.get_errno()
        raise Exception(os.strerror(err))

    return ret


class Dirent(ctypes.Structure):
    _fields_ = [
        ("d_ino", ctypes.c_ulong),
        ("d_off", ctypes.c_ulong),
        ("d_reclen", ctypes.c_uint16),
        ("d_namlen", ctypes.c_uint16),
        ("d_type", ctypes.c_uint8),
        ("d_name", ctypes.c_char * 256),
    ]


def get_volfile(host, volume):
    # This is set to a large value to exercise the "buffer not big enough"
    # path.  More realistically, you'd just start with a huge buffer.
    BUF_LEN = 512

    fs = gfapi_prototype('glfs_new', ctypes.c_void_p, ctypes.c_char_p)(decode_to_bytes(volume))
    if not fs:
        err = ctypes.get_errno()
        raise Exception(os.strerror(err))

    # api.glfs_set_logging(fs,"/dev/stderr",7)
    do_func('glfs_set_volfile_server', (fs, decode_to_bytes("tcp"), decode_to_bytes(host), 24007), ctypes.c_int,
            ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p,
            ctypes.c_int)

    do_func('glfs_init', (fs,), ctypes.c_int, ctypes.c_void_p)

    time.sleep(2)

    dirfp = do_func('glfs_opendir', (fs, decode_to_bytes("/")), ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p)

    vbuf = Dirent()
    vbuf.d_reclen = 512
    cursor = ctypes.POINTER(Dirent)()

    while not do_func('glfs_readdir_r', (dirfp, ctypes.byref(vbuf), ctypes.byref(cursor)), ctypes.c_int, ctypes.c_void_p,
                  ctypes.POINTER(Dirent),
                  ctypes.POINTER(ctypes.POINTER(Dirent))):
        time.sleep(1)
        print(cursor.contents.d_name)


if __name__ == "__main__":
    import sys

    print(get_volfile('192.168.15.103', 'test4'))
