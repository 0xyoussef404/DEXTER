"""
ML Classifier (Layer 4) - Random Forest with Ensemble

Implements machine learning classification for false positive detection.
"""
import os
import pickle
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import precision_score, recall_score, f1_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from app.core.logging import logger
from app.ml.feature_extraction import FeatureExtractor


class MLClassifier:
    """
    Machine Learning classifier for false positive detection.
    
    Uses Random Forest with ensemble voting.
    Features: 13 features from feature_extraction.py
    Threshold: 0.80 confidence
    """
    
    def __init__(self, model_path: str = None):
        """
        Initialize ML classifier.
        
        Args:
            model_path: Path to saved model file
        """
        self.model_path = model_path or "app/ml/models/trained_models/rf_classifier.pkl"
        self.feature_extractor = FeatureExtractor()
        self.model = None
        self.ensemble_models = []
        self.ensemble_weights = [0.4, 0.4, 0.2]  # Weights for ensemble voting
        self.confidence_threshold = 0.80
        self.feature_names = [
            'payload_length', 'payload_entropy', 'special_char_count',
            'encoding_layers', 'response_time', 'response_size',
            'response_code', 'header_count', 'reflection_count',
            'reflection_context', 'context_break_success',
            'error_indicator_count', 'anomaly_score'
        ]
        
        # Load model if exists
        if os.path.exists(self.model_path):
            self.load_model()
        elif SKLEARN_AVAILABLE:
            self._initialize_default_model()
    
    def _initialize_default_model(self):
        """Initialize default Random Forest model."""
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn not available, ML classification disabled")
            return
        
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        logger.info("Initialized default Random Forest model")
    
    def predict(self, finding: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict if finding is a false positive.
        
        Args:
            finding: Dictionary containing finding data
            
        Returns:
            Dictionary with prediction results
        """
        if not SKLEARN_AVAILABLE or self.model is None:
            return {
                'is_false_positive': False,
                'confidence': 0.5,
                'ml_score': 0.5,
                'note': 'ML classifier not available'
            }
        
        # Extract features
        features = self.feature_extractor.extract_features(finding)
        feature_vector = self._features_to_vector(features)
        
        # Make prediction
        try:
            # Get probability estimates
            probabilities = self.model.predict_proba([feature_vector])[0]
            
            # probabilities[0] = probability of True Positive (class 0)
            # probabilities[1] = probability of False Positive (class 1)
            confidence_true_positive = probabilities[0]
            confidence_false_positive = probabilities[1]
            
            # Ensemble prediction if multiple models available
            if self.ensemble_models:
                ensemble_confidence = self._ensemble_predict(feature_vector)
                confidence_true_positive = ensemble_confidence
                confidence_false_positive = 1 - ensemble_confidence
            
            is_false_positive = confidence_false_positive > 0.5
            
            return {
                'is_false_positive': is_false_positive,
                'confidence': max(confidence_true_positive, confidence_false_positive),
                'ml_score': confidence_true_positive,  # Confidence that it's a real vulnerability
                'false_positive_probability': confidence_false_positive,
                'feature_importance': self._get_feature_importance(features)
            }
        
        except Exception as e:
            logger.error(f"ML prediction failed: {e}")
            return {
                'is_false_positive': False,
                'confidence': 0.5,
                'ml_score': 0.5,
                'note': f'Prediction error: {str(e)}'
            }
    
    def _features_to_vector(self, features: Dict[str, float]) -> np.ndarray:
        """Convert feature dictionary to numpy array."""
        return np.array([features.get(name, 0.0) for name in self.feature_names])
    
    def _ensemble_predict(self, feature_vector: np.ndarray) -> float:
        """
        Ensemble prediction using weighted voting.
        
        Args:
            feature_vector: Feature vector
            
        Returns:
            Weighted ensemble confidence score
        """
        if not self.ensemble_models:
            return 0.5
        
        predictions = []
        for model in self.ensemble_models:
            try:
                prob = model.predict_proba([feature_vector])[0][0]  # Probability of True Positive
                predictions.append(prob)
            except:
                predictions.append(0.5)
        
        # Weighted average
        ensemble_score = sum(p * w for p, w in zip(predictions, self.ensemble_weights[:len(predictions)]))
        ensemble_score /= sum(self.ensemble_weights[:len(predictions)])
        
        return ensemble_score
    
    def _get_feature_importance(self, features: Dict[str, float]) -> Dict[str, float]:
        """Get feature importance scores."""
        if not SKLEARN_AVAILABLE or self.model is None:
            return {}
        
        try:
            if hasattr(self.model, 'feature_importances_'):
                importances = self.model.feature_importances_
                return {
                    name: float(importance)
                    for name, importance in zip(self.feature_names, importances)
                }
        except:
            pass
        
        return {}
    
    def train(self, training_data: List[Dict[str, Any]], labels: List[int]) -> Dict[str, float]:
        """
        Train the ML model.
        
        Args:
            training_data: List of finding dictionaries
            labels: List of labels (0 = True Positive, 1 = False Positive)
            
        Returns:
            Dictionary with training metrics
        """
        if not SKLEARN_AVAILABLE:
            logger.error("scikit-learn not available, cannot train model")
            return {}
        
        # Extract features
        features_list = self.feature_extractor.extract_batch(training_data)
        X = np.array([self._features_to_vector(f) for f in features_list])
        y = np.array(labels)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train main model
        if self.model is None:
            self._initialize_default_model()
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        
        metrics = {
            'precision': precision_score(y_test, y_pred, average='binary'),
            'recall': recall_score(y_test, y_pred, average='binary'),
            'f1_score': f1_score(y_test, y_pred, average='binary'),
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Model trained: Precision={metrics['precision']:.3f}, "
                   f"Recall={metrics['recall']:.3f}, F1={metrics['f1_score']:.3f}")
        
        return metrics
    
    def save_model(self, path: str = None):
        """Save model to disk."""
        save_path = path or self.model_path
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'ensemble_models': self.ensemble_models,
            'ensemble_weights': self.ensemble_weights,
            'feature_names': self.feature_names,
            'confidence_threshold': self.confidence_threshold,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(save_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Model saved to {save_path}")
    
    def load_model(self, path: str = None):
        """Load model from disk."""
        load_path = path or self.model_path
        
        if not os.path.exists(load_path):
            logger.warning(f"Model file not found: {load_path}")
            return False
        
        try:
            with open(load_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data.get('model')
            self.ensemble_models = model_data.get('ensemble_models', [])
            self.ensemble_weights = model_data.get('ensemble_weights', [0.4, 0.4, 0.2])
            self.feature_names = model_data.get('feature_names', self.feature_names)
            self.confidence_threshold = model_data.get('confidence_threshold', 0.80)
            
            logger.info(f"Model loaded from {load_path}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def add_feedback(self, finding: Dict[str, Any], correct_label: int):
        """
        Add feedback for continuous learning.
        
        Args:
            finding: Finding dictionary
            correct_label: Correct label (0 = TP, 1 = FP)
        """
        # TODO: Implement incremental learning or store for batch retraining
        logger.info(f"Feedback received: {finding.get('id')} -> {correct_label}")
