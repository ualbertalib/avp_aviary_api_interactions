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
    parser.add_argument('--server', required=True, help='Server name.')
    parser.add_argument('--output_dir', required=True, help='Directory to store output.')
    parser.add_argument('--collection', required=False, help='Limit to a given collection.')
    parser.add_argument('--resource', required=False, help='Limit to a given resource.')
    parser.add_argument('--wait', required=False, help='Time to wait between API calls.', type=float, default=0.1)
    parser.add_argument('--logging_level', required=False, help='Logging level.', default=logging.INFO)
    return parser.parse_args()


#
def process_supplemental_files(args, session, path, supplemental_list):
    count=0
    for id in supplemental_list:
        supplemental_str = aviaryApi.get_supplemental_files_item(args, session, id)
        supplemental = json.loads(supplemental_str)
        path_supplemental = os.path.join(path, 'supplemental', str(id))
        output_generic(path_supplemental, supplemental, id)
        count += 1
    if count > 1:
        logging.warning(f"Check: supplementals count: [{count}] - 'supplemental' property {path} {supplemental_list}")


#
def process_transcripts(args, session, path, transcript_list):
    count=0
    for item in transcript_list:
        id = item['id']
        transcript_str = aviaryApi.get_transcripts_item(args, session, id)
        transcript = json.loads(transcript_str)
        path_transcript = os.path.join(path, 'transcript', str(id))
        output_generic(path_transcript, transcript, id)
        count += 1
    if count > 1:
        logging.warning(f"Check: transcripts count: [{count}] - 'transcripts' property {path} {transcript_list}")


#
def process_indexes(args, session, path, indexes_list):
    count=0
    for item in indexes_list:
        # extract ID from a json array
        id = item['id']
        indexes_str = aviaryApi.get_indexes_item_v2(args, session, id)
        indexes = json.loads(indexes_str)
        path_transcript = os.path.join(path, 'indexes', str(id))
        output_generic(path_transcript, indexes, id)
        count += 1
    if count > 1:
        logging.warning(f"Check: indexes count: [{count}] - 'indexes' property {path} {indexes_list}")


#
def process_media_by_resource(args, session, path, item):
    count=0
    for id in item['media_file_id']:
        media_str = aviaryApi.get_media_item(args, session, id)
        media = json.loads(media_str)
        #logging.warning(f"id: {id} \n    {item} \n    {media}")
        path_media = os.path.join(path, 'media', f"{str(id)}")
        output_generic(path_media, media, id)
        # transcript attached to media
        process_transcripts(args, session, path_media, media['data']['transcripts'])
        # index attached to media
        process_indexes(args, session, path_media, media['data']['indexes'])
        # supplemental file attached to resource 
        process_supplemental_files(args, session, path, item['supplemental_id'])
        count += 1
    if count > 10:
        logging.debug(f"Check: media files count: [{count}] media_files_count: [{item['media_files_count']}] - 'media_file_id' property for a 10 item limit.\n{item}")
        logging.debug(f"Media count {count}")
    if count < item['media_files_count']:
        logging.error(f"Check: media files count: [{count}] media_files_count: [{item['media_files_count']}] - count 'media_file_id' <> 'media_files_count .\n{item}")


# build collection directory from specified path and ID and store collection metadata in a file named after the ID
def output_generic(path, item, id):
    if not os.path.exists(path):
        os.makedirs(path)
    file_path = os.path.join(path, f"{id}.json")
    with open(file_path, 'w') as file:
        logging.debug(file_path)
        json.dump(item, file, indent=4)

#
def process_resource(args, session, collection_path, id):
    path = os.path.join(collection_path, 'collection_resources', str(id))
    logging.debug(f"Path: {path}")
    resource_str = aviaryApi.get_resource_item(args, session, id)
    resource = json.loads(resource_str)
    output_generic(path, resource, id)
    process_media_by_resource(args, session, path, resource['data'])


#
def process_resources_by_collection(args, session, collection_path, collection_id):
    page_number=1
    page_next=True
    # add test if page_number doesn't work to prevent infinite looping
    first_id_of_page=0
    while page_next:
        try:
            resources = aviaryApi.get_collection_resources(args, session, collection_id, page_number)
            resource_list = json.loads(resources)

            for index, item in enumerate(resource_list['data']):
                # Test if the first id of the current page is the same id of last page
                #   if true pagination failed; break out of process
                if (index == 0):
                    if (first_id_of_page == item['resource_id']):
                        logging.error(f"Pagination failed to move to the next page current {item['resource_id']} first {first_id_of_page} current page: {page_number}")
                        page_next = False 
                        break
                    else:
                        first_id_of_page = item['resource_id']
                        logging.info(f"Pagination {item['resource_id']} first {first_id_of_page} current page: {page_number}")
                process_resource(args, session, collection_path, item['resource_id'])
                process_media_by_resource(args, session, path, item)
            logging.info(f"Count resources: {index+1}")
            if AVIARY_PAGE_SIZE > (index+1):
                page_next = False 
            else:
                time.sleep(args.wait)
        except Exception as e:
            logging.error(f"{e}")
            traceback.print_exc()
            break;
        else:
            page_number+=1


# Todo: setup pagination as decorator? 
def process_collection(args, session):
    page_number=1
    page_next=True
    # add test if page_number doesn't work to prevent infinite looping
    first_collection_id_of_page=0
    while page_next:
        try:
            if (args.collection):
                # a single collection therefore no next page
                collection_list = { "data": [ {"id": f"{args.collection}", "title": ""} ] } 
                page_next = False
            else:
                collections = aviaryApi.get_collection_list(args, session, page_number)
                collection_list = json.loads(collections)
            for index, collection in enumerate(collection_list['data']):
                logging.info(f"Collection: {collection['id']} Title: {collection['title']} Page: {page_number}")
                # Test if the first id of the current page is the same id of last page
                #   if true pagination failed; break out of process
                if (index == 0):
                    if (first_collection_id_of_page == collection['id']):
                        logging.error(f"Pagination failed to move to the next page current {collection['id']} first {first_collection_id_of_page} current page: {page_number}")
                        page_next = False 
                        break
                    else:
                        first_collection_id_of_page = collection['id']
                path = os.path.join(args.output_dir, f"{str(collection['id'])}")
                output_generic(path, collection, str(collection['id']))
                #process_resources_by_collection(args, session, path, collection['id'])
            logging.info(f"Count collections {index+1}")
            if AVIARY_PAGE_SIZE > (index+1):
                page_next = False 
            else:
                time.sleep(args.wait)
        except Exception as e:
            logging.error(f"{e}")
            traceback.print_exc()
            break;
        else:
            page_number+=1


#        
def process(args, session):
    if args.resource:
        process_resource(args, session, args.output_dir, args.resource)
    else: 
        process_collection(args, session)

#
def main():

    args = parse_args()

    logging.basicConfig(level=args.logging_level)

    session = aviaryApi.init_session_api_key(args)

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    process(args, session)

if __name__ == "__main__":
    main()
