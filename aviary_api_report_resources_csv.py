##############################################################################################
# desc: connect to the Aviary API and get media item metadata 
#       Missing 2023-03-27: pagination (no documentation) thus result only contains 100 of `N` items per collection 
#       exploritory / proof-of-concept code
# usage: python3 aviary_api_report_resources_csv.py --server ${aviary_server_name} --output ${output_path}
# license: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication
# date: June 15, 2022
##############################################################################################

# Proof-of-concept only

from getpass import getpass
from requests_toolbelt import MultipartEncoder
from random import uniform
from time import sleep
from urllib.parse import urljoin
import argparse
import csv
import json
import requests
from aviary import api as aviaryApi

#
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', required=True, help='Servername.')
    parser.add_argument('--output', required=True, help='Location to store CSV output file.')
    parser.add_argument('--wait', required=False, help='Time to wait between API calls.', default=0.1)
    return parser.parse_args()

#
def process(args, session, report_csv):
  collections = aviaryApi.get_collection_list(args, session)
  collection_list = json.loads(collections)
  for collection in collection_list['data'] :
    resources = aviaryApi.get_collection_resources(args, session, collection['id'])
    resource_list = json.loads(resources)
    for resource in resource_list['data'] :
        if ('resource_id' in resource):
            item = aviaryApi.get_resource_item(args, session, resource['resource_id'])
            item_json = json.loads(item)
            report_csv.writerow(
                {
                "Collection ID": collection['id'],
                "Collection Label": collection['title'],
                "Resource ID": item_json['data']['id'],
                "Resource Title": item_json['data']['title'],
                "Custom Unique ID":item_json['data']['custom_unique_identifier'],
                "Access":item_json['data']['access'],
                "Is Featured":item_json['data']['is_featured'],
                "Media File IDs":item_json['data']['media_file_id'],
                "Media Files Count":item_json['data']['media_files_count'],
                "Transcripts Count":item_json['data']['indexes_count'],
                "Indexes Count":item_json['data']['title'],
                "Persistent_URL": item_json['data']['persistent_url'],
                "Direct URL": item_json['data']['direct_url'],
                "Updated At": item_json['data']['updated_at'],
                "Created At":item_json['data']['created_at'],
                "Metadata": item_json['data']['metadata']
                }
            )
        else:
            print(resource)

        sleep(args.wait)

        # for media_id in resource['media_file_id'] :
            # media = get_media_item(args, session, media_id)
            # media = json.loads(media)
            # print(media['id'])

#
def main():
    args = parse_args()

    username = input('Username:')
    password = getpass('Password:')

    session = aviaryApi.init_session(args, username, password)

    with open(args.output, 'wt', encoding="utf-8", newline='') as output_file:
        report_csv = csv.DictWriter(output_file, fieldnames=[
            "Collection ID",
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
        ])
        report_csv.writeheader()
        process(args, session, report_csv)


if __name__ == "__main__":
    main()
