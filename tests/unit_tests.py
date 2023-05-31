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

        self.maxDiff = None

        with open("tests/assets/resource.json", 'r', encoding="utf-8", newline='') as input_file:
            item = input_file.read()
            tmp = aviaryUtilities.processResourceJSON(item, 'testz')
            expected = {
                'Resource ID': 9,
                'Collection title': 'testz',
                'Resource title': 'title-9',
                'Custom unique ID': 'c9',
                'Access': 'public',
                'Is featured': False,
                'Media file IDs': [1, 2, 3, 4],
                'Media files count': 4,
                'Transcripts count': 0,
                'Indexes count': 0,
                'Persistent URL': 'https://example.org/1',
                'Direct URL': 'https://example.org/2',
                'Updated at': '2023-03-26 19:03:37 +0000',
                'Created at': '2023-03-01 20:47:29 +0000',
                'Metadata': ['test']
            }
            self.assertEqual(tmp, expected)

    def test_media_processing(self):

        self.maxDiff = None

        with open("tests/assets/media.json", 'r', encoding="utf-8", newline='') as input_file:
            item = input_file.read()
            tmp = aviaryUtilities.processMediaJSON(item, 'testz', 'cui', 'lrid', 'lrt')
            expected = {
                'Media ID': 1,
                'Collection title': 'testz',
                'Collection resource ID': 2,
                'Linked resource ID': 'lrid',
                'Linked resource title': 'lrt',
                'Custom unique resource ID': 'cui',
                'Display name': '03.mp3',
                'File name': '',
                'Duration': '00:15:34.791',
                'Access': 'True',
                'Is 360': 'False',
                'Is downloadable': 'False',
                'Sequence No': 1,
                'Transcripts': [{'id': 38337, 'title': 'YouTube en', 'language': 'en', 'is_caption': 'False', 'is_public': 'False', 'has_annotation_set': 'False'}],
                'Indexes': [],
                'Updated At': '2023-04-19T15:28:39.000+00:00',
                'Created At': '2023-04-19T15:27:14.000+00:00',
                'Metadata': [],
                'Thumbnail url': 'https://cloudfront.net/collection_resource_files/thumbnails/000/0.jpg?8',
                'Turn on cc': 'False',
                'Downloadable duration': '',
                'Download enabled for': '',
                'Media download url': '',
                'Media embed url': 'https://example.com',
                'Media embed type': '',
                'Media embed code': '',
                'Transcode url': ''
            }
            self.assertEqual(tmp, expected)

    def test_transcript_processing(self):

        self.maxDiff = None

        with open("tests/assets/transcript.json", 'r', encoding="utf-8", newline='') as input_file:
            item = input_file.read()
            tmp = aviaryUtilities.processTranscriptJSON(item, {
                'Collection title': 'c1',
                'Linked resource title': 'lrt',
                'Linked resource ID': 'lrid',
                "media_file_id": "7",
                "custom_unique_identifier": "8",
                "has_annotation_set": "True"
            })
            expected = {
                'Transcript ID': 3,
                'Collection title': 'c1',
                'Linked resource title': "lrt",
                'Linked resource ID': "lrid",
                'Custom unique resource ID': '8',
                'Resource file ID': 1,
                'Media ID': '7',
                'Is caption': True,
                'Is public': True,
                'Title': '1.srt',
                'Language': 'en',
                'Description': 'Avalon SRT Caption',
                'Is downloadable': 'Yes',
                'Has annotation set': 'True'
            }
            self.assertEqual(tmp, expected)

    def test_supplemental_file_processing(self):

        self.maxDiff = None

        with open("tests/assets/supplemental_file.json", 'r', encoding="utf-8", newline='') as input_file:
            item = input_file.read()
            tmp = aviaryUtilities.processSupplementalFilesJSON(item)
            expected = {
                'Supplemental files ID': 1,
                'Collection resource ID': 6,
                'Title': 'Time',
                'Description': '2020.',
                'Access': 'public',
                'Status': 'True',
                'Sort order': '',
                'Associated file name': 'd.pdf',
                'Associated file content type': 'application/pdf',
                'File': 'https://s3.com/',
                'Created at': '2022-02-07T17:12:19.000+00:00',
                'Updated at': '2022-10-27T16:16:24.000+00:00'
            }
            self.assertEqual(tmp, expected)


if __name__ == '__main__':
    unittest.main()
