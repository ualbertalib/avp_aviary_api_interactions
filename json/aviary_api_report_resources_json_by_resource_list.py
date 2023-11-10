##############################################################################################
# desc: connect to the Aviary API and get media item metadata
#       output: CSV
#       input: CSV from the Aviary web UI resource export (API limits number of results from the collection resource listing API call with no pagination information 2023-03-27)
#       exploritory / proof-of-concept code
# usage: python3 aviary_api_report_resources_json_by_resource_list.py \
#           --server ${aviary_server_name} --output ${output_path} -input ${input_path}
# license: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication
# date: Nov, 2023
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
    parser.add_argument('--server', required=True, help='Servername.')
    parser.add_argument('--output', required=True, help='Location to store output file.')
    parser.add_argument('--input', required=True, help='List of resource IDs to add to the report.')
    parser.add_argument('--wait', required=False, help='Time to wait between API calls.', default=0.1)
    parser.add_argument('--logging_level', required=False, help='Logging level.', default=logging.WARNING)
    return parser.parse_args()


#
def process(args, session, input_csv, output_file):

    # hold json in memory
    data = []
    # should use the following but the documentation doesn't include pagination details
    # aviaryApi.get_collection_list(args, session)
    # aviaryApi.get_collection_resources(args, session, collection['id'])
    for i, resource in enumerate(input_csv):
        try:
            item = aviaryApi.get_resource_item(args, session, resource['aviary ID'])
            data.append(json.loads(item))
        except BaseException as e:
            logging.error(f"{e} \n{item}")
            # add a line to the CSV output with the error
        sleep(args.wait)
        aviaryUtilities.progressIndicator(i, args.logging_level)
    output_file.write(json.dumps(data))
    print(f"\nItems processed: {i + 1}")


#
def main():
    args = parse_args()

    username = input('Username:')
    password = getpass('Password:')

    session = aviaryApi.init_session(args, username, password)

    with open(args.input, 'r', encoding="utf-8", newline='') as input_file:
        input_csv = csv.DictReader(input_file)
        with open(args.output, 'wt', encoding="utf-8", newline='') as output_file:
            process(args, session, input_csv, output_file)


if __name__ == "__main__":
    main()
