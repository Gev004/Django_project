from django.contrib.auth.models import User
from django.db import models

# Create your models here.

def profile_avatar_dir_path(instance, filename):
    user_id = instance.user.id if instance.user else 'unknown'
    return f"profile/avatar_{user_id}/{filename}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    agreement_accepted = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to=profile_avatar_dir_path, null=True, blank=True)