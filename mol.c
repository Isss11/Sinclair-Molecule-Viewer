#include "mol.h"

/*This function copies the values pointed to by element, x, y, and z into the atom stored at atom.*/
void atomset( atom *atom, char element[3], double *x, double *y, double *z ) {
    atom -> x = * x;
    atom -> y = * y;
    atom -> z = * z;

    strcpy(atom -> element, element);
}

/*This function should copy the values in the atom stored at atom to the locations pointed to by element, x, y, and z.
This is basically the reverse of the previous function*/
void atomget( atom *atom, char element[3], double *x, double *y, double *z ) {
    * x = atom -> x;
    * y = atom -> y;
    * z = atom -> z;
    
    strcpy(element, atom -> element);
}

/*This function should copy the values a1, a2 and epairs into the corresponding structure attributes in bond.*/
void bondset( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs ) {
    bond -> a1 = * a1;
    bond -> a2 = * a2;
    bond -> atoms = * atoms;
    bond -> epairs = * epairs;

    compute_coords(bond);
}

/*This function should copy the structure attributes in bond to their corresponding arguments: a1, a2 and epairs.
Note that this is basically the inverse of the previous function. Just like the above function, we're not copying atom structures,
just the address to the atom structures*/
void bondget( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs ) {
    // we're dereferencing each variable so that we don't change the pass-by-reference address
    * a1 = bond -> a1;
    * a2 = bond -> a2;
    * atoms = bond -> atoms;
    * epairs = bond -> epairs;
}

/*This function should return the address of a malloced area of memory, large enough to hold a molecule. It creates a new molecule
and stores corresponding values into it.*/
molecule *molmalloc( unsigned short atom_max, unsigned short bond_max) {
    molecule * newMolecule = NULL;

    newMolecule = malloc(sizeof(molecule)); // calloced this to see if it would deal with uninitialized values issue (seemed towork =)

    if (newMolecule == NULL) {
        fprintf(stderr, "Memory not allocated\n");
        return NULL;
    }

    newMolecule -> atom_max = atom_max;
    newMolecule -> atom_no = 0;
    newMolecule -> bond_max = bond_max;
    newMolecule -> bond_no = 0;

    // allocating space based on specifications

    // this needs to hold the atom_max number of atoms
    newMolecule -> atoms = malloc(sizeof(atom) * atom_max);

    if (newMolecule -> atoms == NULL) {
        fprintf(stderr, "Memory not allocated.\n");
        return NULL;
    }

    // this holds the atom_max number of pointers to atoms
    newMolecule -> atom_ptrs = malloc(sizeof(atom *) * atom_max);

    if (newMolecule -> atom_ptrs == NULL) {
        fprintf(stderr, "Memory not allocated.\n");
        return NULL;
    }

    // allocating space based on specifications
    // this holds enough memory to hold bond_max number of bonds
    newMolecule -> bonds = malloc(sizeof(bond) * bond_max);

    if (newMolecule -> bonds == NULL) {
        fprintf(stderr, "Memory not allocated\n");
        return NULL;
    }

    // this holds enough memory to hold bond_max number of pointers to bonds
    newMolecule -> bond_ptrs = malloc(sizeof(bond *) * bond_max);

    if (newMolecule -> bond_ptrs == NULL) {
        fprintf(stderr, "Memory not allocated\n");
        return NULL;
    }

    return newMolecule;
}

/*This creates a new molecule, that coppies the src molecule's values into it, and returns the address to it.*/
molecule *molcopy( molecule *src ) {
    molecule * dest; 
    int temp_bond_no, temp_atom_no;
    bond tempBond;

    // initializing copied molecule with atom_max and bond_max
    dest = molmalloc(src -> atom_max, src -> bond_max);

    if (dest == NULL) {
        fprintf(stderr, "Memory not allocated\n");
        return NULL;
    }

    // storing these temporary variables so that we know how long we have to iterate through each array (when appending)
    // issues were caused when assigning these values directly to dest
    temp_bond_no = src -> bond_no;
    temp_atom_no = src -> atom_no;

    // now copying elements into the corresponding arrays, using the append function
    // copying atoms first
    for (int i = 0; i < temp_atom_no; ++i) {
        molappend_atom(dest, &(src -> atoms[i])); // copying the pointed to value in src to the dest molecule
    }

    // copying bonds second
    for (int i = 0; i < temp_bond_no; ++i) {
        // setting temporary bond (need so that I can change the atoms ptr since we're copying this bond into a different memory space)
        bondset(&tempBond, &(src -> bonds[i].a1), &(src -> bonds[i].a2), &(src -> bonds[i].atoms), &(src -> bonds[i].epairs));
        tempBond.atoms = dest -> atoms; // changing atoms ptr

        molappend_bond(dest, &tempBond);
    }   

    return dest; // address of malloced area in memory
}

/*Frees memory associated with a molecule pointed to by ptr. This includes all the arrays.*/
void molfree( molecule *ptr ) {

    free(ptr -> atoms);
    free(ptr -> atom_ptrs);
    free(ptr -> bonds);
    free(ptr -> bond_ptrs);
    free(ptr);

    ptr = NULL; // for good practice
}

/*Copies data pointed to by atom to the first empty atom in atoms in the molecule pointed by molecule. Also sets the first empty pointer
in atoms_ptrs array to the same atom in the atoms array. Increments certain integers as well.*/
void molappend_atom( molecule *molecule, atom *atom ) {

    // for reallocating array

    if (molecule -> atom_max == molecule -> atom_no) {
        // case where there are zero atoms
        if (molecule -> atom_max == 0) {
            ++(molecule -> atom_max);
        // case where the two are equal and non-zero
        } else {
            molecule -> atom_max *= 2;
        }

        // now reallocing the two arrays

        molecule -> atoms = realloc(molecule -> atoms, sizeof(struct atom) * (molecule -> atom_max));

        if (molecule -> atoms == NULL) {
            fprintf(stderr, "Memory not allocated\n");
            exit(0);
        }

        molecule -> atom_ptrs = realloc(molecule -> atom_ptrs, sizeof(struct atom *) * (molecule -> atom_max));

        if (molecule -> atom_ptrs == NULL) {
            fprintf(stderr, "Memory not allocated\n");
            exit(0);
        }

        // need to update pointers stored in atom_ptrs, as the atoms array could've been moved in memory after a realloc
        updateAtomPointers(molecule);
    }

    // putting element at the end of the arrays (using atom_no)
    atomset(&molecule -> atoms[molecule -> atom_no], atom -> element, &(atom -> x), &(atom -> y), &(atom -> z)); // copying data
    molecule -> atom_ptrs[molecule -> atom_no] = &(molecule -> atoms[molecule -> atom_no]); // copying pointer

    ++(molecule -> atom_no);
}

/*This function is basically a copy of molappend_atom, just replacing 'atom' with 'bond'.*/
void molappend_bond( molecule *molecule, bond *bond ) {

    // for reallocating array

    if (molecule -> bond_max == molecule -> bond_no) {
        // case where there are zero bonds
        if (molecule -> bond_max == 0) {
            ++(molecule -> bond_max);
        // case where the two are equal and non-zero
        } else {
            molecule -> bond_max *= 2;
        }

        // now reallocing the two arrays

        molecule -> bonds = realloc(molecule -> bonds, sizeof(struct bond) * (molecule -> bond_max));

        if (molecule -> bonds == NULL) {
            fprintf(stderr, "Memory not allocated\n");
            exit(0);
        }

        molecule -> bond_ptrs = realloc(molecule -> bond_ptrs, sizeof(struct bond *) * (molecule -> bond_max));

        if (molecule -> bond_ptrs == NULL) {
            fprintf(stderr, "Memory not allocated\n");
            exit(0);
        }

        // need to update pointers stored in bond_ptrs, as the bonds array could've been moved in memory after a realloc
        updateBondPointers(molecule);
    }

    // putting element at the end of the arrays (using bond_no)
    bondset(&molecule -> bonds[molecule -> bond_no], &bond -> a1, &bond -> a2, &bond -> atoms, &bond -> epairs); // copying data
    molecule -> bond_ptrs[molecule -> bond_no] = &(molecule -> bonds[molecule -> bond_no]); // copying pointer

    ++(molecule -> bond_no);
}

/*Sorts both bonds_prts and atoms_ptrs, based on the assignment specifications.*/
// I used this resource to help create this: https://www.geeksforgeeks.org/quick-sort/
void molsort( molecule *molecule ) {

    // sorting atom_ptrs using qsort
    qSortAtoms(molecule -> atom_ptrs, 0, molecule -> atom_no - 1);

    // sorting bond_ptrs
    qSortBonds(molecule -> bond_ptrs, 0, molecule -> bond_no - 1);
}

// created to simplify comparison statement for the bond sorting
int compareZBonds(bond * bond1, bond * bond2) {
    double bondOneAvg, bondTwoAvg;

    bondOneAvg = (bond1 -> atoms[bond1 -> a1].z + bond1 -> atoms[bond1 -> a2].z) / 2; 
    bondTwoAvg = (bond2 -> atoms[bond2 -> a1].z + bond2 -> atoms[bond2 -> a2].z) / 2;

    // basically just a simpler comparison statement
    if (bondOneAvg < bondTwoAvg) {
        return 1;
    } else {
        return 0;
    }
}

/*This function will allocate, compute, and return an affine transformation matrix corresponding to a rotation of deg degrees around the x-axis. 
This matrix must be freed by the user when no-longer needed. This is more of a note for my own reference, but I used this source to 
determine what these affine transformation matrices were all about: https://medium.com/swlh/understanding-3d-matrix-transforms-with-pixijs-c76da3f8bd8*/
void xrotation( xform_matrix xform_matrix, unsigned short deg ) {
    // we have been given a pointer to the xform maxtrix, so we will need to reference it's 2d array
    double rad;

    rad = deg * (PI/180);

    // now creating transformation matrix
    // fixed x-axis
    xform_matrix[0][0] = 1;
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = 0;

    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = cos(rad);
    xform_matrix[1][2] = -1 * sin(rad);

    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = sin(rad);
    xform_matrix[2][2] = cos(rad);
}

void yrotation( xform_matrix xform_matrix, unsigned short deg ) {
    double rad;

    rad = deg * (PI/180);

    // now creating transformation matrix
    xform_matrix[0][0] = cos(rad);
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = sin(rad); // might be an issue here with sign

    // fixed y-axis
    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = 1;
    xform_matrix[1][2] = 0;

    xform_matrix[2][0] = -1 * sin(rad); // might be an issue here with sign
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = cos(rad);
}

void zrotation( xform_matrix xform_matrix, unsigned short deg ) {
    double rad;

    rad = deg * (PI/180);

    // now creating transformation matrix
    xform_matrix[0][0] = cos(rad);
    xform_matrix[0][1] = -1 * sin(rad);
    xform_matrix[0][2] = 0;

    xform_matrix[1][0] = sin(rad);
    xform_matrix[1][1] = cos(rad);
    xform_matrix[1][2] = 0;

    // fixed z-axis
    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = 1;
}

/*This function will apply the transformation matrix to all the atoms of the molecule by performing a vector matrix multiplication on the 
x, y, z coordinates.*/
void mol_xform( molecule *molecule, xform_matrix matrix ) {
    double newX, newY, newZ;

    // iterates through atoms array (goes through all atoms)
    for (int i = 0; i < molecule -> atom_no; ++i) {
        newX = newY = newZ = 0; // resetting new values for next atom

        // now performing matrix multiplication
        // finding the new value of x
        newX = matrix[0][0] * molecule -> atoms[i].x + matrix[0][1] * molecule -> atoms[i].y + matrix[0][2] * molecule -> atoms[i].z;
        
        // finding the new value of y
        newY = matrix[1][0] * molecule -> atoms[i].x + matrix[1][1] * molecule -> atoms[i].y + matrix[1][2] * molecule -> atoms[i].z;

        // finding the new value of z
        newZ = matrix[2][0] * molecule -> atoms[i].x + matrix[2][1] * molecule -> atoms[i].y + matrix[2][2] * molecule -> atoms[i].z;

        // now actualy changing the x, y and z values after their corresponding transformed values have been calcualted

        molecule -> atoms[i].x = newX;
        molecule -> atoms[i].y = newY;
        molecule -> atoms[i].z = newZ;
    }

    // now performing compute_coords on all the molecule bonds
    for (int i = 0; i < molecule -> bond_no; ++i) {
        compute_coords(&(molecule -> bonds[i]));
    }
}

/*This function computes the z, x1, y1, x2, y2, len, dx and dy values of the bond and set them in the appropriate structure member variables.*/
void compute_coords( bond *bond ) {

        // updating x and y values for each respective bond
        bond -> x1 = bond -> atoms[bond -> a1].x;
        bond -> y1 = bond -> atoms[bond -> a1].y;

        bond -> x2 = bond -> atoms[bond -> a2].x;
        bond -> y2 = bond -> atoms[bond -> a2].y;

        // updating z value (average z-value in bond)
        bond -> z = (bond -> atoms[bond -> a1].z + bond -> atoms[bond -> a2].z) / 2;

        // calculating distance using formula
        bond -> len = sqrt((bond -> x2 - bond -> x1) * (bond -> x2 - bond -> x1) + 
        (bond -> y2 - bond -> y1) * (bond -> y2 - bond -> y1));

        bond -> dx = (bond -> x2 - bond -> x1) / bond -> len;
        bond -> dy = (bond -> y2 - bond -> y1) / bond -> len;

        // special case where we check if len is 0 (to avoid nAn values)
        if (bond -> len < 0.00000000000000001) {
            bond -> dx = 0;
            bond -> dy = 0;
        }
}

/*This function is to be used after a realloc, to update any changed pointers in the atom_ptrs array.*/
void updateAtomPointers(molecule *molecule) {
    // copies new atom pointers into atom_ptrs
    for (int i = 0; i < molecule -> atom_no; ++i) {
        molecule -> atom_ptrs[i] = &molecule -> atoms[i]; // gets the address of the new area where the atoms[i] pointer is in the heap
    }
}

/*This function is to be used after a realloc, to update any changed pointers in the bond_ptrs array.*/
void updateBondPointers(molecule * molecule) {
    // copies new bond pointers into bond_ptrs
    for (int i = 0; i < molecule -> bond_no; ++i) {
        molecule -> bond_ptrs[i] = &molecule -> bonds[i]; // getting the address of the new area where the bonds[i] pointer is in the heap
    }
}

// Sourced from GeeksForGeeks, revised to conform to program.
void swapAtoms(atom ** atom_ptr1, atom ** atom_ptr2) {
    atom * temp; // holds a pointer to an atom temporarily

    temp = * atom_ptr1;
    *atom_ptr1 = *atom_ptr2;
    *atom_ptr2 = temp;
}

// Had to create a separate functions for bonds and atoms since implementation detail is different
int partitionAtoms(atom ** atom_ptrs, int low, int high) {
    atom * pivotAtom;

    pivotAtom = atom_ptrs[high]; // pivot

    int i= (low - 1);
 
    for (int j = low; j <= high - 1; j++) {
        // If current element is smaller than the pivot (note that we're trying to compare the double z value associated)
        if (atom_ptrs[j] -> z < pivotAtom -> z) {
            i++; 
            swapAtoms(&atom_ptrs[i], &atom_ptrs[j]);
        }
    }
    swapAtoms(&atom_ptrs[i + 1], &atom_ptrs[high]);

    return (i + 1);
}
 
// Implemented with this with void pointers to avoid having to duplicate this function
void qSortAtoms(atom ** atom_ptrs, int low, int high) {
    if (low < high) {
        int pIndex;

        pIndex = partitionAtoms(atom_ptrs, low, high);

        qSortAtoms(atom_ptrs, low, pIndex - 1);
        qSortAtoms(atom_ptrs, pIndex + 1, high);
    }
}

// Now this is the bond_ptrs sorting.
// Sourced from GeeksForGeeks, revised to conform to program.
void swapBonds(bond ** bond_ptr1, bond ** bond_ptr2) {
    bond * temp; // holds a pointer to an bond temporarily

    temp = * bond_ptr1;
    *bond_ptr1 = *bond_ptr2;
    *bond_ptr2 = temp;
}

// Had to create a separate functions for bonds and bonds since implementation detail is different
int partitionBonds(bond ** bond_ptrs, int low, int high) {
    bond * pivotBond;

    pivotBond = bond_ptrs[high]; // pivot

    int i= (low - 1);
 
    for (int j = low; j <= high - 1; j++) {
        // If current element is smaller than the pivot (note that we're trying to compare the double z value associated)

        // casting pointers to compare, and calling bond_comp which is just a wrapper function around compareZBonds
        if (bond_comp((const void *) bond_ptrs[j], (const void *) pivotBond)) {
            i++; 

            swapBonds(&bond_ptrs[i], &bond_ptrs[j]);
        }
    }
    swapBonds(&bond_ptrs[i + 1], &bond_ptrs[high]);

    return (i + 1);
}

/*This function was just created to comply with the A2 autograder. It just calls my bond comparison function and returns its value.*/
int bond_comp( const void *a, const void *b ) {
    // could probably just call compareZBonds here.
    return compareZBonds((bond *) a, (bond *) b);
}
 
// Implemented with this with void pointers to avoid having to duplicate this function
void qSortBonds(bond ** bond_ptrs, int low, int high) {
    if (low < high) {
        int pIndex;

        pIndex = partitionBonds(bond_ptrs, low, high);
 
        qSortBonds(bond_ptrs, low, pIndex - 1);
        qSortBonds(bond_ptrs, pIndex + 1, high);
    }
}
