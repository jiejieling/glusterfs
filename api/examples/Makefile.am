# The bits needed for glfsxmp
EXTRA_PROGRAMS = glfsxmp
glfsxmp_SOURCES = glfsxmp.c
GLFS_CFLAGS = -I/usr/local/include/glusterfs/
GLFS_LIBS = -L/usr/local/lib/ -lgfapi
glfsxmp_CFLAGS = $(GLFS_CFLAGS) -Wall
glfsxmp_LDADD = $(GLFS_LIBS)

