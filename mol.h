#ifndef MOL_H
#define MOL_H

/*IMPORTING LIBRARIES*/
#include <stdlib.h>
#include <string.h>
#include <math.h> 
#include <stdio.h> 

/*CONSTANTS*/
#define DIMENSION 3
#define PI 3.141592653589793238462643383279

/*STRUCT DEFINITIONS*/

typedef struct atom {
    char element[3];
    double x, y, z;
} atom;

// this is the A2 version of bond
typedef struct bond {
    unsigned short a1, a2;
    unsigned char epairs;
    atom *atoms;
    double x1, x2, y1, y2, z, len, dx, dy;
} bond;

typedef struct molecule {
    unsigned short atom_max, atom_no;
    atom *atoms, **atom_ptrs;
    unsigned short bond_max, bond_no;
    bond *bonds, **bond_ptrs;
} molecule;

typedef double xform_matrix[3][3]; // now this is a pointer to an array

// added in for A4
typedef struct mx_wrapper {
  xform_matrix xform_matrix;
} mx_wrapper;

/*FUNCTION PROTOTYPES*/
// bondset and bondget hae been updated since A2

void atomset( atom *atom, char element[3], double *x, double *y, double *z );
void atomget( atom *atom, char element[3], double *x, double *y, double *z );
void bondset( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs );
void bondget( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs );
molecule *molmalloc( unsigned short atom_max, unsigned short bond_max);
molecule *molcopy( molecule *src );
void molfree( molecule *ptr );
void molappend_atom( molecule *molecule, atom *atom );
void molappend_bond( molecule *molecule, bond *bond );
void molsort( molecule *molecule );
void xrotation( xform_matrix xform_matrix, unsigned short deg );
void yrotation( xform_matrix xform_matrix, unsigned short deg );
void zrotation( xform_matrix xform_matrix, unsigned short deg );
void mol_xform( molecule *molecule, xform_matrix matrix );

// introduced in A2
void compute_coords( bond *bond );
int bond_comp( const void *a, const void *b ); // FIXME -- not quite sure how this will work in the context of the program

/*HELPER FUNCTIONS*/
/*For sorting atoms*/
void swapAtoms(atom ** atom_ptr1, atom ** atom_ptr2);
int partitionAtoms(atom ** atom_ptrs, int low, int high);
void qSortAtoms(atom ** atom_ptrs, int low, int high);

/*For updating atom/bond pointers after a realloc*/
void updateAtomPointers(molecule *molecule);
void updateBondPointers(molecule * molecule);

/*For sorting bonds*/
int compareZBonds(bond * bond1, bond * bond2);
void swapBonds(bond ** bond_ptr1, bond ** bond_ptr2);
int partitionBonds(bond ** bond_ptrs, int low, int high);
void qSortBonds(bond ** bond_ptrs, int low, int high);

#endif
