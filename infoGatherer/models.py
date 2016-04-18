from django.db import models
from django_countries.fields import CountryField
from django.core.exceptions import ValidationError
from django_languages.fields import LanguageField
from localflavor.us.models import USStateField, USSocialSecurityNumberField, PhoneNumberField
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from audit_log.models.managers import AuditLog
from django.forms.models import model_to_dict
from simple_history.models import HistoricalRecords

GENDER_CHOICES = (('Female', 'Female'), ('Male', 'Male'), ('Undifferentiated', 'Undifferentiated'), ('Blank', ''))

RACE_CHOICES = (('American Indian or Alaska Native', 'American Indian or Alaska Native'), \
                ('Asian', 'Asian'), \
                ('Black or African American', 'Black or African American'), \
                ('Hispanic or Latino', 'Hispanic or Latino'), \
                ('Native Hawaiian or Other Pacific Islander','Native Hawaiian or Other Pacific Islander'), \
                ('White', 'White'),\
                ('PD', 'Patient Declined'), ('Blank', ''))

ETHNICITY_CHOICES = (('Hispanic or Latino', 'Hispanic or Latino'), \
                     ('Not Hispanic or Latino', 'Not Hispanic or Latino'), \
                     ('PD', 'Patient Declined'), ('Blank', ''))

EMP_STATUS_CHOICES = (('Employed','Employed'),('Unemployed','Unemployed'),\
                      ('Full-Time Student','Full-Time Student'), \
                      ('Part-Time Student','Part-Time Student'), \
                      ('Other','Other'),('Retired','Retired'),('Child','Child'),('Blank',''))

CALL_PREF_CHOICES = (('Home','Home Phone'),('Cell','Cell Phone'))

WRITTEN_PREF_CHOICES = (('Email','Email'),('Post','Postal Mail'))

ACCOUNT_TYPE_CHOICES = (('9','09: Self-pay'),
('10','10: Central Certification'),
('11','11: Other Non-Federal Programs'),
('12','12: Preferred Provider Org. (PPO)'),
('13','13: Point of Service (POS)'),
('14','14: Exclusive Provider Org. (EPO)'),
('15','15: Indemnity Insurance'),
('16','16: Health Maintenance Org. (HMO)'),
('AM','AM: Automobile Medical'),
('BL','BL: Blue Cross/Blue Shield'),
('CH','CH: Champus'),
('CI','CI: Commercial Insurance Co.'),
('DS','DS: Disability'),
('HM','HM: Health Maintenance Org.'),
('LI','LI: Liability'),
('LM','LM: Liability Medical'),
('MB','MB: Medicare Part B'),
('MC','MC: Medicaid'),
('OF','OF: Other'),
('TV','TV: Title V'),
('VA','VA: Veteran Administration Plan'),
('WC','WC: Workers Compensation'),
('Blank','')
)


ACCOUNT_STATUS_CHOICES = (('Current','Current'),('Archived','Archived'))

SIGN_CHOICES = (('Yes','Yes'),('No','No'))

INSURANCE_LEVEL_CHOICES = (('Primary','Primary'),('Secondary','Secondary'),('Tertiary','Tertiary'))

INSURANCE_STATUS_CHOICES = (('Active','Active'),('Inactive','Inactive'),('Invalid','Invalid'),('Not Found','Not Found'))

PAYER_TYPE_CHOICE = (('M','Medicare'),('C','Commercial'))

RELATION_CHOICES = (('Self','Self'),('Other','Other'))

PROVIDER_ROLE_CHOICES = (
    ('Billing', 'Billing'),
    ('Rendering', 'Rendering'),
    ('Dual', 'Dual'),
    ('Location', 'Location'),
    ('Referring', 'Referring'),
)

POS_CHOICES = (('Home','Home'),('Hospital','Hospital'),('Office','Office'))

POS = (
    ("42","Ambulance - Air or Water (42)"),
    ("41","Ambulance - Land (41)"),
    ("24","Ambulatory Surgical Center (24)"),
    ("13","Assisted Living Facility (13)"),
    ("25","Birthing Center (25)"),
    ("53","Community Mental Health Center (53)"),
    ("61","Comprehensive Inpatient Rehabilitation Facility (61)"),
    ("62","Comprehensive Outpatient Rehabilitation Facility (62)"),
    ("33","Custodial Care Facility (33)"),
    ("23","Emergency Room - Hospital (23)"),
    ("65","End-Stage Renal Disease Treatment Facility (65)"),
    ("50","Federally Qualified Health Center (50)"),
    ("14","Group Home (14)"),
    ("12","Home (12)"),
    ("04","Homeless Shelter (04)"),
    ("34","Hospice (34)"),
    ("49","Independent Clinic (49)"),
    ("81","Independent Laboratory (81)"),
    ("05","Indian Health Service Free-standing Facility (05)"),
    ("06","Indian Health Service Provider-based Facility (06)"),
    ("21","Inpatient Hospital (21)"),
    ("51","Inpatient Psychiatric Facility (51)"),
    ("54","Intermediate Care Facility/Mentally Retarded (54)"),
    ("60","Mass Immunization Center (60)"),
    ("26","Military Treatment Facility (26)"),
    ("15","Mobile Unit (15)"),
    ("57","Non-residential Substance Abuse Treatment Facility (57)"),
    ("32","Nursing Facility (32)"),
    ("19","Off Campus - Outpatient Hospital (19)"),
    ("11","Office (11)"),
    ("22","On Campus - Outpatient Hospital (22)"),
    ("99","Other Place of Service (99)"),
    ("01","Pharmacy (01)"),
    ("09","Prison-Correctional Facility (09)"),
    ("52","Psychiatric Facility-Partial Hospitalization (52)"),
    ("56","Psychiatric Residential Treatment Center (56)"),
    ("71","Public Health Clinic (71)"),
    ("55","Residential Substance Abuse Treatment Facility (55)"),
    ("72","Rural Health Clinic (72)"),
    ("03","School (03)"),
    ("31","Skilled Nursing Facility (31)"),
    ("16","Temporary Lodging (16)"),
    ("07","Tribal 638 Free-standing Facility (07)"),
    ("08","Tribal 638 Provider-based Facility (08)"),
    ("20","Urgent Care Facility (20)"),
    ("17","Walk-in Retail Health Clinic (17)"),
)

HEALTHPLAN = (
    ('Medicare', 'Medicare'),
    ('Medicaid', 'Medicaid'),
    ('Tricare', 'Tricare'),
    ('Champva', 'Champva'),
    ('GroupHealthPlan', 'GroupHealthPlan'),
    ('FECA_Blk_Lung', 'FECA Blk Lung'),
    ('Other', 'Other'),
)
SEX = (
    ('', '-----'),
    ('M', 'Male'),
    ('F', 'Female'),
)
PAT_RELA_TO_INSURED = (
    ('--' , '-----'),
    ('Self', 'Self'),
    ('Spouse', 'Spouse'),
    ('Child', 'Child'),
    ('Other', 'Other'),
)
DX_PT = (
    ('', '---'),
    ('A', 'A'),
    ('B', 'B'),
    ('C', 'C'),
    ('D', 'D'),
    ('E', 'E'),
    ('F', 'F'),
    ('G', 'G'),
    ('H', 'H'),
    ('I', 'I'),
    ('J', 'J'),
    ('K', 'K'),
    ('L', 'L'),
)
UNIT = (
    ('ME', 'Milligram'),
    ('F2', 'International Unit'),
    ('GR', 'Gram'),
    ('ML', 'Milliliter'),
    ('UN', 'Unit'),
)


"""
CATEGORIES = (
    ('LAB', 'labor'),
    ('CAR', 'cars'),
    ('TRU', 'trucks'),
    ('WRI', 'writing'),
)
"""


#New stuf

class CPT(models.Model):
    cpt_code=   models.CharField(max_length=50)
    cpt_description=    models.CharField(max_length=200)
    cpt_mod_a=  models.CharField(max_length=10, null=True, blank=True)
    cpt_mod_b=  models.CharField(max_length=10, null=True, blank=True)
    cpt_mod_c=  models.CharField(max_length=10, null=True, blank=True)
    cpt_mod_d=  models.CharField(max_length=10, null=True, blank=True)
    history = HistoricalRecords()

    cpt_charge= models.FloatField()

    class Meta:
        verbose_name = 'Procedure Codes (CPT)'
        verbose_name_plural = 'Procedure Codes (CPT)'

    def __unicode__(self):
        return self.cpt_code+" "+self.cpt_description


class PostAd(models.Model):
    insured_idnumber= models.CharField(max_length=50)
    insured_name= models.CharField(max_length=100)
    insured_address= models.CharField(max_length=100, null=True, blank=True)
    insured_streetaddress = models.TextField(max_length=100)
    insured_city    = models.TextField(max_length=50)
    insured_zip     = models.CharField(max_length=5,default='')
    insured_state   = USStateField(default='')
    insured_telephone= PhoneNumberField()
    insured_other_insured_policy=models.TextField(max_length=100)
    insured_birth_date  = models.DateField()
    other_cliam_id  = models.TextField(max_length=50)
    insured_plan_name_program= models.TextField(max_length=100)
    claim_codes= models.TextField(max_length=50)
    birth_date  = models.DateField()
    pat_streetaddress = models.TextField(max_length=100)
    pat_city    = models.TextField(max_length=50)
    pat_zip     = models.CharField(max_length=5,default='')
    pat_state   = USStateField(default='')
    pat_telephone= PhoneNumberField()
    pat_other_insured_name=models.TextField(max_length=100)
    pat_other_insured_policy=models.TextField(max_length=100)
    pat_reservednucc1=models.TextField(max_length=50)
    pat_reservednucc2=models.TextField(max_length=50)
    pat_reservednucc3=models.TextField(max_length=50)
    pat_insuranceplanname=models.TextField(max_length=100)
    pat_auto_accident_state=USStateField(default='')
    pat_name    = models.TextField(max_length=50)
    payer_num = models.CharField(max_length=100)
    payer_name = models.CharField(max_length=100)
    payer_address = models.CharField(max_length=200)



class ReferringProvider(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    address1 = models.CharField(max_length=200,default='', blank=True)
    address2 = models.CharField(max_length=200,null=True, blank=True)
    city= models.CharField(max_length=200,default='',null=True, blank=True)
    state=USStateField(default='',null=True, blank=True)
    zip=models.IntegerField(default='',null=True, blank=True)
    phone_work=PhoneNumberField(default='',null=True, blank=True)
    fax=models.CharField(max_length=100,null=True, blank=True)
    email=models.CharField(max_length=100,null=True, blank=True)
    taxonomy=models.CharField(max_length=100,default='',null=True, blank=True)
    NPI=models.IntegerField()
    tax_id=models.CharField(max_length=100,null=True, blank=True)
    history = HistoricalRecords()

    def __unicode__(self):
        return self.first_name+" "+self.last_name


class dx(models.Model):
    ICD_10 = models.CharField(max_length=200, primary_key=True)
    description = models.CharField(max_length=200)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Diagnostic Codes'
        verbose_name_plural = 'Diagnostic Codes'

    def __unicode__(self):
        return self.ICD_10


#New stuff

class Personal_Information(models.Model):
    first_name = models.CharField(max_length=128, default='')
    middle_name = models.CharField(max_length=128, default='', null=True, blank=True)
    last_name = models.CharField(max_length=128, default='')
    dob = models.DateField()
    sex = models.CharField(choices=GENDER_CHOICES, max_length=32, default='Blank')
    race = models.CharField(choices=RACE_CHOICES, max_length=64, default='Blank')
    ethnicity = models.CharField(choices=ETHNICITY_CHOICES, max_length=64, default='Blank')
    language = LanguageField(default='en')
    country = CountryField(blank_label='',default='US')
    ssn = USSocialSecurityNumberField(null=True, blank=True, help_text='XXX-XX-XXXX')
    address = models.CharField(max_length=128,default='')
    city = models.CharField(max_length=128,default='')
    state = USStateField(default='')
    zip = models.CharField(max_length=5,default='')
    home_phone = PhoneNumberField(help_text='XXX-XXX-XXXX')
    cell_phone = PhoneNumberField(null=True, blank=True, help_text='XXX-XXX-XXXX')
    email = models.EmailField(null=True, blank=True)
    call_pref = models.CharField(choices=CALL_PREF_CHOICES, max_length=10, default='Home')
    written_pref = models.CharField(choices=WRITTEN_PREF_CHOICES, max_length=12, default='Post')
    emp_status = models.CharField(choices=EMP_STATUS_CHOICES, max_length=64, default='Blank')

    #Account Information
    chart_no = models.AutoField(primary_key=True)
    date_registered = models.DateField(default=timezone.now)
    account_type = models.CharField(choices=ACCOUNT_TYPE_CHOICES, max_length=64, default='Blank')
    account_status = models.CharField(choices=ACCOUNT_STATUS_CHOICES, max_length=64, default='Current')
    sign = models.CharField(choices=SIGN_CHOICES, max_length=3, default='Yes')
    guarantor = models.ForeignKey("self", null=True, blank=True)

    audit_log = AuditLog()
    history = HistoricalRecords()

    def get_admin_url(self):
        return urlresolvers.reverse("admin:%s__%s__change" %
            (self._meta.app_label, self._meta.model_name), args=(self.pk,))

    class Meta:
        verbose_name = 'Patient Details'
        verbose_name_plural = 'Patient Details'

    def __unicode__(self):
        return self.get_full_name()

    def natural_key(self):
        return dict({
            'chart_no': self.chart_no,
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'dob': self.dob
        })


    @property
    def full_address(self):
        return '%s, %s, %s %s' % (self.address, self.city, self.state, self.zip)

    @property
    def get_ssn(self):
        return str(self.ssn)

    @property
    def get_home_phone(self):
        return str(self.home_phone)

    @property
    def full_name(self):
        if(self.middle_name):
            return '%s %s %s' % (self.first_name, self.middle_name, self.last_name)
        else:
            return '%s %s' % (self.first_name, self.last_name)

    @property
    def format_name(self):
        if(self.middle_name):
            return '%s, %s, %s' % (self.last_name, self.first_name, self.middle_name)
        else:
            return '%s, %s' % (self.last_name, self.first_name)

    @property
    def age(self):
        today = timezone.now().date()
        return today.year - \
                self.dob.year - \
                ((today.month, today.day) < (self.dob.month, self.dob.day))

    def get_full_name(self):
        return self.full_name

    def get_format_name(self):
        return self.format_name

    def get_data(self):
        details = model_to_dict(self, exclude=['audit_log','dob','date_registered','state','country'])
        details['dob'] = str(self.dob)
        details['date_registerd'] = str(self.date_registered)
        details['state'] = str(self.state)
        details['country'] = str(self.country)
        return details

    @property
    def get_primary_insurane(self):
        if(self.insurance_information_set.all().filter(level='primary').exists()):
            return str(self.insurance_information_set.all().filter(level='primary')[0].payer.name)
        else:
            return ""

class Guarantor_Information(models.Model):
    patient = models.ForeignKey(Personal_Information)
    relation = models.CharField(choices=RELATION_CHOICES,max_length=128)

    #If relation is self, auto fill rest of the details
    first_name = models.CharField(max_length=128, default='', null=True, blank=True)
    middle_name = models.CharField(max_length=128, default='', null=True, blank=True)
    last_name = models.CharField(max_length=128, default='', null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    sex = models.CharField(choices=GENDER_CHOICES, max_length=32, default='Blank')
    race = models.CharField(choices=RACE_CHOICES, max_length=64, default='Blank')
    ethnicity = models.CharField(choices=ETHNICITY_CHOICES, max_length=64, default='Blank')
    language = LanguageField(default='en')
    country = CountryField(blank_label='',default='US')
    ssn = USSocialSecurityNumberField(null=True, blank=True, help_text='XXX-XX-XXXX')
    address = models.CharField(max_length=128,default='', null=True, blank=True)
    city = models.CharField(max_length=128,default='', null=True, blank=True)
    state = USStateField(default='')
    zip = models.CharField(max_length=5, default='',null=True, blank=True)
    home_phone = PhoneNumberField(help_text='XXX-XXX-XXXX', null=True, blank=True)

    class Meta:
        verbose_name = 'Guarantor'
        verbose_name_plural = 'Guarantor'

    def __unicode__(self):
        return str(self.patient.pk)

class Payer(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=256, default='')
    address = models.CharField(max_length=256, default='')
    city = models.CharField(max_length=128,default='')
    state = USStateField(default='')
    zip = models.IntegerField(default='')
    phone = PhoneNumberField(null=True, blank=True, help_text='XXX-XXX-XXXX')
    type = models.CharField(choices=PAYER_TYPE_CHOICE,max_length=1,default='C')
    history = HistoricalRecords()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Insurance (payer) Details'
        verbose_name_plural = 'Insurance (payer) Details'


    @property
    def full_address(self):
        return '%s, %s, %s %s' % (self.address, self.city, self.state, self.zip)


    def natural_key(self):
        return dict({'code': self.code, 'name': self.name})

class Insurance_Information(models.Model):
    level = models.CharField(choices=INSURANCE_LEVEL_CHOICES,max_length=10,default='Primary')
    status = models.CharField(choices=INSURANCE_STATUS_CHOICES,max_length=10,default='Active')
    payer = models.ForeignKey(Payer)
    patient = models.ForeignKey(Personal_Information)
    insurance_id = models.CharField(max_length=32,default='')
    audit_log = AuditLog()
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Paitent - Insurance Details'
        verbose_name_plural = 'Paitent - Insurance Details'

    def __unicode__(self):
        return self.payer.name

    def get_payer_name(self):
        return self.payer.name

class Locations(models.Model):
    location_name = models.CharField(max_length=128,default='')
    address = models.CharField(max_length=256, default='')
    city = models.CharField(max_length=128,default='')
    state = USStateField(default='')
    phone = PhoneNumberField(null=True, blank=True, help_text='XXX-XXX-XXXX')

    def __unicode__(self):
        return self.location_name

class Provider(models.Model):
    provider_name = models.CharField(max_length=128,default='')
    role = models.CharField(choices=PROVIDER_ROLE_CHOICES,max_length=10,default='Rendering')
    tax_id = models.IntegerField(default='',null=True, blank=True)
    npi = models.IntegerField(default='',null=True, blank=True)
    provider_ssn= models.CharField(max_length=128,default='',null=True, blank=True)
    provider_ein= models.CharField(max_length=128,default='',null=True, blank=True)
    speciality = models.CharField(max_length=128,default='',null=True, blank=True)
    provider_address = models.CharField(max_length=256, default='',null=True, blank=True)
    provider_city = models.CharField(max_length=128,default='',null=True, blank=True)
    provider_state = USStateField(default='',null=True, blank=True)
    provider_zip = models.IntegerField(default='',null=True, blank=True)
    provider_phone = PhoneNumberField(null=True, blank=True, help_text='XXX-XXX-XXXX',)
    place_of_service = models.CharField(choices=POS,max_length=200,default='',null=True, blank=True)
    history = HistoricalRecords()


    def __unicode__(self):
        return self.provider_name

    def full_clean(self, *args, **kwargs):
        dic={}
        if self.npi is None:
            dic['npi']='Please provide npi'
        if len(self.provider_address)==0:
            dic['provider_address']='Please provide address'
        if len(self.provider_city)==0:
            dic['provider_city']='Please provide city'
        if self.provider_state is None:
            dic['provider_state']='Please provide state'
        if self.provider_zip is None:
            dic['provider_zip']='Please provide zip'
        if len(self.provider_phone)==0:
            dic['provider_phone']='Please provide phone number'

        if self.place_of_service is None:
            dic['place_of_service']='Please provide POS'

        if self.role == 'Billing' or self.role == 'Dual' or self.role == 'Rendering':
            if self.tax_id is None:
                dic['tax_id']='Please provide tax id'
            if len(self.speciality)==0:
                dic['speciality']='Please provide speciality'
        raise ValidationError(dic)

