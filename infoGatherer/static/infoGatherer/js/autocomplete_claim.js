function autocomplete_claim(api_urls) {
    // "use strict";

    // Disable default behavior when submit form
    $('#make-claims-form').submit(function(e) {
        return false;
    });

    $('#id_insured_other_benifit_plan').prop('checked', false);

    // Autocomplete causes binded field to clear its value when page is loaded from back and forward button.
    // Workaround is to have hidden field to store previous value and assign to that field if available
    $("#id_pat_name").val($('#hidden_id_pat_name').val() || $("#id_pat_name").attr('value'));
    $("#id_insured_name").val($('#hidden_id_insured_name').val() || $("#id_insured_idnumber").attr('value'));
    $("#id_insured_idnumber").val($('#hidden_id_insured_id').val() || $("#id_payer_num").attr('value'));
    $("#id_payer_num").val($('#hidden_id_payer_num').val() || $("#id_payer_num").attr('value'));
    $("#id_payer_name").val($('#hidden_id_payer_name').val() || $("#id_payer_name").attr('value'));
    $("#id_first_name").val($('#hidden_id_first_name').val() || $("#id_first_name").attr('value'));
    $("#id_billing_provider_name").val($('#hidden_id_billing_provider_name').val() || $("#id_billing_provider_name").attr('value'));
    $("#id_location_provider_name").val($('#hidden_id_location_provider_name').val() || $("#id_location_provider_name").attr('value'));
    $("#id_rendering_provider_name").val($('#hidden_id_rendering_provider_name').val() || $("#id_rendering_provider_name").attr('value'));
    $("#id_pat_other_insured_name").val($('#hidden_id_pat_other_insured_name').val() || $("#id_pat_other_insured_name").attr('value'));

    // Make ajax call for auto-suggestion
    $.ajax({
        url: api_urls[0],
    }).done(function(obj) {
        var patient_lookup = [];

        for(var p of obj['patients'])
            patient_lookup.push({
                value: p.last_name + ", " + p.first_name,
                data: p.chart_no,
                hint: p.address + ", " + p.city,
            })

        // Set auto suggestion for patient's name
        $("#id_pat_name").autocomplete({
            minChars: 0,
            lookup: patient_lookup,
            formatResult: addHint,
            onSelect: function (suggestion) {
                // Get patient information
                $.post(
                    api_urls[1],
                    {personal_chart_no: suggestion.data},
                    function(obj) {
                        var patient_info = obj['personal_information'][0];

                        // Auto populate fields in patient section
                        var birth_date_str = patient_info.dob.substr(0,4) + "-" + patient_info.dob.substr(5,2) + "-" + patient_info.dob.substr(8,2);
                        $("#id_pat_streetaddress").val(patient_info.address);
                        $("#id_pat_city").val(patient_info.city);
                        $("#id_pat_state").val(patient_info.state);
                        $("#id_pat_zip").val(patient_info.zip);
                        $("#id_pat_telephone").val(patient_info.home_phone);
                        $("#id_birth_date").val(birth_date_str);
                        $("#id_pat_sex").val(patient_info.sex.substr(0,1));

                        $('#hidden_id_pat_name').val(suggestion.value);
                    }
                );
            },
        });

        // Set auto suggestion for insured's name
        $("#id_insured_name").autocomplete({
            minChars: 0,
            lookup: patient_lookup,
            formatResult: addHint,
            onSelect: function (suggestion) {
                // Get insured information and insurance according to that person
                $.post(
                    api_urls[2],
                    {personal_chart_no: suggestion.data},
                    function(obj) {
                        // Auto populate fields in insured section
                        var insured_info = obj["personal_information"][0];
                        var birth_date_str = insured_info.dob.substr(0,4) + "-" + insured_info.dob.substr(5,2) + "-" + insured_info.dob.substr(8,2);
                        $("#id_insured_streetaddress").val(insured_info.address);
                        $("#id_insured_city").val(insured_info.city);
                        $("#id_insured_state").val(insured_info.state);
                        $("#id_insured_zip").val(insured_info.zip);
                        $("#id_insured_telephone").val(insured_info.home_phone);
                        $("#id_insured_birth_date").val(birth_date_str);
                        $("#id_insured_sex").val(insured_info.sex.substr(0,1));

                        $('#hidden_id_insured_name').val(suggestion.value);

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

        // Set auto suggestion for other insured's name
        $("#id_pat_other_insured_name").autocomplete({
            minChars: 0,
            lookup: patient_lookup,
            formatResult: addHint,
            onSelect: function (suggestion) {
                $('#hidden_id_pat_other_insured_name').val(suggestion.value);
            },
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
            formatResult: addHint,
            onSelect: function (suggestion) {
                $('#id_first_name').val(suggestion.value);
                $('#id_NPI').val(suggestion.data.NPI);

                $('#hidden_id_first_name').val(suggestion.value);
            },
        });
    });

    // Prepare auto-suggestion for provider section
    $.ajax({
        url: api_urls[4],
    }).done(function(obj) {
        // For billing provider
        var billing_p_lookup = [];
        for(var p of obj['Billing']) {
            billing_p_lookup.push({
                value: p.provider_name,
                data: p.provider_name,
                hint: p.provider_city + ", " + p.provider_state,
            });
        }

        $("#id_billing_provider_name").autocomplete({
            minChars: 0,
            lookup: billing_p_lookup,
            formatResult: addHint,
            onSelect: function (suggestion) {
                $('#hidden_id_billing_provider_name').val(suggestion.value);
            },
        });

        // For location provider
        var billing_p_lookup = [];
        for(var p of obj['Location']) {
            billing_p_lookup.push({
                value: p.provider_name,
                data: p.provider_name,
                hint: p.provider_city + ", " + p.provider_state,
            });
        }

        $("#id_location_provider_name").autocomplete({
            minChars: 0,
            lookup: billing_p_lookup,
            formatResult: addHint,
            onSelect: function (suggestion) {
                $('#hidden_id_location_provider_name').val(suggestion.value);
            },
        });

        // For billing provider
        var billing_p_lookup = [];
        for(var p of obj['Rendering']) {
            billing_p_lookup.push({
                value: p.provider_name,
                data: p.provider_name,
                hint: p.provider_city + ", " + p.provider_state,
            });
        }

        $("#id_rendering_provider_name").autocomplete({
            minChars: 0,
            lookup: billing_p_lookup,
            formatResult: addHint,
            onSelect: function (suggestion) {
                $('#hidden_id_rendering_provider_name').val(suggestion.value);
            },
        });
    });

    // Prepare auto-suggestion for CPT parts
    $.ajax({
        url: api_urls[5],
    }).done(function(obj) {
        var cpt_lookup = [];
        for(var p of obj['cpts']) {
            cpt_lookup.push({
                value: p.cpt_code,
                data: p,
                hint: p.cpt_description,
            });
        }

        $(".cpt_code").autocomplete({
            minChars: 0,
            lookup: cpt_lookup,
            formatResult: addHint,
            onSelect: function (suggestion) {
                // Populate modifier of its own line
                var cpt = suggestion.data;
                var line_no = this.name.substr(this.name.lastIndexOf('_')+1);
                $('#id_mod_a_' + line_no).val(cpt.cpt_mod_a);
                $('#id_mod_b_' + line_no).val(cpt.cpt_mod_b);
                $('#id_mod_c_' + line_no).val(cpt.cpt_mod_c);
                $('#id_mod_d_' + line_no).val(cpt.cpt_mod_d);
                $('#id_cpt_charge_' + line_no).val(cpt.cpt_charge);
                
                // Will not override if this field is already set
                if(!$('#id_fees_' + line_no).val())
                    $('#id_fees_' + line_no).val(cpt.cpt_charge);

                calculateTotal(line_no);
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

        $("#hidden_id_insured_id").val(insurance.insurance_id);
        $("#hidden_id_payer_num").val(insurance.payer.code);
        $("#hidden_id_payer_name").val(insurance.payer.name);
    }

    function detailString(text) {
        return "<span class='detail'>" + text + "</span>"
    }

    function addHint(suggestion, currentValue) {
        return suggestion.value + detailString(suggestion.hint);
    }

};

function bindCollapse(i) {
    (function() {
        self = $('#id_service_start_date_' + i);

        self.click(function(e) {
            e.preventDefault();
        });

        var picker = new Pikaday({
            field: self[0],
            onSelect: function(date) {
                self.val(this.toString('YYYY-MM-DD'));
                self.removeClass('placeholder');
            }
        });
    })();

    (function() {
        // Time dropdown
        var timepickerConfig = {
            minuteStep: 1,
            appendWidgetTo: 'body',
            showSeconds: false,
            showMeridian: false,
            defaultTime: false
        };
        $('#id_start_time_' + i).timepicker(timepickerConfig).on('changeTime.timepicker', calculateUnitDiff);
        $('#id_end_time_' + i).timepicker(timepickerConfig).on('changeTime.timepicker', calculateUnitDiff);

        function calculateUnitDiff() {
            var start = $('#id_start_time_' + i).val();
            var end = $('#id_end_time_' + i).val();

            if(start.length>0 && end.length>0) {
                var startDate = new Date(1, 1, 1, start.split(":")[0], start.split(":")[1]);
                var endDate = new Date(1, 1, 1, end.split(":")[0], end.split(":")[1]);

                var unitDiff = Math.ceil((endDate-startDate)/(1000*60*15));
                $('#id_time_units_' + i).val(Math.max(unitDiff, 0));

                calculateTotal(i);
            }
        }
    })();

    // Bind auto calculation for total charge
    $('#procedure_line_' + i).focusout(function() {
        calculateTotal(i);
    });
}

function calculateTotal(i) {
    var baseUnits = parseInt($('#id_base_units_' + i).val());
    var TimeUnits = parseInt($('#id_time_units_' + i).val());
    var fees = parseInt($('#id_fees_' + i).val());
    var cptCharge = parseInt($('#id_cpt_charge_' + i).val());
    var total;

    xxx = $('#collapse_' + i).attr('aria-expanded');

    if($('#collapse_' + i).attr('aria-expanded') == 'true' && baseUnits && TimeUnits && fees) {
        total = (baseUnits + TimeUnits) * fees;
    }
    else {
        total = $('#id_cpt_charge_' + i).val();
    }

    $('#total_' + i).val(total);
}

function dropDown(a,i){
    $( "#trigger_calc_"+i).on( "click", function() {
        $('#btn_calc_'+i).trigger( "click" );
    });
    $( "#trigger_drug_"+i ).on( "click", function() {
        $('#btn_druginfo_'+i).trigger( "click" );
    });

    var child = a.children[0];
    $( "#trigger_calc_"+i ).trigger( "click" );
    $( "#trigger_drug_"+i ).trigger( "click" );

    calculateTotal(i);
};