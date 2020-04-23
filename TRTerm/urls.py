"""TRTerm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path
from medsearch import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('results/', views.ResultsView.as_view()),
    path('', views.SearchView.as_view()),
    path('radiation/', views.RadiationView.as_view()),
    path('microgravity/', views.MicroView.as_view()),
    path('vision/', views.VisionView.as_view()),
    path('dystrophy/', views.DystrophyView.as_view()),
    path('isolation/', views.IsolationView.as_view()),
    path('reverse-blood/', views.ReverseView.as_view()),
 #   path('search/', views.SearchView.as_view())
]
