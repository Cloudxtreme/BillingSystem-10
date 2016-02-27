"""BillingSystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
import infoGatherer

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^info/', include('infoGatherer.urls')),
    url(r'^claims/', include('claims.urls')),
    url(r'^accounts/', include('accounts.urls')),
]


# Initial Administrator account once server run
from django.conf import settings
from config import config
from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(email=config.get('default_admin_email')).exists():
    admin = User.objects.create_superuser(
        email=config.get('default_admin_email'),
        password=config.get('default_admin_password'),
        first_name=config.get('default_admin_first_name'),
        last_name=config.get('default_admin_last_name')
    );

    print '\n'
    print 'Default admin has been created.  Account\'s details are as follow:'
    print 'Email\t\t:\t%s' % (admin.email)
    print 'Password\t:\t%s' % (config.get('default_admin_password'))
    print 'Full Name\t:\t%s' % (admin.get_full_name())
    print '\n\n\n'
