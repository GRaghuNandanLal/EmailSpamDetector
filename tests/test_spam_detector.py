import unittest
import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.spam_detector import SpamDetector

class TestSpamDetector(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.detector = SpamDetector()
        
    def test_spam_prediction(self):
        """Test spam message detection"""
        # Test known spam messages
        spam_texts = [
            "URGENT! You have won a 1 week FREE membership",
            "FREE entry in 2 a wkly comp to win FA Cup final tkts",
            "Congratulations! You've won a $1000 gift card. Click here to claim"
        ]
        
        for text in spam_texts:
            result = self.detector.predict(text)
            self.assertTrue(result['is_spam'], f"Failed to detect spam: {text}")
            self.assertGreater(result['confidence'], 50, 
                             "Confidence should be greater than 50% for spam")
    
    def test_ham_prediction(self):
        """Test legitimate (ham) message detection"""
        # Test known ham messages
        ham_texts = [
            "Hi, when will you be home for dinner?",
            "The meeting is scheduled for 3 PM tomorrow",
            "Thanks for sending the documents yesterday"
        ]
        
        for text in ham_texts:
            result = self.detector.predict(text)
            self.assertFalse(result['is_spam'], f"Incorrectly flagged as spam: {text}")
            self.assertGreater(result['confidence'], 50, 
                             "Confidence should be greater than 50% for ham")
    
    def test_empty_input(self):
        """Test handling of empty input"""
        with self.assertRaises(ValueError):
            self.detector.predict("")
    
    def test_prediction_format(self):
        """Test the format of prediction results"""
        text = "Sample text for testing"
        result = self.detector.predict(text)
        
        # Check if result contains all required keys
        self.assertIn('is_spam', result)
        self.assertIn('confidence', result)
        self.assertIn('prediction', result)
        
        # Check types of returned values
        self.assertIsInstance(result['is_spam'], bool)
        self.assertIsInstance(result['confidence'], float)
        self.assertIsInstance(result['prediction'], str)
        
        # Check confidence range
        self.assertGreaterEqual(result['confidence'], 0)
        self.assertLessEqual(result['confidence'], 100)
    
    def test_special_characters(self):
        """Test handling of special characters"""
        text = "!@#$%^&*()_+ Special chars test"
        try:
            result = self.detector.predict(text)
            self.assertIn('is_spam', result)
        except Exception as e:
            self.fail(f"Failed to handle special characters: {e}")
    
    def test_long_text(self):
        """Test handling of long text"""
        long_text = "This is a test " * 1000  # Create a very long text
        try:
            result = self.detector.predict(long_text)
            self.assertIn('is_spam', result)
        except Exception as e:
            self.fail(f"Failed to handle long text: {e}")

if __name__ == '__main__':
    unittest.main() 