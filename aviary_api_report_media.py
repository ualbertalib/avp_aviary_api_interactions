##############################################################################################
# desc: connect to the Aviary API and get media item metadata
#       exploritory / proof-of-concept code
# usage: python3 aviary_media_api_get.py --server ${aviary_server_name} --media_id ${media_id}
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
import datetime
import json
import os
import requests
import sys
import traceback
from aviary import api as aviaryApi

# auth api endpoint
auth_endpoint = 'api/v1/auth/sign_in'


#
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', required=True, help='Servername.')
    parser.add_argument('--output', required=True, help='Location to store CSV output file.')
    return parser.parse_args()


#
def process(args, session):

    # Get list of collections
    collections = aviaryApi.get_collection_list(args, session)
    collection_list = json.loads(collections)
    for collection in collection_list['data']:
        # Get list of resources attached to the given collections
        resources = aviaryApi.get_collection_resources(args, session, collection['id'])
        resource_list = json.loads(resources)
        for resource in resource_list['data']:
            # Get list of media items attached to the given resource
            for media_id in resource['media_file_id']:
                media = aviaryApi.get_media_item(args, session, media_id)
                media = json.loads(media)
                print(media['data']['id'])
                print("Test only - not done - see media_csv_by_list")
            break


#
def main():
    args = parse_args()

    username = input('Username:')
    password = getpass('Password:')

    session = aviaryApi.init_session(args, username, password)

    process(args, session)


if __name__ == "__main__":
    main()
