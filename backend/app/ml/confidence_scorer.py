"""
Confidence Scoring System

Implements multi-factor confidence scoring for vulnerability findings.
"""
from typing import Dict, Any
from app.core.logging import logger


class ConfidenceScorer:
    """
    Multi-factor confidence scoring system.
    
    Factors:
    - payload_reflection: 0.3 (positive) / -0.5 (negative)
    - context_break: 0.4 (positive) / -0.3 (negative)
    - execution_proof: 0.9 (positive) / 0.0 (negative)
    - multiple_techniques: 0.3 (positive) / 0.0 (negative)
    - behavioral_anomaly: 0.2 (positive) / 0.0 (negative)
    - ml_confidence: 0.4 weight
    - oob_callback: 0.8 (positive) / 0.0 (negative)
    
    Thresholds:
    - confirmed: >= 0.85
    - likely: >= 0.70
    - uncertain: >= 0.50 (manual review)
    - unlikely: >= 0.30
    - rejected: < 0.15
    """
    
    def __init__(self):
        self.thresholds = {
            'confirmed': 0.85,
            'likely': 0.70,
            'uncertain': 0.50,
            'unlikely': 0.30,
            'rejected': 0.15
        }
    
    def calculate_confidence(
        self,
        finding: Dict[str, Any],
        rule_validation: Dict[str, Any] = None,
        ml_prediction: Dict[str, Any] = None,
        behavioral_analysis: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Calculate overall confidence score for a finding.
        
        Args:
            finding: Finding dictionary
            rule_validation: Results from rule-based validation
            ml_prediction: Results from ML prediction
            behavioral_analysis: Results from behavioral analysis
            
        Returns:
            Dictionary with confidence score and classification
        """
        scores = []
        factors = {}
        
        # Factor 1: Payload Reflection
        reflection_score = self._score_reflection(finding)
        scores.append(reflection_score)
        factors['payload_reflection'] = reflection_score
        
        # Factor 2: Context Break
        context_score = self._score_context_break(finding)
        scores.append(context_score)
        factors['context_break'] = context_score
        
        # Factor 3: Execution Proof
        execution_score = self._score_execution_proof(finding)
        scores.append(execution_score)
        factors['execution_proof'] = execution_score
        
        # Factor 4: Multiple Techniques
        techniques_score = self._score_multiple_techniques(finding)
        scores.append(techniques_score)
        factors['multiple_techniques'] = techniques_score
        
        # Factor 5: Behavioral Anomaly
        behavioral_score = self._score_behavioral_anomaly(finding, behavioral_analysis)
        scores.append(behavioral_score)
        factors['behavioral_anomaly'] = behavioral_score
        
        # Factor 6: ML Confidence (weighted at 0.4)
        ml_score = self._score_ml_confidence(ml_prediction)
        scores.append(ml_score * 0.4)
        factors['ml_confidence'] = ml_score
        
        # Factor 7: OOB Callback
        oob_score = self._score_oob_callback(finding)
        scores.append(oob_score)
        factors['oob_callback'] = oob_score
        
        # Apply rule validation adjustments
        if rule_validation:
            rule_adjustment = rule_validation.get('confidence_adjustment', 0.0)
            scores.append(rule_adjustment)
            factors['rule_validation_adjustment'] = rule_adjustment
        
        # Calculate weighted average
        base_confidence = self._calculate_base_confidence(finding)
        total_score = sum(scores)
        
        # Normalize to 0-1 range
        confidence = max(0.0, min(1.0, base_confidence + total_score))
        
        # Classify based on thresholds
        classification = self._classify_confidence(confidence)
        
        # Determine if manual review needed
        manual_review_needed = self._needs_manual_review(
            confidence, finding, rule_validation
        )
        
        result = {
            'confidence_score': confidence,
            'classification': classification,
            'manual_review_needed': manual_review_needed,
            'factors': factors,
            'total_adjustment': total_score,
            'base_confidence': base_confidence
        }
        
        logger.debug(f"Confidence calculated: {confidence:.3f} ({classification})")
        
        return result
    
    def _calculate_base_confidence(self, finding: Dict[str, Any]) -> float:
        """Calculate base confidence from finding's initial confidence."""
        return finding.get('confidence', 0.5)
    
    def _score_reflection(self, finding: Dict[str, Any]) -> float:
        """
        Score payload reflection.
        +0.3 if reflected, -0.5 if not reflected
        """
        payload = finding.get('payload', '')
        response = finding.get('response', '')
        
        if not payload or not response:
            return -0.5
        
        if payload.lower() in response.lower():
            return 0.3
        else:
            return -0.5
    
    def _score_context_break(self, finding: Dict[str, Any]) -> float:
        """
        Score context break success.
        +0.4 if broke context, -0.3 if not
        """
        proof = finding.get('proof', {})
        context_broken = proof.get('context_break_success', False)
        
        if context_broken:
            return 0.4
        else:
            return -0.3
    
    def _score_execution_proof(self, finding: Dict[str, Any]) -> float:
        """
        Score execution proof.
        +0.9 if execution confirmed, 0.0 otherwise
        """
        proof = finding.get('proof', {})
        
        # Check for various execution proofs
        execution_confirmed = (
            proof.get('execution_confirmed', False) or
            proof.get('browser_execution', False) or
            proof.get('alert_triggered', False)
        )
        
        if execution_confirmed:
            return 0.9
        else:
            return 0.0
    
    def _score_multiple_techniques(self, finding: Dict[str, Any]) -> float:
        """
        Score multiple techniques confirmation.
        +0.3 if multiple techniques, 0.0 otherwise
        """
        proof = finding.get('proof', {})
        techniques = proof.get('techniques_confirmed', [])
        
        if len(techniques) >= 2:
            return 0.3
        else:
            return 0.0
    
    def _score_behavioral_anomaly(
        self,
        finding: Dict[str, Any],
        behavioral_analysis: Dict[str, Any] = None
    ) -> float:
        """
        Score behavioral anomaly.
        +0.2 if significant anomaly, 0.0 otherwise
        """
        if behavioral_analysis:
            anomaly_score = behavioral_analysis.get('anomaly_score', 0.0)
            if anomaly_score > 0.5:  # Significant anomaly
                return 0.2
        
        # Fallback to finding's anomaly score
        anomaly_score = finding.get('anomaly_score', 0.0)
        if anomaly_score > 0.5:
            return 0.2
        
        return 0.0
    
    def _score_ml_confidence(self, ml_prediction: Dict[str, Any] = None) -> float:
        """
        Score ML confidence.
        Weight: 0.4 (will be applied externally)
        """
        if not ml_prediction:
            return 0.5  # Neutral
        
        # ML score represents confidence that it's a real vulnerability
        ml_score = ml_prediction.get('ml_score', 0.5)
        
        return ml_score
    
    def _score_oob_callback(self, finding: Dict[str, Any]) -> float:
        """
        Score out-of-band callback.
        +0.8 if callback received, 0.0 otherwise
        """
        proof = finding.get('proof', {})
        
        if proof.get('callback_received', False):
            return 0.8
        else:
            return 0.0
    
    def _classify_confidence(self, confidence: float) -> str:
        """
        Classify confidence score into categories.
        
        Args:
            confidence: Confidence score (0-1)
            
        Returns:
            Classification string
        """
        if confidence >= self.thresholds['confirmed']:
            return 'confirmed'
        elif confidence >= self.thresholds['likely']:
            return 'likely'
        elif confidence >= self.thresholds['uncertain']:
            return 'uncertain'
        elif confidence >= self.thresholds['unlikely']:
            return 'unlikely'
        else:
            return 'rejected'
    
    def _needs_manual_review(
        self,
        confidence: float,
        finding: Dict[str, Any],
        rule_validation: Dict[str, Any] = None
    ) -> bool:
        """
        Determine if finding needs manual review.
        
        Criteria:
        - confidence < 0.7
        - high severity
        - new vulnerability type
        - unusual context
        """
        # Low confidence
        if confidence < 0.7:
            return True
        
        # High severity with moderate confidence
        severity = finding.get('severity', '').lower()
        if severity in ['critical', 'high'] and confidence < 0.85:
            return True
        
        # Rule validation failed multiple checks
        if rule_validation:
            checks_failed = rule_validation.get('checks_failed', [])
            if len(checks_failed) >= 3:
                return True
        
        # New or unusual vulnerability type
        vuln_type = finding.get('vulnerability_type', '').lower()
        unusual_types = ['deserialization', 'xxe', 'ssti']
        if vuln_type in unusual_types and confidence < 0.9:
            return True
        
        return False
    
    def get_confidence_explanation(self, result: Dict[str, Any]) -> str:
        """
        Generate human-readable explanation of confidence score.
        
        Args:
            result: Confidence calculation result
            
        Returns:
            Explanation string
        """
        confidence = result['confidence_score']
        classification = result['classification']
        factors = result['factors']
        
        explanation = f"Confidence: {confidence:.2%} ({classification})\n\n"
        explanation += "Contributing factors:\n"
        
        for factor, score in factors.items():
            if score != 0:
                sign = '+' if score > 0 else ''
                explanation += f"  - {factor}: {sign}{score:.2f}\n"
        
        if result['manual_review_needed']:
            explanation += "\n⚠️  Manual review recommended"
        
        return explanation
