"""
False Positive Filter - Main Orchestrator

Combines all 6 layers of validation to filter false positives.
"""
from typing import Dict, Any, List
from app.core.logging import logger
from app.ml.feature_extraction import FeatureExtractor
from app.ml.rule_validators import RuleBasedValidator
from app.ml.classifier import MLClassifier
from app.ml.confidence_scorer import ConfidenceScorer


class FalsePositiveFilter:
    """
    Multi-layer false positive filter.
    
    Layers:
    1. Rule-Based Validation
    2. Context Analysis
    3. Behavioral Analysis
    4. ML Classification
    5. Automated Verification
    6. Manual Review Queue
    
    Goal: Reduce false positive rate to < 5%
    """
    
    def __init__(self, ml_model_path: str = None):
        """
        Initialize false positive filter.
        
        Args:
            ml_model_path: Path to ML model file
        """
        self.feature_extractor = FeatureExtractor()
        self.rule_validator = RuleBasedValidator()
        self.ml_classifier = MLClassifier(ml_model_path)
        self.confidence_scorer = ConfidenceScorer()
        
        # Statistics
        self.stats = {
            'total_findings': 0,
            'passed_filters': 0,
            'failed_filters': 0,
            'manual_review': 0,
            'false_positive_rate': 0.0
        }
    
    def filter_finding(self, finding: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply multi-layer filtering to a vulnerability finding.
        
        Args:
            finding: Dictionary containing finding data
            
        Returns:
            Dictionary with filtering results and final decision
        """
        self.stats['total_findings'] += 1
        
        result = {
            'finding_id': finding.get('id'),
            'original_confidence': finding.get('confidence', 0.5),
            'layers': {},
            'final_decision': None,
            'final_confidence': 0.0,
            'manual_review_needed': False,
            'reasons': []
        }
        
        try:
            # Layer 1: Rule-Based Validation
            rule_result = self.rule_validator.validate(finding)
            result['layers']['rule_based'] = rule_result
            
            if not rule_result['valid']:
                result['reasons'].append('Failed rule-based validation')
                logger.debug(f"Finding {finding.get('id')}: Failed rule-based validation")
            
            # Layer 2 & 3: Context and Behavioral Analysis
            # Extract features (includes context and behavioral analysis)
            features = self.feature_extractor.extract_features(finding)
            result['layers']['features'] = features
            
            # Layer 4: ML Classification
            ml_prediction = self.ml_classifier.predict(finding)
            result['layers']['ml_prediction'] = ml_prediction
            
            if ml_prediction.get('is_false_positive'):
                result['reasons'].append('ML classifier marked as false positive')
                logger.debug(f"Finding {finding.get('id')}: ML marked as false positive")
            
            # Calculate final confidence score
            confidence_result = self.confidence_scorer.calculate_confidence(
                finding=finding,
                rule_validation=rule_result,
                ml_prediction=ml_prediction
            )
            
            result['final_confidence'] = confidence_result['confidence_score']
            result['classification'] = confidence_result['classification']
            result['confidence_factors'] = confidence_result['factors']
            result['manual_review_needed'] = confidence_result['manual_review_needed']
            
            # Make final decision
            final_decision = self._make_final_decision(
                confidence_result,
                rule_result,
                ml_prediction
            )
            
            result['final_decision'] = final_decision
            
            # Update statistics
            if final_decision == 'accept':
                self.stats['passed_filters'] += 1
            elif final_decision == 'reject':
                self.stats['failed_filters'] += 1
            elif final_decision == 'manual_review':
                self.stats['manual_review'] += 1
            
            # Generate explanation
            result['explanation'] = self.confidence_scorer.get_confidence_explanation(
                confidence_result
            )
            
            logger.info(
                f"Finding {finding.get('id')}: {final_decision} "
                f"(confidence: {result['final_confidence']:.2%})"
            )
        
        except Exception as e:
            logger.error(f"Error filtering finding {finding.get('id')}: {e}", exc_info=True)
            result['final_decision'] = 'error'
            result['error'] = str(e)
            result['reasons'].append(f'Error during filtering: {str(e)}')
        
        return result
    
    def _make_final_decision(
        self,
        confidence_result: Dict[str, Any],
        rule_result: Dict[str, Any],
        ml_prediction: Dict[str, Any]
    ) -> str:
        """
        Make final decision on finding.
        
        Returns:
            'accept', 'reject', or 'manual_review'
        """
        confidence = confidence_result['confidence_score']
        classification = confidence_result['classification']
        manual_review_needed = confidence_result['manual_review_needed']
        
        # High confidence - accept
        if classification == 'confirmed' and confidence >= 0.85:
            return 'accept'
        
        # Very low confidence - reject
        if classification == 'rejected' or confidence < 0.15:
            return 'reject'
        
        # Manual review needed
        if manual_review_needed or classification == 'uncertain':
            return 'manual_review'
        
        # Medium-high confidence - accept
        if classification in ['likely', 'confirmed']:
            return 'accept'
        
        # Default to manual review for edge cases
        return 'manual_review'
    
    def filter_batch(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter a batch of findings.
        
        Args:
            findings: List of finding dictionaries
            
        Returns:
            List of filtering results
        """
        results = []
        
        for finding in findings:
            result = self.filter_finding(finding)
            results.append(result)
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get filtering statistics.
        
        Returns:
            Dictionary with statistics
        """
        if self.stats['total_findings'] > 0:
            self.stats['false_positive_rate'] = (
                self.stats['failed_filters'] / self.stats['total_findings']
            )
        
        return self.stats.copy()
    
    def reset_statistics(self):
        """Reset statistics counters."""
        self.stats = {
            'total_findings': 0,
            'passed_filters': 0,
            'failed_filters': 0,
            'manual_review': 0,
            'false_positive_rate': 0.0
        }


class ManualReviewQueue:
    """
    Manage findings that need manual review.
    
    Criteria for manual review:
    - confidence < 0.7
    - high severity
    - new vulnerability type
    - unusual context
    """
    
    def __init__(self):
        self.queue = []
    
    def add_to_queue(
        self,
        finding: Dict[str, Any],
        filter_result: Dict[str, Any]
    ):
        """
        Add finding to manual review queue.
        
        Args:
            finding: Original finding
            filter_result: Result from false positive filter
        """
        review_item = {
            'finding_id': finding.get('id'),
            'finding': finding,
            'filter_result': filter_result,
            'confidence': filter_result.get('final_confidence', 0.0),
            'reasons': filter_result.get('reasons', []),
            'priority': self._calculate_priority(finding, filter_result),
            'status': 'pending',
            'reviewed_by': None,
            'review_decision': None,
            'review_notes': None
        }
        
        self.queue.append(review_item)
        
        # Sort by priority (highest first)
        self.queue.sort(key=lambda x: x['priority'], reverse=True)
        
        logger.info(
            f"Added finding {finding.get('id')} to manual review queue "
            f"(priority: {review_item['priority']})"
        )
    
    def _calculate_priority(
        self,
        finding: Dict[str, Any],
        filter_result: Dict[str, Any]
    ) -> int:
        """
        Calculate priority for manual review.
        Higher number = higher priority.
        """
        priority = 50  # Base priority
        
        # Severity boost
        severity = finding.get('severity', '').lower()
        severity_boost = {
            'critical': 40,
            'high': 30,
            'medium': 20,
            'low': 10,
            'info': 5
        }
        priority += severity_boost.get(severity, 0)
        
        # Confidence penalty (lower confidence = higher priority)
        confidence = filter_result.get('final_confidence', 0.5)
        if confidence < 0.5:
            priority += 20
        elif confidence < 0.7:
            priority += 10
        
        # Multiple failed checks
        rule_result = filter_result.get('layers', {}).get('rule_based', {})
        checks_failed = len(rule_result.get('checks_failed', []))
        if checks_failed >= 3:
            priority += 15
        
        return priority
    
    def get_queue(self, status: str = None) -> List[Dict[str, Any]]:
        """
        Get manual review queue.
        
        Args:
            status: Filter by status (pending, reviewed, approved, rejected)
            
        Returns:
            List of review items
        """
        if status:
            return [item for item in self.queue if item['status'] == status]
        return self.queue.copy()
    
    def mark_reviewed(
        self,
        finding_id: int,
        reviewed_by: str,
        decision: str,
        notes: str = None
    ):
        """
        Mark a finding as reviewed.
        
        Args:
            finding_id: Finding ID
            reviewed_by: Reviewer username/email
            decision: Review decision (approve, reject, uncertain)
            notes: Review notes
        """
        for item in self.queue:
            if item['finding_id'] == finding_id:
                item['status'] = 'reviewed'
                item['reviewed_by'] = reviewed_by
                item['review_decision'] = decision
                item['review_notes'] = notes
                
                logger.info(
                    f"Finding {finding_id} reviewed by {reviewed_by}: {decision}"
                )
                break
    
    def get_stats(self) -> Dict[str, int]:
        """Get queue statistics."""
        return {
            'total': len(self.queue),
            'pending': len([i for i in self.queue if i['status'] == 'pending']),
            'reviewed': len([i for i in self.queue if i['status'] == 'reviewed']),
            'approved': len([i for i in self.queue if i.get('review_decision') == 'approve']),
            'rejected': len([i for i in self.queue if i.get('review_decision') == 'reject'])
        }
