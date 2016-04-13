from django.conf.urls import url
from . import views

app_name = 'dashboard'
urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^api_create_note/$', views.api_create_note, name="api_create_note"),
]