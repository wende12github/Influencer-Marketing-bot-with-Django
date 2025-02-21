from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Influencer(models.Model):
    name = models.CharField(max_length=100)
    instagram_id = models.CharField(max_length=100, unique=True)
    followers_count = models.IntegerField(default=0)
    engagement_rate = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    niche = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.instagram_id})"

class Demographics(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]

    influencer = models.OneToOneField(Influencer, on_delete=models.CASCADE)
    age_13_17 = models.FloatField(default=0.0)
    age_18_24 = models.FloatField(default=0.0)
    age_25_34 = models.FloatField(default=0.0)
    age_35_44 = models.FloatField(default=0.0)
    age_45_plus = models.FloatField(default=0.0)
    gender_distribution = models.JSONField(default=dict)
    top_locations = models.JSONField(default=list)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Demographics for {self.influencer.name}"

class Post(models.Model):
    influencer = models.ForeignKey(Influencer, on_delete=models.CASCADE)
    post_id = models.CharField(max_length=100, unique=True)
    caption = models.TextField(blank=True)
    media_type = models.CharField(max_length=20)
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    engagement_rate = models.FloatField(default=0.0)
    posted_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post {self.post_id} by {self.influencer.name}"

class Campaign(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    target_audience_age = models.JSONField(default=list)
    target_audience_gender = models.JSONField(default=list)
    target_locations = models.JSONField(default=list)
    min_followers = models.IntegerField(default=1000)
    min_engagement_rate = models.FloatField(default=1.0)
    niche = models.CharField(max_length=50)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class CampaignInfluencer(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed')
    ]

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    influencer = models.ForeignKey(Influencer, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    ai_score = models.FloatField(default=0.0)
    proposed_rate = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('campaign', 'influencer')

    def __str__(self):
        return f"{self.campaign.name} - {self.influencer.name}" 