function init(){
    
    document.getElementById('show_hide').style.display='none';
    document.getElementById('input_show_hide').style.display='none';

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
    // jQuery.validator.addMethod("selectnic", function(value, element){
    //     if (/^[0-9]{9}[vVxX]$/.test(value)) {
    //         return false;
    //     } else {
    //         return true;
    //     };
    // }, "wrong nic number"); 


    // form validation
    $('form').validate({
        errorPlacement: function(error, element) {},
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
            first_name: "required",
            last_name: "required",
            NPI: "required",
            billing_provider_name: "required",
            location_provider_name: "required",
            rendering_provider_name: "required",
            cpt_code_1: "required",
            service_start_date_1: "required"
        },
        highlight: function(element) {
            console.log($(element));
            if($(element).attr("id")===("id_cpt_code_1")){
                console.log("123");

                // not working
                $(element).addClass('has-error');
            }else{
                $(element).closest('.form-group').addClass('has-error');
            }
        },
        unhighlight: function(element) {
            $(element).closest('.form-group').removeClass('has-error');
        }

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
    

}
window.onload = init;
$('.btn-number').click(function(e){
    e.preventDefault();
    
    fieldName = $(this).attr('data-field');
    type      = $(this).attr('data-type');
    var input = $("input[name='"+fieldName+"']");
    var currentVal = parseInt(input.val());
    if (!isNaN(currentVal)) {
        if(type == 'minus') {
            
            if(currentVal > input.attr('min')) {
                input.val(currentVal - 1).change();
            } 
            if(parseInt(input.val()) == input.attr('min')) {
                $(this).attr('disabled', true);
            }

        } else if(type == 'plus') {

            if(currentVal < input.attr('max')) {
                input.val(currentVal + 1).change();
            }
            if(parseInt(input.val()) == input.attr('max')) {
                $(this).attr('disabled', true);
            }

        }
    } else {
        input.val(0);
    }
});
$('.input-number').focusin(function(){
   $(this).data('oldValue', $(this).val());
});
$('.input-number').change(function() {
    
    minValue =  parseInt($(this).attr('min'));
    maxValue =  parseInt($(this).attr('max'));
    valueCurrent = parseInt($(this).val());
    
    name = $(this).attr('name');
    if(valueCurrent >= minValue) {
        $(".btn-number[data-type='minus'][data-field='"+name+"']").removeAttr('disabled')
    } else {
        alert('Sorry, the minimum value was reached');
        $(this).val($(this).data('oldValue'));
    }
    if(valueCurrent <= maxValue) {
        $(".btn-number[data-type='plus'][data-field='"+name+"']").removeAttr('disabled')
    } else {
        alert('Sorry, the maximum value was reached');
        $(this).val($(this).data('oldValue'));
    }
    
    
});
$(".input-number").keydown(function (e) {
        // Allow: backspace, delete, tab, escape, enter and .
        if ($.inArray(e.keyCode, [46, 8, 9, 27, 13, 190]) !== -1 ||
             // Allow: Ctrl+A
            (e.keyCode == 65 && e.ctrlKey === true) || 
             // Allow: home, end, left, right
            (e.keyCode >= 35 && e.keyCode <= 39)) {
                 // let it happen, don't do anything
                 return;
        }
        // Ensure that it is a number and stop the keypress
        if ((e.shiftKey || (e.keyCode < 48 || e.keyCode > 57)) && (e.keyCode < 96 || e.keyCode > 105)) {
            e.preventDefault();
        }
    });
