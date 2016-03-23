
var tab="patient";
var sideTab="mod";


function startUp(){
    runThis();
    $("#auditContent").css( "display", "block" );
}
window.onload = startUp;

function runThis(){
    function modCreDel(){
        if($("#mod").hasClass("active")){
            return 'mod';
        }
        else if($("#del").hasClass("active")){
            return 'del';
        }
        else if($("#cre").hasClass("active")){
            return 'cre';
        }
        
    };

    function searchTable(ele){
        var this_js_script = $('script[src*=audit_log]');

        if(typeof ele == 'undefined'){
            ele=this_js_script.attr('display');
        }
        var disp=ele;

        $('#search').keyup(function() {
            // So that the correct url is generated on each keyup
            $("#fillMe").html(replaceMe(tab, sideTab, this_js_script.attr('row_m')));

            var $rows = $('#'+disp+' tbody tr');

            var val = $.trim($(this).val()).replace(/ +/g, ' ').toLowerCase();
            
            if(modCreDel()=="mod"){
                $rows.show().filter(function() {    
                    var text = $(this).text().replace(/\s+/g, ' ').toLowerCase();
                    return !~text.indexOf(val);
                }).hide();
            }else{
                $rows.show().not(':first').filter(function() {
                    var text = $(this).text().replace(/\s+/g, ' ').toLowerCase();
                    return !~text.indexOf(val);
                }).hide();
            }
        });
    }


    // Stylize text
    $(document).ready(function(){
        var $ele=$(".whatChanged"); 

        // console.log($ele.length);
        // console.log($ele[0]);
        // var r=$ele;
        // console.log(r[0].val());

        $("td.whatChanged").each(function (index,value){
            $(this).html($(this).html().replace(/_/g, ' '));
        });

        // for(i=0;i<$ele.length;i++){
        //     $ele[i].html($ele[i].html().replace(/_/g, ' '));
        // }
    });



    $(document).ready(function(){
        var this_js_script = $('script[src*=audit_log]');

        //serach at startup
        searchTable();

        $("#mod").click(function(){
            sideTab="mod";
            $('#search').keyup();
            $("#fillMe").html(replaceMe(this_js_script.attr('display'),"mod",this_js_script.attr('row_m')));
        });
        $("#cre").click(function(){
            sideTab="cre";
            $('#search').keyup();
            $("#fillMe").html(replaceMe(this_js_script.attr('display'),"cre",this_js_script.attr('row_m')));
        });
        $("#del").click(function(){
            sideTab="del";
            $('#search').keyup();
            $("#fillMe").html(replaceMe(this_js_script.attr('display'),"del",this_js_script.attr('row_m')));
        });

    });


    // Fill in search bar
    $(document).ready(function(){
        var this_js_script = $('script[src*=audit_log]');
        $("#search").val(this_js_script.attr('search'));
        $("#search").keyup();
    });


    $(document).ready(function(){
        $(function(){
            $(".myTable").tablesorter();
        });

    });

    $(document).ready(function(){
        var this_js_script = $('script[src*=audit_log]');

        // $("#showEntriesNav").html(showEntry(this_js_script.attr('row_m')));


        $('#patienthref').on('click', function(){
            tab="patient";
            $("#fillMe").html(replaceMe("patient",modCreDel(),this_js_script.attr('row_m')));
        });
        $('#payerhref').on('click', function(){
            tab="payer";
            $("#fillMe").html(replaceMe("payer",modCreDel(),this_js_script.attr('row_m')));
        });
        $('#insurancehref').on('click', function(){
            tab="insurance";
            $("#fillMe").html(replaceMe("insurance",modCreDel(),this_js_script.attr('row_m')));
        });
        $('#providerhref').on('click', function(){
            tab="provider";
            $("#fillMe").html(replaceMe("provider",modCreDel(),this_js_script.attr('row_m')));
        });
        $('#rphref').on('click', function(){
            tab="rp";
            $("#fillMe").html(replaceMe("rp",modCreDel(),this_js_script.attr('row_m')));
        });
        $('#cpthref').on('click', function(){
            tab="cpt";
            $("#fillMe").html(replaceMe("cpt",modCreDel(),this_js_script.attr('row_m')));
        });
        $('#dxhref').on('click', function(){
            tab="dx";
            $("#fillMe").html(replaceMe("dx",modCreDel(),this_js_script.attr('row_m')));
        });

        // Replace text in page dropdown

        $('.changeDropdownContent').on('click', function(){
            // send this!!!
            searchTable($(this).attr("href").substring(1));
            $("#search").keyup();
        });
        
    });


    $(document).ready(function(){
        var this_js_script = $('script[src*=audit_log]');
        if(typeof this_js_script.attr('typemcd') != 'undefined'){
            var display = this_js_script.attr('typemcd');
            if(display.localeCompare("mod")==0){
                $( "#mod a" ).trigger( "click" );
            }
            else if(display.localeCompare("cre")==0){
                $( "#cre a" ).trigger( "click" );
            }
            else if(display.localeCompare("del")==0){
                $( "#del a" ).trigger( "click" );
            }
        }
    });


    $(document).ready(function(){
        var this_js_script = $('script[src*=audit_log]');
        if(typeof this_js_script.attr('display') != 'undefined'){
            var display = this_js_script.attr('display');
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

    function replaceMe(ele, typemcd, entries){
        var srch="";
        if($("#search").val()!=""){
            srch=$("#search").val();
        }
        var dump = '<a href="#" data-toggle="dropdown"><strong id="showEntriesNav">Show '+entries+' Entries</strong><span class="caret"></span></a>'+
                                    '                    <ul class="dropdown-menu" role="menu">'+
                                    '                        <li><a href="?num_m=5&num_c=5&num_d=5&'+'typemcd='+typemcd+'&'+ele+'=1&'+'search='+srch+'">5</a></li>'+
                                    '                        <li><a href="?num_m=10&num_c=10&num_d=10&'+'typemcd='+typemcd+'&'+ele+'=1&'+'search='+srch+'">10 (default)</a></li>'+
                                    '                        <li><a href="?num_m=25&num_c=25&num_d=15&'+'typemcd='+typemcd+'&'+ele+'=1&'+'search='+srch+'">25</a></li>'+
                                    '                        <li><a href="?num_m=all&num_c=all&num_d=all&'+'typemcd='+typemcd+'&'+ele+'=1&'+'search='+srch+'">All</a></li>'+
                                    '                    </ul>';
        return dump
    }
}




