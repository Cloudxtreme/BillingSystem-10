function hideAll(){
	$(".field-tax_id").css('display','none');
	$(".field-npi").css('display','none');
	$(".field-speciality").css('display', 'none');
	$(".field-provider_address").css('display', 'none');
	$(".field-provider_city").css('display', 'none');
	$(".field-provider_state").css('display', 'none');
	$(".field-provider_zip").css('display', 'none');
	$(".field-provider_phone").css('display', 'none');
	$(".field-provider_ssn").css('display', 'none');
	$(".field-provider_ein").css('display', 'none');
	$(".field-place_of_service").css('display', 'none');

}
function rendering(){
	$(".field-tax_id").css('display','block');
	$(".field-npi").css('display','block');
	$(".field-speciality").css('display', 'block');
	$(".field-provider_address").css('display', 'block');
	$(".field-provider_city").css('display', 'block');
	$(".field-provider_state").css('display', 'block');
	$(".field-provider_zip").css('display', 'block');
	$(".field-provider_phone").css('display', 'block');
}
function addRequiredLabel(){
	$("#id_tax_id").parent().children("label").addClass("required");
	$("#id_npi").parent().children("label").addClass("required");
	$("#id_speciality").parent().children("label").addClass("required");
	$("#id_provider_address").parent().children("label").addClass("required");
	$("#id_provider_city").parent().children("label").addClass("required");
	$("#id_provider_phone").parent().children("label").addClass("required");
	$("#id_provider_zip").parent().children("label").addClass("required");
	$("#id_provider_state").parent().children("label").addClass("required");
	
}

function helper(){
			if($('#id_role').val()==="Rendering"){
				hideAll();
				rendering();
			}
			else if ($('#id_role').val()==="Billing"){
				hideAll();
				$(".field-tax_id").css('display','block');
				$(".field-npi").css('display','block');
				$(".field-provider_ssn").css('display', 'block');
				$(".field-provider_ein").css('display', 'block');
				$(".field-speciality").css('display', 'block');
				$(".field-provider_address").css('display', 'block');
				$(".field-provider_city").css('display', 'block');
				$(".field-provider_state").css('display', 'block');
				$(".field-provider_zip").css('display', 'block');
				$(".field-provider_phone").css('display', 'block');

				// chang class label to required
			}
			else if ($('#id_role').val()==="Location"){
				hideAll();
				$(".field-npi").css('display','block');
				$(".field-provider_address").css('display', 'block');
				$(".field-provider_city").css('display', 'block');
				$(".field-provider_state").css('display', 'block');
				$(".field-provider_zip").css('display', 'block');
				$(".field-provider_phone").css('display', 'block');
				$(".field-place_of_service").css('display', 'block');
				$(".field-place_of_service").addClass("required");
			}else{
				hideAll();
				$(".field-tax_id").css('display','block');
				$(".field-npi").css('display','block');
				$(".field-provider_ssn").css('display', 'block');
				$(".field-provider_ein").css('display', 'block');
				$(".field-provider_address").css('display', 'block');
				$(".field-provider_city").css('display', 'block');
				$(".field-provider_state").css('display', 'block');
				$(".field-provider_zip").css('display', 'block');
				$(".field-provider_phone").css('display', 'block');
			}
}
function init(){
	if(window.location.href.indexOf("add")>=0){
		hideAll();
		rendering();
		addRequiredLabel();
		$(document).ready( function() {
		// $("#id_role").on("change", function () {
			helper();
		});

		$("#id_role").on("change", function(){
			helper()
		});
		
	}
}
window.onload = init;