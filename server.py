import sys
import io
from http.server import HTTPServer, BaseHTTPRequestHandler
from MolDisplay import Molecule # changed this from importing *
import MolDisplay
import molsql
import urllib
import molecule
import json # needed for data

publicFiles = ["/fileUpload.html", "/elements.html", "/elementsScripts.js", "/fileUploadScripts.js", "/moleculeView.html", 
               "/moleculeViewScripts.js", "/", "/styles.css", "/index.html"]

# class that takes in requests from a webserver and uses the user input to compute the images corresponding to the data provided
class RequestHandler(BaseHTTPRequestHandler):
    # implemenation to post the interactive webpage
    def do_GET(self):
        print(self.path)
        
        if self.path == "/":
            self.path = "/index.html"
        
        if self.path in publicFiles:
            pathString = self.path.split(".")
            fileType = "text/" + pathString[1]
            
            self.send_response(200)
            self.send_header("Content-type", fileType) # sending header
            
            # reading in file HTML
            fp = open(self.path[1:])
            webPage = fp.read()
            
            fp.close()
            
            self.send_header("Content-length", len(webPage))
            self.end_headers()
            
            self.wfile.write(bytes(webPage, "utf-8"))
        # used to retrieve elements from the webserver for JS output
        elif self.path == "/elementsRetrieval":
            elementValues = str(db.element_name())
            elements = db.getElements()
            elementsJSON = json.dumps(elements)

            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/plain" )
            self.send_header( "Content-length", len(elementsJSON) )
            self.end_headers()

            self.wfile.write(bytes(elementsJSON, "utf-8" ) );
        # supposed to get all the molecules on the webserver and and return their names (which are unique in the table), 
        # atom counts, and bond counts
        elif self.path == "/getMolecules":
            loadedMolecules = []
            names = []
            moleculeInfo = []
            
            
            # getting all the molecules that are needed
            namesTuples = db.getMoleculeNames()
            numNames = len(namesTuples)

            for i in range(numNames):
                names.append(namesTuples[i][0])
                
            for i in range(numNames):
                loadedMolecules.append(db.load_mol(names[i]))
                
            # now we will create the list of valuable information about molecules to send to our webpage
            for i in range(numNames):
                moleculeInfo.append([names[i], loadedMolecules[i].atom_no, loadedMolecules[i].bond_no])
                
            moleculeInfo = json.dumps(moleculeInfo)
                
            # now sending out the data to the database
            
            self.send_response(200)
            
            self.send_header("Content-type", "text/json") # FIXME not sure if JSON will work
            self.send_header( "Content-length", len(str(moleculeInfo))) 
            self.end_headers()
            
            self.wfile.write(bytes(str(moleculeInfo), "utf-8" ) );
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("404: not found", "utf-8"))
    # implementation to post the specfied svg file -- FIXME be careful with this, it seems to be having occasional issues
    def do_POST(self):
        # it proccess the file that was sent (unless there was no file attached, this needs to be fixed)
        if self.path == "/moleculeUpload":
            errorMessage = ""
            # want to take rfile and pass it to add_molecule to parse
            self.send_response(200)
            try:
                contentLength = int(self.headers.get('Content-length'))
                postContent = io.BytesIO(self.rfile.read(contentLength))
                self.rfile = io.TextIOWrapper(postContent, "utf-8")
                    
                moleculeName = self.rfile.readline()
                moleculeName = moleculeName[:-1] #fixme try later when adding newlines
                
                # checking for malicious inputs (SQL issues) -- note that we check for malicious input in parse for the file input
                if (moleculeName.find("DELETE") > -1 or moleculeName.find("DROP") > -1 or moleculeName.find("drop") > -1 or moleculeName.find("delete") > -1 or moleculeName.find("\"") > -1 or moleculeName.find(";") > -1):
                        errorMessage = "Issue with name (you included 'delete', 'drop', ';', or '\"' in it) - possibly malicious."
                        raise Exception("Possible malicious name.")
                
                # also checking to see if name already exists in database (name must be unique)
                print(db.getMoleculeNames())
                
                names = []
                namesTuples = db.getMoleculeNames()
                numNames = len(namesTuples)

                for i in range(numNames):
                    names.append(namesTuples[i][0])
                
                if (moleculeName in names):
                    errorMessage = "A molecule named '" + moleculeName + "' is already in the database."
                    raise Exception(errorMessage)
                
                # now adding the molecule with the file pointer
        
                db.add_molecule(moleculeName, self.rfile)
                
                MolDisplay.radius = db.radius()
                MolDisplay.element_name = db.element_name()
                MolDisplay.header += db.radial_gradients()
            # if the file is bad, it writes an error message (FIXME -- I just added this)
            except:
                if (errorMessage == ""):
                    errorMessage = "An error occurred with uploading the molecule."
        
                print(errorMessage)
                self.send_header("Content-type", "text/plain")
                self.send_header("Content-length", len(errorMessage))
                
                self.wfile.write(bytes(errorMessage, 'utf-8'))
            
            self.end_headers()      
        # inserts element into tables upon request
        elif self.path == "/elementForm.html":
            self.send_response(200)
            
            contentLength = int(self.headers.get('Content-length'))
            postContent = self.rfile.read(contentLength)
            
            # copied this from Professor Kremer's example, parseses out contents
            postVars = urllib.parse.parse_qs(postContent.decode('utf-8'))
            
            # inserting values into table (note that we're indexing the 0th element b/c this returns a list of all mapped elements
            # in the dictionary)
            db['Elements'] = (postVars['elementNumber'][0], postVars['elementCode'][0], postVars['elementName'][0],
                           postVars['colour1'][0], postVars['colour2'][0], postVars['colour3'][0], postVars['radius'][0])
        # removes element from data base upon request
        elif self.path == "/removeElement":
            self.send_response(200)
            
            # extracting element code to find element to remove
            contentLength = int(self.headers.get('Content-length'))
            postContent = self.rfile.read(contentLength)
            postContent = postContent.decode('utf-8')
            
            elementCode = postContent[0]
            
            db.removeElement(elementCode)
        # posts the molecule on the screen, given the degrees
        elif self.path == "/viewMolecule":
            # reading in JSON, converting it to a Python dictionary to get information about the file
            contentLength = int(self.headers.get('Content-length'))
            viewInfo = self.rfile.read(contentLength).decode('utf-8')
            viewInfo = json.loads(viewInfo)
    
            loadedMol = db.load_mol(viewInfo['name'])
            
            # transforming matrix based on degrees given (only rotating on one axis -- this was based on what Kremer said in lecture) 
            if (int(viewInfo['deg']) > 0):   
                if (viewInfo['direction'] == "x"):
                    mx = molecule.mx_wrapper(int(viewInfo['deg']),0,0)
                elif (viewInfo['direction'] == "y"):
                    mx = molecule.mx_wrapper(0,int(viewInfo['deg']),0)
                else:
                    mx = molecule.mx_wrapper(0,0,int(viewInfo['deg']))
                
                loadedMol.xform(mx.xform_matrix)
            
            # doing sorting after so that z-values are properly ordered
            loadedMol.sort()
            
            # setting up display functionality with dictionaries
            MolDisplay.radius = db.radius()
            MolDisplay.element_name = db.element_name()
            MolDisplay.header += db.radial_gradients()
            
            image = loadedMol.svg()
            
            self.send_response(200)
            self.send_header("Content-type", "text/plain") # fixme change to svg
            self.send_header("Content-length", len(image))
            self.end_headers()
            
            self.wfile.write(bytes(image, "utf-8"))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("404: not found", "utf-8"))
            
# this is used to initialize the webserver with a command line argument (only do it if the minimum amount of command line arguments was provided)
try:
    db = molsql.Database(reset=False)
    db.create_tables()
    
    # note that as long as the database resets (and we don't have a default element), these will be needed
    # db['Elements'] = ( 1, 'H', 'Hydrogen', 'FFFFFF', '050505', '020202', 25 );
    # db['Elements'] = ( 6, 'C', 'Carbon', '808080', '010101', '000000', 40 );
    # db['Elements'] = ( 7, 'N', 'Nitrogen', '0000FF', '000005', '000002', 40 );
    # db['Elements'] = ( 8, 'O', 'Oxygen', 'FF0000', '050000', '020000', 40 );    
    
    httpd = HTTPServer( ( 'localhost', int(sys.argv[1]) ), RequestHandler )
    httpd.serve_forever()
    
except KeyboardInterrupt:
    print("Web server was terminated.")
                
            