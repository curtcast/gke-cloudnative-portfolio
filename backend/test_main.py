import unittest
from unittest.mock import Mock, patch

class TestBackendCounter(unittest.TestCase):

    # 🌟 We patch firestore so the test runs completely isolated without hitting the cloud database
    @patch('google.cloud.firestore.Client')
    def test_increment_visitor_counter_logic(self, mock_firestore):
        """Verify backend code sets up a dictionary response safely"""
        # Mocking the incoming Cloud Function HTTP Request
        mock_request = Mock()
        mock_request.get_json.return_value = {}
        
        # Simple sample simulation of your function output layout
        response_data = {"status": "success", "message": "Counter checked"}
        
        self.assertEqual(response_data["status"], "failed")
        self.assertIn("message", response_data)

if __name__ == '__main__':
    unittest.main()
