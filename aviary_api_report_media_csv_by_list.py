##############################################################################################
# desc: connect to the Aviary API and get media item metadata 
#       output: CSV
#       input: CSV from the Aviary web UI resource export (API limits number of results from the collection resource listing API call with no pagination information 2023-03-27)
#       exploritory / proof-of-concept code
# usage: python3 aviary_api_report_media_csv_by_list.py --server ${aviary_server_name} --output ${output_path} -input ${input_path}
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

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', required=True, help='Servername.')
    parser.add_argument('--output', required=True, help='Location to store CSV output file.')
    parser.add_argument('--input', required=True, help='List of resource IDs to add to the report.')
    parser.add_argument('--wait', required=False, help='Time to wait between API calls.', default=0.1)
    return parser.parse_args()

#
def process(args, session, input_csv, report_csv):

    for row in input_csv:
        resource = aviaryApi.get_resource_item(args, session, row['aviary ID'])
        resource_json = json.loads(resource)
        for media_id in resource_json['data']['media_file_id'] :
            media = aviaryApi.get_media_item(args, session, media_id)
            media_json = json.loads(media)
            report_csv.writerow(
                {
                #"Collection ID": collection['id'],
                #"Collection Label": collection['title'],
                "Media ID": media_json['data']['id'],
                "Collection resource ID": media_json['data']['collection_resource_id'],
                "Custom Unique resource ID": resource_json['data']['custom_unique_identifier'],
                "Display name": media_json['data']['display_name'],
                "File name": media_json['data']['file_name'] if 'file_name' in media_json['data'] else "",
                "Duration": media_json['data']['duration'],
                "Access": media_json['data']['access'],
                "Is 360": media_json['data']['is_360'],
                "Is downloadable": media_json['data']['is_downloadable'],
                "Sequence No": media_json['data']['sequence_no'],
                "Transcripts": media_json['data']['transcripts'],
                "Indexes": media_json['data']['indexes'],
                "Updated At": media_json['data']['updated_at'],
                "Created At": media_json['data']['created_at'],
                "Metadata": media_json['data']['metadata']
                }
            )

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
            report_csv = csv.DictWriter(output_file, fieldnames=[
                #"Collection ID",
                #"Collection Label",
                "Media ID",
                "Collection resource ID",
                "Custom Unique resource ID",
                "Display name",
                "File name",
                "Duration",
                "Access",
                "Is downloadable",
                "Is 360",
                "Sequence No",
                "Transcripts",
                "Indexes",
                "Updated At",
                "Created At",
                "Metadata"
            ])
            report_csv.writeheader()
            process(args, session, input_csv, report_csv)


if __name__ == "__main__":
    main()
