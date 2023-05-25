"""
aviary.utilities
~~~~~~~~~~

This module implements some cenvenience utilites.

"""

import json


def processResourceJSON(item):

    item_json = json.loads(item)
    return {
        # "Collection ID": collection['id'],
        # "Collection Label": collection['title'],
        "Resource ID" : item_json['data']['id'],
        "Resource Title" : item_json['data']['title'],
        "Custom Unique ID": item_json['data']['custom_unique_identifier'],
        "Access": item_json['data']['access'],
        "Is Featured": item_json['data']['is_featured'],
        "Media File IDs": item_json['data']['media_file_id'],
        "Media Files Count": item_json['data']['media_files_count'],
        "Transcripts Count": item_json['data']['transcripts_count'],
        "Indexes Count": item_json['data']['indexes_count'],
        "Persistent_URL": item_json['data']['persistent_url'],
        "Direct URL": item_json['data']['direct_url'],
        "Updated At": item_json['data']['updated_at'],
        "Created At": item_json['data']['created_at'],
        "Metadata": item_json['data']['metadata']
    }
