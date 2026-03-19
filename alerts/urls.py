from django.urls import path
from . import views

urlpatterns = [
    # 1. Authentication & Registration
    path('register/', views.register, name='register'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # 2. Dashboards
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('responder-dashboard/', views.responder_dashboard, name='responder_dashboard'),
    
    # 3. Incident/SOS Management
    path('send-sos/', views.send_sos, name='send_sos'),
    path('accept/<int:incident_id>/', views.accept_incident, name='accept_incident'),
    path('resolve/<int:incident_id>/', views.resolve_incident, name='resolve_incident'),
    
    # 4. Password Reset & OTP Helpers
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-password-otp/', views.verify_password_otp, name='verify_password_otp'),
    path('reset-password-now/', views.reset_password_now, name='reset_password_now'),
    path('update-responder-location/', views.update_responder_location, name='update_responder_location'),
]