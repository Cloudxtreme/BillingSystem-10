from django import forms

from localflavor.us.forms import USZipCodeField, USStateSelect, USPhoneNumberField, USStateField
from localflavor.us.us_states import STATE_CHOICES

from .models import *
from base.models import BASE_DECIMAL


class PaymentMakeForm(forms.ModelForm):
    amount = forms.DecimalField(min_value=0)

    class Meta:
        model = Payment
        exclude = ['created', 'modified', "user"]

    def clean(self):
        cleaned_data = super(PaymentMakeForm, self).clean()

        payer_type = cleaned_data.get('payer_type')
        if payer_type == 'Insurance' and \
                cleaned_data.get('payer_insurance') is None:
            self.add_error('payer_insurance', """Payer insurance is
                    required for payer type \"insurance\"""")
        elif payer_type == 'Patient' and \
                cleaned_data.get('payer_patient') is None:
            self.add_error('payer_patient', """Payer patient is
                    required for payer type \"patient\"""")

        if cleaned_data.get('payment_method') == 'Check' and \
                not cleaned_data.get('check_number'):
            self.add_error('check_number', """Check number is
                    required for payment method \"check\"""")


class PaymentClaimSearchForm(forms.Form):
    payment = forms.CharField()
    claim = forms.CharField()
    search_type = forms.CharField()

    def clean(self):
        cleaned_data = super(PaymentClaimSearchForm, self).clean()
        payment_id = cleaned_data.get('payment')
        claim_id = cleaned_data.get('claim')
        search_type = cleaned_data.get('search_type')

        try:
            payment = Payment.objects.get(pk=payment_id)
            # if search_type == 'create_patient_charge' and \
            #         payment.payer_type != 'Patient':
            #     self.add_error('payment',
            #             'Given payment is not payer type \"Patient\"')
        except:
            self.add_error('payment', 'Payment with given ID does not exist')

        try:
            Claim.objects.get(pk=claim_id)
        except:
            self.add_error('claim', 'Claim with given ID does not exist')


class ProcedureForm(forms.Form):
    procedure = forms.CharField()
    amount = forms.DecimalField(min_value=0, required=False, **BASE_DECIMAL)
    adjustment = forms.DecimalField(required=False, **BASE_DECIMAL)
    reference = forms.CharField(required=False)


class ProcedureModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return '%s, Ins Bal: $%s, Pat Bal: $%s, Total: $%s' % (
                obj.cpt.cpt_code,
                obj.insurance_balance,
                obj.patient_balance,
                obj.balance)


class PatientChargeForm(forms.Form):
    payment = forms.ModelChoiceField(
            queryset=Payment.objects.all(),
            required=False)
    charge_amount = forms.DecimalField(
            min_value=0,
            required=False,
            **BASE_DECIMAL)
    resp_type = forms.ChoiceField(
            choices=[(None, '-----')] + RESPONSIBILITY_TYPE,
            required=False)
    apply_amount = forms.DecimalField(
            min_value=0,
            required=False,
            **BASE_DECIMAL)
    reference = forms.CharField(max_length=100, required=False)

    def __init__(self, *args, **kwargs):
        claim_id = kwargs.pop('claim_id', None)

        super(PatientChargeForm, self).__init__(*args, **kwargs)
        self.fields['procedure'] = ProcedureModelChoiceField(
                queryset=Procedure.objects.filter(
                    claim=claim_id),
                required=False)

    def clean(self):
        cleaned_data = super(PatientChargeForm, self).clean()

        procedure = cleaned_data.get('procedure')
        payment = cleaned_data.get('payment')
        charge_amount = cleaned_data.get('charge_amount')
        apply_amount = cleaned_data.get('apply_amount')
        resp_type = cleaned_data.get('resp_type')
        if len(resp_type) < 1:
            resp_type = None
            cleaned_data['resp_type'] = resp_type

        procedure_err = {
                'field': 'procedure',
                'error': 'Procedure is required'}
        charge_err = {
                'field': 'charge_amount',
                'error': 'Amount of charge is required'}
        resp_type_err = {
                'field': 'resp_type',
                'error': 'Responsibility type is required'}

        if procedure is not None:
            if not charge_amount:
                self.add_error(**charge_err)
            if resp_type is None:
                self.add_error(**resp_type_err)

        if charge_amount:
            if procedure is None:
                self.add_error(**procedure_err)
            if resp_type is None:
                self.add_error(**resp_type_err)

        if resp_type is not None:
            if procedure is None:
                self.add_error(**procedure_err)
            if not charge_amount:
                self.add_error(**charge_err)

        if apply_amount:
            if procedure is None:
                self.add_error(**procedure_err)
            if not charge_amount:
                self.add_error(**charge_err)
            if resp_type is None:
                self.add_error(**resp_type_err)

        if charge_amount and apply_amount:
            if apply_amount > charge_amount:
                self.add_error('apply_amount', 'Apply amount exceeds charge one')

        if payment is not None and \
                apply_amount and \
                payment.payer_type != 'Patient':
            self.add_error('payment', """Cannot apply payment from
                non-patient payer to charge of patient responsibility""")



class BasePatientChargeFormSet(forms.BaseFormSet):
    def clean(self):
        if any(self.errors):
            return

        total_apply = dict()

        for form in self.forms:
            cleaned_data = form.cleaned_data
            if cleaned_data:
                payment = cleaned_data.get('payment')
                apply_amount = cleaned_data.get('apply_amount') or 0
                total = total_apply.get(payment) or 0

                total_apply[payment] = apply_amount + total

        for payment, total in total_apply.iteritems():
            if total > payment.unapplied_amount:
                raise forms.ValidationError(
                        'Total applied amount exceeds remaining balance.')


class ChargeForm(forms.ModelForm):
    charge = forms.DecimalField(min_value=0)

    class Meta:
        model = Charge
        exclude = ['created', 'modified']

    def clean(self):
        cleaned_data = super(ChargeForm, self).clean()

        payer_type = cleaned_data.get('payer_type')
        resp_type = cleaned_data.get('resp_type')

        if payer_type == 'Patient' and resp_type is None:
            self.add_error('resp_type',
                    """Responsibility type is required for
                        payer type \"Patient\"""")
        elif payer_type == 'Insurance':
            self.cleaned_data['resp_type'] = None


class ApplyForm(forms.ModelForm):
    amount = forms.DecimalField(min_value=0, required=False)
    adjustment = forms.DecimalField(min_value=0, required=False)

    class Meta:
        model = Apply
        exclude = ['created', 'modified', "user"]

    def __init__(self, *args, **kwargs):
        claim_id = kwargs.pop('claim_id', None)
        payment_id = kwargs.pop('payment_id', None)
        payment = Payment.objects.get(pk=payment_id)

        super(ApplyForm, self).__init__(*args, **kwargs)
        self.fields['charge'] = forms.ModelChoiceField(
                queryset=Charge.objects.filter(
                    procedure__claim=claim_id,
                    payer_type=payment.payer_type))

    def clean(self):
        cleaned_data = super(ApplyForm, self).clean()

        payment = cleaned_data.get('payment')
        charge = cleaned_data.get('charge')
        amount = cleaned_data.get('amount')
        adjustment = cleaned_data.get('adjustment')
        reference = cleaned_data.get('reference')

        if charge.payer_type != payment.payer_type:
            self.add_error('charge', """payer type of \"Charge\" and
                    \"Payment\" are not the same""")

        if payment.payer_type == 'Insurance':
            if reference and amount is None and adjustment is None:
                self.add_error('reference', """Reference needs to be
                        with either amount or adjustment.""")

            if amount is not None and adjustment is None:
                adjustment = 0
                cleaned_data['adjustment'] = adjustment
            if adjustment is not None and amount is None:
                amount = 0
                cleaned_data['amount'] = amount

            if amount is not None and adjustment is not None:
                if charge.balance < amount + adjustment:
                    self.add_error('amount', """Amount plus adjustment
                            exceeds balance on procedure \"%s\".  Please
                            check the value""" % \
                            charge.procedure.cpt.cpt_code)
        else:
            # Check validity against charge of Patient
            if reference and amount is None:
                self.add_error('amount',
                        'Amount is required when there is reference')

            if amount:
                if charge.balance < amount:
                    self.add_error('amount', """Amount exceeds balance
                            on procedure \"%s\".  Please check the
                            value""" % charge.procedure.cpt.cpt_code)


class BaseApplyFormSet(forms.BaseFormSet):
    def clean(self):
        if any(self.errors):
            return

        total_apply = dict()

        for form in self.forms:
            cleaned_data = form.cleaned_data
            if cleaned_data:
                payment = cleaned_data.get('payment')
                amount = cleaned_data.get('amount') or 0
                total = total_apply.get(payment) or 0

                total_apply[payment] = amount + total

        for payment, total in total_apply.iteritems():
            if total > payment.unapplied_amount:
                raise forms.ValidationError(
                        'Total applied amount exceeds remaining balance.')


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        exclude = ['created', 'modified', 'author']
