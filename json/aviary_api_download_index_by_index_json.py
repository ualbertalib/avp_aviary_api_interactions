##############################################################################################
# desc: connect to the Aviary API and download index file
#       output_path: directory path to store downloaded files
#       input: Indexes JSON from the aviary_api_report_index_by_media_json.py (API limits number of results from the collection resource listing API call with no pagination information 2023-03-27)
#       exploratory / proof-of-concept code
# usage: python3 aviary_api_download_index_by_index_json.py \
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
    parser.add_argument('--output_path', required=True, help='Location to store output file.')
    parser.add_argument('--input', required=True, help='JSON output from index API.')
    parser.add_argument('--wait', required=False, help='Time to wait between API calls.', default=1)
    parser.add_argument('--logging_level', required=False, help='Logging level.', default=logging.WARNING)
    return parser.parse_args()


#
def process(args, session, input_json):

    # hold json in memory
    data = []
    for i, index in enumerate(input_json):
        try:
            logging.info(f"{index['data']['id']} {index['data']['export']['file']} {index['data']['export']['file_name']}")

            if ( index['data']['export']['file_name'] ) :
                file_name = index['data']['export']['file_name']
            else :
                file_name = f"{index['data']['id']}.webvtt"

            logging.info(f"{file_name} {index['data']['export']['file_content_type']}")

            aviaryUtilities.download_file(
                session,
                index['data']['export']['file'],
                file_name,
                path=args.output_path,
                headers={}
                )
        except BaseException as e:
            logging.error(f"{e} \n{index}")
            # add a line to the CSV output with the error
        sleep(int(args.wait))
        aviaryUtilities.progressIndicator(i, args.logging_level)
    print(f"\nItems processed: {i + 1}")


#
def main():
    args = parse_args()

    username = input('Username:')
    password = getpass('Password:')

    session = aviaryApi.init_session(args, username, password)

    with open(args.input, 'r', newline='') as input_file:
        input_json = json.load(input_file)
        process(args, session, input_json)


if __name__ == "__main__":
    main()
