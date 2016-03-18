

$(document).ready(function(){
    $(function(){
        var this_js_script = $('script[src*=audit_log]');
        $(".m").children(".btn-group").children(".dropButton").html(this_js_script.attr('row_m')+" Entries");
        $(".c").children(".btn-group").children(".dropButton").html(this_js_script.attr('row_c')+" Entries");
        $(".d").children(".btn-group").children(".dropButton").html(this_js_script.attr('row_d')+" Entries");
    });

});


$(document).ready(function(){
    $(function(){
        $(".myTable").tablesorter();
    });

});

$(document).ready(function(){
    var this_js_script = $('script[src*=audit_log]');
    $('#patienthref').on('click', function(){
        $("#fillMe").html(replaceMe("patient"));
    });
    $('#payerhref').on('click', function(){
        $("#fillMe").html(replaceMe("payer"));
    });
    $('#insurancehref').on('click', function(){
        $("#fillMe").html(replaceMe("insurance"));
    });
    $('#providerhref').on('click', function(){
        $("#fillMe").html(replaceMe("provider"));
    });
    $('#rphref').on('click', function(){
        $("#fillMe").html(replaceMe("rp"));
    });
    $('#cpthref').on('click', function(){
        $("#fillMe").html(replaceMe("cpt"));
    });
    $('#dxhref').on('click', function(){
        $("#fillMe").html(replaceMe("dx"));
    });

    // Replace text in page dropdown
    $('.changeDropdownContent').on('click', function(){
        $("#showEntriesNav").html(showEntry(this_js_script.attr('row_m')));
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
        else if(display.localeCompare("provider")==0){
            $( "#providerhref" ).trigger( "click" );
        }
        else if(display.localeCompare("cpt")==0){
            $( "#cpthref" ).trigger( "click" );
        }
        else if(display.localeCompare("dx")==0){
            $( "#dxhref" ).trigger( "click" );
        }
        else if(display.localeCompare("rp")==0){
            $( "#rphref" ).trigger( "click" );
        }
    }
});

function showEntry(ele){
    return 'Show '+ele+' Entries';
}

function replaceMe(ele){
    var dump = '<a href="#" data-toggle="dropdown"><strong id="showEntriesNav">Show 10 Entries</strong><span class="caret"></span></a>'+
                                '                    <ul class="dropdown-menu" role="menu">'+
                                '                        <li><a href="?num_m=5&num_c=5&num_d=5&'+ele+'=1">5</a></li>'+
                                '                        <li><a href="?num_m=10&num_c=10&num_d=10&'+ele+'=1">10 (default)</a></li>'+
                                '                        <li><a href="?num_m=25&num_c=25&num_d=15&'+ele+'=1">25</a></li>'+
                                '                        <li><a href="?num_m=all&num_c=all&num_d=all&'+ele+'=1">All</a></li>'+
                                '                    </ul>';
    return dump
}






// $(document).ready(function(){
//     var this_js_script = $('script[src*=audit_log]');
//     var display_rows = this_js_script.attr('datamy');
    
//     function removeClassLi(){
//         $("#_5").removeClass("active");
//         $("#_10").removeClass("active");
//         $("#_25").removeClass("active");
//         $("#_100").removeClass("active");
//     }
//     $(function(){
//         var i=display_rows;
//         if(i==5){
//             $(".page-size").html("5");
//             removeClassLi();
//             $("#_5").addClass("active");
//         }
//         else if(i==10){
//             $(".page-size").html("10");
//             removeClassLi();
//             $("#_10").addClass("active");
//         }
//         else if(i==25){
//             $(".page-size").html("25");
//             removeClassLi();
//             $("#_25").addClass("active");
//         }else if(i==100){
//             $(".page-size").html("100");
//             removeClassLi();
//             $("#_100").addClass("active");
//         }else{
//             $(".page-size").html("10");
//             removeClassLi();
//             $("#_10").addClass("active");
//         }

//     });

// });

