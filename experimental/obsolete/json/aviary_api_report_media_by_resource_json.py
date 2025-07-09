##############################################################################################
# desc: connect to the Aviary API and get media item metadata
#       output: JSON
#       input: Resource JSON from the aviary_api_report_resources_json_by_resource_list.py (API limits number of results from the collection resource listing API call with no pagination information 2023-03-27)
#       exploratory / proof-of-concept code
# usage: python3 aviary_api_report_media_by_resource_json.py \
#           --server ${aviary_server_name} --output ${output_path} -input ${input_path}
# license: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication
# date: March, 2024
##############################################################################################

# Proof-of-concept only

from getpass import getpass
from time import sleep
import argparse
import csv
import json
import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aviary import api as aviaryApi
from aviary import utilities as aviaryUtilities


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', required=True, help='Server name.')
    parser.add_argument('--output', required=True, help='Location to store output file.')
    parser.add_argument('--input', required=True, help='List of resource IDs to add to the report.')
    parser.add_argument('--wait', required=False, help='Time to wait between API calls.', default=0.1)
    parser.add_argument('--logging_level', required=False, help='Logging level.', default=logging.WARNING)
    return parser.parse_args()


#
def process(args, session, input_json, output_file):

    # hold json in memory
    data = []
    # should use the following but the documentation doesn't include pagination details
    # aviaryApi.get_collection_list(args, session)
    # aviaryApi.get_collection_resources(args, session, collection['id'])
    for i, resource in enumerate(input_json):
        logging.info(f"{resource['data']['media_file_id']}")
        for j, media_file_id in enumerate(resource['data']['media_file_id']):
            try:
                item = aviaryApi.get_media_item(args, session, media_file_id)
                data.append(json.loads(item))
            except BaseException as e:
                logging.error(f"{e} \n{media_file_id}")
                # add a line to the CSV output with the error
            if j >= 10:
                logging.warning(f"Check number of media files - this workaround may miss items as 'media_file_id' property may limit to only 10.\n{item}")
            sleep(iint(args.wait))
        aviaryUtilities.progressIndicator(i, args.logging_level)
    output_file.write(json.dumps(data))
    print(f"\nItems processed: {i + 1}")


#
def main():
    args = parse_args()

    username = input('Username:')
    password = getpass('Password:')

    session = aviaryApi.init_session(args, username, password)

    with open(args.input, 'r', newline='') as input_file:
        input_json = json.load(input_file)
        with open(args.output, 'wt', encoding="utf-8", newline='') as output_file:
            process(args, session, input_json, output_file)


if __name__ == "__main__":
    main()
