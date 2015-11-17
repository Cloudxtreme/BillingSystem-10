from django.conf.urls import patterns, url, include
from infoGatherer import views
from django.contrib.auth.views import logout
urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^log$', views.admin_log, name='log'),
        url(r'^login/$', views.user_login, name='login'),
        url(r'^logout/$', views.user_logout, name='logout', kwargs={'next_page': '/info/login/'}),
        )