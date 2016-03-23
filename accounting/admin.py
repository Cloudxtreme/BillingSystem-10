from django.contrib import admin
from accounting.models import *

# Register your models here.

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_date','payer_type','payer_type','payment_method','check_number','amount')
    search_fields = ['payment_date','payer_type','payer_type','payment_method','check_number','amount',]


admin.site.register(Payment, PaymentAdmin)