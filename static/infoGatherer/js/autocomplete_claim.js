function autocomplete_claim(api_urls) {
    'use strict';

    // Disable default behavior when submit form
    $('#make-claims-form').submit(function(e) {
        return false;
    });

    $('#id_insured_other_benifit_plan').prop('checked', false);

    // Check if url has patient ID or not.  If it does,
    // execute autocomplete for patient section.
    var patient_id = getUrlParameter('patient');
    if(patient_id) {
        $(document).ready(function() {
            setUpPatient({data: patient_id});
        });
    }

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
        $("#id_pat_name").devbridgeAutocomplete({
            minChars: 0,
            lookup: patient_lookup,
            formatResult: addHint,
            onSelect: setUpPatient,
        });

        // Set auto suggestion for insured's name
        $("#id_insured_name").devbridgeAutocomplete({
            minChars: 0,
            lookup: patient_lookup,
            formatResult: addHint,
            onSelect: setupAutoInsurance
        });

        // Set auto suggestion for other insured's name
        $("#id_pat_other_insured_name").devbridgeAutocomplete({
            minChars: 0,
            lookup: patient_lookup,
            formatResult: addHint,
            onSelect: function (suggestion) {
                $('#hidden_id_pat_other_insured_name').val(suggestion.value);

                $('#id_other_insured_id').val(suggestion.data);
            },
        });
    });

    function setUpPatient(suggestion) {
        // Get patient information
        $.post(
            api_urls[1],
            {personal_chart_no: suggestion.data},
            function(obj) {
                // Auto populate fields in patient section
                var patient = obj[0].fields;
                var birth_date_str = patient.dob.substr(5,2) + "/" + patient.dob.substr(8,2) + "/" + patient.dob.substr(0,4);
                $("#id_pat_streetaddress").val(patient.address);
                $("#id_pat_city").val(patient.city);
                $("#id_pat_state").val(patient.state);
                $("#id_pat_zip").val(patient.zip);
                $("#id_pat_telephone").val(patient.home_phone);
                $("#id_pat_birth_date").val(birth_date_str);
                $("#id_pat_sex").val(patient.sex.substr(0,1));
                $('#id_pat_name').val(patient.format_name);
                $('#id_pat_id').val(obj[0].pk);
            }
        );
    };

    // Get insured information and insurance according to that person
    function setupAutoInsurance(suggestion) {
        $.post(
            api_urls[2],
            {personal_chart_no: suggestion.data},
            function(obj) {
                var insured_info = obj["personal_information"][0];

                // Auto populate fields in insured section
                $('#id_insured_id').val(insured_info.chart_no);
                var birth_date_str = insured_info.dob.substr(5,2) + "/" + insured_info.dob.substr(8,2) + "/" + insured_info.dob.substr(0,4);
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

                $("#id_insured_idnumber").devbridgeAutocomplete({
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

                $("#id_payer_name").devbridgeAutocomplete({
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

                $("#id_payer_num").devbridgeAutocomplete({
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
        $("#id_referring_name").devbridgeAutocomplete({
            minChars: 0,
            lookup: physicians_lookup,
            formatResult: addHint,
            onSelect: function (suggestion) {
                $('#id_referring_name').val(suggestion.value);
                $('#id_NPI').val(suggestion.data.NPI);

                $('#hidden_id_referring_name').val(suggestion.value);

                $('#id_referring_provider_id').val(suggestion.data.id);
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
                id: p.id,
            });
        }

        $("#id_billing_provider_name").devbridgeAutocomplete({
            minChars: 0,
            lookup: billing_p_lookup,
            formatResult: addHint,
            onSelect: function (suggestion) {
                $('#hidden_id_billing_provider_name').val(suggestion.value);

                $('#id_billing_provider_id').val(suggestion.id);
            },
        });

        // For location provider
        var billing_p_lookup = [];
        for(var p of obj['Location']) {
            billing_p_lookup.push({
                value: p.provider_name,
                data: p.provider_name,
                hint: p.provider_city + ", " + p.provider_state,
                id: p.id,
                pos: p.place_of_service,
            });
        }

        $("#id_location_provider_name").devbridgeAutocomplete({
            minChars: 0,
            lookup: billing_p_lookup,
            formatResult: addHint,
            onSelect: function (suggestion) {
                $('#hidden_id_location_provider_name').val(suggestion.value);

                $('#id_location_provider_id').val(suggestion.id);

                // adding value and text to POS
                for(i=1; i<=6; i++){
                    $("#place_of_service_"+(i)+"_pos").attr("value",suggestion.pos);
                    $("#place_of_service_"+(i)+"_pos").text(suggestion.pos);
                }

            },
        });

        // For billing provider
        var billing_p_lookup = [];
        for(var p of obj['Rendering']) {
            billing_p_lookup.push({
                value: p.provider_name,
                data: p.provider_name,
                hint: p.provider_city + ", " + p.provider_state,
                id: p.id,
            });
        }

        $("#id_rendering_provider_name").devbridgeAutocomplete({
            minChars: 0,
            lookup: billing_p_lookup,
            formatResult: addHint,
            onSelect: function (suggestion) {
                $('#hidden_id_rendering_provider_name').val(suggestion.value);

                $('#id_rendering_provider_id').val(suggestion.id);
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

        $("input[name^=cpt_code]").devbridgeAutocomplete({
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

        $("#id_payer_id").val(insurance.payer.code);
    }

    function detailString(text) {
        return "<span class='detail'>" + text + "</span>"
    }

    function addHint(suggestion, currentValue) {
        return suggestion.value + detailString(suggestion.hint);
    }


    // Autocomplete for diagnonsis codes
    $('.dx_code').each(function() {
        $(this).typeahead({
            hint: true,
            highlight: true,
            minLength: 0,
        }, {
            limit: 50,
            source: new Bloodhound({
                datumTokenizer: Bloodhound.tokenizers.whitespace,
                queryTokenizer: Bloodhound.tokenizers.whitespace,
                remote: {
                    url: api_urls[6] + '?q=%Q',
                    wildcard: '%Q',
                },
            }),
            display: 'pk',
            templates: {
                notFound: '<div class="tt-notfound">unable to find any diagnosis codes that match the current value</div>',
                suggestion: function(data) {
                    return _.template('<div><%= data.pk %> - <%= data.fields.description %></div>')({data: data});
                }
            }
        });
    });


    // self_checkbox_insured
    $("#id_pat_relationship_insured").change(function(){
        if($("#id_pat_relationship_insured option:selected").text().localeCompare("Self") == 0) {
            $("#id_insured_name").val($("#id_pat_name").val());
            $("#id_insured_streetaddress").val($("#id_pat_streetaddress").val());
            $("#id_insured_city").val($("#id_pat_city").val());
            $("#id_insured_state").val($("#id_pat_state").val());
            $("#id_insured_zip").val($("#id_pat_zip").val());
            $("#id_insured_telephone").val($("#id_pat_telephone").val());
            $("#id_insured_birth_date").val($("#id_pat_birth_date").val());
            $("#id_insured_sex").val($("#id_pat_sex").val());

            setupAutoInsurance({data: $('#id_pat_id').val()});
        }
    });
};

function bindCollapse(i) {
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

function updateNote(i) {
    var text = '';
    if($('#collapse_' + i).attr('aria-expanded') == 'true') {
        var start = $('#id_start_time_' + i).val();
        var end = $('#id_end_time_' + i).val();

        if(start && end) {
            var startDate = new Date(1, 1, 1, start.split(":")[0], start.split(":")[1]);
            var endDate = new Date(1, 1, 1, end.split(":")[0], end.split(":")[1]);
            var diffTime = Math.ceil((endDate-startDate)/(1000*60));

            start = start.split(':');
            end = end.split(':');
            startSuffix = convert24To12(start);
            endSuffix = convert24To12(end);

            text += 'start ' + start[0] + start[1] + ' ' + startSuffix + ' ';
            text += 'end ' + end[0] + end[1] + ' ' + endSuffix + ', ';
            text += 'total ' + diffTime + ' min';
            text = text.toUpperCase();

            $('#id_note_' + i).val(text);
        }

    }
    else if($('#collapse2_' + i).attr('aria-expanded') == 'true') {
        var desc = $('#id_proc_code_' + i).val();
        var ndc = $('#id_ndc_' + i).val();

        var quantity = $('#id_qty_' + i).val();
        var unit = $('#id_unit_' + i).val();

        if(desc && ndc && quantity && unit) {
            text = desc + ' ' + 'N4' + ndc + ' ' + unit+ quantity;
            text = text.toUpperCase();

            $('#id_note_' + i).val(text);
        }
    }
}

function convert24To12(arrTime) {
    if(arrTime[0] > 12) {
        arrTime[0] -= 12;
        return 'PM';
    }
    else {
        return 'AM';
    }
}

function calculateTotal(i) {
    var baseUnits = $('#id_base_units_' + i).val();
    var TimeUnits = $('#id_time_units_' + i).val();
    var fees = $('#id_fees_' + i).val();
    var cptCharge = $('#id_cpt_charge_' + i).val();
    var total;

    if($('#collapse_' + i).attr('aria-expanded') == 'true' && baseUnits && TimeUnits && fees) {
        var baseUnits = parseFloat(baseUnits);
        var TimeUnits = parseFloat(TimeUnits);
        var fees = parseFloat(fees);
        var cptCharge = parseFloat(cptCharge);
        total = (baseUnits + TimeUnits) * fees;
    }
    else {
        total = $('#id_cpt_charge_' + i).val();
    }

    total = Math.round(total * 100) / 100
    $('#id_total_' + i).val(total);

    updateNote(i);
}

function dropDown(a,i){
    $('#btn_calc_'+i).trigger( "click" );
    $('#btn_druginfo_'+i).trigger( "click" );

    calculateTotal(i);
};