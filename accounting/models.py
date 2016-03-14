from __future__ import unicode_literals

from django.db import models


from base.models import *
from infoGatherer.models import (Personal_Information, Payer, Provider, ReferringProvider)


PAYER_TYPE = (
    ('Insurance', 'Insurance'),
    ('Patient', 'Patient')
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
    what has been printed out.
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


class Procedure(BaseModel):
    claim = models.ForeignKey(Claim)
    rendering_provider = models.ForeignKey(Provider, limit_choices_to={'role': 'rendering'}, related_name='procedure_rendering_provider')
    cpt_code = models.CharField(max_length=20)
    charge = models.DecimalField(max_digits=MAX_DIGITS, decimal_places=DECIMAL_PLACES)


class Payment(BaseModel):
    billing_provider = models.ForeignKey(Provider, limit_choices_to={'role': 'Billing'}, related_name='payment_billing_provider')
    rendering_provider = models.ForeignKey(Provider, limit_choices_to={'role': 'Rendering'}, related_name='payment_rendering_provider')
    payment_date = models.DateField()
    payer_type = models.CharField(max_length=50, choices=PAYER_TYPE, default=PAYER_TYPE[0])
    payer_patient = models.ForeignKey(Personal_Information, null=True)
    payer_insurance = models.ForeignKey(Payer, null=True)
    payment_method = models.CharField(max_length=255, choices=PAYMENT_METHOD)
    check_number = models.CharField(max_length=30, blank=True)
    amount = models.DecimalField(max_digits=MAX_DIGITS, decimal_places=DECIMAL_PLACES)
    description = models.CharField(max_length=255, blank=True)


class AppliedPayment(BaseModel):
    claim = models.ForeignKey(Claim)
    payment = models.ForeignKey(Payment)
    procedure = models.ForeignKey(Procedure)
    amount = models.DecimalField(max_digits=MAX_DIGITS, decimal_places=DECIMAL_PLACES)
