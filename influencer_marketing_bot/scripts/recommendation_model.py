import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Tuple
import joblib
from datetime import datetime

class InfluencerRecommender:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.feature_names = [
            'followers_count',
            'engagement_rate',
            'audience_match_score',
            'content_relevance_score',
            'brand_safety_score',
            'authenticity_score'
        ]

    def _extract_features(self, influencer_data: Dict) -> np.ndarray:
        """
        Extract features from influencer data for model input.
        
        Args:
            influencer_data: Dictionary containing influencer metrics
            
        Returns:
            numpy array of features
        """
        features = []
        for feature in self.feature_names:
            features.append(influencer_data.get(feature, 0))
        return np.array(features).reshape(1, -1)

    def _calculate_audience_match_score(
        self,
        influencer_demographics: Dict,
        target_demographics: Dict
    ) -> float:
        """
        Calculate how well an influencer's audience matches target demographics.
        
        Args:
            influencer_demographics: Dictionary containing influencer's audience demographics
            target_demographics: Dictionary containing target audience demographics
            
        Returns:
            float: Match score between 0 and 1
        """
        if not influencer_demographics or not target_demographics:
            return 0.0

        scores = []
        
        # Age match
        if 'age_distribution' in influencer_demographics and 'target_age' in target_demographics:
            age_match = sum(
                min(influencer_demographics['age_distribution'].get(age, 0),
                    target_demographics['target_age'].get(age, 0))
                for age in target_demographics['target_age']
            )
            scores.append(age_match)
        
        # Gender match
        if 'gender_distribution' in influencer_demographics and 'target_gender' in target_demographics:
            gender_match = sum(
                min(influencer_demographics['gender_distribution'].get(gender, 0),
                    target_demographics['target_gender'].get(gender, 0))
                for gender in target_demographics['target_gender']
            )
            scores.append(gender_match)
        
        # Location match
        if 'top_locations' in influencer_demographics and 'target_locations' in target_demographics:
            influencer_locations = {
                loc['location']: loc['percentage']
                for loc in influencer_demographics['top_locations']
            }
            target_locations = set(target_demographics['target_locations'])
            location_match = sum(
                influencer_locations.get(loc, 0)
                for loc in target_locations
            ) / 100
            scores.append(location_match)

        return np.mean(scores) if scores else 0.0

    def _calculate_content_relevance(
        self,
        influencer_content: List[Dict],
        target_keywords: List[str]
    ) -> float:
        """
        Calculate content relevance score based on keyword matching.
        
        Args:
            influencer_content: List of dictionaries containing influencer's content
            target_keywords: List of target keywords
            
        Returns:
            float: Relevance score between 0 and 1
        """
        if not influencer_content or not target_keywords:
            return 0.0

        keyword_matches = 0
        total_posts = len(influencer_content)
        
        for post in influencer_content:
            caption = post.get('caption', '').lower()
            hashtags = [tag.lower() for tag in post.get('hashtags', [])]
            
            # Check for keyword matches in caption and hashtags
            matches = sum(
                1 for keyword in target_keywords
                if keyword.lower() in caption or keyword.lower() in hashtags
            )
            keyword_matches += matches / len(target_keywords)

        return keyword_matches / total_posts if total_posts > 0 else 0.0

    def train_model(
        self,
        training_data: List[Dict],
        campaign_success: List[int]
    ) -> None:
        """
        Train the recommendation model.
        
        Args:
            training_data: List of dictionaries containing influencer data
            campaign_success: List of binary values indicating campaign success
        """
        X = np.array([self._extract_features(data)[0] for data in training_data])
        y = np.array(campaign_success)

        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)

    def save_model(self, model_path: str, scaler_path: str) -> None:
        """
        Save the trained model and scaler.
        
        Args:
            model_path: Path to save the model
            scaler_path: Path to save the scaler
        """
        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, scaler_path)

    def load_model(self, model_path: str, scaler_path: str) -> None:
        """
        Load a trained model and scaler.
        
        Args:
            model_path: Path to the saved model
            scaler_path: Path to the saved scaler
        """
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)

    def recommend_influencers(
        self,
        influencers: List[Dict],
        campaign_criteria: Dict
    ) -> List[Dict]:
        """
        Recommend influencers based on campaign criteria.
        
        Args:
            influencers: List of dictionaries containing influencer data
            campaign_criteria: Dictionary containing campaign requirements
            
        Returns:
            List of recommended influencers with scores
        """
        recommendations = []
        
        for influencer in influencers:
            # Calculate audience match score
            audience_match = self._calculate_audience_match_score(
                influencer.get('demographics', {}),
                campaign_criteria.get('demographics', {})
            )
            
            # Calculate content relevance
            content_relevance = self._calculate_content_relevance(
                influencer.get('recent_posts', []),
                campaign_criteria.get('keywords', [])
            )
            
            # Prepare features for prediction
            features = {
                'followers_count': influencer.get('followers_count', 0),
                'engagement_rate': influencer.get('engagement_rate', 0),
                'audience_match_score': audience_match,
                'content_relevance_score': content_relevance,
                'brand_safety_score': influencer.get('brand_safety_score', 0.5),
                'authenticity_score': influencer.get('authenticity_score', 0.5)
            }
            
            X = self._extract_features(features)
            X_scaled = self.scaler.transform(X)
            
            # Get prediction probability
            success_probability = self.model.predict_proba(X_scaled)[0][1]
            
            # Calculate overall score
            overall_score = np.mean([
                success_probability,
                audience_match,
                content_relevance,
                features['engagement_rate'] / 100
            ])
            
            recommendations.append({
                'influencer_id': influencer.get('id'),
                'name': influencer.get('name'),
                'overall_score': round(overall_score * 100, 2),
                'success_probability': round(success_probability * 100, 2),
                'audience_match': round(audience_match * 100, 2),
                'content_relevance': round(content_relevance * 100, 2),
                'engagement_rate': round(features['engagement_rate'], 2),
                'followers_count': features['followers_count']
            })
        
        # Sort by overall score
        recommendations.sort(key=lambda x: x['overall_score'], reverse=True)
        return recommendations

# Example usage:
if __name__ == "__main__":
    recommender = InfluencerRecommender()
    
    # Example training data
    sample_training_data = [
        {
            'followers_count': 50000,
            'engagement_rate': 3.5,
            'audience_match_score': 0.8,
            'content_relevance_score': 0.7,
            'brand_safety_score': 0.9,
            'authenticity_score': 0.85
        },
        {
            'followers_count': 100000,
            'engagement_rate': 2.8,
            'audience_match_score': 0.6,
            'content_relevance_score': 0.8,
            'brand_safety_score': 0.95,
            'authenticity_score': 0.9
        }
    ]
    
    # Example campaign success data (1 = successful, 0 = unsuccessful)
    sample_success = [1, 0]
    
    # Train model
    recommender.train_model(sample_training_data, sample_success)
    
    # Example influencers to recommend
    sample_influencers = [
        {
            'id': '1',
            'name': 'Influencer A',
            'followers_count': 75000,
            'engagement_rate': 4.2,
            'demographics': {
                'age_distribution': {'18-24': 0.4, '25-34': 0.6},
                'gender_distribution': {'M': 0.3, 'F': 0.7},
                'top_locations': [
                    {'location': 'New York', 'percentage': 30},
                    {'location': 'Los Angeles', 'percentage': 20}
                ]
            },
            'recent_posts': [
                {
                    'caption': 'Loving this new fitness routine! #fitness #health',
                    'hashtags': ['fitness', 'health', 'workout']
                }
            ]
        }
    ]
    
    # Example campaign criteria
    sample_criteria = {
        'demographics': {
            'target_age': {'18-24': 0.5, '25-34': 0.5},
            'target_gender': {'F': 0.8, 'M': 0.2},
            'target_locations': ['New York', 'Los Angeles']
        },
        'keywords': ['fitness', 'health', 'wellness']
    }
    
    # Get recommendations
    recommendations = recommender.recommend_influencers(sample_influencers, sample_criteria)
    
    # Print recommendations
    for rec in recommendations:
        print(f"\nRecommendation for {rec['name']}:")
        print(f"Overall Score: {rec['overall_score']}%")
        print(f"Success Probability: {rec['success_probability']}%")
        print(f"Audience Match: {rec['audience_match']}%")
        print(f"Content Relevance: {rec['content_relevance']}%")
        print(f"Engagement Rate: {rec['engagement_rate']}%") 