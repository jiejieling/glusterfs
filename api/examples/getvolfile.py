#!/usr/bin/python3

from __future__ import print_function
import ctypes
import ctypes.util

api = ctypes.CDLL("../src/.libs/libgfapi.dylib")
api.glfs_get_volfile.argtypes = [ctypes.c_void_p,
                                 ctypes.c_void_p,
                                 ctypes.c_ulong]
api.glfs_get_volfile.restype = ctypes.c_long


def get_volfile(host, volume):
    # This is set to a large value to exercise the "buffer not big enough"
    # path.  More realistically, you'd just start with a huge buffer.
    BUF_LEN = 0
    fs = api.glfs_new(volume)
    # api.glfs_set_logging(fs,"/dev/stderr",7)
    api.glfs_set_volfile_server(fs, "tcp", host, 24007)
    api.glfs_init(fs)
    vbuf = ctypes.create_string_buffer(BUF_LEN)
    vlen = api.glfs_get_volfile(fs, vbuf, BUF_LEN)
    if vlen < 0:
        vlen = BUF_LEN - vlen
        vbuf = ctypes.create_string_buffer(vlen)
        vlen = api.glfs_get_volfile(fs, vbuf, vlen)
    api.glfs_fini(fs)
    if vlen <= 0:
        return vlen
    return vbuf.value[:vlen]


if __name__ == "__main__":
    print(get_volfile('192.168.15.103', 'test4'))
