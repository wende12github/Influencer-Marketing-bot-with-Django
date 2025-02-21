from typing import Dict, List, Tuple
import numpy as np
from datetime import datetime, timedelta

class EngagementAnalyzer:
    def __init__(self):
        self.engagement_weights = {
            'likes': 1.0,
            'comments': 2.0,
            'saves': 3.0,
            'shares': 4.0
        }

    def calculate_engagement_rate(self, posts_data: List[Dict], followers_count: int) -> float:
        """
        Calculate the engagement rate for a set of posts.
        
        Args:
            posts_data: List of post dictionaries containing engagement metrics
            followers_count: Number of followers for the influencer
            
        Returns:
            float: Engagement rate as a percentage
        """
        if not posts_data or followers_count == 0:
            return 0.0

        total_engagement = 0
        for post in posts_data:
            weighted_engagement = (
                post.get('likes_count', 0) * self.engagement_weights['likes'] +
                post.get('comments_count', 0) * self.engagement_weights['comments'] +
                post.get('saves_count', 0) * self.engagement_weights['saves'] +
                post.get('shares_count', 0) * self.engagement_weights['shares']
            )
            total_engagement += weighted_engagement

        avg_engagement = total_engagement / len(posts_data)
        engagement_rate = (avg_engagement / followers_count) * 100
        return round(engagement_rate, 2)

    def analyze_engagement_trends(self, posts_data: List[Dict]) -> Dict:
        """
        Analyze engagement trends over time.
        
        Args:
            posts_data: List of post dictionaries with timestamps and engagement metrics
            
        Returns:
            Dict containing trend analysis results
        """
        if not posts_data:
            return {}

        # Sort posts by date
        posts = sorted(posts_data, key=lambda x: x['posted_at'])
        
        # Calculate daily engagement rates
        daily_rates = {}
        for post in posts:
            date = post['posted_at'].date()
            engagement = (post.get('likes_count', 0) + post.get('comments_count', 0))
            
            if date in daily_rates:
                daily_rates[date].append(engagement)
            else:
                daily_rates[date] = [engagement]

        # Calculate average daily engagement
        avg_daily_rates = {
            date: sum(rates) / len(rates)
            for date, rates in daily_rates.items()
        }

        # Calculate trend metrics
        dates = list(avg_daily_rates.keys())
        rates = list(avg_daily_rates.values())
        
        if len(rates) > 1:
            trend = np.polyfit(range(len(rates)), rates, 1)[0]
        else:
            trend = 0

        return {
            'daily_engagement': avg_daily_rates,
            'trend': trend,
            'trend_direction': 'increasing' if trend > 0 else 'decreasing' if trend < 0 else 'stable'
        }

    def get_best_posting_times(self, posts_data: List[Dict]) -> List[Tuple[int, float]]:
        """
        Determine the best times to post based on historical engagement.
        
        Args:
            posts_data: List of post dictionaries with timestamps and engagement metrics
            
        Returns:
            List of tuples containing (hour, avg_engagement)
        """
        if not posts_data:
            return []

        # Group engagement by hour
        hourly_engagement = {}
        for post in posts_data:
            hour = post['posted_at'].hour
            engagement = (post.get('likes_count', 0) + post.get('comments_count', 0))
            
            if hour in hourly_engagement:
                hourly_engagement[hour].append(engagement)
            else:
                hourly_engagement[hour] = [engagement]

        # Calculate average engagement for each hour
        avg_hourly_engagement = [
            (hour, sum(engagements) / len(engagements))
            for hour, engagements in hourly_engagement.items()
        ]

        # Sort by engagement (highest to lowest)
        return sorted(avg_hourly_engagement, key=lambda x: x[1], reverse=True)

    def calculate_engagement_quality(self, post_data: Dict) -> Dict:
        """
        Calculate the quality of engagement for a post.
        
        Args:
            post_data: Dictionary containing post engagement metrics
            
        Returns:
            Dict containing engagement quality metrics
        """
        total_engagement = (
            post_data.get('likes_count', 0) +
            post_data.get('comments_count', 0) +
            post_data.get('saves_count', 0) +
            post_data.get('shares_count', 0)
        )

        if total_engagement == 0:
            return {
                'engagement_score': 0,
                'engagement_distribution': {
                    'likes': 0,
                    'comments': 0,
                    'saves': 0,
                    'shares': 0
                }
            }

        # Calculate weighted engagement score
        engagement_score = (
            post_data.get('likes_count', 0) * self.engagement_weights['likes'] +
            post_data.get('comments_count', 0) * self.engagement_weights['comments'] +
            post_data.get('saves_count', 0) * self.engagement_weights['saves'] +
            post_data.get('shares_count', 0) * self.engagement_weights['shares']
        ) / total_engagement

        # Calculate engagement distribution
        engagement_distribution = {
            'likes': (post_data.get('likes_count', 0) / total_engagement) * 100,
            'comments': (post_data.get('comments_count', 0) / total_engagement) * 100,
            'saves': (post_data.get('saves_count', 0) / total_engagement) * 100,
            'shares': (post_data.get('shares_count', 0) / total_engagement) * 100
        }

        return {
            'engagement_score': round(engagement_score, 2),
            'engagement_distribution': {
                k: round(v, 2) for k, v in engagement_distribution.items()
            }
        }

# Example usage:
if __name__ == "__main__":
    analyzer = EngagementAnalyzer()
    
    # Example post data
    sample_posts = [
        {
            'posted_at': datetime.now() - timedelta(days=1),
            'likes_count': 1000,
            'comments_count': 50,
            'saves_count': 20,
            'shares_count': 10
        },
        {
            'posted_at': datetime.now() - timedelta(days=2),
            'likes_count': 1500,
            'comments_count': 75,
            'saves_count': 30,
            'shares_count': 15
        }
    ]
    
    # Calculate engagement rate
    engagement_rate = analyzer.calculate_engagement_rate(sample_posts, followers_count=10000)
    print(f"Engagement Rate: {engagement_rate}%")
    
    # Analyze trends
    trends = analyzer.analyze_engagement_trends(sample_posts)
    print(f"Engagement Trend: {trends['trend_direction']}")
    
    # Get best posting times
    best_times = analyzer.get_best_posting_times(sample_posts)
    print("Best posting times:")
    for hour, engagement in best_times[:3]:
        print(f"{hour}:00 - Avg. Engagement: {engagement}") 