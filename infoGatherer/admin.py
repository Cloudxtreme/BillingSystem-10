from django.contrib import admin
from infoGatherer.models import Payer, Diagnosis_Codes,  Procedure_Codes, Provider, Personal_Information, Guarantor_Information
      

class PayerAdmin(admin.ModelAdmin):
    list_display = ('code','name','address','city','state','zip','phone','type',)
    list_editable = ('code','name','address','city','state','zip','phone','type',)

class GuarantorAdmin(admin.ModelAdmin):
    pass

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

admin.site.register(Payer, PayerAdmin)
admin.site.register(Guarantor_Information, GuarantorAdmin)
admin.site.register(Diagnosis_Codes,DiagnosisCodes_Admin)
admin.site.register(Procedure_Codes,ProcedureCodes_Admin)
admin.site.register(Provider,Provider_Admin)

admin.site.register(Personal_Information,Patient_Admin)
# admin.site.register(Test,Test_Admin)