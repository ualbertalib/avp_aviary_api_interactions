##############################################################################################
# desc: connect to the Aviary API and get metadata for a specificed type and output as CSV 
#       A quick based on:
#           * files in experimental/obsolete/csv 
#           * aviary_api_export_2-24-11-08.py
#       exploratory / proof-of-concept code
# usage:
#       python3 -m experimental.aviary_api_export_metadata_csv --server ${aviary_server_name} --output ${output_path} --type [r|s|m|i|t]
#       * [Create API Key and store](https://coda.aviaryplatform.com/edit-user-profile-83#_luHGN)
#           * export AVIARY_API_KEY=string_from step above
#           * export AVIARY_API_ORGANIZATION_ID=128
# license: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication
# date: June 15, 2022
##############################################################################################

# Proof-of-concept only

import argparse
import csv
import json
import logging
import os
import time
import traceback

from aviary import api as aviaryApi
from aviary import utilities as aviaryUtilities


AVIARY_PAGE_SIZE = 100


#
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', required=True, help='Server name.')
    parser.add_argument('--output', required=True, help='File path to store output.')
    parser.add_argument('--type', required=True, help='Type: r: Resource, s: supplemental, m: Media, i: index, t: Transcript.')
    parser.add_argument('--wait', required=False, help='Time to wait between API calls.', type=float, default=0.1)
    parser.add_argument('--logging_level', required=False, help='Logging level.', default=logging.WARN)
    return parser.parse_args()


#
def process_supplemental_files(args, session, report_csv, supplemental_list):
    count = 0
    for id in supplemental_list:
        supplemental_str = aviaryApi.get_supplemental_files_item(args, session, id)
        # print(supplemental_str)
        # print(aviaryUtilities.processSupplementalFilesJSON(supplemental_str))
        report_csv.writerow(aviaryUtilities.processSupplementalFilesJSON(supplemental_str))
        count += 1
    if count > 1:
        logging.debug(f"Check: supplementals count: [{count}] - 'supplemental' property {supplemental_list}")



def process_transcripts(args, session, report_csv, transcript_list):
    count = 0
    for item in transcript_list:
        id = item['id']
        transcript_str = aviaryApi.get_transcripts_item(args, session, id)
        print(transcript_str)
        report_csv.writerow(aviaryUtilities.processTranscriptJSON(transcript_str, additional={}))
        count += 1
    if count > 1:
        logging.debug(f"Check: transcripts count: [{count}] - 'transcripts' property {transcript_list}")


#
def process_indexes(args, session, report_csv, indexes_list):
    count = 0
    for item in indexes_list:
        # extract ID from a json array
        id = item['id']
        indexes_str = aviaryApi.get_indexes_item_v2(args, session, id)
        report_csv.writerow(aviaryUtilities.processIndexJSON(indexes_str, additional={}))
        count += 1
    if count > 1:
        logging.debug(f"Check: indexes count: [{count}] - 'indexes' property {indexes_list}")


#
def process_media_by_resource(args, session, report_csv, resource):
    count = 0
    for id in resource['data']['media_file_id']:
        media_str = aviaryApi.get_media_item(args, session, id)
        media = json.loads(media_str)
        logging.debug(f"id: {id} \n    {resource} \n    {media}")
        if args.type == 'm':
            # Media metadata
            report_csv.writerow(aviaryUtilities.processMediaJSON(media_str, "", "", resource['data']['id'], resource['data']['title']))
        elif args.type == 'i':
            # index attached to media
            process_indexes(args, session, report_csv, media['data']['indexes'])
        elif args.type == 't':
            # transcript attached to media
            process_transcripts(args, session, report_csv, media['data']['transcripts'])
        count += 1
    aviaryUtilities.validateResourceMediaList(resource)
    if count > 10:
        logging.debug(f"Check: media files count: [{count}] media_files_count: [{resource['data']['media_files_count']}] - 'media_file_id' property for a 10 item limit.\n{resource}")
        logging.debug(f"Media count {count}")
    if count < resource['data']['media_files_count']:
        logging.error(f"Check: media files count: [{count}] media_files_count: [{resource['data']['media_files_count']}] - count 'media_file_id' <> 'media_files_count .\n{resource}")


#
def process_resource(args, session, report_csv, id):
    try:
        resource_str = aviaryApi.get_resource_item(args, session, id)
        resource = json.loads(resource_str)
        if args.type == 'r':
            # Resource metadata
            report_csv.writerow(aviaryUtilities.processResourceJSON(resource_str, ""))
        elif args.type == 's':
            # Supplemental metadata
            process_supplemental_files(args, session, report_csv, resource['data']['supplemental_id'])
        else:
            # Media, Index, Transcript metadata
            process_media_by_resource(args, session, report_csv, resource)
    except Exception as e:
        logging.error(f"Resource ID {id} Exception: {e}")
        traceback.print_exc()
        exit(1)


#
def process_resources_by_collection(args, session, report_csv, collection_id):
    page_number = 1
    page_next = True
    # Resource pagination not documented in the API in 2023 
    # add test if page_number doesn't work to prevent infinite looping
    # July 2025: "total_entries" introduced; refactor pageination
    first_id_of_page = 0
    while page_next:
        try:
            resources = aviaryApi.get_collection_resources(args, session, collection_id, page_number, AVIARY_PAGE_SIZE)
            resource_list = json.loads(resources)

            for index, item in enumerate(resource_list['data']):
                # Test if the first id of the current page is the same id of last page
                #   if true pagination failed; break out of process
                if (index == 0):
                    if ('errors' in item):
                        logging.error(f"Pagination failed {item}")
                        break
                    elif (first_id_of_page == item['resource_id']):
                        logging.error(f"Pagination failed to move to the next page current {item['resource_id']} first {first_id_of_page} current page: {page_number}")
                        page_next = False
                        break
                    else:
                        first_id_of_page = item['resource_id']
                        logging.info(f"Pagination {item['resource_id']} first {first_id_of_page} current page: {page_number}")
                process_resource(args, session, report_csv, item['resource_id'])
            print(f"Count resources: {index + 1}")
            if AVIARY_PAGE_SIZE > (index + 1):
                page_next = False
            else:
                time.sleep(args.wait)
        except Exception as e:
            logging.error(f"{e}")
            traceback.print_exc()
        else:
            page_number += 1


# Todo: setup pagination as decorator?
def process_collection(args, session, report_csv):
    page_number = 1
    page_next = True
    # Collection pagination not enabled in the API as of 2025-07-04
    # add test if page_number doesn't work to prevent infinite looping
    first_collection_id_of_page = 0
    while page_next:
        try:
            collections = aviaryApi.get_collection_list(args, session, page_number, AVIARY_PAGE_SIZE)
            collection_list = json.loads(collections)
            for index, collection in enumerate(collection_list['data']):
                print(f"Collection: {collection['id']} Title: {collection['title']} Page: {page_number}")
                # Test if the first id of the current page is the same id of last page
                #   if true pagination failed; break out of process
                if (index == 0):
                    if (first_collection_id_of_page == collection['id']):
                        logging.error(f"Pagination failed to move to the next page: current {collection['id']} first {first_collection_id_of_page} current page: {page_number}")
                        page_next = False
                        break
                    else:
                        first_collection_id_of_page = collection['id']
                process_resources_by_collection(args, session, report_csv, collection['id'])
            print(f"Count collections {index + 1}")
            if AVIARY_PAGE_SIZE > (index + 1):
                page_next = False
            else:
                time.sleep(args.wait)
        except Exception as e:
            logging.error(f"{e}")
            traceback.print_exc()
        else:
            page_number += 1


#
def process(args, session):
    with open(args.output, 'wt', encoding="utf-8", newline='') as output_file:
        fieldnames = {}
        match args.type:
            case 'r': #Resourses
                fieldnames=aviaryUtilities._resource_csv_fieldnames
            case 's': #Supplemental
                fieldnames=aviaryUtilities._supplemental_files_csv_fieldnames
            case 'm': #Media
                fieldnames=aviaryUtilities._media_csv_fieldnames
            case 'i': #Indexes
                fieldnames=aviaryUtilities._index_csv_fieldnames
            case 't': #Transcripts
                fieldnames=aviaryUtilities._transcript_csv_fieldnames
            case _:
                logging.error(f"Unknown type: {args.type}")
                return 
        report_csv = csv.DictWriter(output_file, fieldnames=fieldnames)
        report_csv.writeheader()
        process_collection(args, session, report_csv)

        


#
def main():

    args = parse_args()

    logging.basicConfig(level=args.logging_level)

    session = aviaryApi.init_session_api_key(args.server)

    if not os.path.exists(os.path.dirname(args.output)):
        os.makedirs(os.path.dirname(args.output))

    process(args, session)


if __name__ == "__main__":
    main()
