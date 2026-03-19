from django.contrib import admin
from .models import UserProfile, Incident

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'specialization', 'is_verified')
    list_filter = ('user_type', 'specialization', 'is_verified')

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    # 'resolved' ko satta 'status' use gareko xau, so yaha pani change garne
    list_display = ('user', 'emergency_type', 'lat', 'lng', 'status', 'timestamp')
    list_filter = ('status', 'emergency_type')
    search_fields = ('user__username', 'emergency_type')