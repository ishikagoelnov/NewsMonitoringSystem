"""NewsMonitoring URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.urlpatterns import format_suffix_patterns
from myNewsApp import api
from myNewsApp.api import StoryList, StoryDetail

urlpatterns = [
    path('', include('myNewsApp.urls')),
    path('__debug__/', include('debug_toolbar.urls')),
    path('admin/', admin.site.urls),
    path('api/stories_list/', api.StoryList, name='stories_list'),
    path('api/stories_list/<int:pk>', api.StoryDetail, name='story_detail'),
    path('api-auth', include('rest_framework.urls',
                             namespace='rest_framework'))
]
urlpatterns = format_suffix_patterns(urlpatterns)

# if settings.DEBUG:
#     urlpatterns += path('__debug__/', include('debug_toolbar.urls'))
