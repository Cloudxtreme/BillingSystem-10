from __future__ import unicode_literals

from decimal import Decimal
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
        total_applied_payment_amount = Decimal(AppliedPayment.objects.filter(procedure=self.pk).\
            aggregate(Sum('amount')).get('amount__sum') or 0)

        total_applied_payment_adjustment = Decimal(AppliedPayment.objects.filter(procedure=self.pk).\
            aggregate(Sum('adjustment')).get('adjustment__sum') or 0)

        return (self.charge + total_applied_payment_adjustment) - total_applied_payment_amount


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
        return '%s, %s' % (self.id, str(self.amount))

    @property
    def payer_name(self):
        if self.payer_type == 'Insurance':
            return self.payer_insurance.name
        else:
            return self.patient.get_full_name()

    @property
    def unapplied_amount(self):
        total_applied_payment = Decimal(AppliedPayment.objects.filter(payment=self.pk).\
            aggregate(Sum('amount')).get('amount__sum') or 0)

        return self.amount - total_applied_payment

    def natural_key(self):
        return dict({
            'id': self.id,
            'payment_date': self.payment_date,
            'payer_type': self.payer_type,
            'amount': self.amount,
            'check_number': self.check_number
        })


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
        return '%s, %s, %s' % (self.id, str(self.amount), str(self.adjustment))

    def natural_key(self):
        return dict({
            'id': self.id,
            'amount': self.amount,
            'adjustment': self.adjustment
        })
