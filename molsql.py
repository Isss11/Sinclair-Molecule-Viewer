import sqlite3
import os
import MolDisplay

# creating as some sort of constant for an element
radialGradientSVG = """
    <radialGradient id="%s" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%">
        <stop offset="0%%" stop-color="#%s"/>
        <stop offset="50%%" stop-color="#%s"/>
        <stop offset="100%%" stop-color="#%s"/>
    </radialGradient>""";

class Database:
    # starts up conn with local server
    def __init__(self, reset=False) -> None:
        if reset and os.path.exists('molecules.db'):
            os.remove('molecules.db')
        
        self.conn = sqlite3.connect('molecules.db')
        self.cur = self.conn.cursor()
        
    # creates all the necessary tables for the data base   
    def create_tables(self):           
        # Elements table creation
        # on each table, we're making sure it has been created thus far
        
        self.cur.execute("""SELECT COUNT (*) FROM sqlite_master WHERE type="table" AND name='Elements'""")
        tableExists = self.cur.fetchall()[0][0]
        
        if (not tableExists):
            self.conn.execute("""CREATE TABLE Elements (
                                        ELEMENT_NO  INTEGER NOT NULL,
                                        ELEMENT_CODE VARCHAR(3) NOT NULL,
                                        ELEMENT_NAME VARCHAR(32) NOT NULL,
                                        COLOUR1 CHAR(6) NOT NULL,
                                        COLOUR2 CHAR(6) NOT NULL,
                                        COLOUR3 CHAR(6) NOT NULL,
                                        RADIUS  DECIMAL(3) NOT NULL,
                                        PRIMARY KEY (ELEMENT_CODE));""")
        
        # Atoms table creation
        self.cur.execute("""SELECT COUNT (*) FROM sqlite_master WHERE type="table" AND name='Atoms'""")
        tableExists = self.cur.fetchall()[0][0]
        
        if (not tableExists):
            self.conn.execute("""CREATE TABLE Atoms (
                                        ATOM_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                        ELEMENT_CODE VARCHAR(3) NOT NULL, 
                                        X   DECIMAL(7,4) NOT NULL,
                                        Y   DECIMAL(7,4) NOT NULL,
                                        Z   DECIMAL(7,4) NOT NULL,
                                        FOREIGN KEY (ELEMENT_CODE) REFERENCES Elements);""")
        

        # Bonds table creation
        self.cur.execute("""SELECT COUNT (*) FROM sqlite_master WHERE type="table" AND name='Bonds'""")
        tableExists = self.cur.fetchall()[0][0]
        
        if (not tableExists):
            self.conn.execute("""CREATE TABLE Bonds (
                                        BOND_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                        A1 INTEGER NOT NULL,
                                        A2 INTEGER NOT NULL,
                                        EPAIRS INTEGER NOT NULL);""")
        
        # creating Molecules table 
        self.cur.execute("""SELECT COUNT (*) FROM sqlite_master WHERE type="table" AND name='Molecules'""")
        tableExists = self.cur.fetchall()[0][0]
        
        if (not tableExists):
            self.conn.execute("""CREATE TABLE Molecules (
                                        MOLECULE_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                        NAME    TEXT UNIQUE NOT NULL);""")
        
        # MoleculeAtom creation
        self.cur.execute("""SELECT COUNT (*) FROM sqlite_master WHERE type="table" AND name='MoleculeAtom'""")
        tableExists = self.cur.fetchall()[0][0]
        
        if (not tableExists):
            self.conn.execute("""CREATE TABLE MoleculeAtom (
                                        MOLECULE_ID INTEGER NOT NULL,
                                        ATOM_ID INTEGER NOT NULL,
                                        PRIMARY KEY (MOLECULE_ID,ATOM_ID),
                                        FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules,
                                        FOREIGN KEY (ATOM_ID) REFERENCES Atoms);""")
        
        # MoleculeBond creation
        self.cur.execute("""SELECT COUNT (*) FROM sqlite_master WHERE type="table" AND name='MoleculeBond'""")
        tableExists = self.cur.fetchall()[0][0]
        
        if (not tableExists):
            self.conn.execute("""CREATE TABLE MoleculeBond (
                                        MOLECULE_ID INTEGER NOT NULL,
                                        BOND_ID INTEGER NOT NULL,
                                        PRIMARY KEY (MOLECULE_ID, BOND_ID),
                                        FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules,
                                        FOREIGN KEY (BOND_ID) REFERENCES Bonds);""")
        
    # this should provide a method to allow indexing of the table and set the values with a tuple
    def __setitem__(self, table, values): 
        try:
            # had to create if statements to allow autoincrement to work
            if (table == "Elements" or table == "MoleculeAtom" or table == "MoleculeBond"):
                self.conn.execute(f"INSERT INTO {table} VALUES {values};") # uses an fstring
            elif (table == "Atoms"):
                self.conn.execute("INSERT INTO Atoms (ELEMENT_CODE, X, Y, Z) VALUES (?, ?, ?, ?)", (values[0], values[1], values[2], values[3]))
            elif (table == "Bonds"):
                self.conn.execute("INSERT INTO Bonds (A1, A2, EPAIRS) VALUES (?, ?, ?)", (values[0], values[1], values[2]))
            elif (table == "Molecules"):
                self.conn.execute("INSERT INTO Molecules (NAME) VALUES (?)", (values[0],))
     
            self.conn.commit()
        except:
            print("An error occurred with inserting element into the specified table.")
        
    # inserts needed values into atoms table and then into MoleculeAtom
    def add_atom(self, molname, atom):
        
        self['Atoms'] = (atom.element, atom.x, atom.y, atom.z)
        
        # now trying to link Atoms table and MoleculeAtom table
        self.cur.execute("""SELECT Molecules.MOLECULE_ID FROM Molecules WHERE NAME = ?""", (molname,))     
        moleculeID = ((self.cur.fetchall())[0])[0]
        
        # getting ATOM_ID
        self.cur.execute("""SELECT Atoms.ATOM_ID FROM Atoms WHERE ELEMENT_CODE = ? AND X = ? AND Y = ? AND Z = ?;""",
                       (atom.element, atom.x, atom.y, atom.z))
        
        atomID = ((self.cur.fetchall())[-1])[0] # not sure if -1 is okay given randomness of ordering of queries
        
        self['MoleculeAtom'] = (moleculeID, atomID)
        
    # adds attributes of bonds, and links them to the table
    def add_bond(self, molname, bond):
        
        self['Bonds'] = (bond.a1, bond.a2, bond.epairs)
        
        # now trying to link Atoms table and MoleculeAtom table
        self.cur.execute("""SELECT Molecules.MOLECULE_ID FROM Molecules WHERE NAME = ?""", (molname,))     
        moleculeID = ((self.cur.fetchall())[0])[0]
        
        # getting BOND_ID
        self.cur.execute("""SELECT Bonds.BOND_ID FROM Bonds WHERE A1 = ? AND A2 = ? AND EPAIRS = ?;""",
                       (bond.a1, bond.a2, bond.epairs))
        
        bondID = ((self.cur.fetchall()[-1]))[0]
        
        self['MoleculeBond'] = (moleculeID, bondID)
    
    def add_molecule(self, name, fp):
        # parsing out file input
        moleculeToAdd = MolDisplay.Molecule()
        
        moleculeToAdd.parse(fp)
            
        self['Molecules'] = (name,)
            
        # now add atoms and bonds
        # adding atoms first
        for i in range(moleculeToAdd.atom_no):
            self.add_atom(name, moleculeToAdd.get_atom(i))
                
            # adding bonds
        for i in range(moleculeToAdd.bond_no):
            self.add_bond(name, moleculeToAdd.get_bond(i))
            
    # gets atom ID and converts it to an integer for comparison
    def getServerIDs(self, e):
        return int(e[0])
        
    # returns a MolDisplay.Molecule object that was loaded from the webserver    
    def load_mol(self, name):
        newMolecule = MolDisplay.Molecule()
        
        # doing an inner join
        self.cur.execute("""SELECT Atoms.ATOM_ID, Atoms.ELEMENT_CODE, Atoms.X, Atoms.Y, Atoms.Z FROM Molecules, 
                                MoleculeAtom, Atoms WHERE (Molecules.NAME = ? AND MoleculeAtom.MOLECULE_ID = Molecules.MOLECULE_ID
                                AND Atoms.ATOM_ID = MoleculeAtom.ATOM_ID)""", (name, ))
        
        # returns a list of atom items and sorts them by ATOM_ID
        atomsOutput = self.cur.fetchall()
        atomsOutput.sort(key=self.getServerIDs)
        
        # traversing through list in ascending order, appending atoms to molecule
        for i in atomsOutput:
            newMolecule.append_atom(i[1], i[2], i[3], i[4])
        
        # now getting bonds from the server and appending them in the same way
        # doing an inner join -- had to use DISINCT to not get triple output for some reason
        self.cur.execute("""SELECT Bonds.BOND_ID, Bonds.A1, Bonds.A2, Bonds.Epairs FROM Molecules, 
                                MoleculeBond, Bonds WHERE (Molecules.NAME = ? AND MoleculeBond.MOLECULE_ID = Molecules.MOLECULE_ID
                                AND Bonds.BOND_ID = MoleculeBond.BOND_ID)""", (name, ))
        
        bondsOutput = self.cur.fetchall()
        bondsOutput.sort(key=self.getServerIDs)
        
        # traversing through list to add bonds
        for i in bondsOutput:
            newMolecule.append_bond(i[1], i[2], i[3])
            
        return newMolecule
    
    # returns a Python dictionary mapping ELEMENT_CODE values to Radius values based on the elements table
    def radius(self):
        # getting ELEMENT_CODE and RADIUS values (from the Elements table) first to create a dictionary
        radiusDict = {}

        try:
            self.cur.execute("""SELECT ELEMENT_CODE, RADIUS FROM Elements""")
            combinations = self.cur.fetchall()
            
            # now creating Python dictionary (mapping ELEMENT_CODE values to RADIUS)
            
            for i in combinations:
                radiusDict.update({i[0]:i[1]})
                
            radiusDict.update({"ZZ":25})
        except:
            print("An error has occurred in the radius function.")
            
        return radiusDict
    
    # returns a Python dictionary mapping ELEMENT_CODE values to ELEMENT_NAME values based on the Elements table
    def element_name(self):
        # fetching needed data from the webserver
        nameDict = {}

        try:
            self.cur.execute("""SELECT ELEMENT_CODE, ELEMENT_NAME FROM Elements""")
            combinations = self.cur.fetchall()
            
            # now creating Python dictionary as stated in the function header comment
            
            
            for i in combinations:
                nameDict.update({i[0]:i[1]})
                
            nameDict.update({'ZZ':'Default'}) # adding in default
        except:
            print("An error has occurred with element_name.")
           
        return nameDict
           
    # returns a Python string with all the concatentations of the elements in the Elements table
    def radial_gradients(self):
        elementsString = ""
        
        try:
            self.cur.execute("""SELECT ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3 FROM Elements""")
            elementValues = self.cur.fetchall()
            
            for i in elementValues:
                elementsString += radialGradientSVG % (i[0], i[1], i[2], i[3])
                
            elementsString += radialGradientSVG % ("Default", "E965AA", "050000", "000002")
        except:
            print("An error has occurred with radial_gradients.")
            
        return elementsString
    
    # removes elements from the table, given the primary key element code
    def removeElement(self, elementCode):
        self.cur.execute("""DELETE FROM Elements WHERE (ELEMENT_CODE = ?)""", (elementCode,))
        self.conn.commit()
        
    # gets all the elements, and their corresponding table values
    def getElements(self):
        self.cur.execute("""SELECT ELEMENT_NO, ELEMENT_CODE, ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3, RADIUS FROM Elements""")
        elements = self.cur.fetchall()
    
        return elements
        
    # getting all the names of the molecules in the table so that we can load them in server.py
    def getMoleculeNames(self):
        self.cur.execute("""SELECT (NAME) FROM Molecules""")
        names = self.cur.fetchall()
        
        return names