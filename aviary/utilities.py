"""
aviary.utilities
~~~~~~~~~~

This module implements some cenvenience utilites.

"""

import json

_resource_csv_fieldnames=[
                # "Collection ID",
                "Collection Label",
                "Resource ID",
                "Resource Title",
                "Custom Unique ID",
                "Access",
                "Is Featured",
                "Media File IDs",
                "Media Files Count",
                "Transcripts Count",
                "Indexes Count",
                "Persistent_URL",
                "Direct URL",
                "Updated At",
                "Created At",
                "Metadata"
            ]

_media_csv_fieldnames=[
                # "Collection ID",
                "Collection Label",
                "Media ID",
                "Collection resource ID",
                "Custom Unique resource ID",
                "Display name",
                "File name",
                "Duration",
                "Access",
                "Is downloadable",
                "Is 360",
                "Sequence No",
                "Transcripts",
                "Indexes",
                "Updated At",
                "Created At",
                "Metadata"
            ]

# Todo: redo when pagination is active
def processResourceJSON(item, collection_title):

    item_json = json.loads(item)
    if 'data' not in item_json:
        raise ValueError('Does not contain a valid response')
    return {
        # "Collection ID": collection['id'],
        # "Collection Label": collection['title'],
        "Collection Label": collection_title,
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


# Todo: redo when pagination is active
def processMediaJSON(item, collection_title, custom_unique_identifier):

    media_json = json.loads(item)
    if 'data' not in media_json:
        raise ValueError('Does not contain a valid response')
    return {
        # "Collection ID": collection['id'],
        # "Collection Label": collection['title'],
        "Collection Label": collection_title,
        "Media ID": media_json['data']['id'],
        "Collection resource ID": media_json['data']['collection_resource_id'],
        # "Custom Unique resource ID": resource_json['data']['custom_unique_identifier'],
        "Custom Unique resource ID": custom_unique_identifier, 
        "Display name": media_json['data']['display_name'],
        "File name": media_json['data']['file_name'] if 'file_name' in media_json['data'] else "",
        "Duration": media_json['data']['duration'],
        "Access": media_json['data']['access'],
        "Is 360": media_json['data']['is_360'],
        "Is downloadable": media_json['data']['is_downloadable'],
        "Sequence No": media_json['data']['sequence_no'],
        "Transcripts": media_json['data']['transcripts'],
        "Indexes": media_json['data']['indexes'],
        "Updated At": media_json['data']['updated_at'],
        "Created At": media_json['data']['created_at'],
        "Metadata": media_json['data']['metadata']
    }



