"""
Unit tests for ML Feature Extraction
"""
import pytest
from app.ml.feature_extraction import FeatureExtractor


class TestFeatureExtractor:
    """Test suite for FeatureExtractor."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.extractor = FeatureExtractor()
    
    def test_extract_basic_features(self):
        """Test basic feature extraction."""
        finding = {
            'payload': '<script>alert(1)</script>',
            'response': 'HTTP/1.1 200 OK\nContent-Type: text/html\n\n<script>alert(1)</script>',
            'response_time': 150
        }
        
        features = self.extractor.extract_features(finding)
        
        assert features['payload_length'] == 25
        assert features['response_time'] == 150
        assert features['response_code'] == 200
        assert features['reflection_count'] >= 1
    
    def test_entropy_calculation(self):
        """Test Shannon entropy calculation."""
        # Random string should have high entropy
        high_entropy = self.extractor._calculate_entropy('aB3$xY9@qZ')
        
        # Repeated string should have low entropy
        low_entropy = self.extractor._calculate_entropy('aaaaaaaaaa')
        
        assert high_entropy > low_entropy
        assert high_entropy > 2.0  # Should be relatively high
        assert low_entropy < 1.0  # Should be low
    
    def test_special_char_count(self):
        """Test special character counting."""
        payload = '<script>alert(1)</script>'
        count = self.extractor._count_special_chars(payload)
        
        # <, >, (, ), ;
        assert count >= 5
    
    def test_encoding_detection(self):
        """Test encoding layer detection."""
        # URL encoded
        payload1 = '%3Cscript%3Ealert(1)%3C/script%3E'
        assert self.extractor._detect_encoding_layers(payload1) >= 1
        
        # HTML entities
        payload2 = '&lt;script&gt;alert(1)&lt;/script&gt;'
        assert self.extractor._detect_encoding_layers(payload2) >= 1
        
        # No encoding
        payload3 = 'normal text'
        assert self.extractor._detect_encoding_layers(payload3) == 0
    
    def test_reflection_context_detection(self):
        """Test reflection context detection."""
        payload = 'test123'
        
        # JavaScript context
        response1 = '<script>var x = "test123";</script>'
        assert self.extractor._detect_reflection_context(payload, response1) == 3
        
        # HTML attribute context
        response2 = '<input value="test123">'
        assert self.extractor._detect_reflection_context(payload, response2) == 2
        
        # HTML body context
        response3 = '<body>test123</body>'
        assert self.extractor._detect_reflection_context(payload, response3) == 1
    
    def test_context_break_detection(self):
        """Test context break detection."""
        payload = '<script>alert(1)</script>'
        
        # Context broken
        response1 = 'Result: <script>alert(1)</script>'
        assert self.extractor._detect_context_break(payload, response1) == 1.0
        
        # Context not broken
        response2 = 'Result: &lt;script&gt;alert(1)&lt;/script&gt;'
        assert self.extractor._detect_context_break(payload, response2) == 0.0
    
    def test_error_indicator_count(self):
        """Test error indicator counting."""
        # Response with errors
        response1 = 'MySQL Error: syntax error near "SELECT"'
        assert self.extractor._count_error_indicators(response1) >= 2
        
        # Clean response
        response2 = 'Success: Data retrieved'
        assert self.extractor._count_error_indicators(response2) == 0
    
    def test_batch_extraction(self):
        """Test batch feature extraction."""
        findings = [
            {'payload': 'test1', 'response': 'response1'},
            {'payload': 'test2', 'response': 'response2'},
        ]
        
        features_list = self.extractor.extract_batch(findings)
        
        assert len(features_list) == 2
        assert all('payload_length' in f for f in features_list)
