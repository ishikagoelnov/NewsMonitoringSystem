from django.urls import path

from . import views

app_name = 'myNewsApp'

urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.register, name="register"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name='logout'),
    path("sourcing", views.sourcing, name='sourcing'),
    path('source_listing', views.source_listing, name='source_listing'),
    path('stories_listing', views.stories_listing, name='stories_listing'),
    path("editing/<int:pk>", views.editing, name='editing'),
    path('sourceDelete/<int:pk>', views.sourceDelete, name='sourceDelete'),
    path('search_source', views.search_source, name='search_source'),
    path('addstory', views.addstory, name='addstory'),
    path('storyDelete/<int:pk>', views.storyDelete, name='storyDelete'),
    path('editStories/<int:pk>', views.editStories, name="editStories"),
    path('search_story', views.search_story, name='search_story')
]
