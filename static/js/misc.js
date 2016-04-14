// Automatically add trailing two decimals for input type number
$(document).ready(function() {
    $("input[type=number]").each(function() {

        // Add trailing decimals only if the input is meant
        // to be for decimal type
        if($(this)[0].hasAttribute("step")) {
            // Let default decimal be two digits but try to get
            // custom length from "step" attribute if it has one.
            var decimal = 2;
            var step = $(this).prop("step");
            var i = step.indexOf(".");
            if(i > -1) {
                step = step.substr(i + 1);
                decimal = step.length;
            }

            $(this).blur(function() {
                var value = $(this).val();
                if(value || value === 0)
                    $(this).val(parseFloat(value).toFixed(decimal));
            });
        }
    });
});

// Function to get parameter from URL
function getUrlParameter(sParam) {
    var sPageURL = decodeURIComponent(window.location.search.substring(1)),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : sParameterName[1];
        }
    }
};
