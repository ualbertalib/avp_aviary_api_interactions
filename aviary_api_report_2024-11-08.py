##############################################################################################
# desc: connect to the Aviary API and get metadata
#       exploratory / proof-of-concept code
# usage: python3 aviary_api_report_2024-11-08.py --server ${aviary_server_name} --output ${output_path}
# license: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication
# date: June 15, 2022
##############################################################################################

# Proof-of-concept only

from getpass import getpass
from time import sleep

import argparse
import json
import logging
import os
import time
import traceback

from aviary import api as aviaryApi
from aviary import utilities as aviaryUtilities


AVIARY_PAGE_SIZE=100

#
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', required=True, help='Servername.')
    parser.add_argument('--output_dir', required=True, help='Directory to store output.')
    parser.add_argument('--collection', required=False, help='Limit to a given collection.')
    parser.add_argument('--resource', required=False, help='Limit to a given resource.')
    parser.add_argument('--wait', required=False, help='Time to wait between API calls.', type=float, default=0.1)
    parser.add_argument('--logging_level', required=False, help='Logging level.', default=logging.WARNING)
    return parser.parse_args()

#
def is_next_page():
    return True

#
def process_2(args, session, output_file):

    collections = aviaryApi.get_collection_list(args, session)
    collection_list = json.loads(collections)
    for collection in collection_list['data']:
        print(f"Collection: {collection['id']}")
        resources = aviaryApi.get_collection_resources(args, session, collection['id'])
        # resources = aviaryApi.get_collection_resources(args, session, 2226)
        # resources = aviaryApi.get_collection_resources(args, session, 1787)
        resource_list = json.loads(resources)
        for i, resource in enumerate(resource_list['data']):
            if ('resource_id' in resource):
                item = aviaryApi.get_resource_item(args, session, resource['resource_id'])
                output_file.write(json.dumps(json.loads(item)))
                output_file.write("\n")
            else:
                output_file.write(json.dumps(resource))
                output_file.write("\n")
                print(resource)  # error
            sleep(args.wait)
            aviaryUtilities.progressIndicator(i, args.logging_level)
        print(f"\nResource count: {i + 1}")
    print("Test only - pagination FAILS 2023 April due to no upstream documentation on how to paginate")

#
def process(args, session):
    page_number=0
    # add test if page_number doesn't work to prevent infinite looping
    first_collection_id_of_page=0
    while True:
        try:
            collections = aviaryApi.get_collection_list(args, session, page_number)
            collection_list = json.loads(collections)
            for collection in collection_list['data']:
                print(f"Collection: {collection['id']} page: {page_number}")
            time.sleep(2)
        except Exception as e:
            print(f"{e}")
            traceback.print_exc()
            break;
        else:
            page_number+=1
            break;
        

#
def main():
    args = parse_args()

    session = aviaryApi.init_session_api_key(args)

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    process(args, session)

if __name__ == "__main__":
    main()
