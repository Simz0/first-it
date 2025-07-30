"""
URL configuration for test_first_it project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

import test_first_it_app.views as views

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'api/guides/<str:type>/', 
        views.GuideAPIView.as_view(), 
        name='guide-list'
    ),
    path(
        'api/guides/<str:type>/<uuid:obj_id>/', 
        views.GuideAPIView.as_view(), 
        name='guide-detail'
    ),
    
    path(
        'api/cashflows/', 
        views.CashFlowGenericAPIView.as_view(), 
        name='cashflow-list'
    ),

    path(
        'api/cashflows/<str:obj_id>/',
        views.CashFlowGenericAPIView.as_view(),
        name='cashflow-list-details'
    )
]
