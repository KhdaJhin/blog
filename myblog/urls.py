"""myblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path, re_path
from jhin import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index),
    path('index/', views.index, name='index'),
    path('code/', views.code, name='code'),
    path('digg/', views.digg),
    path('comment/', views.comment, name='comment'),
    path('backend/', views.backend),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('backend/add_article/', views.add_article),
    path('upload/', views.upload, name='upload'),
    path('register/', views.register, name='register'),
    re_path('(?P<username>\w+)/$', views.blog, name='blog'),
    re_path('(?P<username>\w+)/article/(?P<article_id>\d+)$', views.article, name='article'),
    re_path('(?P<username>\w+)/(?P<condition>category|tag|time)/(?P<cate>.*)', views.blog, name='blog'),

]
