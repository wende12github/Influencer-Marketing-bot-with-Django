from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Influencer, Campaign, Demographics, Post, CampaignInfluencer
from datetime import datetime, timedelta
from decimal import Decimal

class InfluencerTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.influencer = Influencer.objects.create(
            name='Test Influencer',
            instagram_id='test123',
            followers_count=10000,
            engagement_rate=4.5,
            niche='fitness'
        )
        
        Demographics.objects.create(
            influencer=self.influencer,
            age_13_17=10.0,
            age_18_24=30.0,
            age_25_34=40.0,
            age_35_44=15.0,
            age_45_plus=5.0,
            gender_distribution={'M': 40, 'F': 60},
            top_locations=[{'location': 'New York', 'percentage': 30}]
        )

    def test_list_influencers(self):
        url = reverse('influencer-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Influencer')

    def test_create_influencer(self):
        url = reverse('influencer-list')
        data = {
            'name': 'New Influencer',
            'instagram_id': 'new123',
            'followers_count': 20000,
            'engagement_rate': 3.5,
            'niche': 'fashion'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Influencer.objects.count(), 2)

class CampaignTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.campaign = Campaign.objects.create(
            name='Test Campaign',
            user=self.user,
            target_audience_age={'18-24': 50, '25-34': 50},
            target_audience_gender={'F': 70, 'M': 30},
            target_locations=['New York', 'Los Angeles'],
            min_followers=5000,
            min_engagement_rate=3.0,
            niche='fitness',
            budget=Decimal('1000.00'),
            start_date=datetime.now().date(),
            end_date=(datetime.now() + timedelta(days=30)).date()
        )

    def test_list_campaigns(self):
        url = reverse('campaign-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Campaign')

    def test_create_campaign(self):
        url = reverse('campaign-list')
        data = {
            'name': 'New Campaign',
            'target_audience_age': {'18-24': 60, '25-34': 40},
            'target_audience_gender': {'F': 80, 'M': 20},
            'target_locations': ['Chicago', 'Miami'],
            'min_followers': 10000,
            'min_engagement_rate': 4.0,
            'niche': 'fashion',
            'budget': '2000.00',
            'start_date': datetime.now().date().isoformat(),
            'end_date': (datetime.now() + timedelta(days=60)).date().isoformat()
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Campaign.objects.count(), 2)

class DemographicsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.influencer = Influencer.objects.create(
            name='Test Influencer',
            instagram_id='test123',
            followers_count=10000,
            engagement_rate=4.5,
            niche='fitness'
        )
        
        self.demographics = Demographics.objects.create(
            influencer=self.influencer,
            age_13_17=10.0,
            age_18_24=30.0,
            age_25_34=40.0,
            age_35_44=15.0,
            age_45_plus=5.0,
            gender_distribution={'M': 40, 'F': 60},
            top_locations=[{'location': 'New York', 'percentage': 30}]
        )

    def test_get_demographics(self):
        url = reverse('demographics-detail', args=[self.demographics.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['age_18_24'], 30.0)
        self.assertEqual(response.data['gender_distribution'], {'M': 40, 'F': 60})

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_dashboard_view(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_instagram_auth_view(self):
        response = self.client.get(reverse('instagram_auth'))
        self.assertEqual(response.status_code, 302)  # Should redirect to Instagram

class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.influencer = Influencer.objects.create(
            name='Test Influencer',
            instagram_id='test123',
            followers_count=10000,
            engagement_rate=4.5,
            niche='fitness'
        )
        
        self.campaign = Campaign.objects.create(
            name='Test Campaign',
            user=self.user,
            target_audience_age={'18-24': 50, '25-34': 50},
            target_audience_gender={'F': 70, 'M': 30},
            target_locations=['New York', 'Los Angeles'],
            min_followers=5000,
            min_engagement_rate=3.0,
            niche='fitness',
            budget=Decimal('1000.00'),
            start_date=datetime.now().date(),
            end_date=(datetime.now() + timedelta(days=30)).date()
        )

    def test_influencer_str(self):
        self.assertEqual(
            str(self.influencer),
            'Test Influencer (test123)'
        )

    def test_campaign_str(self):
        self.assertEqual(
            str(self.campaign),
            'Test Campaign'
        )

    def test_campaign_influencer_creation(self):
        campaign_influencer = CampaignInfluencer.objects.create(
            campaign=self.campaign,
            influencer=self.influencer,
            status='pending',
            ai_score=0.85,
            proposed_rate=Decimal('200.00')
        )
        self.assertEqual(
            str(campaign_influencer),
            'Test Campaign - Test Influencer'
        ) 