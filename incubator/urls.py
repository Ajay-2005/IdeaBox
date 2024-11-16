from django.urls import path
from . import views

urlpatterns = [
    # Add your URL patterns here
    path('', views.home, name='home'),
    path('register/',views.register,name='register'),
    path('verify_otp/',views.verify_otp,name='verify_otp'),
    path('login/',views.login_view,name='login'),
    path('resend_otp/',views.resend_otp,name='resend_otp')
    
]
