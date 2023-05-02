$(document).ready(
    function() {
        // adding molecules and listeners
        addMolecules(),
        $("#rotateX").val(0);
        $("#rotateY").val(0);
        $("#rotateZ").val(0);
        $("#x").prop('checked',true);
        $("#rotateX").attr("readonly", false);
        $("#rotateY").attr("readonly", true);
        $("#rotateZ").attr("readonly", true);

        $("#viewButton").click(
            // will get value, and then output the svg of said file
            function() {
                name = $("input[type='radio'][name='molChoice']:checked").val();

                const direction  = $("input[type='radio'][name='degChoice']:checked").val();

                // getting degrees so that we can write the molecule
                if (direction == "x") {
                    deg = $("#rotateX").val();
                } else if (direction == "y") {
                    deg = $("#rotateY").val();
                } else {
                    deg = $("#rotateZ").val();
                }

		// testing to make sure an integer was input (otherwise just casting it)
		deg = parseInt(deg);

                const viewInfo = JSON.stringify({name, direction, deg});


                    // checking to see if rotation values are valid before sending request to the server
                    if (deg >= 0) {
                        // making sure that the name exists
                        if (name !== "undefined") {
                            // retrieves SVG file and appends it to the div to show it on the same page
                            $.post("/viewMolecule", viewInfo, function(data, status) { 
                                $("#moleculeImage").empty();
                                $("#moleculeImage").append(data);
                            });

                            $("#dialog").text("An image has been generated. See below.");  
                        } else {
                            $("#dialog").text("No molecule selected to display."); 
                        }
                        
                    } else {
                        $("#dialog").text("Wrong input for degrees.");
                    }
        });

        // event handler that resets other input fields for degrees
        $(".degChoice").click(
            function() {
                if ($("input[type='radio'][name='degChoice']:checked").val() == "x") {
                    $("#rotateY").val(0);
                    $("#rotateZ").val(0);

                    $("#rotateX").attr("readonly", false);
                    $("#rotateY").attr("readonly", true);
                    $("#rotateZ").attr("readonly", true);
                } else if ($("input[type='radio'][name='degChoice']:checked").val() == "y") {
                    $("#rotateX").val(0);
                    $("#rotateZ").val(0);

                    $("#rotateX").attr("readonly", true);
                    $("#rotateY").attr("readonly", false);
                    $("#rotateZ").attr("readonly", true);
                } else {
                    $("#rotateX").val(0);
                    $("#rotateY").val(0);

                    $("#rotateX").attr("readonly", true);
                    $("#rotateY").attr("readonly", true);
                    $("#rotateZ").attr("readonly", false);
                }
            }
        );
    },
);

// gets all the needed molecule values and adds them to the HTML UL list
function addMolecules() {
    $.get("/getMolecules", function(data, status) {
        moleculesList = data;
        // checks to make sure there is actually elements that exist (disabling buttons as needed)
        if (moleculesList.length > 0) {
            moleculesList.forEach(addMoleculeOption);
        }
    });
}

// adds an individual molecule to the list, setting up event listeners
function addMoleculeOption(infoList) {
    let newListName = infoList[0];
    let newListText = newListName + " (Atoms: " + infoList[1] + ", Bonds: " + infoList[2] + ")";
    let radioLabel = $("<label>").text(newListText);
    let radioButton = $("<input type='radio' name='molChoice'>");

    radioButton.val(infoList[0]);
    let option = $("<div></div>");
    
    option.append(radioButton);
    option.append(radioLabel);
    $("#molForm").prepend(option);
}
