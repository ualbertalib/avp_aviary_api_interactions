"""
aviary.utilities
~~~~~~~~~~

This module implements some convenience utilities.

"""

import json
import logging

_resource_csv_fieldnames = [
    "Resource ID",
    # "Collection ID",
    "Collection title",
    "Resource title",
    "Custom unique ID",
    "Access",
    "Is featured",
    "Media file IDs",
    "Media files count",
    "Transcripts count",
    "Indexes count",
    "Persistent URL",
    "Direct URL",
    "Updated at",
    "Created at",
    "Metadata"
]

_media_csv_fieldnames = [
    "Media ID",
    # "Collection ID",
    "Collection title",
    "Collection resource ID",
    "Linked resource ID",
    "Linked resource title",
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
    "Collection title",
    "Linked resource title",
    "Linked resource ID",
    "Custom unique resource ID",
    "Resource file ID",
    "Media ID",
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
    "Collection title",
    "Linked resource title",
    "Linked resource ID",
    "Resource file ID",
    "Media ID",
    "Custom unique resource ID",
    "Title",
    "language",
    "Is public"
]

_supplemental_files_csv_fieldnames = [
    "Supplemental files ID",
    # "Collection ID",
    # "Collection title",
    "Collection resource ID",
    "Title",
    "Description",
    "Access",
    "Status",
    "Sort order",
    "Associated file name",
    "Associated file content type",
    "File",
    "Created at",
    "Updated at"
]


# Todo: redo when pagination is active
def processResourceJSON(item, collection_title):

    item_json = json.loads(item)
    if 'data' not in item_json:
        raise ValueError('Does not contain a valid response')
    return {
        "Resource ID": item_json['data']['id'],
        # "Collection ID": collection['id'],
        # "Collection title": collection['title'],
        "Collection title": collection_title,
        "Resource title": item_json['data']['title'],
        "Custom unique ID": item_json['data']['custom_unique_identifier'],
        "Access": item_json['data']['access'],
        "Is featured": item_json['data']['is_featured'],
        "Media file IDs": item_json['data']['media_file_id'],
        "Media files count": item_json['data']['media_files_count'],
        "Transcripts count": item_json['data']['transcripts_count'],
        "Indexes count": item_json['data']['indexes_count'],
        "Persistent URL": item_json['data']['persistent_url'],
        "Direct URL": item_json['data']['direct_url'],
        "Updated at": item_json['data']['updated_at'],
        "Created at": item_json['data']['created_at'],
        "Metadata": item_json['data']['metadata']
    }


# Todo: redo when pagination is active
def processMediaJSON(item, collection_title, custom_unique_identifier, linked_resource_id, linked_resource_title):

    media_json = json.loads(item)
    if 'data' not in media_json:
        raise ValueError(f"Does not contain a valid response: {media_json}")
    return {
        "Media ID": media_json['data']['id'],
        # "Collection ID": collection['id'],
        # "Collection title": collection['title'],
        "Collection title": collection_title,
        "Collection resource ID": media_json['data']['collection_resource_id'],
        "Linked resource ID": linked_resource_id,
        "Linked resource title": linked_resource_title,
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
def processTranscriptJSON(item, additional):

    transcript_json = json.loads(item)
    if 'data' not in transcript_json:
        raise ValueError('Does not contain a valid response')
    return {
        "Transcript ID": transcript_json['data']['id'],
        # "Collection ID": collection['id'],
        # "Collection title": collection['title'],
        "Collection title": additional['Collection title'],
        "Linked resource title": additional['Linked resource title'],
        "Linked resource ID": additional['Linked resource ID'],
        "Custom unique resource ID": additional['custom_unique_identifier'],
        "Resource file ID": transcript_json['data']['resource_file_id'],
        "Media ID": additional['media_file_id'],
        "Is caption": transcript_json['data']['is_caption'],
        "Is public": transcript_json['data']['is_public'],
        "Title": transcript_json['data']['title'],
        "Language": transcript_json['data']['language'],
        "Description": transcript_json['data']['description'],
        "Is downloadable": transcript_json['data']['is_downloadable'],
        "Has annotation set": additional['has_annotation_set']
    }


# Todo: redo when pagination is active
def processIndexJSON(item, additional):

    index_json = json.loads(item)
    if 'data' not in index_json:
        raise ValueError('Does not contain a valid response')
    return processIndexDict(index_json['data'], additional)


# Todo: redo when pagination is active
def processIndexDict(item, additional):

    return {
        "Index ID": item['id'],
        # "Collection ID": collection['id'],
        # "Collection title": collection['title'],
        "Collection title": additional['Collection title'],
        "Linked resource title": additional['Linked resource title'],
        "Linked resource ID": additional['Linked resource ID'],
        "Media ID": additional['media_file_id'],
        "Custom unique resource ID": additional['custom_unique_identifier'],
        "Title": item['title'],
        "language": item['language'],
        "Is public": item['is_public'],
    }


# Todo: redo when pagination is active
def processSupplementalFilesJSON(item):

    item_json = json.loads(item)
    if 'data' not in item_json:
        raise ValueError('Does not contain a valid response')
    return {
        "Supplemental files ID": item_json['data']['id'],
        # "Collection ID": collection['id'],
        # "Collection title": collection['title'],
        "Collection resource ID": item_json['data']['collection_resource_id'],
        "Title": item_json['data']['title'],
        "Description": item_json['data']['description'],
        "Access": item_json['data']['access'],
        "Status": item_json['data']['status'],
        "Sort order": item_json['data']['sort_order'] if 'sort_order' in item_json['data'] else "",
        "Associated file name": item_json['data']['associated_file_file_name'],
        "Associated file content type": item_json['data']['associated_file_content_type'],
        "File": item_json['data']['file'],
        "Created at": item_json['data']['created_at'],
        "Updated at": item_json['data']['updated_at']

        # "Collection title": parent['Collection title'],
        # "Custom unique resource ID": parent['custom_unique_identifier'],
    }


# Validate that the resource media count is the same as the number of items in the media id list
def validateResourceMediaList(resource_json):
    if (len(resource_json['data']['media_file_id']) != resource_json['data']['media_files_count']):
        logging.warning(f"""Resource {resource_json['data']['id']} is missing media ids
            -- expected count: {resource_json['data']['media_files_count']}
            -- actual count: {len(resource_json['data']['media_file_id'])} actual id list: {resource_json['data']['media_file_id']}""")


# Progress indicator: simple
# Todo: replace with Python module?
def progressIndicator(i, logging_level):
    if (i % 50 == 0 and logging_level in [logging.ERROR, logging.WARNING]):
        print(f"{i}.", end="", flush=True)


# download a file via stream & chunks
def download_file(session, url, filename='tmp', path="/tmp/", headers=""):
    logging.info(f"Download URL: {url}")
    local_file_path = path + '/' + filename
    with session.get(url, stream=True, headers=headers) as response:
        logging.info(f"Status: {response.status_code} Response URL: {response.request.url}")
        response.raise_for_status()
        with open(local_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    logging.info(f"Stored: {local_file_path}")

    return local_file_path
