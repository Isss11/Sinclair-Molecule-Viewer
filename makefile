CC = clang
CFLAGS = -Wall -std=c99 -pedantic

all: _molecule.so

libmol.so: mol.o
	$(CC) mol.o -shared -o libmol.so

mol.o:  mol.c mol.h
	$(CC) $(CFLAGS) -c mol.c -fPIC -o mol.o

_molecule.so: molecule_wrap.o libmol.so # dynamiclib will produce a warning (still, do not remove)
	$(CC) molecule_wrap.o -shared -L. -lpython3.7m -L /usr/lib/python3.7/config-3.7m-x86_64-linux-gnu -lmol -dynamiclib -o _molecule.so

molecule_wrap.c molecule.py: molecule.i
	swig -python molecule.i

molecule_wrap.o: molecule_wrap.c # FIXME -- copy in old file name with PROPER python path above instead of -L.
	$(CC) $(CFLAGS) -c molecule_wrap.c -fPIC -I /usr/include/python3.7m -o molecule_wrap.o

main.o:  testPart1.c mol.h
	$(CC) $(CFLAGS) -c testPart1.c -o main.o

clean:  
	rm -f molecule.py molecule_wrap.c *.o *.so myprog

myprog:  main.o libmol.so # note the need to use export LD_LIBRARY_PATH=`pwd`
	$(CC) main.o -L. -lmol -o myprog -lm
