# Sinclair MolViewer
This is a full-stack web application that I made for CIS*2750 (Software Systems Development and Integration) at the University of Guelph.

The Sinclair MolViewer takes uploaded SDF files of molecules, and creates a corresponding SVG image file to represent them on the website. It outputs the SVG file to the webserver, allowing
the user to rotate it as they want to see the molecule from different angles. The user also has the ability to choose the size and colours of different atom elements.

## **Technologies Used**
Front-End: JavaScript, JQuery, HTML/CSS  
Back-End: Python, C, Swig, SQLite

With the front-end, JQuery was used for the majority of the JavaScript programming, while HTML and CSS was used to design and structure the webpages.  

On the back-end, a C library was programmed to perform molecule-specific computations quickly, which was used by the Python scripts in the project. Python was used to interface with the SQLite database and perform back-end web-server operations.  

The Swig file used to allow my program to interface the C library with Python was created by Professor Kremer.

## Images

*Determining how an Oxygen Element will Look*
![Screenshot 2023-05-01 205105](https://user-images.githubusercontent.com/89956249/235558402-e46450fd-e7ab-440a-83a7-53c263d267b3.png)

*Uploading a Molecule*
![Screenshot 2023-05-01 205253](https://user-images.githubusercontent.com/89956249/235558521-4487d0f3-ac88-45c1-9367-f0ea98186ded.png)

*Molecule Viewer Interface*
![Screenshot 2023-05-01 210923](https://user-images.githubusercontent.com/89956249/235558830-783ba829-f0bf-409b-9f97-6462bf89091a.png)

*Caffeine Molecule*
![Screenshot 2023-05-01 205454](https://user-images.githubusercontent.com/89956249/235558936-8b316c3a-1fd4-43fe-8616-efc691bcf0c7.png)

*Rotating the Caffeine Molecule*
![Screenshot 2023-05-01 211316](https://user-images.githubusercontent.com/89956249/235558693-a59ec1f2-0964-4a19-9be0-b301defe0466.png)
