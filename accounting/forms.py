from django import forms

from localflavor.us.forms import USZipCodeField, USStateSelect, USPhoneNumberField, USStateField
from localflavor.us.us_states import STATE_CHOICES

from .models import *
from base.models import BASE_DECIMAL


class PaymentMakeForm(forms.ModelForm):
    amount = forms.DecimalField(min_value=0)

    class Meta:
        model = Payment
        exclude = ['created', 'modified']

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


class PaymentApplyReadForm(forms.Form):
    payment = forms.CharField(required=True)
    claim = forms.CharField(required=True)

    def clean(self):
        cleaned_data = super(PaymentApplyReadForm, self).clean()
        payment_id = cleaned_data.get('payment')
        claim_id = cleaned_data.get('claim')

        try:
            Payment.objects.get(pk=payment_id)
        except:
            self.add_error('payment', 'Payment with given ID does not exist')

        try:
            Claim.objects.get(pk=claim_id)
        except:
            self.add_error('claim', 'Claim with given ID does not exist')


class PaymentApplyCreateForm(forms.Form):
    amount = forms.DecimalField(max_digits=MAX_DIGITS, decimal_places=DECIMAL_PLACES, min_value=0, required=False)
    adjustment = forms.DecimalField(max_digits=MAX_DIGITS, decimal_places=DECIMAL_PLACES, required=False)
    reference = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        claim_id = kwargs.pop('claim_id', None)
        payment_id = kwargs.pop('payment_id', None)

        super(PaymentApplyCreateForm, self).__init__(*args, **kwargs)
        self.fields['procedure'] = forms.ModelChoiceField(queryset=Procedure.objects.filter(claim=claim_id))
        self.fields['payment'] = forms.ModelChoiceField(queryset=Payment.objects.all())

    def clean(self):
        cleaned_data = super(PaymentApplyCreateForm, self).clean()

        amount = cleaned_data.get('amount')
        adjustment = cleaned_data.get('adjustment')
        reference = cleaned_data.get('reference')

        if reference and (amount is None and adjustment is None):
            self.add_error('reference', 'Reference needs to be with either amount or adjustment.')

        if amount and adjustment is None:
            adjustment = 0
            cleaned_data['adjustment'] = adjustment
        if adjustment and amount is None:
            amount = 0
            cleaned_data['amount'] = amount

        procedure = cleaned_data.get('procedure')

        if amount is not None and adjustment is not None:
            if procedure.balance < amount + adjustment:
                self.add_error('amount', 'Amount plus adjustment exceeds balance on procedure \"%s\".  Please check the value' % procedure.cpt.cpt_code)


class BasePaymentApplyCreateFormSet(forms.BaseFormSet):
    def clean(self):
        if any(self.errors):
            return

        applied_set = dict()
        # Sum up all amount and adjustment
        for form in self.forms:
            if form.cleaned_data:
                cleaned_data = form.cleaned_data
                payment = cleaned_data.get('payment')

                if payment:
                    amount = cleaned_data.get('amount') or 0
                    adjustment = cleaned_data.get('adjustment') or 0
                    total = applied_set.get(payment.pk) or 0

                    applied_set[payment.pk] = total + amount

        # Check if total amount and adjustment exceeds
        # unapplied amount of relative payment or not
        for payment_pk, total in applied_set.iteritems():
            payment = Payment.objects.get(pk=payment_pk)

            if total > payment.unapplied_amount:
                raise forms.ValidationError('Total amount and adjustment exceeds unapplied_amount of payment ID \"%s\"' % payment_pk)


class ProcedureForm(forms.Form):
    procedure = forms.CharField()
    amount = forms.DecimalField(max_digits=MAX_DIGITS, decimal_places=DECIMAL_PLACES, min_value=0, required=False)
    adjustment = forms.DecimalField(max_digits=MAX_DIGITS, decimal_places=DECIMAL_PLACES, required=False)
    reference = forms.CharField(required=False)


class ChargeForm(forms.ModelForm):
    charge = forms.DecimalField(min_value=0)

    class Meta:
        model = Charge
        exclude = ['created', 'modified']


class ApplyForm(forms.ModelForm):
    amount = forms.DecimalField(min_value=0, required=False)
    adjustment = forms.DecimalField(min_value=0, required=False)

    class Meta:
        model = Apply
        exclude = ['created', 'modified']

    def __init__(self, *args, **kwargs):
        claim_id = kwargs.pop('claim_id', None)

        super(ApplyForm, self).__init__(*args, **kwargs)
        self.fields['charge'] = forms.ModelChoiceField(
                queryset=Charge.objects.filter(procedure__claim=claim_id))

    def clean(self):
        cleaned_data = super(ApplyForm, self).clean()

        payment = cleaned_data.get('payment')
        charge = cleaned_data.get('charge')
        amount = cleaned_data.get('amount')
        adjustment = cleaned_data.get('adjustment')
        reference = cleaned_data.get('reference')
        resp_type = cleaned_data.get('resp_type')

        if payment.payer_type == 'Insurance':
            # Check validity against charge of Insurance
            # if amount is None and adjustment is None:
            #     self.add_error('amount', """Must have value in
            #             either amount or adjustment field for payer
            #             type \"Insurance\"""")
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
                            check the value""" % charge.procedure.cpt.cpt_code)
        else:
            # Check validity against charge of Patient
            if amount is None:
                self.add_error('amount',
                        'Amount is required for payer type \"Patient\"')
            if resp_type is None:
                self.add_error('resp_type',
                        """Responsibility type is required for
                        payer type \"Patient\"""")


class ApplyFormSet(forms.BaseFormSet):
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
            if total > payment.balance:
                raise forms.ValidationError(
                        'Total applied amount exceeds remaining balance.')



# class PatientChargeForm(forms.ModelForm):
#     amount = forms.DecimalField(
#             max_digits=MAX_DIGITS,
#             decimal_places=DECIMAL_PLACES,
#             min_value=0)

#     class Meta:
#         model = PatientCharge
#         fields = '__all__'

#     def __init__(self, *args, **kwargs):
#         claim_id = kwargs.pop('claim_id', None)
#         super(PatientChargeForm, self).__init__(*args, **kwargs)
#         self.fields['procedure'] = forms.ModelChoiceField(
#                 queryset=Procedure.objects.filter(claim=claim_id))


# class PatientAppliedPaymentForm(forms.ModelForm):
#     payment = forms.ModelChoiceField(
#             queryset=Payment.objects.filter(payer_type='Patient'))
#     amount = forms.DecimalField(
#             max_digits=MAX_DIGITS,
#             decimal_places=DECIMAL_PLACES,
#             min_value=0)

#     class Meta:
#         model = PatientAppliedPayment
#         fields = '__all__'

#     def clean(self):
#         cleaned_data = super(PatientAppliedPaymentForm, self).clean()

#         patient_charge = cleaned_data.get('patient_charge')
#         amount = cleaned_data.get('amount')

#         if amount is not None:
#             if patient_charge.balance < amount:
#                 self.add_error('amount',
#                         """Patient apply amount exceeds balance of
#                         patient responsibility. (on line CPT: \"%s\")""" % \
#                         procedure.cpt.cpt_code)


# class PatientAppliedPaymentFormSet(forms.BaseFormSet):
#     def clean(self):
#         if any(self.errors):
#             return

#         total_applied_to_charge = dict()
#         total_applied_to_payment = dict()

#         for form in self.forms:
#             cleaned_data = form.cleaned_data
#             if cleaned_data:
#                 payment = cleaned_data.get('payment')
#                 patient_charge = cleaned_data.get('patient_charge')
#                 amount = cleaned_data.get('amount')

#                 if amount is not None:
#                     total_applied_to_charge[patient_charge] = \
#                             amount + (total_applied_to_charge\
#                             .get(patient_charge) or 0)

#                     total_applied_to_payment[payment] = \
#                             amount + (total_applied_to_payment\
#                             .get(payment) or 0)

#         # Check if total applied amount exceeds that charge or not
#         for charge, total in total_applied_to_charge.iteritems():
#             if total > charge.balance:
#                 raise forms.ValidationError(
#                         """Total patient applied amount exceeds patient
#                         balance. (on patient charge: \"%s\")""" % \
#                         charge.__str__)

#         # Check if total applied amount exceeds payment
#         # unapplied amount or not
#         for payment, total in total_applied_to_payment.iteritems():
#             if total > payment.unapplied_amount:
#                 raise forms.ValidationError(
#                         """Total patient applied amount exceeds payment
#                         unapplied amount. (on payment: \"%s\")""" % \
#                         payment.__str__)
