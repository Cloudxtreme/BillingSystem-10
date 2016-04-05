from __future__ import unicode_literals

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Sum

from base.models import *
from infoGatherer.models import (
        Personal_Information,
        Payer,
        Provider,
        ReferringProvider,
        CPT)


PAYER_TYPE = [
    ('Insurance', 'Insurance'),
    ('Patient', 'Patient'),
]

PAYMENT_METHOD = [
    ('Check', 'Check'),
    ('Credit Card', 'Credit Card'),
    ('Cash', 'Cash')
]

RESPONSIBILITY_TYPE = [
    ('Co-pay', 'Co-pay'),
    ('Deductible', 'Deductible'),
    ('Other PR', 'Other PR'),
]



class Claim(BaseModel):
    """
    Claim model captures foreign keys and some information which will
    be used for seaching and reporting.  Non important information
    will be saved in field named with '_detail' suffix just in case we
    can backtrack what has been printed out in claim form.
    """
    payer = models.ForeignKey(Payer)
    payer_detail = models.TextField()

    patient = models.ForeignKey(
            Personal_Information,
            related_name='patient')
    patient_dob = models.DateField()
    patient_detail = models.TextField()

    insured = models.ForeignKey(
            Personal_Information,
            related_name='insured')
    insured_dob = models.DateField()
    insured_detail = models.TextField()

    other_insured = models.ForeignKey(
            Personal_Information,
            related_name='other_insured',
            null=True)
    other_insured_detail = models.TextField()

    referring_provider = models.ForeignKey(ReferringProvider)
    referring_provider_npi = models.CharField(max_length=10)
    referring_provider_detail = models.TextField()

    rendering_provider = models.ForeignKey(
            Provider,
            limit_choices_to={'role': 'rendering'},
            related_name='claim_rendering_provider')
    rendering_provider_npi = models.CharField(max_length=10)
    rendering_provider_detail = models.TextField()

    location_provider = models.ForeignKey(
            Provider,
            limit_choices_to={'role': 'location'},
            related_name='claim_location_provider')
    location_provider_npi = models.CharField(max_length=10)
    location_provider_detail = models.TextField()

    billing_provider = models.ForeignKey(
            Provider,
            limit_choices_to={'role': 'billing'},
            related_name='claim_billing_provider')
    billing_provider_npi = models.CharField(max_length=10)
    billing_provider_detail = models.TextField()

    claim_detail = models.TextField()

    def __str__(self):
        return '%s: %s' % (self.id, self.patient.full_name)

    @property
    def get_patient_insurance(self):
        return self.patient.get_primary_insurane or ''

    @property
    def ins_pmnt_per_claim(self):
        ins_pmnt=0
        for charge_table in Charge.objects.filter(procedure__claim=self.pk).filter(payer_type="insurance"):
            ins_pmnt=ins_pmnt+(charge_table.apply_set.all().aggregate(Sum('amount')).get('amount__sum') or 0)
        return ins_pmnt

    @property
    def ins_adjustment_per_claim(self):
        ins_adjustment=0
        for charge_table in Charge.objects.filter(procedure__claim=self.pk).filter(payer_type="insurance"):
            ins_adjustment=ins_adjustment+(charge_table.apply_set.all().aggregate(Sum('adjustment')).get('adjustment__sum') or 0)
        return ins_adjustment


    @property
    def pat_responsible_per_claim(self):
        pat_responsible=0
        pat_responsible=Charge.objects.filter(procedure__claim=self.pk)\
                                .filter(payer_type="patient")\
                                .aggregate(Sum('amount'))['amount__sum'] or 0
        return pat_responsible

    @property
    def pat_pmnt_per_claim(self):
        pat_pmnt=0
        for charge_table in Charge.objects.filter(procedure__claim=self.pk).filter(payer_type="patient"):
            pat_pmnt=pat_pmnt+(charge_table.apply_set.all().aggregate(Sum('amount')).get('amount__sum') or 0)
        return pat_pmnt

    @property
    def total_charge(self):
        charge=0
        charge=Charge.objects.filter(procedure__claim=self.pk)\
                                .filter(payer_type="insurance")\
                                .aggregate(Sum('amount'))\
                                .get('amount__sum') or 0
        return charge


class claim_pdf(BaseModel):
    claim = models.ForeignKey(Claim)
    _data = models.TextField(
        db_column='data',
        blank=True)

    def set_data(self, data):
        self._data = base64.encodestring(data)

    def get_data(self):
        return base64.decodestring(self._data)

    data = property(get_data, set_data)

class Procedure(BaseModel):
    """
    Procedure model captures one line of cpt code and details that
    appears on claim form.
    """
    claim = models.ForeignKey(Claim)
    rendering_provider = models.ForeignKey(
            Provider,
            limit_choices_to={'role': 'rendering'},
            related_name='procedure_rendering_provider')
    cpt = models.ForeignKey(CPT)
    date_of_service = models.DateField()

    @property
    def balance(self):
        return self.insurance_balance + self.patient_balance

    @property
    def insurance_balance(self):
        ins_charge_q_set = Charge.objects.filter(
                procedure=self.pk,
                payer_type='Insurance')
        ins_total = 0
        for charge in ins_charge_q_set:
            ins_total += charge.balance

        return ins_total

    @property
    def patient_balance(self):
        pat_charge_q_set = Charge.objects.filter(
                procedure=self.pk,
                payer_type='Patient')
        pat_total = 0
        for charge in pat_charge_q_set:
            pat_total += charge.balance

        return pat_total

    @property
    def ins_pmnt_per_procedure(self):
        var=Charge.objects.filter(procedure_id=self.pk)\
                    .filter(payer_type='insurance')\
                    .apply_set.all()\
                    .aggregate(Sum('amount'))\
                    .get('amount__sum') or 0
        print var
        return var

    def __str__(self):
        return '%s: %s' % (self.id, self.cpt.cpt_description)


class Payment(BaseModel):
    """
    Payment model is to capture a payment Xenon Health receives and
    will be distributed some amount to cover procedure that payer
    is charged.
    """
    billing_provider = models.ForeignKey(
            Provider,
            limit_choices_to={'role': 'Billing'},
            related_name='payment_billing_provider')
    rendering_provider = models.ForeignKey(
            Provider,
            limit_choices_to={'role': 'Rendering'},
            related_name='payment_rendering_provider')
    payment_date = models.DateField()
    payer_type = models.CharField(max_length=20, choices=PAYER_TYPE)
    payer_patient = models.ForeignKey(Personal_Information, null=True, blank=True)
    payer_insurance = models.ForeignKey(Payer, null=True, blank=True)
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD)
    check_number = models.CharField(max_length=30, blank=True)
    amount = models.DecimalField(**BASE_DECIMAL)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return '%s, %s' % (self.id, self.amount)

    @property
    def applied_amount(self):
        return self.amount - self.unapplied_amount

    @property
    def payer_name(self):
        if self.payer_type == 'Insurance':
            return self.payer_insurance.name
        else:
            return self.payer_patient.full_name

    @property
    def unapplied_amount(self):
        total_apply = Apply.objects\
                .filter(payment=self.pk)\
                .aggregate(Sum('amount'))\
                .get('amount__sum') or 0

        return self.amount - total_apply

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


class Charge(BaseModel):
    """
    Charge model captures the amount of money that is responsible by
    payer indicated by "payer_type" field for one procedure which
    appears on a claim form.

    In case of payer is
    insurance company, "resp_type" should be null in this case.

    In case that the charge will be paid by patient,
    "resp_type" field will indicate reasons of that charge.
    """
    procedure = models.ForeignKey(Procedure)
    payer_type = models.CharField(max_length=20, choices=PAYER_TYPE)
    amount = models.DecimalField(**BASE_DECIMAL)
    resp_type = models.CharField(
            max_length=20,
            choices=RESPONSIBILITY_TYPE,
            null=True,
            blank=True)

    @property
    def balance(self):
        if self.payer_type == 'Insurance':
            total_apply = Apply.objects\
                    .filter(charge=self.pk)\
                    .aggregate(Sum('amount'), Sum('adjustment'))
            amount = total_apply.get('amount__sum') or 0
            adjustment = total_apply.get('adjustment__sum') or 0

            return self.amount - (amount + adjustment)
        else:
            total_apply = Apply.objects\
                    .filter(charge=self.pk)\
                    .aggregate(Sum('amount'))\
                    .get('amount__sum') or 0
            return self.amount - total_apply

    @property
    def total_apply(self):
        total = Apply.objects\
                .filter(charge=self.pk)\
                .aggregate(Sum('amount'))
        return total.get('amount__sum') or Decimal('0.00')

    @property
    def total_adjustment(self):
        total = Apply.objects\
                .filter(charge=self.pk)\
                .aggregate(Sum('adjustment'))
        return total.get('adjustment__sum') or Decimal('0.00')

    def __str__(self):
        return '%s: %s --- $%s' % (
                self.id,
                self.payer_type,
                self.amount)


class Apply(BaseModel):
    """
    Apply model captures amount of payment that payer, indicated by
    "payer_type" of "payment" field, pays for a charge.  Amount
    to be applied must not exceed remaining balance of that charge.
    In case that "payer_type" of "charge" is Insurance, it is normal
    that the company will not pay a full amount of charge.  In such
    case, "adjustment" is a field to cover up the remaining amount
    in order to make total amount which is responsible by the insurance
    becomes zero on a report.  In case that "payer_type" is Patient,
    adjustment should be null.
    """
    payment = models.ForeignKey(Payment)
    charge = models.ForeignKey(Charge)
    amount = models.DecimalField(
            null=True,
            blank=True,
            **BASE_DECIMAL)
    adjustment = models.DecimalField(
            null=True,
            blank=True,
            **BASE_DECIMAL)
    reference = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return '%s: %s --- $%s, $%s' % (
                self.id,
                self.charge,
                self.amount,
                self.adjustment)

    def natural_key(self):
        return dict({
            'id': self.id,
            'amount': self.amount,
            'adjustment': self.adjustment
        })

    @property
    def payer(self):
        p = Payment.objects.filter(id=self.payment_id).values()[0]
        payerType = p['payer_type']
        if(payerType=='Insurance'):
            return Payer.objects.filter(code=p['payer_insurance_id']).values()[0]['name']
        else:
            name=Personal_Information.objects.filter(pk=p['payer_patient_id']).values()[0]
            return name['last_name']+", "+name['first_name']

    @property
    def rpi(self):
        return self.payment_id

    @property
    def dos(self):
        return Procedure.objects.filter(id=self.charge.procedure.pk).values()[0]['date_of_service']

    @property
    def payment_date(self):
        return Payment.objects.filter(id=self.payment.pk).values()[0]['payment_date']

    @property
    def patient_Id(self):
        claimID=Procedure.objects.filter(id=self.charge.procedure.pk).values()[0]['claim_id']
        return Claim.objects.filter(id=claimID).values()[0]['patient_id']

    @property
    def patient_name(self):
        claimID=Procedure.objects.filter(id=self.charge.procedure.pk).values()[0]['claim_id']
        patID=Claim.objects.filter(id=claimID).values()[0]['patient_id']
        pat=Personal_Information.objects.filter(chart_no=patID).values()[0]
        return pat['last_name']+", "+pat['first_name']


class Note(BaseModel):
    claim = models.ForeignKey(Claim)
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    desc = models.CharField(max_length=255)


class Document(BaseModel):
    claim = models.ForeignKey(Claim)
    docfile = models.FileField(upload_to='documents/')


