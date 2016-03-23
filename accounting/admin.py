from django.contrib import admin
from accounting.models import *

# Register your models here.

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_date','payer_type','payer','payment_method','check_number','payment_Amount', 'applied_Amount',)
    search_fields = ['payment_date','payer_type','payer','payment_method','check_number','applied_Amount','payment_Amount',]

    def payer(self, obj):
        if (obj.payer_type == "Insurance"):
            return obj.payer_insurance
        else:
            return obj.payer_patient

    def payment_Amount(self, obj):
    	return "$"+str(obj.amount)

    def applied_Amount(self, obj):
        return "$"+str(obj.applied_amount)


admin.site.register(Payment, PaymentAdmin)