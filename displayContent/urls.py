from django.conf.urls import url, include
from displayContent import views
from django.contrib.auth.views import logout

app_name ='displayContent'
urlpatterns = [
    url(r'^dashboard/', views.view_dashboard, name="view_dashboard"),
    url(r'^[0-9]+/claimhistory', views.view_claims, name="view_claims"),
    url(r'^[0-9]+/', views.view_patient, name="view_patient"),

    url(r'^api_search_patient/', views.api_search_patient, name="api_search_patient"),
]
