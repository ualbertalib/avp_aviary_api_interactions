##############################################################################################
# desc: connect to the Aviary API and get transcript item metadata 
#       output: CSV
#       input: CSV from the Aviary web UI resource export (API limits number of results from the collection resource listing API call with no pagination information 2023-03-27)
#       exploritory / proof-of-concept code
# usage: python3 aviary_api_report_transcripts_csv_by_list.py --server ${aviary_server_name} --output ${output_path} -input ${input_path}
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
    parser.add_argument('--input', required=True, help='List of resource IDs to add to the report.')
    parser.add_argument('--wait', required=False, help='Time to wait between API calls.', default=0.1)
    return parser.parse_args()

#
def process(args, session, input_csv, report_csv):

    # Todo: redo once upstream API documents pagination
    for row in input_csv:
        resource = aviaryApi.get_resource_item(args, session, row['aviary ID'])
        resource_json = json.loads(resource)
        if resource_json and 'data' in resource_json :
            for media_id in resource_json['data']['media_file_id'] :
                media = aviaryApi.get_media_item(args, session, media_id)
                media_json = json.loads(media)
                for transcript in media_json['data']['transcripts'] :
                    # transcript in media json looks like
                    #   {"id": 38337, "title": "YouTube en", "language": "en", "is_caption": False, "is_public": False, "has_annotation_set": False}
                    transcript_item = aviaryApi.get_transcripts_item(args, session, transcript['id'])
                    print(transcript_item)
                    parent = {
                        'Collection Label': row['Collection Title'],
                        'custom_unique_identifier': resource_json['data']['custom_unique_identifier'],
                        'media_file_id': media_id,
                        'has_annotation_set': transcript['has_annotation_set']
                    }
                    report_csv.writerow(aviaryUtilities.processTranscriptJSON(transcript_item, parent)) 
                sleep(int(args.wait))
        else:
            print('ERROR: no data')
            print(resource)
            report_csv.writerow({'Collection Label': row['aviary ID'], 'Title': resource})

#
def main():
    args = parse_args()

    username = input('Username:')
    password = getpass('Password:')

    session = aviaryApi.init_session(args, username, password)

    with open(args.input, 'r', encoding="utf-8", newline='') as input_file:
        input_csv = csv.DictReader(input_file)
        with open(args.output, 'wt', encoding="utf-8", newline='') as output_file:
            report_csv = csv.DictWriter(output_file, fieldnames=aviaryUtilities._transcript_csv_fieldnames)
            report_csv.writeheader()
            process(args, session, input_csv, report_csv)


if __name__ == "__main__":
    main()
