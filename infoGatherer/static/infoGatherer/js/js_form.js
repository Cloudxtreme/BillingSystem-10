function init(){
    
    // document.getElementById('show_hide').style.display='none';
    // document.getElementById('input_show_hide').style.display='none';

    // nav bars
    function hideAllNavs(){
        $("#patient").css('display','none');
        $("#insured").css('display','none');
        $("#physician").css('display','none');
    }
    function hideAllCLass(){
        $("#nav_patient").removeClass("active");
        $("#nav_insurance").removeClass("active");
        $("#nav_physician").removeClass("active");
    }
    $( "#nav_insurance" ).click(function() {
        hideAllNavs();
        hideAllCLass();
        $("#insured").css('display','block');
        $("#nav_insurance").addClass("active");
    });
    $( "#nav_patient" ).click(function() {
        hideAllNavs();
        hideAllCLass();
        $("#patient").css('display','block');
        $("#nav_patient").addClass("active");
    });
    $( "#nav_physician" ).click(function() {
        hideAllNavs();
        hideAllCLass();
        $("#physician").css('display','block');
        $("#nav_physician").addClass("active");
    });
    hideAllNavs();
    $("#patient").css('display','block');

    // Div tasgs
    var d = document.getElementsByClassName("fieldWrapper");
    for(i=0;i<d.length;i++){
        d[i].className+=" form-group";
    }

    // Label tags
    var d = document.getElementsByTagName("label");
    for(i=0;i<d.length;i++){
        d[i].className+=" control-label";
    }

    // Input tags
    var d = document.getElementsByTagName("input");
    for(i=0;i<d.length;i++){
        if(d[i].type !== 'checkbox')
            d[i].className+=" form-control";
            //d[i].setAttribute("required", "");
    }
    document.getElementById("id_pat_relation_emp").className="";
    document.getElementById("id_pat_relation_auto_accident").className="";
    document.getElementById("id_pat_relation_other_accident").className="";
    document.getElementById("id_insured_other_benifit_plan").className="";
    
    
    // Select tags
    var d = document.getElementsByTagName("select");
    for(i=0;i<d.length;i++){
        d[i].className+=" form-control";
    }

    // OnClick for 9 (a) ---- (d)
    document.getElementById("id_insured_other_benifit_plan").onclick=function(){if (document.getElementById('show_hide').style.display==='none'){document.getElementById('show_hide').style.display = "block"} else {document.getElementById('show_hide').style.display = "none"}}

    // Adding class to state # box
    document.getElementById("id_pat_auto_accident_state").className+=" input-sm";
    
    // Onlick state for Auto Accident
    document.getElementById("id_pat_relation_auto_accident").onclick=function(){if (document.getElementById('input_show_hide').style.display==='none'){document.getElementById('input_show_hide').style.display = "inline-block"} else {document.getElementById('input_show_hide').style.display = "none"}}

    //Filling default value
    $("#id_insured_other_insured_policy").val("NONE");

    // render page only after script has loaded
    document.getElementById("hideAll").style.display = "block";
            
    // Custom Validation
    jQuery.validator.addMethod("validation_diagnosis", function(value, element){
        
        if(value.charCodeAt(0)>=65 && value.charCodeAt(0)<=76){
            var s="#id_ICD_10_"+(value.charCodeAt(0)-"A".charCodeAt(0)+1).toString();
            // console.log(s);
            if($(s).val().length==0){
                return false;
            }
        }
        return true;
    }); 

    jQuery.validator.addMethod("validation_date", function(value, element){
        if(value.length==0){
            var num=$(element).attr("id").substr($(element).attr("id").length - 1);
            // console.log($("#id_cpt_code_"+num).val().length);
            if($("#id_cpt_code_"+num).val().length!=0){
                return false;
            }
        }
        return true;
    });

    // form validation
    $('form').validate({
        errorPlacement: function(error, element) {},
        ignore: [],
        rules: {
            pat_name: "required",
            pat_streetaddress: "required",
            pat_city: "required",
            pat_state: "required",
            pat_zip: "required",
            pat_telephone: {
                required: true,
                phoneUS: true
            },
            birth_date: {
                required: true,
                date: true
            },
            insured_idnumber: "required",
            insured_name: "required",
            insured_streetaddress: "required",
            insured_city: "required",
            insured_state: "required",
            insured_zip: "required",
            insured_telephone: {
                required: true,
                phoneUS: true
            },
            insured_other_insured_policy: "required",
            insured_birth_date: {
                required: true,
                date: true
            },
            other_cliam_id: {
                required: false
            },
            insured_plan_name_program: "required",
            payer_num: "required",
            payer_name: "required",
            payer_address: {
                required: false
            },
            referring_name: "required",
            NPI: "required",
            billing_provider_name: "required",
            location_provider_name: "required",
            rendering_provider_name: "required",
            cpt_code_1: "required",
            cpt_charge_1: "required"
        },
        highlight: function(element) {
            // console.log($(element));
            if($(element).attr("id")===("id_cpt_code_1")){
                $(element).parent().addClass('has-error');
            }
            else if($(element).attr("id")===("id_cpt_charge_1")){
                $(element).parent().addClass('has-error');
            }
            else if($(element).attr("id").substring(3, 5)==="dx"){
                // console.log(123);
                for(i=1;i<=4;i++){
                    var s="id_dx_pt_s"+i; // regex match
                    // console.log($(element).attr("id").substring(0,11), s);
                    if($(element).attr("id").substring(0,11).localeCompare(s)==0){
                        // console.log("matched!");
                        $(element).parent().addClass('has-error');
                    }
                }
            }
            else if($(element).attr("id").substring(3,16)==="service_start"){
                $(element).parent().addClass('has-error');
            }
            else{
                $(element).closest('.form-group').addClass('has-error');
            }
            
        },
        unhighlight: function(element) {
            $(element).closest('.form-group').removeClass('has-error');
            $(element).parent().removeClass('has-error');
        }

    });
    jQuery.validator.addClassRules('dropValidation', {
        validation_diagnosis : true
    });
    jQuery.validator.addClassRules('dateValidation', {
        validation_date : true
    });
    
    // Hide-Display block for service
    (function($){
        var originalVal = $('.input-number').val;
        $('.input-number').val = function(){
            var prev;
            if(arguments.length>0){
                prev = originalVal.apply(this,[]);
            }
            var result =originalVal.apply(this,arguments);
            if(arguments.length>0 && prev!=originalVal.apply(this,[]))
                $(this).change();
            return result;
        };
    })(jQuery);
    $('.input-number').change(function(){
        // Hide the previous
        $('.service2').css("display","none");
        $('.service3').css("display","none");
        $('.service4').css("display","none");
        $('.service5').css("display","none");
        $('.service6').css("display","none");

        // Display as many as in val
        var iter=$('.input-number').val();
        while(iter>0){
            var cls=".service"+iter;
            $(cls).css("display","block");
            iter--;
        }
    });

    // default dropdown of calculator
    for( i=1;i<=6;i++){
        $('#btn_calc_'+i).trigger( "click" );
    }
    $("div.toggle").width("124px");
    $("div.toggle-group").width("295px");
    

    // Javascript validation for diagnosis - service information

    // var cells = [1,0,0,0,0,0,0,0,0,0,0,0];


    
    // var element="#id_dx_pt_s1_1";
    // var val=($(element).val()).charCodeAt(0)-"A".charCodeAt(0);
    // // console.log($(element).val());
    // if(cells[val]!=1){
    //     cells[val]=1;
    // }
    // else{
    //     // console.log("123123");
    //     element.parent().addClass('has-error');
    //     // Red the box
    // }
    
    
    // // $("#selectBox option[value='option1']").remove();
    // var cells = [1,0,0,0,0,0,0,0,0,0,0,0];
    // //Define a onchange handler:
    // var changeHandler = function() {
    //     //You can alert the value of the selected option, using this:
    //     var val=this.value.charCodeAt(0)-"A".charCodeAt(0);
    //     // console.log(this.value);
    //     if(cells[val]!=1){
    //         cells[val]=1;
    //     }
    //     else{
    //         // console.log("123123");
    //         // console.log($($(this).attr("id")));
    //         $($(this).attr("id")).parent().addClass('has-error');
    //         // Red the box
    //     }
    //     // console.log(cells);


    // }
    // var filter=document.getElementById("id_dx_pt_s1_1");
    // if(filter.addEventListener)
    //   filter.addEventListener("change", changeHandler, false);
    // //If it doesn't exist, try attachEvent, the IE way:
    // else if(filter.attachEvent)
    //   filter.attachEvent("onchange", changeHandler);
    // //Just use onchange if neither exist
    // else
    //   filter.onchange = changeHandler;

}
window.onload = init;
