from django.conf.urls import url, include
from displayContent import views
from django.contrib.auth.views import logout

app_name ='displayContent'
urlpatterns = [
    url(r'^dashboard/$', views.view_dashboard, name="view_dashboard"),
    url(r'^(?P<chart>\d+)/$', views.view_patient, name="view_patient"),
    url(r'^(?P<chart>\d+)/claimhistory/$', views.view_claims, name="view_claims"),
    url(r'^api_search_patient/$', views.api_search_patient, name="api_search_patient"),

    # url(r'^payment/apply/(?P<payment_id>\w+)/(?P<claim_id>\w+)/patient/$', views.charge_patient_create, name="charge_patient_create"),

    
]
