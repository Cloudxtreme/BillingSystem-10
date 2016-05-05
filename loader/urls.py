from django.conf.urls import url
from . import views


app_name ='loader'
urlpatterns = [
    url(r'^$', views.loader_read, name="loader_read"),
]
