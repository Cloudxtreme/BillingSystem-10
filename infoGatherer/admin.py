from django.contrib import admin
from infoGatherer.models import Personal_Information, Payer, Insurance_Information, Diagnosis_Codes, Test, Provider
      
class PIAdmin(admin.ModelAdmin):
    #fields = (('first_name','middle_name','last_name'),)
    #list_dsipaly = (('first_name','middle_name','last_name'),)
    #list_editable = ()
    pass

class PayerAdmin(admin.ModelAdmin):
    list_display = ('code','name','address','city','state','zip','phone','type',)
    list_editable = ('code','name','address','city','state','zip','phone','type',)
    
class IIAdmin(admin.ModelAdmin):
    list_display = ('insurance_id',)

class LogAdmin(admin.ModelAdmin):
    pass

class DiagnosisCodes_Admin(admin.ModelAdmin):
    pass

class Provider_Admin(admin.ModelAdmin):
    pass

class Test_Admin(admin.ModelAdmin):
    pass

admin.site.register(Personal_Information, PIAdmin) 
admin.site.register(Payer, PayerAdmin)
admin.site.register(Insurance_Information, IIAdmin)
admin.site.register(Diagnosis_Codes,DiagnosisCodes_Admin)
admin.site.register(Provider,Provider_Admin)
admin.site.register(Test,Test_Admin)