from django.conf.urls import url, include
from displayContent import views
from displayContent.views import open_pdf
from django.contrib.auth.views import logout

app_name ='displayContent'
urlpatterns = [
    url(r'^dashboard/$', views.view_dashboard, name="view_dashboard"),
    url(r'^(?P<chart>\d+)/$', views.view_patient, name="view_patient"),
    url(r'^(?P<chart>\d+)/claimhistory/$', views.view_claims, name="view_claims"),
    url(r'^claim/payment/$', views.payment_details, name="payment_details"),
    url(r'^(?P<chart>\d+)/statement/$', views.generate_statement, name="generate_statement"),
    url(r'^(?P<yr>\d+)/(?P<mo>\d+)/(?P<da>\d+)/(?P<claim>\d+)/pdf$', views.open_pdf, name="open_pdf"),

    url(r'^get_blank/(?P<yr>\d+)/(?P<mo>\d+)/(?P<da>\d+)/(?P<claim>\d+)/pdf$', views.api_get_blank_claim, name="api_get_blank_claim"),

    url(r'^api_search_patient/$', views.api_search_patient, name="api_search_patient"),
    url(r'^api_view_claim/$', views.api_view_claim, name="api_view_claim"),
]
