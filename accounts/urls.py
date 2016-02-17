from django.conf.urls import url
from . import views

app_name = 'accounts'
urlpatterns = [
    url(r'^$', views.sign_in, name='sign_in'),
    url(r'^register/$', views.register, name='register'),
    url(r'^sign_out/$', views.sign_out, name='sign_out'),
    url(r'^success/$', views.success, name='success'),
]