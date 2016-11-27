"""iot_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from iot_storage import views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken import views as auth_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^iot_storage/api/v1/api-token-auth/$', auth_views.obtain_auth_token),
    url(r'^iot_storage/api/v1/devices/$', views.device_list, name='device-list'),
    url(r'^iot_storage/api/v1/devices/(?P<deviceid>[a-z0-9]{16})/$', views.device_detail, name='device-detail'),
    url(r'^iot_storage/api/v1/devices/(?P<deviceid>[a-z0-9]{16})/datanodes/$', views.datanodes_list, name='datanodes-list'),
    url(r'^iot_storage/api/v1/data/write/(?P<deviceid>[a-z0-9]{16})/$', views.data_write, name='data-write'),
    url(r'^iot_storage/api/v1/data/read/(?P<deviceid>[a-z0-9]{16})$', views.data_read, name='data-read'),
]

urlpatterns = format_suffix_patterns(urlpatterns)

