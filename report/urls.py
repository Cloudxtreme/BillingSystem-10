from django.conf.urls import url
from . import views

app_name = 'report'
urlpatterns = [
    url(r'^statement/create/(?P<patient_id>[^/]+)/(?P<today_page>[^/]+)/$', views.statement_create, name='statement_create'),
    url(r'^statement/read/$', views.statement_read, name='statement_read'),
    url(r'^statement/history/read/(?P<history_id>[^/]+)/$', views.statement_history_read, name='statement_history_read'),
    url(r'^statement/file/read/(?P<statement_id>[^/]+)/$', views.statement_file_read, name='statement_file_read'),
    url(r'^transactionreport$', views.TransactionReport, name='TransactionReport'),
    url(r'^transactionreportpayment$', views.TransactionReportPayment, name='TransactionReportPayment'),
    url(r'^report_search$', views.report_search, name='report_search'),

    # url(r'^sign_in/$', views.sign_in, name='sign_in'),
    # url(r'^sign_out/$', views.sign_out, name='sign_out'),
    # url(r'^register/$', views.register, name='register'),
    # url(r'^success/$', views.success, name='success'),
    # url(r'^password_reset/$', views.password_reset, name='password_reset'),
    # url(r'^password_reset_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.password_reset_confirm, name='password_reset_confirm'),
]
