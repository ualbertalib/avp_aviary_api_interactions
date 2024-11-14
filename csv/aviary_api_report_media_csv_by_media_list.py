##############################################################################################
# desc: connect to the Aviary API and get media item metadata
#       output: CSV
#       input: CSV from the Aviary web UI media export (to workaround the API limits number of results from the collection resource listing API call with no pagination information 2023-03-27)
#       exploritory / proof-of-concept code
# usage: python3 aviary_api_report_media_csv_by_media_list.py --server ${aviary_server_name} --output ${output_path} -input ${input_path}
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
    parser.add_argument('--input', required=True, help='List of media IDs to add to the report.')
    parser.add_argument('--wait', required=False, help='Time to wait between API calls.', default=0.1)
    parser.add_argument('--logging_level', required=False, help='Logging level.', default=logging.WARNING)
    return parser.parse_args()


#
def process(args, session, input_csv, report_csv):

    # Todo: redo once upstream API documents pagination
    # Iterate through the media list
    for i, row in enumerate(input_csv):
        # Get the media attached to the given resource
        try:
            media = aviaryApi.get_media_item(args, session, row['aviary ID'])
            report_csv.writerow(aviaryUtilities.processMediaJSON(media, row['Collection Title'], "", row['Linked Resource Id'], row['Linked Resource Title']))
        except BaseException as e:
            logging.error(f"[{row['aviary ID']}] {e}")
        sleep(args.wait)
        aviaryUtilities.progressIndicator(i, args.logging_level)
    print(f"\nMedia: {i + 1}")


#
def main():
    args = parse_args()

    logging.basicConfig(level=args.logging_level)

    username = input('Username:')
    password = getpass('Password:')

    session = aviaryApi.init_session(args, username, password)

    with open(args.input, 'r', encoding="utf-8", newline='') as input_file:
        input_csv = csv.DictReader(input_file)
        with open(args.output, 'wt', encoding="utf-8", newline='') as output_file:
            report_csv = csv.DictWriter(output_file, fieldnames=aviaryUtilities._media_csv_fieldnames)
            report_csv.writeheader()
            process(args, session, input_csv, report_csv)


if __name__ == "__main__":
    main()
