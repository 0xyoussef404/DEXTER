"""
Unit tests for Confidence Scorer
"""
import pytest
from app.ml.confidence_scorer import ConfidenceScorer


class TestConfidenceScorer:
    """Test suite for ConfidenceScorer."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.scorer = ConfidenceScorer()
    
    def test_high_confidence_finding(self):
        """Test scoring of high confidence finding."""
        finding = {
            'id': 1,
            'confidence': 0.7,
            'payload': '<script>alert(1)</script>',
            'response': 'Result: <script>alert(1)</script>',
            'proof': {
                'execution_confirmed': True,
                'context_break_success': True,
                'callback_received': False,
                'techniques_confirmed': ['reflected', 'executed']
            }
        }
        
        result = self.scorer.calculate_confidence(finding)
        
        assert result['confidence_score'] >= 0.7
        assert result['classification'] in ['confirmed', 'likely']
        assert 'factors' in result
    
    def test_low_confidence_finding(self):
        """Test scoring of low confidence finding."""
        finding = {
            'id': 2,
            'confidence': 0.3,
            'payload': 'test',
            'response': 'No reflection here',
            'proof': {}
        }
        
        result = self.scorer.calculate_confidence(finding)
        
        assert result['confidence_score'] < 0.5
        assert result['classification'] in ['uncertain', 'unlikely', 'rejected']
    
    def test_manual_review_needed(self):
        """Test manual review criteria."""
        # Low confidence
        finding1 = {
            'id': 3,
            'confidence': 0.6,
            'severity': 'high',
            'proof': {}
        }
        
        result1 = self.scorer.calculate_confidence(finding1)
        assert result1['manual_review_needed'] is True
        
        # High severity with moderate confidence
        finding2 = {
            'id': 4,
            'confidence': 0.75,
            'severity': 'critical',
            'proof': {}
        }
        
        result2 = self.scorer.calculate_confidence(finding2)
        assert result2['manual_review_needed'] is True
    
    def test_classification_thresholds(self):
        """Test classification threshold logic."""
        assert self.scorer._classify_confidence(0.9) == 'confirmed'
        assert self.scorer._classify_confidence(0.75) == 'likely'
        assert self.scorer._classify_confidence(0.55) == 'uncertain'
        assert self.scorer._classify_confidence(0.35) == 'unlikely'
        assert self.scorer._classify_confidence(0.10) == 'rejected'
    
    def test_reflection_scoring(self):
        """Test payload reflection scoring."""
        # Reflected
        finding1 = {
            'payload': 'test123',
            'response': 'Result: test123'
        }
        assert self.scorer._score_reflection(finding1) == 0.3
        
        # Not reflected
        finding2 = {
            'payload': 'test123',
            'response': 'Result: nothing'
        }
        assert self.scorer._score_reflection(finding2) == -0.5
    
    def test_execution_proof_scoring(self):
        """Test execution proof scoring."""
        # With proof
        finding1 = {
            'proof': {'execution_confirmed': True}
        }
        assert self.scorer._score_execution_proof(finding1) == 0.9
        
        # Without proof
        finding2 = {
            'proof': {}
        }
        assert self.scorer._score_execution_proof(finding2) == 0.0
    
    def test_oob_callback_scoring(self):
        """Test OOB callback scoring."""
        # With callback
        finding1 = {
            'proof': {'callback_received': True}
        }
        assert self.scorer._score_oob_callback(finding1) == 0.8
        
        # Without callback
        finding2 = {
            'proof': {}
        }
        assert self.scorer._score_oob_callback(finding2) == 0.0
    
    def test_confidence_explanation(self):
        """Test confidence explanation generation."""
        result = {
            'confidence_score': 0.85,
            'classification': 'confirmed',
            'factors': {
                'payload_reflection': 0.3,
                'execution_proof': 0.9,
                'ml_confidence': 0.8
            },
            'manual_review_needed': False
        }
        
        explanation = self.scorer.get_confidence_explanation(result)
        
        assert '0.85' in explanation or '85%' in explanation
        assert 'confirmed' in explanation
        assert 'payload_reflection' in explanation
