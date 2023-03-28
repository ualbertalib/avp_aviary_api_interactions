##############################################################################################
# desc: connect to the Aviary API and test media file upload 
#       exploritory / proof-of-concept code
# usage: python3 aviary_media_api_upload_chunked.py --server ${aviary_server_name} --input input.sample.csv
# license: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication
# date: June 15, 2022
##############################################################################################

# Proof-of-concept only

from getpass import getpass
from requests_toolbelt import MultipartEncoder
from random import uniform
from time import sleep
from urllib.parse import urljoin
import argparse
import csv
import json

from aviary import api as aviaryApi


#
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', required=True, help='Servername.')
    parser.add_argument('--input', required=True, help='Input CSV file describing the media to upload to Aviary')
    return parser.parse_args()

#
def process(args, session):

    with open(args.input, 'r', encoding="utf-8", newline='') as input_file:
        input_csv = csv.DictReader(input_file)
        for item in input_csv:
            print(item['title'])
            aviaryApi.put_media_item(args, session, item)
            #aviaryApi.upload_based_on_avp_documentation(args, session, item)

    # the input file DictReader returns an object similar to the following
    #media_item_90m = {
    #    "resource_id" : "75072",
    #    "filepath" : "testsrc_7200.mp4",
    #    "access" : "true",
    #    "is_360" : "false",
    #    "title" : "ztestz $ title",
    #    "display_name" : "ztestz $ title"
    #}
    #put_media_item(args, session, media_item_90m)

#
def main():
    args = parse_args()

    username = input('Username:')
    password = getpass('Password:')

    session = aviaryApi.init_session(args, username, password)

    process(args, session)


if __name__ == "__main__":
    main()
