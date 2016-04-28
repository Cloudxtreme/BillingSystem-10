from django.conf.urls import url
from . import views

app_name = 'report'
urlpatterns = [
    url(r'^statement/$', views.statment_create, name='statment_create'),
    url(r'^statement/read/$', views.statment_read, name='statment_read'),
    url(r'^$', views.index, name='index'),
    url(r'^transactionreport$', views.TransactionReport, name='TransactionReport'),
    url(r'^transactionreportpayment$', views.TransactionReportPayment, name='TransactionReportPayment'),
    # url(r'^sign_in/$', views.sign_in, name='sign_in'),
    # url(r'^sign_out/$', views.sign_out, name='sign_out'),
    # url(r'^register/$', views.register, name='register'),
    # url(r'^success/$', views.success, name='success'),
    # url(r'^password_reset/$', views.password_reset, name='password_reset'),
    # url(r'^password_reset_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.password_reset_confirm, name='password_reset_confirm'),
]
