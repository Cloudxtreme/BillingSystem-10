


// $(document).ready(function(){
//     $( "#patienthref" ).on('click',function() {
//         console.log("123");
//         href=$("#patienthrefhidden").attr('href');
//         window.location.href = href;
//     });
//     $( "#payerhref" ).on('click',function() {
//         console.log("456");
//         href=$("#payerhrefhidden").attr('href');
//         window.location.href = href;
//     });
// });

var butt_m="<button type=\"button\" class=\"btn btn-primary dropButton\" >Modified</button>"+
                "<button type=\"button\" class=\"btn btn-primary dropdown-toggle dropButton2\" data-toggle=\"dropdown\">"+
                    "<span class=\"caret\"></span>"+
                    "<span class=\"sr-only\">Toggle Dropdown</span>"+
                "</button>"+
                "<ul class=\"dropdown-menu\" role=\"menu\">"+
                    "<li><a href=\"?num_m=5&amp;num_c={{display_rows_c}}&amp;num_d={{display_rows_d}}&amp;"+console.log(this)
                    +"=1\">5</a></li>"+
                    "<li><a href=\"?num_m=10&amp;num_c={{display_rows_c}}&amp;num_d={{display_rows_d}}&amp;patient=1\">10 (default)</a></li>"+
                    "<li><a href=\"?num_m=25&amp;num_c={{display_rows_c}}&amp;num_d={{display_rows_d}}&amp;patient=1\">25</a></li>"+
                    "<li><a href=\"?num_m=all&amp;num_c={{display_rows_c}}&amp;num_d={{display_rows_d}}&amp;patient=1\">All</a></li>"+
                "</ul><p></p>";


$(document).ready(function(){
    $(".mod").html(butt_m);
});



$(document).ready(function(){
    $(function(){
        $(".myTable").tablesorter();
    });

});


$(document).ready(function(){
    var this_js_script = $('script[src*=audit_log]');
    if(typeof this_js_script.attr('display') != 'undefined'){
        var display = this_js_script.attr('display');
        console.log(display);
        if(display.localeCompare("patient")==0){
            $( "#patienthref" ).trigger( "click" );
        }
        else if(display.localeCompare("payer")==0){
            $( "#payerhref" ).trigger( "click" );
        }
        else if(display.localeCompare("insurance")==0){
            $( "#insurancehref" ).trigger( "click" );
        }
    }
});

$(document).ready(function(){
    var this_js_script = $('script[src*=audit_log]');
    var display_rows = this_js_script.attr('datamy');
    
    function removeClassLi(){
        $("#_5").removeClass("active");
        $("#_10").removeClass("active");
        $("#_25").removeClass("active");
        $("#_100").removeClass("active");
    }
    $(function(){
        var i=display_rows;
        if(i==5){
            $(".page-size").html("5");
            removeClassLi();
            $("#_5").addClass("active");
        }
        else if(i==10){
            $(".page-size").html("10");
            removeClassLi();
            $("#_10").addClass("active");
        }
        else if(i==25){
            $(".page-size").html("25");
            removeClassLi();
            $("#_25").addClass("active");
        }else if(i==100){
            $(".page-size").html("100");
            removeClassLi();
            $("#_100").addClass("active");
        }else{
            $(".page-size").html("10");
            removeClassLi();
            $("#_10").addClass("active");
        }

    });

});

