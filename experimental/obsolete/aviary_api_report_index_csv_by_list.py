##############################################################################################
# desc: connect to the Aviary API and get index item metadata
#       output: CSV
#       input: CSV from the Aviary web UI resource export (API limits number of results from the collection resource listing API call with no pagination information 2023-03-27)
#       exploritory / proof-of-concept code
# usage: python3 aviary_api_report_index_csv_by_list.py --server ${aviary_server_name} --output ${output_path} -input ${input_path}
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
from aviary import api as aviaryApi
from aviary import utilities as aviaryUtilities


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', required=True, help='Servername.')
    parser.add_argument('--output', required=True, help='Location to store CSV output file.')
    parser.add_argument('--input', required=True, help='List of resource IDs to add to the report.')
    parser.add_argument('--wait', required=False, help='Time to wait between API calls.', default=0.1)
    parser.add_argument('--logging_level', required=False, help='Logging level.', default=logging.WARNING)
    return parser.parse_args()


#
def process(args, session, input_csv, report_csv):

    # Todo: redo once upstream API documents pagination
    # Iterate through the resource list
    for i, row in enumerate(input_csv):
        # Get the resource details via the API (differs from the resource list from the Web UI)
        resource = aviaryApi.get_resource_item(args, session, row['aviary ID'])
        resource_json = json.loads(resource)
        aviaryUtilities.validateResourceMediaList(resource_json)
        if resource_json and 'data' in resource_json:
            # Lookup media attached to the resource
            for media_id in resource_json['data']['media_file_id']:
                media = aviaryApi.get_media_item(args, session, media_id)
                media_json = json.loads(media)
                # for indexes_id in media_json['data']['indexes'] :
                # Todo: this fails due to the API not supporting the call
                for indexes_id in ['49366']:
                    index = aviaryApi.get_indexes_item(args, session, indexes_id)
                    print(index)
                    parent = {
                        'Collection Label': row['Collection Title'],
                        'custom_unique_identifier': resource_json['data']['custom_unique_identifier'],
                        'media_file_id': media_id
                    }
                    report_csv.writerow(aviaryUtilities.processIndexJSON(index, parent))
                sleep(int(args.wait))
        else:
            print('ERROR: no data')
            print(resource)
            report_csv.writerow({'Collection Label': row['aviary ID'], 'Title': resource})
        aviaryUtilities.progressIndicator(i, args.logging_level)
    print(f"\nResource items processed looking for attached media indexes: {i + 1}")


#
def main():
    args = parse_args()

    print("Index GET request not supported, this script fails -- https://www.aviaryplatform.com/api/v1/documentation#Indexes")
    return

    username = input('Username:')
    password = getpass('Password:')

    session = aviaryApi.init_session(args, username, password)

    with open(args.input, 'r', encoding="utf-8", newline='') as input_file:
        input_csv = csv.DictReader(input_file)
        with open(args.output, 'wt', encoding="utf-8", newline='') as output_file:
            report_csv = csv.DictWriter(output_file, fieldnames=aviaryUtilities._index_csv_fieldnames)
            report_csv.writeheader()
            process(args, session, input_csv, report_csv)


if __name__ == "__main__":
    main()
