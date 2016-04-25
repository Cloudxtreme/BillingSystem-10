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
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.conf import settings

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^info/', include('infoGatherer.urls')),
    url(r'^claims/', include('claims.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^dashboard/', include('dashboard.urls')),
    url(r'^accounting/', include('accounting.urls')),
    url(r'^patient/', include('displayContent.urls')),
    url(r'^report/', include('report.urls')),
    url(r'^tz_detect/', include('tz_detect.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



# Initial Administrator account once server run
from django.conf import settings
from django.contrib.auth import get_user_model


User = get_user_model()
initial_admin = settings.CONFIG.get('initial_admin')

try:
    if not User.objects.filter(email=initial_admin.get('email')).exists():
        admin = User.objects.create_superuser(
            email=initial_admin.get('email'),
            password=initial_admin.get('password'),
            first_name=initial_admin.get('first_name'),
            last_name=initial_admin.get('last_name')
        );

        print '\n\n'
        print 'Default admin has been created.  Account\'s details are as follow:'
        print 'Email\t\t:\t%s' % (admin.email)
        print 'Password\t:\t%s' % (initial_admin.get('password'))
        print 'Full Name\t:\t%s' % (admin.get_full_name())
        print '\n\n\n'
except:
    pass
