from rest_framework import serializers
from django.contrib.auth.models import User
from ...app_bot.models import Influencer, Campaign, Demographics, Post, CampaignInfluencer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class InfluencerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Influencer
        fields = [
            'id',
            'name',
            'instagram_id',
            'followers_count',
            'engagement_rate',
            'niche',
            'created_at',
            'updated_at'
        ]

class DemographicsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Demographics
        fields = [
            'id',
            'influencer',
            'age_13_17',
            'age_18_24',
            'age_25_34',
            'age_35_44',
            'age_45_plus',
            'gender_distribution',
            'top_locations',
            'updated_at'
        ]

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            'id',
            'influencer',
            'post_id',
            'caption',
            'media_type',
            'likes_count',
            'comments_count',
            'engagement_rate',
            'posted_at',
            'created_at'
        ]

class CampaignSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Campaign
        fields = [
            'id',
            'name',
            'user',
            'target_audience_age',
            'target_audience_gender',
            'target_locations',
            'min_followers',
            'min_engagement_rate',
            'niche',
            'budget',
            'start_date',
            'end_date',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['user']

class CampaignInfluencerSerializer(serializers.ModelSerializer):
    influencer = InfluencerSerializer(read_only=True)
    campaign = CampaignSerializer(read_only=True)
    
    class Meta:
        model = CampaignInfluencer
        fields = [
            'id',
            'campaign',
            'influencer',
            'status',
            'ai_score',
            'proposed_rate',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['campaign', 'influencer']

class InfluencerDetailSerializer(InfluencerSerializer):
    demographics = DemographicsSerializer(read_only=True)
    posts = PostSerializer(many=True, read_only=True)
    campaigns = CampaignInfluencerSerializer(many=True, read_only=True, source='campaigninfluencer_set')
    
    class Meta(InfluencerSerializer.Meta):
        fields = InfluencerSerializer.Meta.fields + ['demographics', 'posts', 'campaigns']

class CampaignDetailSerializer(CampaignSerializer):
    influencers = CampaignInfluencerSerializer(many=True, read_only=True, source='campaigninfluencer_set')
    
    class Meta(CampaignSerializer.Meta):
        fields = CampaignSerializer.Meta.fields + ['influencers'] 