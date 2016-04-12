from django.conf.urls import url
from accounting import views


app_name ='accounting'
urlpatterns = [
	url(r'^payment/gross_summary/$', views.gross_payment_summary, name="gross_payment_summary"),

    url(r'^payment/create/$', views.payment_create, name="payment_create"),
    url(r'^payment/apply/$', views.payment_apply_read, name="payment_apply_read"),
    url(r'^payment/apply/(?P<payment_id>\w+)/(?P<claim_id>\w+)/$', views.apply_create, name="payment_apply_create"),
    url(r'^payment/apply/(?P<payment_id>\w+)/(?P<claim_id>\w+)/patient/$', views.charge_patient_create, name="charge_patient_create"),


    url(r'^claim_summary/$', views.claim_summary, name="claim_summary"),
    url(r'^api_search_payment/$', views.api_search_payment, name="api_search_payment"),
    url(r'^api_search_claim/$', views.api_search_claim, name="api_search_claim"),
    url(r'^api_create_note/$', views.api_create_note, name="api_create_note"),
]
