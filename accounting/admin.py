from django.contrib import admin
from accounting.models import *
from decimal import *


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_date','payer_type','payer','payment_method','check_number','payment_Amount', 'applied_Amount', 'user')
    search_fields = ['payment_date','payer_type','payer','payment_method','check_number','applied_Amount','payment_Amount', 'user']

    def user(self, obj):
        return str(obj.user.first_name)+"("+obj.user.email+")"

    def payer(self, obj):
        if (obj.payer_type == "Insurance"):
            return obj.payer_insurance
        else:
            return obj.payer_patient

    def payment_Amount(self, obj):
    	return "$"+str(obj.amount)

    def applied_Amount(self, obj):
        return "$"+str(obj.applied_amount)


class ApplyAdmin(admin.ModelAdmin):
    # pass
    list_display = ('applied_on','payment_date','dos','patient_Id','patient_name' ,'payment_amount','adjustment_amount', 'paymentid', 'payer', 'user')
    search_fields = ['applied_on','payment_date','dos','patient_Id','patient_name' ,'payment_amount','adjustment_amount', 'paymentid', 'payer', 'user']

    def user(self, obj):
        return str(obj.user.first_name)+"("+obj.user.email+")"
        
    def adjustment_amount(self, obj):
        return "$"+str(obj.adjustment)

    def paymentid(self, obj):
        return obj.rpi

    def payment_amount(self, obj):
        return "$"+ str(Decimal(-1*obj.amount))

    def applied_on(self, obj):
        return obj.created

admin.site.register(Payment, PaymentAdmin)
admin.site.register(Apply, ApplyAdmin)
