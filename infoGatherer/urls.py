from django.conf.urls import url, include
from infoGatherer import views
from django.contrib.auth.views import logout

urlpatterns = [
    url(r'^search-form/$', views.search_form),
    url(r'^search-form/print/$', views.print_form),

    url(r'^$', views.index, name='index'),
    url(r'^log$', views.admin_log, name='log'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout', kwargs={'next_page': '/info/login/'}),
    url(r'^patient/new/$',views.get_patient_info),
    url(r'^guarantor/(?P<id>\d+)/$',views.get_guarantor_info),
    url(r'^insurance/(?P<id>\d+)/$',views.get_insurance_info),
    url(r'^view/(?P<who>\w{3})/$',views.get_patient_info),
    url(r'^view/(?P<who>\d+)/$',views.get_patient_info),
    #url(r'^user/password/reset/$', views.user_password_reset, name="password_reset"),
    #url(r'^user/password/reset/done/$',views.user_password_reset_done),
    #url(r'^user/password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', views.user_password_reset_confirm, name='password_reset_confirm'),
    #url(r'^user/password/done/$', views.user_password_reset_complete),



]