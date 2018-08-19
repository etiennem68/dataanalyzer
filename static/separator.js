$(document).ready(function (){
    $('#upload_separator').click(function (e) {

        // Get the value of the separator
        var value = $("#separator").val();

        // Create the JSON data to send to the url
        let separator = {
            separator: value
        };

        // Send the data
        $.getJSON('/separator', separator, function (response) {
            console.log(response['0'])
        });

        console.log(separator)

        // Prevent the page to reload
        e.preventDefault();
    });
});