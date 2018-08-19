$(document).ready(function() {
    // after the page elements are all loaded, then run the script
    // Set the input field with unique ID #email to a value

    // Ask for the lists of x0 and bounds
    $.getJSON('/parameters_data', function(data){

        var x0 = data[0]
        var bounds = data[1]

        for (let k = 1; k < x0.length; k += 1){

            // console.log("Entered function")
            // console.log(data)

            var lower_bound = "#lower_bound_" + k.toString();
            var value = "#value_" + k.toString();
            var upper_bound = "#upper_bound_" + k.toString();



            $(lower_bound).val(bounds[k - 1][0]);
            $(value).val(x0[k - 1]);
            $(upper_bound).val(bounds[k - 1][1]);

        }

    });


});