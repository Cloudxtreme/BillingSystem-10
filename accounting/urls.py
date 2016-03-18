from django.conf.urls import url
from accounting import views


app_name ='accounting'
urlpatterns = [
    url(r'^payment/create/', views.payment_create, name="payment_create"),
    url(r'^payment/apply/', views.payment_apply, name="payment_apply"),


    url(r'^api_search_payment/', views.api_search_payment, name="api_search_payment"),
    url(r'^api_search_claim/', views.api_search_claim, name="api_search_claim"),
]
