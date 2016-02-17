function autocomplete_claim(api_urls) {
    "use strict";

    // Disable default behavior when submit form
    $('#make-claims-form').submit(function(e) {
        return false;
    });

    // Prepare auto suggestion in name fields of both patient and insured
    $.ajax({
        url: api_urls[0],
    }).done(function(data) {
        var jObj = JSON.parse(data);
        var patient_list = jObj.patient_list;
        var patient_list_obj = [];

        for(var patient of patient_list)
            patient_list_obj.push({
                value: patient.first_name + " " + patient.last_name,
                data: patient.chart_no,
                hintAddress: patient.address + ", " + patient.city,
            })

        // Set auto suggestion for patient's name
        $("#id_pat_name").autocomplete({
            minChars: 0,
            lookup: patient_list_obj,
            formatResult: function(suggestion, currentValue) {
                return suggestion.value + detailString(suggestion.hintAddress);
            },
            onSelect: function (suggestion) {
                // Get patient information
                $.post(
                    api_urls[1],
                    {personal_chart_no: suggestion.data},
                    function(patient_info_str) {
                        // Auto populate fields in patient section
                        var patient_info = JSON.parse(patient_info_str)["personal_information"][0];
                        var birth_date_str = patient_info.dob.substr(0,4) + "/" + patient_info.dob.substr(5,2) + "/" + patient_info.dob.substr(8,2);
                        $("#id_pat_streetaddress").val(patient_info.address);
                        $("#id_pat_city").val(patient_info.city);
                        $("#id_pat_state").val(patient_info.state);
                        $("#id_pat_zip").val(patient_info.zip);
                        $("#id_pat_telephone").val(patient_info.home_phone);
                        $("#id_birth_date").val(birth_date_str);
                        $("#id_pat_sex").val(patient_info.sex.substr(0,1));
                    }
                );
            },
        });

        // Set auto suggestion for insured's name
        $("#id_insured_name").autocomplete({
            minChars: 0,
            lookup: patient_list_obj,
            formatResult: function(suggestion, currentValue) {
                return suggestion.value + detailString(suggestion.hintAddress);
            },
            onSelect: function (suggestion) {
                // Get insured information and insurance according to that person
                $.post(
                    api_urls[2],
                    {personal_chart_no: suggestion.data},
                    function(insured_info_str) {
                        // Auto populate fields in insured section
                        var insured_info = JSON.parse(insured_info_str)["personal_information"][0];
                        var birth_date_str = insured_info.dob.substr(0,4) + "/" + insured_info.dob.substr(5,2) + "/" + insured_info.dob.substr(8,2);
                        $("#id_insured_streetaddress").val(insured_info.address);
                        $("#id_insured_city").val(insured_info.city);
                        $("#id_insured_state").val(insured_info.state);
                        $("#id_insured_zip").val(insured_info.zip);
                        $("#id_insured_telephone").val(insured_info.home_phone);
                        $("#id_insured_birth_date").val(birth_date_str);
                        $("#id_insured_sex").val(insured_info.sex.substr(0,1));

                        // Set auto suggestion for insurance id number
                        var insurance_list = JSON.parse(insured_info_str)["insurance_list"];
                        var insuranceNumberListObj = [];
                        for(i of insurance_list)
                            insuranceNumberListObj.push({value: i.insurance_id, insurance_data: i});

                        $("#id_insured_idnumber").autocomplete({
                            minChars: 0,
                            lookup: insuranceNumberListObj,
                            onSelect: populateInsuranceSection,
                            formatResult: function(suggestion, currentValue) {
                                return suggestion.value + detailString(suggestion.insurance_data.payer.name);
                            },
                        });

                        // Set auto suggesntion for insurance name
                        var insuranceNameListObj = [];
                        for(i of insurance_list)
                            insuranceNameListObj.push({value: i.payer.name, insurance_data: i});

                        $("#id_payer_name").autocomplete({
                            minChars: 0,
                            lookup: insuranceNameListObj,
                            onSelect: populateInsuranceSection,
                            formatResult: function(suggestion, currentValue) {
                                return suggestion.value + detailString(suggestion.insurance_data.payer.address + ", " + suggestion.insurance_data.payer.city);
                            },
                        });

                        // Set auto suggestion for insurance code
                        var insuranceCodeListObj = [];
                        for(i of insurance_list)
                            insuranceCodeListObj.push({value: i.payer.code + "", insurance_data: i});

                        $("#id_payer_num").autocomplete({
                            minChars: 0,
                            lookup: insuranceCodeListObj,
                            onSelect: populateInsuranceSection,
                            formatResult: function(suggestion, currentValue) {
                                return suggestion.value + detailString(suggestion.insurance_data.payer.name);
                            },
                        });

                    }
                );
            }
        });
    });

    function populateInsuranceSection(suggestion) {
        // Auto populate fields in insurance section
        var insurance = suggestion.insurance_data;
        var payer = insurance.payer;
        var fullAddress = payer.address + ' ' + payer.city + ' ' + payer.state + ' ' + payer.zip;
        $("#id_insured_idnumber").val(insurance.insurance_id);
        $("#id_payer_num").val(insurance.payer.code);
        $("#id_payer_name").val(insurance.payer.name);
        $("#id_payer_address").val(fullAddress);
    }

    function detailString(text) {
        return "<span class='detail'>" + text + "</span>"
    }

};
