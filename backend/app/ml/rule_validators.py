"""
Rule-Based Validators (Layer 1)

Implements strict rule-based validation for different vulnerability types.
"""
import re
import statistics
from typing import Dict, Any, List, Optional
try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


class RuleBasedValidator:
    """
    Layer 1: Rule-based validation for vulnerability findings.
    
    Validates findings based on strict rules specific to each vulnerability type.
    """
    
    def __init__(self):
        self.xss_validator = XSSRuleValidator()
        self.sqli_validator = SQLiRuleValidator()
        self.ssrf_validator = SSRFRuleValidator()
        self.generic_validator = GenericRuleValidator()
    
    def validate(self, finding: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a finding using rule-based checks.
        
        Args:
            finding: Dictionary containing finding data
            
        Returns:
            Dictionary with validation results and confidence adjustment
        """
        vuln_type = finding.get('vulnerability_type', '').lower()
        
        if vuln_type == 'xss':
            return self.xss_validator.validate(finding)
        elif vuln_type in ['sqli', 'sql_injection']:
            return self.sqli_validator.validate(finding)
        elif vuln_type == 'ssrf':
            return self.ssrf_validator.validate(finding)
        else:
            return self.generic_validator.validate(finding)


class XSSRuleValidator:
    """
    XSS-specific rule-based validator.
    
    Requirements:
    - Must be reflected in response
    - Must break out of context
    - Must execute in browser (verified via headless browser)
    - Must check if WAF blocked
    - Must verify DOM state
    """
    
    def validate(self, finding: Dict[str, Any]) -> Dict[str, Any]:
        """Validate XSS finding."""
        result = {
            'valid': False,
            'confidence_adjustment': 0.0,
            'checks_passed': [],
            'checks_failed': [],
            'notes': []
        }
        
        payload = finding.get('payload', '')
        response = finding.get('response', '')
        proof = finding.get('proof', {})
        
        # Check 1: Payload must be reflected
        if self._is_reflected(payload, response):
            result['checks_passed'].append('payload_reflected')
            result['confidence_adjustment'] += 0.3
        else:
            result['checks_failed'].append('payload_not_reflected')
            result['confidence_adjustment'] -= 0.5
            result['notes'].append('Payload not reflected in response')
            return result
        
        # Check 2: Must break context
        if self._breaks_context(payload, response):
            result['checks_passed'].append('context_break')
            result['confidence_adjustment'] += 0.4
        else:
            result['checks_failed'].append('no_context_break')
            result['confidence_adjustment'] -= 0.3
            result['notes'].append('Payload did not break out of context')
        
        # Check 3: Must execute in browser
        if proof.get('execution_confirmed'):
            result['checks_passed'].append('browser_execution')
            result['confidence_adjustment'] += 0.9
        else:
            result['checks_failed'].append('no_browser_execution')
            result['notes'].append('No browser execution proof')
        
        # Check 4: Check if WAF blocked
        if self._waf_blocked(response):
            result['checks_failed'].append('waf_blocked')
            result['confidence_adjustment'] -= 0.8
            result['notes'].append('WAF appears to have blocked the request')
            return result
        else:
            result['checks_passed'].append('waf_not_blocking')
        
        # Check 5: DOM verification
        if proof.get('dom_verified'):
            result['checks_passed'].append('dom_verified')
            result['confidence_adjustment'] += 0.2
        
        # Final validation
        result['valid'] = len(result['checks_passed']) >= 3
        
        return result
    
    def _is_reflected(self, payload: str, response: str) -> bool:
        """Check if payload is reflected in response."""
        if not payload or not response:
            return False
        return payload.lower() in response.lower()
    
    def _breaks_context(self, payload: str, response: str) -> bool:
        """Check if payload breaks out of its context."""
        break_patterns = [
            r'<script[^>]*>',
            r'</script>',
            r'javascript:',
            r'on\w+\s*=',  # Event handlers
            r'<img[^>]*>',
            r'<svg[^>]*>'
        ]
        
        for pattern in break_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                return True
        return False
    
    def _waf_blocked(self, response: str) -> bool:
        """Detect if WAF blocked the request."""
        waf_indicators = [
            'blocked by',
            'security policy',
            'forbidden',
            'access denied',
            'cloudflare',
            'incapsula',
            'imperva',
            'akamai',
            'f5',
            'mod_security'
        ]
        
        response_lower = response.lower()
        return any(indicator in response_lower for indicator in waf_indicators)


class SQLiRuleValidator:
    """
    SQL Injection rule-based validator.
    
    Requirements:
    - Timing threshold: 5 seconds
    - Statistical confidence: 0.95
    - Multiple technique confirmation (at least 2)
    """
    
    def validate(self, finding: Dict[str, Any]) -> Dict[str, Any]:
        """Validate SQLi finding."""
        result = {
            'valid': False,
            'confidence_adjustment': 0.0,
            'checks_passed': [],
            'checks_failed': [],
            'notes': []
        }
        
        proof = finding.get('proof', {})
        timing_data = proof.get('timing_data', [])
        techniques = proof.get('techniques_confirmed', [])
        
        # Check 1: Timing threshold (for time-based blind)
        if timing_data:
            avg_delay = statistics.mean(timing_data) if timing_data else 0
            if avg_delay >= 5.0:
                result['checks_passed'].append('timing_threshold')
                result['confidence_adjustment'] += 0.4
                
                # Check 2: Statistical confidence
                if self._check_statistical_confidence(timing_data):
                    result['checks_passed'].append('statistical_confidence')
                    result['confidence_adjustment'] += 0.3
                else:
                    result['checks_failed'].append('low_statistical_confidence')
                    result['notes'].append('Timing variance too high for confidence')
            else:
                result['checks_failed'].append('timing_below_threshold')
                result['notes'].append(f'Average delay {avg_delay}s < 5s threshold')
        
        # Check 3: Multiple technique confirmation
        if len(techniques) >= 2:
            result['checks_passed'].append('multiple_techniques')
            result['confidence_adjustment'] += 0.3
        else:
            result['checks_failed'].append('single_technique_only')
            result['notes'].append('Only one SQLi technique confirmed')
        
        # Check 4: Error-based confirmation
        if 'error_based' in techniques:
            result['checks_passed'].append('error_based_confirmed')
            result['confidence_adjustment'] += 0.4
        
        # Check 5: Database extraction proof
        if proof.get('database_version') or proof.get('data_extracted'):
            result['checks_passed'].append('data_extraction')
            result['confidence_adjustment'] += 0.5
        
        result['valid'] = len(result['checks_passed']) >= 2
        
        return result
    
    def _check_statistical_confidence(self, timing_data: List[float]) -> bool:
        """
        Check if timing data has statistical confidence of 0.95.
        Uses t-test to verify timing anomaly.
        """
        if len(timing_data) < 3:
            return False
        
        # Assume baseline of normal response time (< 1 second)
        baseline_mean = 0.5
        
        # Perform one-sample t-test
        sample_mean = statistics.mean(timing_data)
        
        if sample_mean < 2.0:  # Not significantly delayed
            return False
        
        # Calculate t-statistic if scipy is available
        if SCIPY_AVAILABLE:
            try:
                t_stat, p_value = stats.ttest_1samp(timing_data, baseline_mean)
                
                # Check if p-value indicates significance at 0.95 confidence (0.05 alpha)
                return p_value < 0.05 and sample_mean > baseline_mean
            except:
                pass
        
        # Fallback: simple threshold check
        # Check if all samples are significantly above baseline
        return all(t > baseline_mean * 2 for t in timing_data)


class SSRFRuleValidator:
    """
    SSRF rule-based validator.
    
    Requirements:
    - Callback must be received (DNS or HTTP)
    - Timing analysis for blind SSRF
    """
    
    def validate(self, finding: Dict[str, Any]) -> Dict[str, Any]:
        """Validate SSRF finding."""
        result = {
            'valid': False,
            'confidence_adjustment': 0.0,
            'checks_passed': [],
            'checks_failed': [],
            'notes': []
        }
        
        proof = finding.get('proof', {})
        
        # Check 1: Callback received
        if proof.get('callback_received'):
            result['checks_passed'].append('callback_received')
            result['confidence_adjustment'] += 1.0
            
            # Additional: Callback type
            callback_type = proof.get('callback_type', '')
            if callback_type == 'http':
                result['confidence_adjustment'] += 0.1
                result['notes'].append('HTTP callback received')
            elif callback_type == 'dns':
                result['confidence_adjustment'] += 0.05
                result['notes'].append('DNS callback received')
        else:
            result['checks_failed'].append('no_callback')
            result['confidence_adjustment'] -= 0.5
            result['notes'].append('No OOB callback received')
        
        # Check 2: Timing analysis (for internal service detection)
        timing_diff = proof.get('timing_difference', 0)
        if timing_diff > 2.0:  # Significant timing difference
            result['checks_passed'].append('timing_anomaly')
            result['confidence_adjustment'] += 0.6
        
        # Check 3: Metadata in response
        if proof.get('metadata_in_response'):
            result['checks_passed'].append('metadata_found')
            result['confidence_adjustment'] += 1.0
            result['notes'].append('Cloud metadata found in response')
        
        result['valid'] = len(result['checks_passed']) >= 1
        
        return result


class GenericRuleValidator:
    """
    Generic rule-based validator for other vulnerability types.
    
    Requirements:
    - Payload must affect response
    - Must be reproducible
    - Must not be in baseline
    """
    
    def validate(self, finding: Dict[str, Any]) -> Dict[str, Any]:
        """Validate generic finding."""
        result = {
            'valid': False,
            'confidence_adjustment': 0.0,
            'checks_passed': [],
            'checks_failed': [],
            'notes': []
        }
        
        # Check 1: Payload affects response
        if finding.get('response_affected', False):
            result['checks_passed'].append('response_affected')
            result['confidence_adjustment'] += 0.5
        else:
            result['checks_failed'].append('response_not_affected')
            result['confidence_adjustment'] -= 0.3
        
        # Check 2: Reproducible
        if finding.get('reproducible', False):
            result['checks_passed'].append('reproducible')
            result['confidence_adjustment'] += 0.4
        else:
            result['checks_failed'].append('not_reproducible')
            result['confidence_adjustment'] -= 0.5
        
        # Check 3: Not in baseline
        if not finding.get('in_baseline', False):
            result['checks_passed'].append('not_in_baseline')
            result['confidence_adjustment'] += 0.3
        else:
            result['checks_failed'].append('in_baseline')
            result['confidence_adjustment'] -= 0.7
            result['notes'].append('Similar behavior found in baseline')
        
        result['valid'] = len(result['checks_passed']) >= 2
        
        return result
