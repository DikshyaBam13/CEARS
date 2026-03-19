from django.db import models
from django.contrib.auth.models import User

# 1. User Profile: Categorizes users and volunteers
class UserProfile(models.Model):
    USER_TYPES = (
        ('citizen', 'Citizen'),
        ('volunteer', 'Volunteer'),
    )
    # Categories for volunteers
    CATEGORIES = (
        ('Medical', 'Medical'),
        ('Security', 'Police/Security'),
        ('Fire', 'Fire Brigade'),
        ('General', 'General Help'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='citizen')
    
    # Volunteer-specific fields
    organization_name = models.CharField(max_length=100, blank=True, null=True)
    specialization = models.CharField(max_length=50, choices=CATEGORIES, default='General')
    is_verified = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.user.username} ({self.user_type})"

# 2. Incident: Stores SOS Alert details
class Incident(models.Model):
    EMERGENCY_CHOICES = [
        ('Medical', 'Medical Emergency'),
        ('Fire', 'Fire / Short Circuit'),
        ('Accident', 'Road Accident'),
        ('Natural Disaster', 'Flood / Landslide'),
        ('Other', 'Other Problem'), # 'Other' option thapiyo
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    emergency_type = models.CharField(max_length=100, choices=EMERGENCY_CHOICES, default='Other')
    description = models.TextField(default="")
    phone_number = models.CharField(max_length=15, default="") # Victim ko contact
    location_name = models.CharField(max_length=255, default="Fetching...")
    lat = models.FloatField()
    lng = models.FloatField()
    status = models.CharField(max_length=20, default='Pending')
    volunteer = models.ForeignKey(User, related_name='rescuer', null=True, blank=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.emergency_type} by {self.user.username}"