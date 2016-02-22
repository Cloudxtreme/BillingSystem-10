from django.db import models
from django_countries.fields import CountryField
from django_languages.fields import LanguageField
from localflavor.us.models import USStateField, USSocialSecurityNumberField, PhoneNumberField
from django.utils import timezone
from audit_log.models.managers import AuditLog
from django.forms.models import model_to_dict

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

PROVIDER_ROLE_CHOICES = (('Billing','Billing'),('Rendering','Rendering'),('Dual','Dual'),('Location','Location'))

POS_CHOICES = (('Home','Home'),('Hospital','Hospital'),('Office','Office'))

#New stuff
CATEGORIES = (  
    ('LAB', 'labor'),
    ('CAR', 'cars'),
    ('TRU', 'trucks'),
    ('WRI', 'writing'),
)
LOCATIONS = (  
    ('BRO', 'Bronx'),
    ('BRK', 'Brooklyn'),
    ('QNS', 'Queens'),
    ('MAN', 'Manhattan'),
    ('STN', 'Staten Island'),
)

class CPT(models.Model):
    cpt_code=   models.CharField(max_length=50)
    cpt_description=    models.CharField(max_length=200)
    cpt_mod_a=  models.CharField(max_length=10, null=True, blank=True)
    cpt_mod_b=  models.CharField(max_length=10, null=True, blank=True)
    cpt_mod_c=  models.CharField(max_length=10, null=True, blank=True)
    cpt_mod_d=  models.CharField(max_length=10, null=True, blank=True)
    cpt_charge= models.FloatField()
    def __unicode__(self):
        return self.cpt_code+" "+self.cpt_description


class PostAd(models.Model):  
    name        = models.CharField(max_length=50)
    insured_idnumber= models.CharField(max_length=50)
    insured_name= models.CharField(max_length=100)
    insured_address= models.CharField(max_length=100)
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
    email       = models.EmailField()
    gist        = models.CharField(max_length=50)
    category    = models.CharField(max_length=3, choices=CATEGORIES)
    location    = models.CharField(max_length=3, choices=LOCATIONS)
    expire      = models.DateField()
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

    

class RefferingProvider(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    address1 = models.CharField(max_length=200)
    address2 = models.CharField(max_length=200,null=True, blank=True)
    city= models.CharField(max_length=200)
    state=USStateField(default='')
    zip=models.IntegerField()
    phone_work=PhoneNumberField()
    fax=models.CharField(max_length=100,null=True, blank=True)
    email=models.CharField(max_length=100,null=True, blank=True)
    taxonomy=models.CharField(max_length=100)
    NPI=models.IntegerField()
    tax_id=models.CharField(max_length=100,null=True, blank=True)
    def __unicode__(self):
        return self.first_name+" "+self.last_name


class dx(models.Model):
    ICD_10 = models.CharField(max_length=200, primary_key=True)
    description = models.CharField(max_length=200)
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
     
    audit_log = AuditLog()
    
    def __unicode__(self):
        return self.first_name+' '+self.last_name
    
    def get_name(self):
        return self.first_name+" "+self.middle_name+" "+self.last_name
    
    def get_data(self):
        details = model_to_dict(self, exclude=['audit_log','dob','date_registered','state','country'])
        details['dob'] = str(self.dob)
        details['date_registerd'] = str(self.date_registered)
        details['state'] = str(self.state)
        details['country'] = str(self.country)
        return details

    
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
    
    def __unicode__(self):
        return self.name
    
class Insurance_Information(models.Model):
    level = models.CharField(choices=INSURANCE_LEVEL_CHOICES,max_length=10,default='Primary')
    status = models.CharField(choices=INSURANCE_STATUS_CHOICES,max_length=10,default='Active')
    payer = models.ForeignKey(Payer)
    patient = models.ForeignKey(Personal_Information)
    insurance_id = models.CharField(max_length=32,default='')
    
    audit_log = AuditLog()
    
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
    tax_id = models.IntegerField(default='',null=True, blank=True)
    npi = models.IntegerField(default='',null=True, blank=True)
    speciality = models.CharField(max_length=128,default='',null=True, blank=True)
    role = models.CharField(choices=PROVIDER_ROLE_CHOICES,max_length=10,default='Rendering')
    provider_address = models.CharField(max_length=256, default='',null=True, blank=True)
    provider_city = models.CharField(max_length=128,default='',null=True, blank=True)   
    provider_state = USStateField(default='',null=True, blank=True)
    provider_phone = PhoneNumberField(null=True, blank=True, help_text='XXX-XXX-XXXX',)
    provider_zip = models.IntegerField(default='',null=True, blank=True)

     
    def __unicode__(self):
        return self.provider_name
    
class Procedure_Codes(models.Model):
    procedure_name = models.CharField(max_length=128,default='')
    procedure_code = models.IntegerField(default='')
     
    def __unicode__(self):
        return self.procedure_code
     
class Diagnosis_Codes(models.Model):
    diagnosis_name = models.CharField(max_length=128,default='')
    diagnosis_code = models.CharField(max_length=8,default='')
     
    def __unicode__(self):
        return self.diagnosis_code

# class Test(models.Model):
# #     patient = models.ForeignKey()
# #     insurance = models.ForeignKey()
# #     billing and providers
#     dos = models.DateField()
#     billing_provider = models.ForeignKey(Provider, limit_choices_to={'role':'Billing'},)
#     rendering_provider = models.ForeignKey(Provider, limit_choices_to={'role':'Rendering'}, related_name = 'rendering_provider')
#     icd = models.ManyToManyField(Diagnosis_Codes)
    
#     referring_provider

# class Claims(models.Model):
#     dos = models.DateField()
#     pos = models.CharField(choices=POS_CHOICES,max_length=10,default='Office')
#     icd = models.ManyToManyField(Diagnosis_Codes)
#     cpt = models.ManyToManyField(Procedure_Codes)
#     billing_provider = models.ForeignKey(Provider, limit_choices_to={'role':'Billing'},)
#     rendering_provider = models.ForeignKey(Provider, limit_choices_to={'role':'Rendering'}, related_name = 'rendering_provider')
    