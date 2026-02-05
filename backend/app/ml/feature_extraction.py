"""
Feature Extraction for ML-based False Positive Detection

Extracts 13+ features from vulnerability findings for ML classification.
"""
import re
import math
from typing import Dict, Any, List
from collections import Counter


class FeatureExtractor:
    """
    Extract features from vulnerability findings for ML classification.
    
    Features extracted:
    1. payload_length - Length of the payload
    2. payload_entropy - Shannon entropy of payload
    3. special_char_count - Count of special characters
    4. encoding_layers - Number of encoding layers detected
    5. response_time - Response time in milliseconds
    6. response_size - Size of response in bytes
    7. response_code - HTTP status code
    8. header_count - Number of HTTP headers
    9. reflection_count - Number of times payload is reflected
    10. reflection_context - Type of context where reflected
    11. context_break_success - Boolean: successfully broke context
    12. error_indicator_count - Count of error indicators in response
    13. anomaly_score - Behavioral anomaly score
    """
    
    def __init__(self):
        self.special_chars = set('!@#$%^&*()_+-=[]{}|;:\'",.<>?/\\`~')
        self.error_indicators = [
            'error', 'exception', 'warning', 'fatal', 'syntax',
            'unexpected', 'invalid', 'denied', 'forbidden',
            'stack trace', 'traceback', 'mysql', 'postgresql',
            'oracle', 'sql syntax', 'sqlite', 'odbc'
        ]
    
    def extract_features(self, finding: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract all features from a finding.
        
        Args:
            finding: Dictionary containing finding data
            
        Returns:
            Dictionary of extracted features
        """
        payload = finding.get('payload', '')
        response = finding.get('response', '')
        request = finding.get('request', '')
        
        features = {
            'payload_length': self._get_payload_length(payload),
            'payload_entropy': self._calculate_entropy(payload),
            'special_char_count': self._count_special_chars(payload),
            'encoding_layers': self._detect_encoding_layers(payload),
            'response_time': finding.get('response_time', 0),
            'response_size': len(response) if response else 0,
            'response_code': self._extract_status_code(response),
            'header_count': self._count_headers(response),
            'reflection_count': self._count_reflections(payload, response),
            'reflection_context': self._detect_reflection_context(payload, response),
            'context_break_success': self._detect_context_break(payload, response),
            'error_indicator_count': self._count_error_indicators(response),
            'anomaly_score': finding.get('anomaly_score', 0.0)
        }
        
        return features
    
    def _get_payload_length(self, payload: str) -> int:
        """Get length of payload."""
        return len(payload) if payload else 0
    
    def _calculate_entropy(self, text: str) -> float:
        """
        Calculate Shannon entropy of text.
        Higher entropy = more random/complex.
        """
        if not text:
            return 0.0
        
        # Count character frequencies
        counter = Counter(text)
        length = len(text)
        
        # Calculate entropy
        entropy = 0.0
        for count in counter.values():
            probability = count / length
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _count_special_chars(self, text: str) -> int:
        """Count special characters in text."""
        if not text:
            return 0
        return sum(1 for char in text if char in self.special_chars)
    
    def _detect_encoding_layers(self, payload: str) -> int:
        """
        Detect number of encoding layers.
        Common encodings: URL encoding, HTML entities, Base64, Unicode
        """
        if not payload:
            return 0
        
        layers = 0
        
        # URL encoding (%XX)
        if re.search(r'%[0-9A-Fa-f]{2}', payload):
            layers += 1
        
        # HTML entities (&#XXX; or &name;)
        if re.search(r'&#?\w+;', payload):
            layers += 1
        
        # Base64-like patterns
        if re.search(r'[A-Za-z0-9+/]{20,}={0,2}', payload):
            layers += 1
        
        # Unicode escaping (\uXXXX)
        if re.search(r'\\u[0-9A-Fa-f]{4}', payload):
            layers += 1
        
        # Double encoding detection
        if '%%' in payload or '&#' in payload.replace('&#', '', 1):
            layers += 1
        
        return layers
    
    def _extract_status_code(self, response: str) -> int:
        """Extract HTTP status code from response."""
        if not response:
            return 0
        
        # Try to find HTTP status code in first line
        match = re.search(r'HTTP/\d\.\d\s+(\d{3})', response[:200])
        if match:
            return int(match.group(1))
        
        return 0
    
    def _count_headers(self, response: str) -> int:
        """Count HTTP headers in response."""
        if not response:
            return 0
        
        # Split response and count headers (before empty line)
        lines = response.split('\n')
        header_count = 0
        
        for line in lines[1:]:  # Skip status line
            if line.strip() == '':
                break
            if ':' in line:
                header_count += 1
        
        return header_count
    
    def _count_reflections(self, payload: str, response: str) -> int:
        """
        Count how many times the payload is reflected in response.
        """
        if not payload or not response:
            return 0
        
        # Count exact reflections
        count = response.lower().count(payload.lower())
        
        # Also check for partial reflections (significant substrings)
        if len(payload) > 10:
            # Check for 80% of payload
            threshold = int(len(payload) * 0.8)
            for i in range(len(payload) - threshold + 1):
                substring = payload[i:i+threshold]
                if substring.lower() in response.lower():
                    count += 0.5  # Partial match
        
        return int(count)
    
    def _detect_reflection_context(self, payload: str, response: str) -> int:
        """
        Detect the context where payload is reflected.
        Returns enum: 0=none, 1=HTML body, 2=HTML attribute, 3=JavaScript, 4=CSS, 5=URL
        """
        if not payload or not response:
            return 0
        
        # Find payload in response
        payload_lower = payload.lower()
        response_lower = response.lower()
        
        if payload_lower not in response_lower:
            return 0
        
        # Find position of payload
        pos = response_lower.find(payload_lower)
        
        # Check context around payload
        before = response_lower[max(0, pos-100):pos]
        after = response_lower[pos+len(payload):min(len(response_lower), pos+len(payload)+100)]
        
        # JavaScript context
        if '<script' in before or 'javascript:' in before or '</script>' in after:
            return 3
        
        # HTML attribute context
        if '="' in before[-5:] or "='" in before[-5:]:
            return 2
        
        # CSS context
        if '<style' in before or '</style>' in after:
            return 4
        
        # URL context
        if 'href=' in before[-10:] or 'src=' in before[-10:]:
            return 5
        
        # Default: HTML body
        return 1
    
    def _detect_context_break(self, payload: str, response: str) -> float:
        """
        Detect if payload successfully broke out of context.
        Returns 1.0 if context broken, 0.0 otherwise.
        """
        if not payload or not response:
            return 0.0
        
        # XSS context break indicators
        xss_breaks = [
            '<script', '</script>', 'javascript:', 'onerror=',
            'onload=', 'onclick=', 'onfocus=', 'onmouseover='
        ]
        
        # SQL context break indicators
        sql_breaks = [
            "' or", '" or', "' and", '" and', "' union", '" union',
            '--', '/*', '*/', 'sleep(', 'waitfor delay'
        ]
        
        # Check if any break patterns are in response
        response_lower = response.lower()
        payload_lower = payload.lower()
        
        for pattern in xss_breaks + sql_breaks:
            if pattern in payload_lower and pattern in response_lower:
                return 1.0
        
        return 0.0
    
    def _count_error_indicators(self, response: str) -> int:
        """
        Count error indicators in response.
        """
        if not response:
            return 0
        
        response_lower = response.lower()
        count = 0
        
        for indicator in self.error_indicators:
            if indicator in response_lower:
                count += 1
        
        return count
    
    def extract_batch(self, findings: List[Dict[str, Any]]) -> List[Dict[str, float]]:
        """
        Extract features from multiple findings.
        
        Args:
            findings: List of finding dictionaries
            
        Returns:
            List of feature dictionaries
        """
        return [self.extract_features(finding) for finding in findings]
