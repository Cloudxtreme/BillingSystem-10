function autocomplete_claim(api_urls) {
    "use strict";

    // Disable default behavior when submit form
    $('#make-claims-form').submit(function(e) {
        return false;
    });

    // Prepare auto suggestion in name fields of both patient and insured
    $.ajax({
        url: api_urls[0],
    }).done(function(obj) {
        var patient_lookup = [];

        for(var p of obj['patients'])
            patient_lookup.push({
                value: p.first_name + " " + p.last_name,
                data: p.chart_no,
                hint: p.address + ", " + p.city,
            })

        // Set auto suggestion for patient's name
        $("#id_pat_name").autocomplete({
            minChars: 0,
            lookup: patient_lookup,
            formatResult: function(suggestion, currentValue) {
                return suggestion.value + detailString(suggestion.hint);
            },
            onSelect: function (suggestion) {
                // Get patient information
                $.post(
                    api_urls[1],
                    {personal_chart_no: suggestion.data},
                    function(obj) {
                        var patient_info = obj['personal_information'][0];

                        // Auto populate fields in patient section
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
            lookup: patient_lookup,
            formatResult: function(suggestion, currentValue) {
                return suggestion.value + detailString(suggestion.hint);
            },
            onSelect: function (suggestion) {
                // Get insured information and insurance according to that person
                $.post(
                    api_urls[2],
                    {personal_chart_no: suggestion.data},
                    function(obj) {
                        // Auto populate fields in insured section
                        var insured_info = obj["personal_information"][0];
                        var birth_date_str = insured_info.dob.substr(0,4) + "/" + insured_info.dob.substr(5,2) + "/" + insured_info.dob.substr(8,2);
                        $("#id_insured_streetaddress").val(insured_info.address);
                        $("#id_insured_city").val(insured_info.city);
                        $("#id_insured_state").val(insured_info.state);
                        $("#id_insured_zip").val(insured_info.zip);
                        $("#id_insured_telephone").val(insured_info.home_phone);
                        $("#id_insured_birth_date").val(birth_date_str);
                        $("#id_insured_sex").val(insured_info.sex.substr(0,1));

                        // Set auto suggestion for insurance id number
                        var insurance_list = obj["insurance_list"];
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

    // Prepare auto-suggestion for physician information
    $.ajax({
        url: api_urls[3],
    }).done(function(obj) {
        var physicians_lookup = [];
        for(var p of obj.physicians) {
            physicians_lookup.push({
                value: p.last_name + ", " + p.first_name,
                data: p,
                hint: p.city + ", " + p.state + ", NPI: " + p.NPI,
            });
        }

        // Set auto suggestion for patient's name
        $("#id_first_name").autocomplete({
            minChars: 0,
            lookup: physicians_lookup,
            formatResult: function(suggestion, currentValue) {
                return suggestion.value + detailString(suggestion.hint);
            },
            onSelect: function (suggestion) {
                $('#id_first_name').val(suggestion.value);
                $('#id_NPI').val(suggestion.data.NPI);
            },
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
