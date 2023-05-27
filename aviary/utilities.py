"""
aviary.utilities
~~~~~~~~~~

This module implements some cenvenience utilites.

"""

import json

_resource_csv_fieldnames=[
                "Resource ID",
                # "Collection ID",
                "Collection Label",
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
                "Media ID",
                # "Collection ID",
                "Collection Label",
                "Collection resource ID",
                "Custom unique resource ID",
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
                "Metadata",
                'Thumbnail url',
                'Turn on cc',
                'Downloadable duration',
                'Download enabled for',
                'Media download url',
                'Media embed url',
                'Media embed type',
                'Media embed code',
                'Transcode url'
            ]

_transcript_csv_fieldnames = [
                "Transcript ID",
                # "Collection ID",
                "Collection Label",
                "Media ID",
                "Resource file ID",
                "Custom unique resource ID",
                "Is caption",
                "Is public",
                "Title",
                "Language",
                "Description",
                "Is downloadable",
                "Has annotation set"
    ]

_index_csv_fieldnames = [
                "Index ID",
                # "Collection ID",
                "Collection Label",
                "Media ID",
                "Resource file ID",
                "Custom unique resource ID",
    ]

_supplemental_files_csv_fieldnames = [
                "Supplemental files ID",
                # "Collection ID",
                # "Collection Label",
                "Collection resource ID",
                "Title",
                "Description",
                "Access",
                "Status",
                "Sort order",
                "Associated file name",
                "Associated file content type",
                "file",
                "Created at",
                "Updated at"
    ]


# Todo: redo when pagination is active
def processResourceJSON(item, collection_title):

    item_json = json.loads(item)
    if 'data' not in item_json:
        raise ValueError('Does not contain a valid response')
    return {
        "Resource ID" : item_json['data']['id'],
        # "Collection ID": collection['id'],
        # "Collection Label": collection['title'],
        "Collection Label": collection_title,
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
        "Media ID": media_json['data']['id'],
        # "Collection ID": collection['id'],
        # "Collection Label": collection['title'],
        "Collection Label": collection_title,
        "Collection resource ID": media_json['data']['collection_resource_id'],
        # "Custom Unique resource ID": resource_json['data']['custom_unique_identifier'],
        "Custom unique resource ID": custom_unique_identifier, 
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
        "Metadata": media_json['data']['metadata'],
        'Thumbnail url': media_json['data']['thumbnail_url'],
        'Turn on cc': media_json['data']['turn_on_cc'],
        'Downloadable duration': media_json['data']['downloadable_duration'],
        'Download enabled for': media_json['data']['download_enabled_for'],
        'Media download url': media_json['data']['media_download_url'],
        'Media embed url': media_json['data']['aviary_media_embed_url'],
        'Media embed type': media_json['data']['media_embed_type'],
        'Media embed code': media_json['data']['media_embed_code'],
        'Transcode url': media_json['data']['transcode_url'],
    }


# Todo: redo when pagination is active
def processTranscriptJSON(item, parent):

    transcript_json = json.loads(item)
    if 'data' not in transcript_json:
        raise ValueError('Does not contain a valid response')
    return {
        "Transcript ID": transcript_json['data']['id'],
        # "Collection ID": collection['id'],
        # "Collection Label": collection['title'],
        "Collection Label": parent['Collection Label'],
        "Media ID": parent['media_file_id'],
        "Resource file ID": transcript_json['data']['resource_file_id'],
        "Custom unique resource ID": parent['custom_unique_identifier'], 
        "Is caption": transcript_json['data']['is_caption'],
        "Is public": transcript_json['data']['is_public'],
        "Title": transcript_json['data']['title'],
        "Language": transcript_json['data']['language'],
        "Description": transcript_json['data']['description'],
        "Is downloadable": transcript_json['data']['is_downloadable'],
        "Has annotation set": parent['has_annotation_set']
    }


# Todo: redo when pagination is active
def processIndexJSON(item, parent):

    index_json = json.loads(item)
    if 'data' not in index_json:
        raise ValueError('Does not contain a valid response')
    return {
        "Index ID": index_json['data']['id'],
        # "Collection ID": collection['id'],
        # "Collection Label": collection['title'],
        "Collection Label": parent['Collection Label'],
        "Media ID": parent['media_file_id'],
        "Resource file ID": index_json['data']['resource_file_id'],
        "Custom unique resource ID": parent['custom_unique_identifier'], 
    }


# Todo: redo when pagination is active
def processSupplementalFilesJSON(item):

    item_json = json.loads(item)
    if 'data' not in item_json:
        raise ValueError('Does not contain a valid response')
    return {
        "Supplemental files ID": item_json['data']['id'],
        # "Collection ID": collection['id'],
        # "Collection Label": collection['title'],
        "Collection resource ID": item_json['data']['collection_resource_id'],
        "Title": item_json['data']['title'],
        "Description":item_json['data']['description'],
        "Access": item_json['data']['access'],
        "Status": item_json['data']['status'],
        "Sort order": item_json['data']['sort_order'] if 'sort_order' in item_json['data'] else "",
        "Associated file name": item_json['data']['associated_file_file_name'],
        "Associated file content type": item_json['data']['associated_file_content_type'],
        "file": item_json['data']['file'],
        "Created at": item_json['data']['created_at'],
        "Updated at": item_json['data']['updated_at']

        # "Collection Label": parent['Collection Label'],
        # "Custom unique resource ID": parent['custom_unique_identifier'], 
    }

