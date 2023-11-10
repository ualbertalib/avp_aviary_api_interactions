##############################################################################################
# desc: connect to the Aviary API and get index item metadata
#       output: CSV
#       input: CSV from the Aviary web UI media export (API limits number of results from the collection resource listing API call with no pagination information 2023-03-27)
#       exploritory / proof-of-concept code
# usage: python3 aviary_api_report_index_csv_by_media_list.py \
#           --server ${aviary_server_name} --output ${output_path} -input ${input_path}
# license: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication
# date: June 15, 2022
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
    parser.add_argument('--input', required=True, help='List of media IDs to add to the report.')
    parser.add_argument('--wait', required=False, help='Time to wait between API calls.', default=0.1)
    parser.add_argument('--logging_level', required=False, help='Logging level.', default=logging.WARNING)
    return parser.parse_args()


#
def process(args, session, input_csv, output_file):

    # is there a better way then to hold all JSON in memory before writing?
    data = []

    # Todo: redo once upstream API documents pagination
    # Iterate through the media / resource / collection list
    for i, row in enumerate(input_csv):
        media_id = row['aviary ID']
        media = aviaryApi.get_media_item(args, session, media_id)
        media_json = json.loads(media)
        if ('data' in media_json):
            tmp = {
                'Collection title': row['Collection Title'],
                'Linked resource ID': row['Linked Resource Id'],
                'Linked resource title': row['Linked Resource Title'],
                'media_file_id': media_id,
                'indexes': []
            }
            for index in media_json['data']['indexes']:
                # Todo: this fails due to the API not supporting the call
                # for indexes_id in media_json['data']['indexes'] :
                # index = aviaryApi.get_indexes_item(args, session, indexes_id)
                tmp['indexes'].append(index)
                logging.info(index)
            data.append(tmp)
        else:
            logging.error(f"media id:[{media_id}] - {media_json}")
        aviaryUtilities.progressIndicator(i, args.logging_level)
        sleep(int(args.wait))
    output_file.write(json.dumps(data))
    print(f"\nMedia Items processed looking for attached index: {i + 1}")


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
