##############################################################################################
# desc: connect to the Aviary API and get media item metadata
#       output: CSV
#       input: CSV from the Aviary web UI resource export (API limits number of results from the collection resource listing API call with no pagination information 2023-03-27)
#       exploritory / proof-of-concept code
# usage: python3 aviary_api_report_resources_csv_by_list.py --server ${aviary_server_name} --output ${output_path} -input ${input_path}
# license: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication
# date: June 15, 2022
##############################################################################################

# Proof-of-concept only

from time import sleep
import argparse
import csv
import logging

import sys
import os

# Add the sibling directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from aviary import api as aviaryApi
from aviary import utilities as aviaryUtilities


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', required=True, help='Servername.')
    parser.add_argument('--output', required=True, help='Location to store CSV output file.')
    parser.add_argument('--input', required=True, help='List of resource IDs to add to the report (CSV inpute with "aviary ID" column as available from the Aviary resource export).')
    parser.add_argument('--wait', required=False, help='Time to wait between API calls.', default=0.1)
    parser.add_argument('--logging_level', required=False, help='Logging level.', default=logging.WARNING)
    return parser.parse_args()


#
def process(args, session, input_csv, report_csv):

    # should use the following but the documentation doesn't include pagination details
    # aviaryApi.get_collection_list(args, session)
    # aviaryApi.get_collection_resources(args, session, collection['id'])
    for i, resource in enumerate(input_csv):
        try:
            item = aviaryApi.get_resource_item(args, session, resource['aviary ID'])
            collection_title = resource.get('Collection Title', "")
            report_csv.writerow(aviaryUtilities.processResourceJSON(item, collection_title))
        except BaseException as e:
            logging.error(f"Exception [{e}] \n{item}")
            # add a line to the CSV output with the error
            report_csv.writerow({'Resource ID': resource['aviary ID'], 'Resource title': item})
        sleep(args.wait)
        aviaryUtilities.progressIndicator(i, args.logging_level)
    print(f"\nItems processed: {i + 1}")


#
def main():
    args = parse_args()

    session = aviaryApi.init_session_api_key(args.server)

    # todo: Instead of an input file of IDs, use the 2024 Pagination documentation:
    #   https://github.com/ualbertalib/avp_aviary_api_interactions/blob/4a120acb5d89e8f8cccb287f8596cc7da22a3b8a/aviary_api_report_2024-11-08.py#L138-L173
    # The above should be improved upon as implemented as a decorator
    with open(args.input, 'r', encoding="utf-8", newline='') as input_file:
        input_csv = csv.DictReader(input_file)
        with open(args.output, 'wt', encoding="utf-8", newline='') as output_file:
            report_csv = csv.DictWriter(output_file, fieldnames=aviaryUtilities._resource_csv_fieldnames)
            report_csv.writeheader()
            process(args, session, input_csv, report_csv)


if __name__ == "__main__":
    main()
