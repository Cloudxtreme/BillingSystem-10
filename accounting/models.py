from __future__ import unicode_literals

from django.db import models
from django.db.models import Sum
from django.core.validators import MinValueValidator

from base.models import *
from infoGatherer.models import (Personal_Information, Payer, Provider, ReferringProvider, CPT)


PAYER_TYPE = (
    ('Insurance', 'Insurance'),
    ('Patient', 'Patient'),
)

PAYMENT_METHOD = (
    ('Check', 'Check'),
    ('Credit Card', 'Credit Card'),
    ('Cash', 'Cash')
)


class Claim(BaseModel):
    """
    Claim model captures foreign keys and some information which will be
    used for seaching and reporting.  Non important information will be saved
    in field named with '_detail' suffix just in case we can backtrack
    what has been printed out in claim form.
    """
    payer = models.ForeignKey(Payer)
    payer_detail = models.TextField(blank=False)

    patient = models.ForeignKey(Personal_Information, related_name='patient')
    patient_dob = models.DateField()
    patient_detail = models.TextField()

    insured = models.ForeignKey(Personal_Information, related_name='insured')
    insured_dob = models.DateField()
    insured_detail = models.TextField()

    other_insured = models.ForeignKey(Personal_Information, related_name='other_insured', null=True)
    other_insured_detail = models.TextField()

    referring_provider = models.ForeignKey(ReferringProvider)
    referring_provider_npi = models.CharField(max_length=10)
    referring_provider_detail = models.TextField()

    rendering_provider = models.ForeignKey(Provider, limit_choices_to={'role': 'rendering'}, related_name='claim_rendering_provider')
    rendering_provider_npi = models.CharField(max_length=10)
    rendering_provider_detail = models.TextField()

    location_provider = models.ForeignKey(Provider, limit_choices_to={'role': 'location'}, related_name='claim_location_provider')
    location_provider_npi = models.CharField(max_length=10)
    location_provider_detail = models.TextField()

    billing_provider = models.ForeignKey(Provider, limit_choices_to={'role': 'billing'}, related_name='claim_billing_provider', )
    billing_provider_npi = models.CharField(max_length=10)
    billing_provider_detail = models.TextField()

    claim_detail = models.TextField()

    def __str__(self):
        return '%s, %s' % (self.id, self.patient.get_full_name())


class Procedure(BaseModel):
    """
    This model is to capture one line of cpt code and its details appearing on claim form.
    """
    claim = models.ForeignKey(Claim)
    rendering_provider = models.ForeignKey(Provider, limit_choices_to={'role': 'rendering'}, related_name='procedure_rendering_provider')
    cpt = models.ForeignKey(CPT)
    charge = models.DecimalField(max_digits=MAX_DIGITS, decimal_places=DECIMAL_PLACES)
    date_of_service = models.DateField()

    def __str__(self):
        return '%s, %s' % (self.id, self.cpt.cpt_description)

    @property
    def balance(self):
        total_applied_payment = AppliedPayment.objects.filter(procedure=self.pk).\
            aggregate(Sum('amount')).get('amount__sum')

        if total_applied_payment:
            return self.charge - int(total_applied_payment)
        else:
            return  self.charge


class Payment(BaseModel):
    """
    Payment model is to capture a payment Xenon Health receives and will be
    distributed some amount to cover procedure that payer is charged.
    """
    billing_provider = models.ForeignKey(Provider, limit_choices_to={'role': 'Billing'}, related_name='payment_billing_provider')
    rendering_provider = models.ForeignKey(Provider, limit_choices_to={'role': 'Rendering'}, related_name='payment_rendering_provider')
    payment_date = models.DateField()
    payer_type = models.CharField(max_length=50, choices=PAYER_TYPE, default=PAYER_TYPE[0])
    payer_patient = models.ForeignKey(Personal_Information, null=True, blank=True)
    payer_insurance = models.ForeignKey(Payer, null=True, blank=True)
    payment_method = models.CharField(max_length=255, choices=PAYMENT_METHOD)
    check_number = models.CharField(max_length=30, blank=True)
    amount = models.DecimalField(max_digits=MAX_DIGITS, decimal_places=DECIMAL_PLACES, validators=[MinValueValidator(0)])
    description = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        return self.id

    def __str__(self):
        return '%s, $%s' % (self.id, self.amount)

    @property
    def applied_amount(self):
        return self.unapplied_amount  - self.amount

    @property
    def payer_name(self):
        if self.payer_type == 'Insurance':
            return self.payer_insurance.name
        else:
            return self.patient.get_full_name()

    @property
    def unapplied_amount(self):
        total_applied_payment = AppliedPayment.objects.filter(payment=self.pk).\
            aggregate(Sum('amount')).get('amount__sum')

        if total_applied_payment:
            return self.amount - int(total_applied_payment)
        else:
            return  self.amount

    def natural_key(self):
        return dict({
            'id': self.id,
            'payment_date': self.payment_date,
            'payer_type': self.payer_type,
            'amount': self.amount,
            'check_number': self.check_number
        })

    class Meta:
        verbose_name = 'Payments List'
        verbose_name_plural = 'Payments List'


class AppliedPayment(BaseModel):
    """
    AppliedPayment model is to capture some amount of money from payment model
    assigned to cover charge appearing on claim form
    """
    payment = models.ForeignKey(Payment)
    procedure = models.ForeignKey(Procedure)
    amount = models.DecimalField(max_digits=MAX_DIGITS, decimal_places=DECIMAL_PLACES, validators=[MinValueValidator(0)])
    adjustment = models.DecimalField(max_digits=MAX_DIGITS, decimal_places=DECIMAL_PLACES, default=0)
    reference = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return '%s, %s, %s, %s, %s' % (self.id, self.procedure, self.amount, self.adjustment, self.reference)

    def natural_key(self):
        return dict({
            'id': self.id,
            'amount': self.amount,
            'adjustment': self.adjustment
        })

    def __unicode__(self):
        return unicode(self.reference) or u''
    
    # @property
    # def payer(self):
    #     p=Payment.objects.filter(id=self.payment_id).values()[0]
    #     payerType=p['payer_type']
    #     if(payerType=='Insurance'):
    #         return Payer.objects.filter(code=p['payer_insurance_id']).values()[0]['name']
    #     else:
    #         name=Personal_Information.objects.filter(id=p['payer_patient_id']).values()[0]
    #         return name['last_name']+", "+name['first_name']

    # @property 
    # def rpi(self):
    #     return self.payment_id

    # @property
    # def dos(self):
    #     return Procedure.objects.filter(id=self.procedure_id).values()[0]['date_of_service']

    # @property
    # def payment_date(self):
    #     return Payment.objects.filter(id=self.payment_id).values()[0]['payment_date']

    # @property
    # def patient_Id(self):
    #     claimID=Procedure.objects.filter(id=self.procedure_id).values()[0]['claim_id']
    #     return Claim.objects.filter(id=claimID).values()[0]['patient_id']

    # @property
    # def patient_name(self):
    #     claimID=Procedure.objects.filter(id=self.procedure_id).values()[0]['claim_id']
    #     patID=Claim.objects.filter(id=claimID).values()[0]['patient_id']
    #     pat=Personal_Information.objects.filter(chart_no=patID).values()[0]
    #     return pat['last_name']+", "+pat['first_name']
