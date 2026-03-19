from django.contrib import admin
from django.urls import path, include
from alerts import views  
urlpatterns = [
    path('admin/', admin.site.urls),
    
   
    path('', views.login_view, name='home'), 
    
    
    path('alerts/', include('alerts.urls')), 
]