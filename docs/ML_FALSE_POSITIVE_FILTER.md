# AI/ML False Positive Filter - Technical Documentation

## Overview

The AI/ML False Positive Filter is a comprehensive 6-layer validation system designed to reduce false positive rates to under 5% in vulnerability detection. It implements state-of-the-art techniques including rule-based validation, context analysis, behavioral analysis, machine learning classification, automated verification, and manual review queues.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│           False Positive Filter Pipeline                │
└─────────────────────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   ┌────────┐      ┌────────┐      ┌────────┐
   │Layer 1 │      │Layer 2 │      │Layer 3 │
   │  Rule  │      │Context │      │Behavior│
   │  Based │      │Analysis│      │Analysis│
   └────┬───┘      └────┬───┘      └────┬───┘
        │               │               │
        └───────────────┼───────────────┘
                        ▼
                  ┌──────────┐
                  │ Layer 4  │
                  │    ML    │
                  │Classifier│
                  └─────┬────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
   ┌────────┐     ┌────────┐     ┌────────┐
   │Layer 5 │     │Layer 6 │     │Confidence│
   │Auto    │     │Manual  │     │ Scorer  │
   │Verify  │     │Review  │     │         │
   └────────┘     └────────┘     └────────┘
                        │
                        ▼
               ┌──────────────┐
               │Final Decision│
               │ Accept/      │
               │ Reject/      │
               │ Review       │
               └──────────────┘
```

## Components

### 1. Feature Extraction (`feature_extraction.py`)

Extracts 13 features from vulnerability findings for ML classification:

**Features:**
1. `payload_length` - Length of the attack payload
2. `payload_entropy` - Shannon entropy (randomness) of payload
3. `special_char_count` - Count of special characters
4. `encoding_layers` - Number of encoding layers detected
5. `response_time` - HTTP response time in milliseconds
6. `response_size` - Size of HTTP response in bytes
7. `response_code` - HTTP status code
8. `header_count` - Number of HTTP headers
9. `reflection_count` - Times payload appears in response
10. `reflection_context` - Context where payload is reflected (HTML/JS/CSS/URL)
11. `context_break_success` - Boolean: successfully escaped context
12. `error_indicator_count` - Count of error messages in response
13. `anomaly_score` - Behavioral anomaly score

**Usage:**
```python
from app.ml.feature_extraction import FeatureExtractor

extractor = FeatureExtractor()
features = extractor.extract_features(finding_dict)
# Returns: {
#     'payload_length': 25,
#     'payload_entropy': 3.45,
#     'special_char_count': 8,
#     ...
# }
```

### 2. Rule-Based Validators (`rule_validators.py`)

Layer 1: Strict rule-based validation for each vulnerability type.

**XSS Validation:**
- ✅ Payload must be reflected in response
- ✅ Must break out of context (escape quotes, tags, etc.)
- ✅ Must execute in browser (verified via headless browser)
- ✅ Must check if WAF blocked the request
- ✅ Must verify DOM state changes

**SQLi Validation:**
- ✅ Timing threshold: minimum 5 seconds delay
- ✅ Statistical confidence: 0.95 (via t-test)
- ✅ Multiple technique confirmation (at least 2)
- ✅ Error-based confirmation
- ✅ Database extraction proof

**SSRF Validation:**
- ✅ Callback must be received (DNS or HTTP)
- ✅ Timing analysis for blind SSRF
- ✅ Cloud metadata detection in response

**Generic Validation:**
- ✅ Payload must affect response
- ✅ Must be reproducible
- ✅ Must not be in baseline

**Usage:**
```python
from app.ml.rule_validators import RuleBasedValidator

validator = RuleBasedValidator()
result = validator.validate(finding_dict)
# Returns: {
#     'valid': True,
#     'confidence_adjustment': 0.4,
#     'checks_passed': ['payload_reflected', 'context_break', ...],
#     'checks_failed': [],
#     'notes': []
# }
```

### 3. ML Classifier (`classifier.py`)

Layer 4: Random Forest machine learning classifier with ensemble voting.

**Model Specifications:**
- Algorithm: Random Forest (100 estimators)
- Features: 13 features from FeatureExtractor
- Ensemble: 3 models with weights [0.4, 0.4, 0.2]
- Threshold: 0.80 confidence minimum
- Training: Supports incremental learning and feedback

**Usage:**
```python
from app.ml.classifier import MLClassifier

classifier = MLClassifier()
prediction = classifier.predict(finding_dict)
# Returns: {
#     'is_false_positive': False,
#     'confidence': 0.92,
#     'ml_score': 0.92,
#     'false_positive_probability': 0.08,
#     'feature_importance': {...}
# }
```

**Training:**
```python
# Train with labeled data
training_data = [...]  # List of findings
labels = [0, 1, 0, ...]  # 0=True Positive, 1=False Positive

metrics = classifier.train(training_data, labels)
# Returns: {
#     'precision': 0.94,
#     'recall': 0.91,
#     'f1_score': 0.92,
#     ...
# }

# Save model
classifier.save_model()
```

### 4. Confidence Scorer (`confidence_scorer.py`)

Multi-factor confidence scoring system with explainable results.

**Scoring Factors:**
- `payload_reflection`: +0.3 if reflected, -0.5 if not
- `context_break`: +0.4 if broken, -0.3 if not
- `execution_proof`: +0.9 if proven, 0.0 otherwise
- `multiple_techniques`: +0.3 if multiple, 0.0 otherwise
- `behavioral_anomaly`: +0.2 if anomalous, 0.0 otherwise
- `ml_confidence`: 0.4 weight of ML score
- `oob_callback`: +0.8 if received, 0.0 otherwise

**Classification Thresholds:**
- `confirmed`: >= 0.85 (high confidence, accept)
- `likely`: >= 0.70 (medium-high confidence, accept)
- `uncertain`: >= 0.50 (manual review needed)
- `unlikely`: >= 0.30 (low confidence, likely FP)
- `rejected`: < 0.15 (very low confidence, reject)

**Usage:**
```python
from app.ml.confidence_scorer import ConfidenceScorer

scorer = ConfidenceScorer()
result = scorer.calculate_confidence(
    finding=finding_dict,
    rule_validation=rule_result,
    ml_prediction=ml_result
)
# Returns: {
#     'confidence_score': 0.87,
#     'classification': 'confirmed',
#     'manual_review_needed': False,
#     'factors': {...},
#     'total_adjustment': 0.37,
#     'base_confidence': 0.5
# }

# Get explanation
explanation = scorer.get_confidence_explanation(result)
print(explanation)
# Confidence: 87% (confirmed)
# 
# Contributing factors:
#   - payload_reflection: +0.3
#   - context_break: +0.4
#   - execution_proof: +0.9
#   - ml_confidence: +0.35
```

### 5. False Positive Filter (`false_positive_filter.py`)

Main orchestrator that combines all layers.

**Features:**
- Combines all 6 validation layers
- Makes final accept/reject/manual_review decision
- Tracks statistics and false positive rate
- Provides detailed explanations

**Usage:**
```python
from app.ml.false_positive_filter import FalsePositiveFilter

# Initialize filter
fp_filter = FalsePositiveFilter()

# Filter a single finding
result = fp_filter.filter_finding(finding_dict)
# Returns: {
#     'finding_id': 123,
#     'original_confidence': 0.7,
#     'final_confidence': 0.87,
#     'final_decision': 'accept',  # or 'reject' or 'manual_review'
#     'classification': 'confirmed',
#     'manual_review_needed': False,
#     'layers': {...},  # Results from each layer
#     'reasons': [],
#     'explanation': "Confidence: 87% (confirmed)..."
# }

# Filter batch
results = fp_filter.filter_batch([finding1, finding2, ...])

# Get statistics
stats = fp_filter.get_statistics()
# Returns: {
#     'total_findings': 100,
#     'passed_filters': 85,
#     'failed_filters': 10,
#     'manual_review': 5,
#     'false_positive_rate': 0.10  # 10%
# }
```

### 6. Manual Review Queue (`false_positive_filter.py`)

Manages findings that need manual review.

**Criteria for Manual Review:**
- Confidence < 0.7
- High/Critical severity with confidence < 0.85
- New or unusual vulnerability types
- Multiple validation checks failed

**Usage:**
```python
from app.ml.false_positive_filter import ManualReviewQueue

queue = ManualReviewQueue()

# Add finding to queue
queue.add_to_queue(finding, filter_result)

# Get queue (sorted by priority)
pending_reviews = queue.get_queue(status='pending')

# Mark as reviewed
queue.mark_reviewed(
    finding_id=123,
    reviewed_by='analyst@example.com',
    decision='approve',
    notes='Confirmed XSS in login form'
)

# Get statistics
stats = queue.get_stats()
# Returns: {
#     'total': 15,
#     'pending': 10,
#     'reviewed': 5,
#     'approved': 3,
#     'rejected': 2
# }
```

## Integration with Vulnerability Scanners

The false positive filter integrates with the vulnerability detection services:

```python
# In vulnerability scanner (e.g., xss_detector.py)
from app.ml import FalsePositiveFilter

class XSSDetector:
    def __init__(self):
        self.fp_filter = FalsePositiveFilter()
    
    def detect(self, target_url, payloads):
        findings = []
        
        for payload in payloads:
            # Test payload
            result = self._test_payload(target_url, payload)
            
            if result['vulnerable']:
                # Create finding
                finding = {
                    'vulnerability_type': 'xss',
                    'payload': payload,
                    'response': result['response'],
                    'proof': result['proof'],
                    ...
                }
                
                # Apply false positive filter
                filter_result = self.fp_filter.filter_finding(finding)
                
                if filter_result['final_decision'] == 'accept':
                    # Accept as valid finding
                    findings.append(finding)
                elif filter_result['final_decision'] == 'manual_review':
                    # Add to manual review queue
                    finding['needs_review'] = True
                    findings.append(finding)
                # else: reject as false positive
        
        return findings
```

## Performance Metrics

The filter is designed to achieve:

- **False Positive Rate**: < 5%
- **True Positive Rate**: > 95%
- **Precision**: > 0.90
- **Recall**: > 0.95
- **F1 Score**: > 0.92

Actual metrics depend on training data quality and vulnerability type.

## Continuous Improvement

The system supports continuous learning:

1. **Feedback Loop**: Analysts mark findings as TP/FP
2. **Model Retraining**: Weekly automated retraining
3. **A/B Testing**: New models tested against production
4. **Rollback**: Automatic rollback if performance degrades
5. **Metrics Tracking**: Per-vulnerability-type metrics

## Best Practices

1. **Training Data**: Use high-quality labeled dataset (minimum 1000 samples)
2. **Regular Updates**: Retrain models weekly with new feedback
3. **Manual Review**: Always review high-severity findings with confidence < 0.85
4. **WAF Awareness**: Filter integrates WAF detection to avoid false negatives
5. **Baseline Establishment**: Run baseline scans before vulnerability testing
6. **Multi-Payload Testing**: Use minimum 3 different payloads for confirmation

## Troubleshooting

**Issue: High false positive rate**
- Check training data quality
- Verify baseline scans are running
- Review rule validator settings
- Increase confidence threshold

**Issue: Missing true positives**
- Check if WAF detection is too aggressive
- Review confidence scoring weights
- Verify automated verification is working
- Lower confidence threshold temporarily

**Issue: Too many manual reviews**
- Adjust manual review criteria
- Retrain ML model with more data
- Review confidence thresholds
- Optimize rule validators

## Dependencies

- `scikit-learn` >= 1.4.0 - Machine learning
- `scipy` >= 1.12.0 - Statistical analysis
- `numpy` >= 1.26.3 - Numerical computing
- `joblib` >= 1.3.2 - Model persistence

## Testing

Run tests with:
```bash
pytest tests/test_ml/ -v
```

Tests cover:
- Feature extraction accuracy
- Rule validator logic
- ML classifier predictions
- Confidence scoring
- End-to-end filtering pipeline

## Future Enhancements

1. **Deep Learning**: Add neural network models for complex patterns
2. **Transfer Learning**: Use pre-trained models for new vulnerability types
3. **Active Learning**: Automatically identify uncertain cases for labeling
4. **Explainable AI**: Enhanced feature importance and decision explanations
5. **Real-time Learning**: Update models in real-time as analysts review
6. **Ensemble Diversity**: Add XGBoost and other models to ensemble
