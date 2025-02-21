from django.contrib import admin
from .models import Influencer, Campaign, Demographics, Post, CampaignInfluencer

# Register your models here.

@admin.register(Influencer)
class InfluencerAdmin(admin.ModelAdmin):
    list_display = ('name', 'instagram_id', 'followers_count', 'engagement_rate', 'niche')
    list_filter = ('niche', 'created_at')
    search_fields = ('name', 'instagram_id')
    ordering = ('-followers_count',)

@admin.register(Demographics)
class DemographicsAdmin(admin.ModelAdmin):
    list_display = ('influencer', 'age_18_24', 'age_25_34', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('influencer__name',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('post_id', 'influencer', 'likes_count', 'comments_count', 'engagement_rate', 'posted_at')
    list_filter = ('posted_at', 'media_type')
    search_fields = ('post_id', 'influencer__name', 'caption')
    ordering = ('-posted_at',)

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'niche', 'budget', 'start_date', 'end_date')
    list_filter = ('niche', 'start_date', 'end_date')
    search_fields = ('name', 'user__username')
    ordering = ('-created_at',)

@admin.register(CampaignInfluencer)
class CampaignInfluencerAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'influencer', 'status', 'ai_score', 'proposed_rate')
    list_filter = ('status', 'created_at')
    search_fields = ('campaign__name', 'influencer__name')
    ordering = ('-ai_score',) 