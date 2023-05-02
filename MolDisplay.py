import molecule
import re
from math import sqrt

# defining these as pseudo-constants (don't change anything)
header = """<svg version="1.1" width="1000" height="1000"
xmlns="http://www.w3.org/2000/svg">""";
footer = """</svg>""";
offsetx = 500;
offsety = 500;

#Atom wrapper class for the atom struct
class Atom:
    def __init__(self, c_atom) -> None:
        self.atom = c_atom
        self.z = self.atom.z
    # string function
    def __str__(self) -> str:
        return '{} {} {} {}\n' .format(str(self.atom.element), str(self.atom.x), str(self.atom.y), str(self.atom.z))
    # svg method to convert an Atom into an Atom svg file
    def svg(self) -> str: #don't change spacing
        
        if self.atom.element in radius and self.atom.element in element_name:
            return ' <circle cx="%.2f" cy="%.2f" r="%d" fill="url(#%s)"/>\n' % (self.atom.x * 100.0 + offsetx,
            self.atom.y * 100.0 + offsety, radius[self.atom.element], element_name[self.atom.element])
        else: # if an element doesn't exist in the dictionary, use the default element 'ZZ'
           return ' <circle cx="%.2f" cy="%.2f" r="%d" fill="url(#%s)"/>\n' % (self.atom.x * 100.0 + offsetx,
            self.atom.y * 100.0 + offsety, radius["ZZ"], element_name["ZZ"]) 
    
# Bond wrapper class for the bond struct
class Bond:
    def __init__(self, c_bond) -> None:
        self.bond = c_bond
        self.z = self.bond.z
    # string function
    def __str__(self) -> str: # displays inforamtion about bond elements
        return 'a1 = {} a2 = {} \nepairs = {} \nx1 = {} x2 = {} \ny1 = {} y2 = {}\nz = {}\nlen ={} \ndx = {} dy = {}\n'.format(str(self.bond.a1), str(self.bond.a2), str(self.bond.epairs),
        str(self.bond.x1), str(self.bond.x2), str(self.bond.y1), str(self.bond.y2), str(self.bond.z), str(self.bond.len), str(self.bond.dx), str(self.bond.dy))
    def svg(self) -> str:
        dy = self.bond.dy
        dx = self.bond.dx
        
        return ' <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="green"/>\n'\
        % (self.bond.x1 * 100.0 + offsetx + dy * 10, self.bond.y1 * 100 + offsety - dx * 10,
        self.bond.x1 * 100.0 + offsetx - dy * 10, self.bond.y1 * 100 + offsety + dx * 10,
        self.bond.x2 * 100.0 + offsetx - dy * 10, self.bond.y2 * 100 + offsety + dx * 10,
        self.bond.x2 * 100.0 + offsetx + dy * 10, self.bond.y2 * 100 + offsety - dx * 10)

#note how this is a sub class (inheritence)
class Molecule(molecule.molecule):
    def __init__(self) -> None:
        super().__init__()
    # string function
    def __str__(self) -> str:
        returnString = ""
        
        for i in range(self.atom_no):
            returnString += str(Atom(self.get_atom(i)))
            
        for i in range(self.bond_no):
            returnString += str(Bond(self.get_bond(i)))
        
        return returnString
    # method to create the svg representation of the molecule
    def svg(self) -> str:
        # creating a string to return
        outputSvg = ""

        outputSvg += header
        
        # iterating through atoms and bonds, adding in terms of increasing z value (like the final pass in merge sort merging)
        curAtom, curBond = 0, 0

        while curAtom < self.atom_no and curBond < self.bond_no:
            if (self.get_atom(curAtom).z < self.get_bond(curBond).z):
                outputSvg += Atom(self.get_atom(curAtom)).svg()
                curAtom += 1
            else:
                outputSvg += Bond(self.get_bond(curBond)).svg()
                curBond += 1

        # now if iterating through remainder of array if they have not all been added yet
        if curAtom < self.atom_no:
            while curAtom < self.atom_no:
                outputSvg += Atom(self.get_atom(curAtom)).svg()
                curAtom += 1
        elif curBond < self.bond_no:
            while curBond < self.bond_no:
                outputSvg += Bond(self.get_bond(curBond)).svg()
                curBond += 1

        outputSvg += footer

        return outputSvg
    #takes a valid a file object, reads in the info and outputs it into the molecule
    def parse(self, file) -> None:
        fileContent = file.readlines()

        # getting how many atoms and bonds are in file from this line (getting first and second numbers)
        # source: https://www.geeksforgeeks.org/python-extract-numbers-from-string/
        lineCount = 3

        curLine = fileContent[lineCount]
        
        temp = re.findall(r'\d+', curLine)
        res = list(map(int, temp))

        atomsToAdd = res[0]
        bondsToAdd = res[1]

        lineCount += 1

        # now appending atoms and bonds
        for i in range(lineCount, lineCount + atomsToAdd):
            curLine = fileContent[i].split(" ")
            
            # iterating through split strings

            elementsAdded = 0
            elementsList = []

            for j in range (0, len(curLine)):
                if curLine[j] != "" and elementsAdded < 3:
                    elementsList.append(j)
                    elementsAdded += 1
                elif elementsAdded == 3 and curLine[j].isalpha():
                    elementsList.append(j)
                    elementsAdded += 1

            self.append_atom(curLine[elementsList[3]], float(curLine[elementsList[0]]), float(curLine[elementsList[1]]), float(curLine[elementsList[2]]))

        lineCount += atomsToAdd

        # now parsing out bonds out of the sdf file and appending them
        for i in range(lineCount, lineCount + bondsToAdd):
            curLine = fileContent[i].split(" ")

            elementsAdded = 0
            elementsList = []

            for j in range (len(curLine)):
                if curLine[j].isnumeric():
                    elementsList.append(j)
                    elementsAdded += 1
                    
                    # leave loop once we have reached 3 elements
                    if elementsAdded >= 3:
                        break
                    
            # note how epairs was typecasted to an integer, not a character (stored as character, but can be interpreted as an integer
            # update from A3 -- subtracting atom indices so that we start counting from zero instead of 1 (like how the sdf files are)
            
            self.append_bond(int(curLine[elementsList[0]]) - 1, int(curLine[elementsList[1]]) - 1, int(curLine[elementsList[2]]))