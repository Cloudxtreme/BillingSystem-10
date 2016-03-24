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


class AppliedPaymentAdmin(admin.ModelAdmin):

    list_display = ('applied_on','payment_date','dos','patient_Id','name' ,'applied_amount', 'payment_id','payer')

    # 'applied_amount', 'payment_id' , 'payer'


    # def payment_id(self, obj):
    #     return obj.payment_id

    def applied_amount(self, obj):
        return obj.amount

    def applied_on(self, obj):
        return obj.created

    def name(self, obj):
        return obj.patient_name

admin.site.register(Payment, PaymentAdmin)
admin.site.register(AppliedPayment, AppliedPaymentAdmin)