from typing import Dict, List
import numpy as np
from collections import Counter
from datetime import datetime
import json

class DemographicsAnalyzer:
    def __init__(self):
        self.age_ranges = {
            '13-17': (13, 17),
            '18-24': (18, 24),
            '25-34': (25, 34),
            '35-44': (35, 44),
            '45+': (45, 100)
        }

    def analyze_audience_demographics(self, engagement_data: List[Dict]) -> Dict:
        """
        Analyze audience demographics from engagement data.
        
        Args:
            engagement_data: List of dictionaries containing user engagement data
            
        Returns:
            Dict containing demographic analysis results
        """
        if not engagement_data:
            return {}

        # Initialize counters
        age_distribution = {range_name: 0 for range_name in self.age_ranges.keys()}
        gender_distribution = {'M': 0, 'F': 0, 'O': 0}
        location_counter = Counter()
        
        total_users = len(engagement_data)
        
        for user_data in engagement_data:
            # Age analysis
            age = user_data.get('age')
            if age:
                for range_name, (min_age, max_age) in self.age_ranges.items():
                    if min_age <= age <= max_age:
                        age_distribution[range_name] += 1
                        break

            # Gender analysis
            gender = user_data.get('gender', 'O')
            if gender in gender_distribution:
                gender_distribution[gender] += 1

            # Location analysis
            location = user_data.get('location')
            if location:
                location_counter[location] += 1

        # Convert counts to percentages
        age_percentages = {
            range_name: (count / total_users) * 100
            for range_name, count in age_distribution.items()
        }

        gender_percentages = {
            gender: (count / total_users) * 100
            for gender, count in gender_distribution.items()
        }

        # Get top locations
        top_locations = [
            {'location': loc, 'percentage': (count / total_users) * 100}
            for loc, count in location_counter.most_common(10)
        ]

        return {
            'age_distribution': {k: round(v, 2) for k, v in age_percentages.items()},
            'gender_distribution': {k: round(v, 2) for k, v in gender_percentages.items()},
            'top_locations': [
                {
                    'location': item['location'],
                    'percentage': round(item['percentage'], 2)
                }
                for item in top_locations
            ]
        }

    def analyze_demographic_engagement(self, posts_data: List[Dict]) -> Dict:
        """
        Analyze engagement patterns across different demographics.
        
        Args:
            posts_data: List of dictionaries containing post data with demographic information
            
        Returns:
            Dict containing demographic engagement analysis
        """
        if not posts_data:
            return {}

        # Initialize engagement trackers
        age_engagement = {range_name: [] for range_name in self.age_ranges.keys()}
        gender_engagement = {'M': [], 'F': [], 'O': []}
        location_engagement = {}

        for post in posts_data:
            demographics = post.get('demographics', {})
            engagement_rate = post.get('engagement_rate', 0)

            # Age engagement
            age_dist = demographics.get('age_distribution', {})
            for age_range, percentage in age_dist.items():
                if age_range in age_engagement:
                    age_engagement[age_range].append(engagement_rate * percentage)

            # Gender engagement
            gender_dist = demographics.get('gender_distribution', {})
            for gender, percentage in gender_dist.items():
                if gender in gender_engagement:
                    gender_engagement[gender].append(engagement_rate * percentage)

            # Location engagement
            location_dist = demographics.get('location_distribution', {})
            for location, percentage in location_dist.items():
                if location not in location_engagement:
                    location_engagement[location] = []
                location_engagement[location].append(engagement_rate * percentage)

        # Calculate average engagement rates
        avg_age_engagement = {
            age_range: np.mean(rates) if rates else 0
            for age_range, rates in age_engagement.items()
        }

        avg_gender_engagement = {
            gender: np.mean(rates) if rates else 0
            for gender, rates in gender_engagement.items()
        }

        avg_location_engagement = {
            location: np.mean(rates) if rates else 0
            for location, rates in location_engagement.items()
        }

        # Get top engaging locations
        top_locations = sorted(
            [
                {'location': loc, 'engagement_rate': rate}
                for loc, rate in avg_location_engagement.items()
            ],
            key=lambda x: x['engagement_rate'],
            reverse=True
        )[:10]

        return {
            'age_engagement': {k: round(v, 2) for k, v in avg_age_engagement.items()},
            'gender_engagement': {k: round(v, 2) for k, v in avg_gender_engagement.items()},
            'top_engaging_locations': [
                {
                    'location': item['location'],
                    'engagement_rate': round(item['engagement_rate'], 2)
                }
                for item in top_locations
            ]
        }

    def generate_demographic_report(self, engagement_data: List[Dict], posts_data: List[Dict]) -> Dict:
        """
        Generate a comprehensive demographic report combining audience and engagement analysis.
        
        Args:
            engagement_data: List of dictionaries containing user engagement data
            posts_data: List of dictionaries containing post data with demographic information
            
        Returns:
            Dict containing comprehensive demographic analysis
        """
        audience_demographics = self.analyze_audience_demographics(engagement_data)
        demographic_engagement = self.analyze_demographic_engagement(posts_data)

        return {
            'audience_analysis': audience_demographics,
            'engagement_analysis': demographic_engagement,
            'generated_at': datetime.now().isoformat(),
            'total_users_analyzed': len(engagement_data),
            'total_posts_analyzed': len(posts_data)
        }

# Example usage:
if __name__ == "__main__":
    analyzer = DemographicsAnalyzer()
    
    # Example data
    sample_engagement_data = [
        {
            'user_id': '1',
            'age': 25,
            'gender': 'F',
            'location': 'New York'
        },
        {
            'user_id': '2',
            'age': 30,
            'gender': 'M',
            'location': 'Los Angeles'
        }
    ]
    
    sample_posts_data = [
        {
            'post_id': '1',
            'engagement_rate': 5.2,
            'demographics': {
                'age_distribution': {'18-24': 0.3, '25-34': 0.7},
                'gender_distribution': {'M': 0.4, 'F': 0.6},
                'location_distribution': {'New York': 0.6, 'Los Angeles': 0.4}
            }
        }
    ]
    
    # Generate report
    report = analyzer.generate_demographic_report(sample_engagement_data, sample_posts_data)
    print(json.dumps(report, indent=2))