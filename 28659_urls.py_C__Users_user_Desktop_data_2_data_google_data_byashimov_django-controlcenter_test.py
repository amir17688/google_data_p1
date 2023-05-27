from controlcenter.views import controlcenter
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/dashboard/', include(controlcenter.urls)),
    url(r'^admin/', include(admin.site.urls)),
]
