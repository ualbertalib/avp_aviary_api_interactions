##############################################################################################
# desc: connect to the Aviary API and get supplemental files metadata
#       output: CSV
#       input: CSV from the Aviary web UI resource export (API limits number of results from the collection resource listing API call with no pagination information 2023-03-27)
#       exploritory / proof-of-concept code
# usage: python3 aviary_api_report_supplemental_csv_by_list.py --server ${aviary_server_name} --output ${output_path} -input ${input_path}
# license: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication
# date: June 15, 2022
##############################################################################################

# Proof-of-concept only

from getpass import getpass
from time import sleep
import argparse
import csv
import json
from aviary import api as aviaryApi
from aviary import utilities as aviaryUtilities


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', required=True, help='Servername.')
    parser.add_argument('--output', required=True, help='Location to store CSV output file.')
    parser.add_argument('--input', required=True, help='List of supplemental file ID to add to the report.')
    parser.add_argument('--wait', required=False, help='Time to wait between API calls.', default=0.1)
    return parser.parse_args()


#
def process(args, session, input_csv, report_csv):

    # should use the following but the documentation doesn't include pagination details 
    # aviaryApi.get_collection_list(args, session)
    # aviaryApi.get_collection_resources(args, session, collection['id'])
    for row in input_csv:
        try:
            item = aviaryApi.get_supplemental_files_item(args, session, row['ID'])
            report_csv.writerow(aviaryUtilities.processSupplementalFilesJSON(item))
        except:
            print(row)
            # add a line to the CSV output with the error
            report_csv.writerow({'Supplemental Files ID': row['ID'], 'Title': item})
        sleep(args.wait)


#
def main():
    args = parse_args()

    username = input('Username:')
    password = getpass('Password:')

    session = aviaryApi.init_session(args, username, password)

    with open(args.input, 'r', encoding="utf-8", newline='') as input_file:
        input_csv = csv.DictReader(input_file)
        with open(args.output, 'wt', encoding="utf-8", newline='') as output_file:
            report_csv = csv.DictWriter(output_file, fieldnames=aviaryUtilities._supplemental_files_csv_fieldnames)
            report_csv.writeheader()
            process(args, session, input_csv, report_csv)


if __name__ == "__main__":
    main()
