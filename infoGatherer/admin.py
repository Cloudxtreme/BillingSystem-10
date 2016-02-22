from django.contrib import admin
from infoGatherer.models import Payer,Personal_Information, Guarantor_Information, Insurance_Information, Diagnosis_Codes, Procedure_Codes,dx, Provider, Locations, ReferringProvider
      

class PayerAdmin(admin.ModelAdmin):
    list_display = ('code','name','address','city','state','zip','phone','type',)
    list_editable = ('code','name','address','city','state','zip','phone','type',)

class GuarantorAdmin(admin.ModelAdmin):
    pass

class InsuranceAdmin(admin.ModelAdmin):
    list_display = ('payer','patient',)

class DiagnosisCodes_Admin(admin.ModelAdmin):
    list_display = ('diagnosis_code','diagnosis_name',)
    search_fields = ['diagnosis_code','diagnosis_name',]

class ProcedureCodes_Admin(admin.ModelAdmin):
    list_display = ('procedure_code','procedure_name',)
    search_fields = ['procedure_code','procedure_name',]
    
class Provider_Admin(admin.ModelAdmin):
    pass

# class Test_Admin(admin.ModelAdmin):
#     pass

class Patient_Admin(admin.ModelAdmin):
    pass

class RP(admin.ModelAdmin):
    list_display = ('first_name','last_name','taxonomy','NPI')
    search_fields = ['first_name','last_name','taxonomy','NPI',]

class DX(admin.ModelAdmin):
    list_display = ('ICD_10','description')
    search_fields = ['ICD_10','description',]

admin.site.register(Payer, PayerAdmin)
admin.site.register(Diagnosis_Codes,DiagnosisCodes_Admin)
admin.site.register(Procedure_Codes,ProcedureCodes_Admin)
admin.site.register(Provider,Provider_Admin)

admin.site.register(Personal_Information,Patient_Admin)
admin.site.register(Guarantor_Information, GuarantorAdmin)
admin.site.register(Insurance_Information, InsuranceAdmin)

#new stuff
admin.site.register(ReferringProvider, RP)
admin.site.register(dx, DX)

# admin.site.register(Test,Test_Admin)