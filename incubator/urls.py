from django.urls import path
from . import views

urlpatterns = [
    # Add your URL patterns here
    path('', views.home, name='home'),
    path('register/',views.register,name='register'),
    path('verify_otp/',views.verify_otp,name='verify_otp')
]
