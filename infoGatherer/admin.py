from django.contrib import admin
from infoGatherer.models import *
from simple_history.admin import SimpleHistoryAdmin
from import_export.admin import ImportExportModelAdmin

class PayerAdmin(SimpleHistoryAdmin, ImportExportModelAdmin):
    list_display = ('code','name','address','city','state','zip','phone','type',)
    list_editable = ('code','name','address','city','state','zip','phone','type',)

class GuarantorAdmin(SimpleHistoryAdmin, ImportExportModelAdmin):
    pass

class InsuranceAdmin(SimpleHistoryAdmin, ImportExportModelAdmin):
    list_display = ('payer','patient',)

class Provider_Admin(SimpleHistoryAdmin, ImportExportModelAdmin):
    list_display = ('provider_name','role','provider_phone')
    search_fields = ['provider_name','role','provider_phone']
    class Media:
        js = ('js/jquery.min.js','js/model/provider.js')

class Patient_Admin(SimpleHistoryAdmin, ImportExportModelAdmin):
    list_display = ('last_name','first_name','dob','sex',)

class RP(SimpleHistoryAdmin, ImportExportModelAdmin):
    list_display = ('first_name','last_name','taxonomy','NPI')
    search_fields = ['first_name','last_name','taxonomy','NPI',]

class DX(SimpleHistoryAdmin, ImportExportModelAdmin):
    list_display = ('ICD_10','description')
    search_fields = ['ICD_10','description',]

class CPT_codes(SimpleHistoryAdmin, ImportExportModelAdmin):
    list_display = ('cpt_code','cpt_description','cpt_mod_a','cpt_mod_b','cpt_mod_c','cpt_mod_d','cpt_charge')
    search_fields = ['cpt_code','cpt_description','cpt_mod_a','cpt_mod_b','cpt_mod_c','cpt_mod_d','cpt_charge']


admin.site.register(Payer, PayerAdmin)
admin.site.register(Provider,Provider_Admin)
admin.site.register(Personal_Information,Patient_Admin)
admin.site.register(Guarantor_Information, GuarantorAdmin)
admin.site.register(Insurance_Information, InsuranceAdmin)
admin.site.register(ReferringProvider, RP)
admin.site.register(dx, DX)
admin.site.register(CPT, CPT_codes)
