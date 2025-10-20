from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True)
    def __str__(self):
        return self.username
    

# -------------------
# USER PROFILE
# -------------------
class Profile(models.Model):
    CATEGORY_CHOICES = [
        ("gadgets", "Gadgets"),
        ("fashion", "Fashion"),
        ("sports", "Sports"),
        ("books", "Books"),
        ("home", "Home"),
        ("other", "Other"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    is_seller = models.BooleanField(default=False)

    # Seller details
    wallet_address = models.CharField(max_length=42, blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, blank=True, null=True)
    location_city = models.CharField(max_length=100, blank=True, null=True)
    location_country = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    # Farcaster & appearance
    farcaster_fid = models.CharField(max_length=128, blank=True, null=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    # avatar_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}"