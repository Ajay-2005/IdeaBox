from django.urls import path
from . import views
from .views import CustomSkillAutoResponseForm

urlpatterns = [
	# Home page
	path('', views.home, name='home'),
	path('users/register/', views.register, name='register'),
	path('users/login/', views.login_view, name='login'),
	path('users/forgot-password/', views.forgot_password, name='forgot_password'),
	path('users/reset-password/', views.reset_password, name='reset_password'),
	path('users/logout',views.logout_view,name='logout'),
	path('otp/verify/', views.verify_otp, name='verify_otp'),
	path('otp/resend/', views.resend_otp, name='resend_otp'),
	path('profile/setup/', views.profile_setup, name='profile_setup'),
	path('skills-autocomplete/', CustomSkillAutoResponseForm.as_view(), name='skills-autocomplete'),
	path('profile/',views.profile,name='profile'),
	path('dashboard/',views.dashboard,name='dashboard'),
	path('dashboard/submit-idea/',views.submit_idea,name='submit-idea'),
    path('mentors-dashboard/',views.mentordashboard,name='mentor-dashboard'),
    path('forum/',views.discussion_forum,name='discussion-forum'),
    path('forum/ask-question',views.submit_question,name='ask-question'),
    path('forum/post/<int:post_id>/', views.view_post, name='view_post'),
    path('forum/add-comment/',views.add_comment,name='add-comment')
    
    
    
]
	

