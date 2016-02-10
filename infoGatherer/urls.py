from django.conf.urls import patterns, url, include
from infoGatherer import views
from infoGatherer.views import PostAdPage
from django.contrib.auth.views import logout

app_name = 'infoGatherer'
urlpatterns = patterns('',
    url(r'^postad/', PostAdPage.as_view()),
    url(r'^search-form/$', views.search_form),
    url(r'^search-form/print/$', views.print_form),
    url(r'^claim/$', views.view_in_between),

    url(r'^$', views.index, name='index'),
    url(r'^log$', views.admin_log, name='log'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout', kwargs={'next_page': '/info/login/'}),
    url(r'^patient/new/$',views.get_patient_info),
    url(r'^guarantor/(?P<id>\d+)/$',views.get_guarantor_info),
    url(r'^insurance/(?P<id>\d+)/$',views.get_insurance_info),
    url(r'^view/(?P<who>\w{3})/$',views.get_patient_info),
    url(r'^view/(?P<who>\d+)/$',views.get_patient_info),
#         url(r'^user/password/reset/$', views.user_password_reset, name="password_reset"),
#         url(r'^user/password/reset/done/$',views.user_password_reset_done),
#         url(r'^user/password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', views.user_password_reset_confirm, name='password_reset_confirm'),
#         url(r'^user/password/done/$', views.user_password_reset_complete),

    url(r'^get_make_claim_extra_context$', views.get_make_claim_extra_context, name="get_make_claim_extra_context"),

)
