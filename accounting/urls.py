from django.conf.urls import url
from accounting import views


app_name ='accounting'
urlpatterns = [
	url(r'^payment/summary/', views.payment_summary, name="payment_summary"),
    url(r'^payment/create/$', views.payment_create, name="payment_create"),
    url(r'^payment/apply/$', views.payment_apply_read, name="payment_apply"),
    url(r'^payment/apply/(?P<payment_id>\w+)/(?P<claim_id>\w+)/$', views.payment_apply_create, name="payment_apply_create"),


    url(r'^api_search_payment/', views.api_search_payment, name="api_search_payment"),
    url(r'^api_search_claim/', views.api_search_claim, name="api_search_claim"),
]
