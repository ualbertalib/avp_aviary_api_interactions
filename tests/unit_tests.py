"""unittest tests
"""

import json
import sys
import os
import unittest


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aviary import utilities as aviaryUtilities
from aviary import api as aviaryApi


class TestUtilities(unittest.TestCase):

    def test_resource_processing(self):
        with open("tests/assets/resource.json", 'r', encoding="utf-8", newline='') as input_file:
            item = input_file.read()
            tmp = aviaryUtilities.processResourceJSON(item)
            expected = {
                'Resource ID': 9,
                'Resource Title': 'title-9',
                'Custom Unique ID': 'c9',
                'Access': 'public',
                'Is Featured': False,
                'Media File IDs': [1],
                'Media Files Count': 1,
                'Transcripts Count': 0,
                'Indexes Count': 0,
                'Persistent_URL': 'https://example.org/1',
                'Direct URL': 'https://example.org/2',
                'Updated At': '2023-03-26 19:03:37 +0000',
                'Created At': '2023-03-01 20:47:29 +0000',
                'Metadata': ['test']
            }
            self.assertEqual(tmp, expected)


if __name__ == '__main__':
    unittest.main()
