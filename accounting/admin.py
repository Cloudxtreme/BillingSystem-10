from django.contrib import admin
from daterange_filter.filter import DateRangeFilter
from accounting.models import *
from decimal import *
from import_export.admin import ImportExportModelAdmin
from django.forms import TextInput, Textarea


class PaymentAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('payment_date','payer_type','payer','payment_method','check_number','payment_Amount', 'applied_Amount', 'user')
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'30'})},
        models.IntegerField: {'widget': TextInput(attrs={'size':'30'})},
    }
    list_filter=(
        'user',
        ('payment_date', DateRangeFilter),
    )
    search_fields = ['payment_date','payer_type', 'user__first_name', 'user__last_name',
                            'user__email', 'amount','check_number','payment_method',
                            'payer_patient__first_name','payer_patient__last_name',
                            'payer_insurance__name']

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


class ApplyAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    # pass
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'30'})},
        models.IntegerField: {'widget': TextInput(attrs={'size':'30'})},
    }
    list_display = ('applied_on','payment_date','dos','patient_Id','patient_name' ,'payment_amount','adjustment_amount', 'paymentid', 'payer', 'user')
    search_fields = ['created' ,'amount','adjustment','payment__payment_date','charge__procedure__claim__patient__first_name',
                            'charge__procedure__claim__patient__last_name','charge__procedure__claim__patient__chart_no',
                            'charge__procedure__date_of_service','user__first_name', 'user__last_name', 'user__email',
                            'payment__payer_type',
                            ]
    list_filter=(
        'user',
        ('created', DateRangeFilter),
    )

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
