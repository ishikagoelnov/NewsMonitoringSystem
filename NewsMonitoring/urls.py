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
from myNewsApp.api import StoryList, StoryDetail, MyObtainTokenPairView, RegisterView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('', include('myNewsApp.urls')),
    path('__debug__/', include('debug_toolbar.urls')),
    path('admin/', admin.site.urls),
    path('api/stories_list/', StoryList.as_view(), name='stories_list'),
    path('api/stories_list/<int:pk>', StoryDetail.as_view(),
         name='story_detail'),
    path('api-auth', include('rest_framework.urls',
                             namespace='rest_framework')),
    path('login/', MyObtainTokenPairView.as_view(),
         name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(),
         name='token_refresh'),
    path('register/', RegisterView.as_view(), name='auth_register')
]

# if settings.DEBUG:
#     urlpatterns += path('__debug__/', include('debug_toolbar.urls'))
