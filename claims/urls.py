from django.conf.urls import url
from . import views

app_name = 'claims'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^createClaim/$', views.createClaim, name='createClaim'),
    url(r'^generateClaim/$', views.generateClaim, name='generateClaim'),
]