from django.urls import path, include
from rest_framework import routers
from .views import (
    InfluencerViewSet,
    CampaignViewSet,
    DemographicsViewSet,
    EngagementViewSet,
    RecommendationViewSet,
    InstagramAuthView,
    InstagramCallbackView,
    DashboardView
)

# Create a router and register our viewsets with it
router = routers.DefaultRouter()
router.register(r'influencers', InfluencerViewSet, basename='influencer')
router.register(r'campaigns', CampaignViewSet, basename='campaign')
router.register(r'demographics', DemographicsViewSet, basename='demographics')
router.register(r'engagement', EngagementViewSet, basename='engagement')
router.register(r'recommendations', RecommendationViewSet, basename='recommendation')

app_name = 'app_bot'

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # Instagram authentication
    path('instagram/auth/', InstagramAuthView.as_view(), name='instagram_auth'),
    path('instagram/callback/', InstagramCallbackView.as_view(), name='instagram_callback'),
    
    # Dashboard
    path('', DashboardView.as_view(), name='dashboard'),
] 