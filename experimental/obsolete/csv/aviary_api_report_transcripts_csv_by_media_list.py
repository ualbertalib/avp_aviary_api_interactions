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
        media_id = row['aviary ID']
        media = aviaryApi.get_media_item(args, session, media_id)
        media_json = json.loads(media)
        if ('data' in media_json):
            for transcript in media_json['data']['transcripts']:
                # Lookup the transcripts attached to the given media
                # transcript in media json looks like
                #   {"id": 38337, "title": "YouTube en", "language": "en", "is_caption": False, "is_public": False, "has_annotation_set": False}
                transcript_item = aviaryApi.get_transcripts_item(args, session, transcript['id'])
                # print(transcript_item)
                additional = {
                    'Collection title': row['Collection Title'],
                    'Linked resource ID': row['Linked Resource Id'],
                    'Linked resource title': row['Linked Resource Title'],
                    'custom_unique_identifier': "",
                    'media_file_id': media_id,
                    'has_annotation_set': transcript['has_annotation_set']
                }
                report_csv.writerow(aviaryUtilities.processTranscriptJSON(transcript_item, additional))
        else:
            logging.error(f"media id: [{media_id}] - {media_json}")
        aviaryUtilities.progressIndicator(i, args.logging_level)
        sleep(int(args.wait))
    print(f"\nMedia processed looking for attached transcripts: {i + 1}")


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
