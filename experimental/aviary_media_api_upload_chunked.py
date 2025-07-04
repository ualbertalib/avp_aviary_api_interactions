##############################################################################################
# desc: connect to the Aviary API and test media file upload
#       exploritory / proof-of-concept code
# usage: python3 -m experimental.aviary_media_api_upload_chunked --server ${aviary_server_name} --input input.sample.csv
# license: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication
# date: June 15, 2022
##############################################################################################

# Proof-of-concept only

import argparse
import csv
import os

from aviary import api as aviaryApi


#
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', required=True, help='Servername.')
    parser.add_argument('--input', required=True, help='Input CSV file describing the media to upload to Aviary')
    parser.add_argument('--input_media', required=False, default="", help='Media base directory use in the input CSV')
    return parser.parse_args()


#
def process(args, session):

    # Sample media upload CSV file format:
    # resource_id,filepath,access,is_360,title,display_name
    # 75072,testsrc_7200.mp4,true,false,ztestz $ title 
    #
    with open(args.input, 'r', encoding="utf-8", newline='') as input_file:
        input_csv = csv.DictReader(input_file)
        for item in input_csv:
            print(item['title'])
            item['filepath'] = os.path.join(args.input_media, item['filepath'])
            print(item['filepath'])
            aviaryApi.put_media_item(args, session, item)
            # aviaryApi.upload_based_on_avp_documentation(args, session, item)

    # the input file DictReader returns an object similar to the following
    # media_item_90m = {
    #    "resource_id" : "75072",
    #    "filepath" : "testsrc_7200.mp4",
    #    "access" : "true",
    #    "is_360" : "false",
    #    "title" : "ztestz $ title",
    #    "display_name" : "ztestz $ title"
    # }
    # put_media_item(args, session, media_item_90m)


#
def main():

    args = parse_args()

    session = aviaryApi.init_session_api_key(args.server)

    process(args, session)


if __name__ == "__main__":
    main()
