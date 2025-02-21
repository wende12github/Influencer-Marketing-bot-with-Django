import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class InstagramAPI:
    def __init__(self):
        self.access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
        self.api_base_url = 'https://graph.instagram.com/v12.0'
        
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make a request to the Instagram Graph API."""
        if params is None:
            params = {}
        params['access_token'] = self.access_token
        
        response = requests.get(f"{self.api_base_url}/{endpoint}", params=params)
        response.raise_for_status()
        return response.json()

    def get_influencer_data(self, user_id: str) -> Dict:
        """Fetch basic data for a specific influencer."""
        try:
            fields = 'id,username,media_count,followers_count,follows_count'
            return self._make_request(user_id, {'fields': fields})
        except requests.exceptions.RequestException as e:
            print(f"Error fetching influencer data: {e}")
            return {}

    def get_posts(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Get recent posts for an influencer."""
        try:
            fields = 'id,caption,media_type,timestamp,like_count,comments_count'
            params = {
                'fields': fields,
                'limit': limit
            }
            response = self._make_request(f"{user_id}/media", params)
            return response.get('data', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching posts: {e}")
            return []

    def get_post_insights(self, post_id: str) -> Dict:
        """Get insights for a specific post."""
        try:
            metrics = 'engagement,impressions,reach'
            return self._make_request(f"{post_id}/insights", {'metric': metrics})
        except requests.exceptions.RequestException as e:
            print(f"Error fetching post insights: {e}")
            return {}

    def get_audience_demographics(self, user_id: str) -> Dict:
        """Analyze posts/stories for demographic information."""
        try:
            # Note: This is a simplified version. In reality, you'd need business
            # account access and proper permissions for demographic data
            metrics = 'audience_gender_age,audience_locale,audience_country'
            return self._make_request(f"{user_id}/insights", {'metric': metrics})
        except requests.exceptions.RequestException as e:
            print(f"Error fetching audience demographics: {e}")
            return {}

    def calculate_engagement_rate(self, user_id: str) -> float:
        """Calculate engagement rate based on recent posts."""
        try:
            posts = self.get_posts(user_id)
            if not posts:
                return 0.0

            total_engagement = 0
            for post in posts:
                likes = post.get('like_count', 0)
                comments = post.get('comments_count', 0)
                total_engagement += likes + comments

            user_data = self.get_influencer_data(user_id)
            followers = user_data.get('followers_count', 0)
            
            if followers == 0:
                return 0.0

            avg_engagement = total_engagement / len(posts)
            engagement_rate = (avg_engagement / followers) * 100
            return round(engagement_rate, 2)
        except Exception as e:
            print(f"Error calculating engagement rate: {e}")
            return 0.0

    def search_influencers(self, hashtag: str, min_followers: int = 1000) -> List[Dict]:
        """Search for influencers using a hashtag."""
        try:
            # Note: This is a simplified version. In reality, you'd need to implement
            # proper pagination and filtering
            params = {
                'q': hashtag,
                'fields': 'id,username,followers_count'
            }
            response = self._make_request('ig_hashtag_search', params)
            
            # Filter by minimum followers
            influencers = []
            for user in response.get('data', []):
                if user.get('followers_count', 0) >= min_followers:
                    influencers.append(user)
            
            return influencers
        except requests.exceptions.RequestException as e:
            print(f"Error searching influencers: {e}")
            return []

# Example usage:
if __name__ == "__main__":
    api = InstagramAPI()
    
    # Example: Search for influencers
    influencers = api.search_influencers('fitness', min_followers=10000)
    
    # Example: Get influencer data and engagement rate
    for influencer in influencers[:5]:  # Process first 5 influencers
        user_id = influencer['id']
        
        # Get basic data
        data = api.get_influencer_data(user_id)
        
        # Calculate engagement rate
        engagement_rate = api.calculate_engagement_rate(user_id)
        
        print(f"Influencer: {data.get('username')}")
        print(f"Followers: {data.get('followers_count')}")
        print(f"Engagement Rate: {engagement_rate}%")
        print("---") 