from django.conf.urls import patterns, url, include
from infoGatherer import views
from django.contrib.auth.views import logout
urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^log$', views.admin_log, name='log'),
        url(r'^login/$', views.user_login, name='login'),
        url(r'^logout/$', views.user_logout, name='logout', kwargs={'next_page': '/info/login/'}),
        url(r'^user/password/reset/$', views.user_password_reset, name="password_reset"),
        url(r'^user/password/reset/done/$',views.user_password_reset_done),
        url(r'^user/password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', views.user_password_reset_confirm, name='password_reset_confirm'),
        url(r'^user/password/done/$', views.user_password_reset_complete),
        )