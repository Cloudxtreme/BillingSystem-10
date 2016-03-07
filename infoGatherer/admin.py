from django.contrib import admin
# from infoGatherer.models import Payer,Personal_Information, CPT, Guarantor_Information, Insurance_Information, Procedure_Codes,dx, Provider, Locations, RefferingProvider
from infoGatherer.models import *      

class PayerAdmin(admin.ModelAdmin):
    list_display = ('code','name','address','city','state','zip','phone','type',)
    list_editable = ('code','name','address','city','state','zip','phone','type',)

class GuarantorAdmin(admin.ModelAdmin):
    pass

class InsuranceAdmin(admin.ModelAdmin):
    list_display = ('payer','patient',)

# class DiagnosisCodes_Admin(admin.ModelAdmin):
#     list_display = ('diagnosis_code','diagnosis_name',)
#     search_fields = ['diagnosis_code','diagnosis_name',]

class ProcedureCodes_Admin(admin.ModelAdmin):
    list_display = ('procedure_code','procedure_name',)
    search_fields = ['procedure_code','procedure_name',]
    
class Provider_Admin(admin.ModelAdmin):
    list_display = ('provider_name','role','provider_phone')
    search_fields = ['provider_name','role','provider_phone']
    class Media:
        js = ('js/jquery.min.js','js/model/provider.js')

class Patient_Admin(admin.ModelAdmin):
    list_display = ('last_name','first_name','dob','sex',)

class RP(admin.ModelAdmin):
    list_display = ('first_name','last_name','taxonomy','NPI')
    search_fields = ['first_name','last_name','taxonomy','NPI',]

class DX(admin.ModelAdmin):
    list_display = ('ICD_10','description')
    search_fields = ['ICD_10','description',]

class CPT_codes(admin.ModelAdmin):
    list_display = ('cpt_code','cpt_description','cpt_mod_a','cpt_mod_b','cpt_mod_c','cpt_mod_d','cpt_charge')
    search_fields = ['cpt_code','cpt_description','cpt_mod_a','cpt_mod_b','cpt_mod_c','cpt_mod_d','cpt_charge']

admin.site.register(Payer, PayerAdmin)
# admin.site.register(Diagnosis_Codes,DiagnosisCodes_Admin)
admin.site.register(Procedure_Codes,ProcedureCodes_Admin)
admin.site.register(Provider,Provider_Admin)

admin.site.register(Personal_Information,Patient_Admin)
admin.site.register(Guarantor_Information, GuarantorAdmin)
admin.site.register(Insurance_Information, InsuranceAdmin)

#new stuff
admin.site.register(ReferringProvider, RP)
admin.site.register(dx, DX)
admin.site.register(CPT, CPT_codes)

# admin.site.register(Test,Test_Admin)