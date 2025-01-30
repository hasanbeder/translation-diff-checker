import unittest
import json
from unittest.mock import patch, mock_open, MagicMock
from src.translation_diff_checker import analyze_translation, compare_multiple_translations

class TestTranslationAnalyzer(unittest.TestCase):
    def setUp(self):
        # Prepare source and target dictionaries for testing
        self.source_dict = {
            "HELLO": "Hello",
            "WELCOME": "Welcome",
            "NESTED": {
                "KEY1": "Nested Key 1"
            }
        }
        
        self.complete_target_dict = {
            "HELLO": "Merhaba",
            "WELCOME": "Hoş geldiniz",
            "NESTED": {
                "KEY1": "İç İçe Anahtar 1"
            }
        }
        
        self.incomplete_target_dict = {
            "HELLO": "Merhaba",
            "NESTED": {
                "KEY1": "İç İçe Anahtar 1"
            }
        }

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_complete_translation(self, mock_json_load, mock_file):
        # Configure mock JSON load
        mock_json_load.side_effect = [self.source_dict, self.complete_target_dict]
        
        # Simulate file paths
        source_file = '/tmp/source.json'
        target_file = '/tmp/target_complete.json'
        
        # Analyze translation
        analysis = analyze_translation(source_file, target_file)
        
        # Assertions
        self.assertEqual(analysis['total_keys'], 3)  # 3 keys
        self.assertEqual(analysis['translated_keys'], 3)
        self.assertEqual(len(analysis['untranslated_keys']), 0)
        self.assertEqual(analysis['completion_percentage'], 100.0)

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_incomplete_translation(self, mock_json_load, mock_file):
        # Configure mock JSON load
        mock_json_load.side_effect = [self.source_dict, self.incomplete_target_dict]
        
        # Simulate file paths
        source_file = '/tmp/source.json'
        target_file = '/tmp/target_incomplete.json'
        
        # Analyze translation
        analysis = analyze_translation(source_file, target_file)
        
        # Assertions
        self.assertEqual(analysis['total_keys'], 3)  # 3 keys
        self.assertEqual(analysis['translated_keys'], 2)
        self.assertEqual(analysis['untranslated_keys'], ['WELCOME'])
        self.assertAlmostEqual(analysis['completion_percentage'], 66.67, places=2)

if __name__ == '__main__':
    unittest.main()
