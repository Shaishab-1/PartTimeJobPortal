from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('job/<int:id>/', views.job_detail, name='job_detail'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Staff URLs
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/post-job/', views.post_job, name='post_job'),
    path('staff/job/<int:job_id>/applications/', views.view_job_applications, name='view_job_applications'),
    path('staff/job/<int:job_id>/edit/', views.edit_job, name='edit_job'),
    path('staff/job/<int:job_id>/delete/', views.delete_job, name='delete_job'),
    
    # Profile URLs
    path('profile/update/', views.profile_update, name='profile_update'),
    
    # Notification URLs
    path('notifications/', views.notifications, name='notifications'),
    path('applicant/<int:notification_id>/', views.view_applicant_detail, name='view_applicant_detail'),
    path('notification/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('staff/application/<int:application_id>/status/', views.update_application_status, name='update_application_status'),
]