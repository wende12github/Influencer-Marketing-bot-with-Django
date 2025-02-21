from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Influencer, Campaign, Demographics, Post, CampaignInfluencer
from ..influencer_marketing_bot.app_bot.serializers import (
    InfluencerSerializer,
    CampaignSerializer,
    DemographicsSerializer,
    PostSerializer,
    CampaignInfluencerSerializer
)
from scripts.instagram_api import InstagramAPI
from scripts.engagement import EngagementAnalyzer
from scripts.demographics import DemographicsAnalyzer
from scripts.recommendation_model import InfluencerRecommender
import requests
import json

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaigns'] = Campaign.objects.filter(user=self.request.user)
        return context

class InfluencerViewSet(viewsets.ModelViewSet):
    queryset = Influencer.objects.all()
    serializer_class = InfluencerSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def engagement_metrics(self, request, pk=None):
        influencer = self.get_object()
        analyzer = EngagementAnalyzer()
        
        # Get posts for analysis
        posts = Post.objects.filter(influencer=influencer)
        posts_data = PostSerializer(posts, many=True).data
        
        # Calculate metrics
        engagement_rate = analyzer.calculate_engagement_rate(
            posts_data,
            influencer.followers_count
        )
        
        trends = analyzer.analyze_engagement_trends(posts_data)
        best_times = analyzer.get_best_posting_times(posts_data)
        
        return Response({
            'engagement_rate': engagement_rate,
            'trends': trends,
            'best_posting_times': best_times
        })

class CampaignViewSet(viewsets.ModelViewSet):
    serializer_class = CampaignSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Campaign.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def recommend_influencers(self, request, pk=None):
        campaign = self.get_object()
        recommender = InfluencerRecommender()
        
        # Load the trained model
        try:
            recommender.load_model(settings.MODEL_PATH, settings.SCALER_PATH)
        except Exception as e:
            return Response(
                {'error': 'Failed to load recommendation model'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Get all influencers
        influencers = Influencer.objects.all()
        influencers_data = InfluencerSerializer(influencers, many=True).data
        
        # Prepare campaign criteria
        campaign_data = CampaignSerializer(campaign).data
        criteria = {
            'demographics': {
                'target_age': campaign_data['target_audience_age'],
                'target_gender': campaign_data['target_audience_gender'],
                'target_locations': campaign_data['target_locations']
            },
            'min_followers': campaign_data['min_followers'],
            'min_engagement_rate': campaign_data['min_engagement_rate'],
            'niche': campaign_data['niche']
        }
        
        # Get recommendations
        recommendations = recommender.recommend_influencers(
            influencers_data,
            criteria
        )
        
        return Response(recommendations)

class DemographicsViewSet(viewsets.ModelViewSet):
    queryset = Demographics.objects.all()
    serializer_class = DemographicsSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def analyze(self, request, pk=None):
        demographics = self.get_object()
        analyzer = DemographicsAnalyzer()
        
        # Get engagement data for analysis
        influencer = demographics.influencer
        posts = Post.objects.filter(influencer=influencer)
        posts_data = PostSerializer(posts, many=True).data
        
        # Generate demographic report
        report = analyzer.generate_demographic_report(
            [demographics.__dict__],
            posts_data
        )
        
        return Response(report)

class EngagementViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        analyzer = EngagementAnalyzer()
        posts = self.get_queryset()
        posts_data = self.get_serializer(posts, many=True).data
        
        # Calculate overall engagement metrics
        engagement_metrics = {
            'total_posts': len(posts_data),
            'avg_likes': sum(p['likes_count'] for p in posts_data) / len(posts_data) if posts_data else 0,
            'avg_comments': sum(p['comments_count'] for p in posts_data) / len(posts_data) if posts_data else 0,
            'engagement_rate': analyzer.calculate_engagement_rate(
                posts_data,
                posts[0].influencer.followers_count if posts else 0
            )
        }
        
        return Response(engagement_metrics)

class RecommendationViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def create(self, request):
        recommender = InfluencerRecommender()
        
        try:
            # Load the trained model
            recommender.load_model(settings.MODEL_PATH, settings.SCALER_PATH)
            
            # Get influencers and campaign criteria from request
            influencers_data = request.data.get('influencers', [])
            campaign_criteria = request.data.get('criteria', {})
            
            # Get recommendations
            recommendations = recommender.recommend_influencers(
                influencers_data,
                campaign_criteria
            )
            
            return Response(recommendations)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class InstagramAuthView(View):
    def get(self, request):
        # Build the Instagram authorization URL
        auth_url = f"https://api.instagram.com/oauth/authorize"
        params = {
            'client_id': settings.INSTAGRAM_APP_ID,
            'redirect_uri': settings.INSTAGRAM_REDIRECT_URI,
            'scope': 'basic',
            'response_type': 'code'
        }
        
        # Redirect to Instagram authorization page
        auth_url = f"{auth_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
        return redirect(auth_url)

class InstagramCallbackView(View):
    def get(self, request):
        code = request.GET.get('code')
        
        if not code:
            return JsonResponse({'error': 'No authorization code provided'}, status=400)
        
        # Exchange code for access token
        token_url = 'https://api.instagram.com/oauth/access_token'
        data = {
            'client_id': settings.INSTAGRAM_APP_ID,
            'client_secret': settings.INSTAGRAM_APP_SECRET,
            'grant_type': 'authorization_code',
            'redirect_uri': settings.INSTAGRAM_REDIRECT_URI,
            'code': code
        }
        
        try:
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            # Store the access token (you might want to associate it with the user)
            access_token = response.json().get('access_token')
            
            # Initialize Instagram API with the new token
            api = InstagramAPI()
            api.access_token = access_token
            
            return JsonResponse({'success': True})
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500) 