elementsList = []; // global variable

$(document).ready( 
    /* this defines a function that gets called after the document is in memory */
    function() {
      // setting default values for the form
      $("#elementNumberInput").val(0),
      $("#radiusInput").val(25),

      /* add a click handler for our button */
      $("#addButton").click(
        function() {
          // creating form information to send to the webserver (AJAX)
            const formInfo = {
              elementNumber: $("#elementNumberInput").val(),
              elementCode: $("#elementCodeInput").val(),
              elementName: $("#elementName").val(),
              colour1: ($("#colour1In").val()).substring(1),
              colour2: ($("#colour2In").val()).substring(1),
              colour3: ($("#colour3In").val()).substring(1),
              radius: $("#radiusInput").val(),
            }

            // checking to make sure that we have valid inputs in the fields
            try {
              elementNumberInt = parseInt(formInfo.elementNumber);
              radiusFloat = parseFloat(formInfo.radius);
            
              if (isNaN(elementNumberInt) || isNaN(radiusFloat)) {
                throw "Enter a number in your element number and radius input."
              }

              if (!formInfo.elementCode || !formInfo.elementName) {
                throw "Wrong element code and/or name.";
              }

              if (formInfo.elementCode.length > 3 || formInfo.elementName.length > 32) {
                throw "Element code/name too long";
              }

              // now need to check if there is an issue with the element code being the same
              // if index is found (meaning element code already exists, throw an exception)
              const index = elementsList.indexOf(formInfo.elementCode);

              if (index > -1) {
                throw "Element already exists in table."
              }

              // now checking to for injections
              if (formInfo.elementName.search("DELETE") > - 1 || formInfo.elementName.search("delete") > -1
              || formInfo.elementName.search("DROP") > -1 || formInfo.elementName.search("drop") > -1 || formInfo.elementName.search(";") > -1
              || formInfo.elementName.search("\"") > -1) {
                console.log(formInfo.elementName);
                throw "Error. Included 'delete', 'drop', '\"', ';' in name."
              }

              // sending form info
              $.post("/elementForm.html", formInfo)

              // will add note, avoiding a request to server (might need to test this more)
              const newElementArray = [formInfo.elementNumber, formInfo.elementCode, formInfo.elementName, formInfo.colour1, formInfo.colour2,
                                      formInfo.colour3, formInfo.radius];

              addTableElement(newElementArray);
              $("#dialog").text("Added element.");
            } catch (err) {
              $("#dialog").text(err);
            }
        }
      );
        // sets up an event handler to remove an element from screen and from webserver
        addAllTableElements();
    }
  );

  // gets all list elements and adds them into a list on the HTML page
  function addAllTableElements() {
    // getting all the currently loaded elements in the database, and posting them
    $.get("/elementsRetrieval", function(data, status ) {   
      elementsList = JSON.parse(data);
      elementsList.forEach(addTableElement)
    });
  }

  // adds a list element (has multiple values) when called
  function addTableElement(info) {
    let number = $("<td><td>").text(info[0]);
    let code = $("<td><td>").text(info[1]);
    let name = $("<td><td>").text(info[2]);
    let colour1 = $("<td><td>");
    let colour2 = $("<td><td>");
    let colour3 = $("<td><td>");
    let radius = $("<td><td>").text(info[6]);
    let removeButton = $("<input type='button' class='elementRMButton'>").val("-"); // rm for remove
    let newRow = $("<tr></tr>");

    // don't know why I had to remove a second child, but this was the workaround
    number = number[0];
    code = code[0];
    name = name[0];
    colour1 = colour1[0];
    colour2 = colour2[0];
    colour3 = colour3[0];
    radius = radius[0];

    $(colour1).css("background-color", "#" + info[3]);
    $(colour2).css("background-color", "#" + info[4]);
    $(colour3).css("background-color", "#" + info[5]);

    // adding event handler for the button (removal of list element, and for removal from the webserver)
    $(removeButton).click(
      function() {
        newRow.remove();

        // now we will remove the element from the webserver and from the 
        $.post("/removeElement", $(code).text());

        // removing index from list
        // source for this code snippet: https://stackoverflow.com/questions/5767325/how-can-i-remove-a-specific-item-from-an-array-in-javascript
        const index = elementsList.indexOf($(code).text());

        if (index > -1) { // only splice array when item is found
          elementsList.splice(index, 1); // 2nd parameter means remove one item only
        }
      }
    )

    // appending the wrapper element with the button and list information included
    newRow.append(number);
    newRow.append(code);
    newRow.append(name);
    newRow.append(colour1);
    newRow.append(colour2);
    newRow.append(colour3);
    newRow.append(radius);
    newRow.append(removeButton);

    $("#elementsTable").append(newRow);

    // pushing on added element onto global list
    text = $(code).text();
    elementsList.push(String(text));
  }
  
