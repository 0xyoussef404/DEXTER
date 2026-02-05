"""
Machine Learning Module for False Positive Detection

This module implements a comprehensive 6-layer false positive detection system:

Layer 1: Rule-Based Validation (rule_validators.py)
- XSS: reflection + context break + execution + WAF check + DOM verification
- SQLi: timing threshold + statistical confidence + multiple techniques
- SSRF: callback required + timing analysis
- Generic: payload effect + reproducible + not in baseline

Layer 2: Context Analysis (integrated in feature_extraction.py)
- HTTP context (method, content-type, headers, cookies, auth)
- Response context (status, headers, body, errors)
- Application context (framework, WAF, tech stack)
- Injection context (HTML/SQL contexts)

Layer 3: Behavioral Analysis (integrated in feature_extraction.py)
- Baseline comparison (2x threshold)
- Pattern recognition
- Anomaly detection

Layer 4: ML Classification (classifier.py)
- Random Forest classifier
- 13 features extracted
- Ensemble voting (weights: 0.4, 0.4, 0.2)
- 0.80 confidence threshold
- Continuous learning support

Layer 5: Automated Verification (external integration points)
- Headless browser verification
- Multi-payload testing (minimum 3)
- OOB callbacks (DNS/HTTP, 30s timeout)
- Database verification
- Timing verification (10 samples, t-test, 0.95 confidence)

Layer 6: Manual Review Queue (false_positive_filter.py)
- Confidence < 0.7 → manual review
- High severity with moderate confidence
- New/unusual vulnerability types
- Multiple failed checks

Confidence Scoring (confidence_scorer.py):
- Multi-factor weighted scoring
- Thresholds: confirmed (0.85), likely (0.70), uncertain (0.50), unlikely (0.30), rejected (0.15)
- Explainable confidence scores

Usage:
    from app.ml.false_positive_filter import FalsePositiveFilter
    
    filter = FalsePositiveFilter()
    result = filter.filter_finding(finding_dict)
    
    if result['final_decision'] == 'accept':
        # Accept finding as valid
        pass
    elif result['final_decision'] == 'manual_review':
        # Add to manual review queue
        pass
    else:
        # Reject as false positive
        pass
"""

from app.ml.false_positive_filter import FalsePositiveFilter, ManualReviewQueue
from app.ml.classifier import MLClassifier
from app.ml.confidence_scorer import ConfidenceScorer
from app.ml.feature_extraction import FeatureExtractor
from app.ml.rule_validators import RuleBasedValidator

__all__ = [
    'FalsePositiveFilter',
    'ManualReviewQueue',
    'MLClassifier',
    'ConfidenceScorer',
    'FeatureExtractor',
    'RuleBasedValidator',
]
