from django.db import models
from django.contrib.auth.models import User
from colorfield.fields import ColorField
# Create your models here.

LANGUAGE_CHOICES = [
    ("en", "English"),
    ("vi", "Vietnamese"),
    ("jp", "Japanese"),
]

class Level(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20, unique=True)
    color = ColorField(default="#FFFFFF")
    difficulty_rank = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'home'
        ordering = ['difficulty_rank']
        
    def __str__ (self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picure = models.ImageField(
        upload_to="profile_pics/", blank=True, null=True
    )
    native_language = models.CharField(max_length=10, blank=True, choices=LANGUAGE_CHOICES )
    daily_ai_limit = models.PositiveIntegerField(default=20)
    reading_level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'home'

    def __str__(self):
        return self.user.username
    
    @property
    def avatar_url(self):
        if self.profile_picure:
            return self.profile_picure.url
        return None
