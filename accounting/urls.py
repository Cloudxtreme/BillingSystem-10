from django.conf.urls import url
from accounting import views


app_name ='accounting'
urlpatterns = [
    url(r'^payment/create/', views.payment_create, name="payment_create"),
]
