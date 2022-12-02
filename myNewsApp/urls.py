from django.urls import path

from . import views

app_name = 'myNewsApp'

urlpatterns = [
    path("", views.login, name="login"),
    path("register", views.register, name="register"),
    path("home", views.index, name="index"),
    path("logout", views.logout, name='logout')

]
