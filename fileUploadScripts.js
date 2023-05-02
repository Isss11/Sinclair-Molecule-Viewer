$(document).ready(
    function() {
        $("#fileSubmitButton").click(
            function(e) {
                // on click, read the file's text contents and 
                // send that to the server

                // getting file pointer and creating file reader
                let file = $("#sdf_file").prop('files')[0];

                if (!file) {
                    $("#dialog").text("Please input a file.");
                }

                let reader = new FileReader();
                reader.readAsText(file);

                // have to set up a function for this readAsText function
                // https://stackoverflow.com/questions/28658388/filereader-result-return-null
                reader.onload = function(e) {
                    if ($("#moleculeNameInput").val()) {
                        var fileInfo = $("#moleculeNameInput").val() + "\n";
                        fileInfo += reader.result;
                        
                        $("#dialog").text("Uploading file.")
                        // now after getting loaded content, we have to submit it to the server
                        $.post("/moleculeUpload", fileInfo, function(data) {
                            // outputing error messages
                            if (data) {
                                $("#dialog").text(data.split(".")[0] + ".");
                            } else {
                                alert("File upload was successful.");
                                $("#dialog").text("Ready to upload another file.");
                            }
                        });
                    } else {
                        $("#dialog").text("Please input a name.");
                    }
                };

            }
        );
    },
);