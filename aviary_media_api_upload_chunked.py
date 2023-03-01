##############################################################################################
# desc: connect to the Aviary API and test media file upload 
#       exploritory / proof-of-concept code
# usage: python3 aviary_media_api_upload_chunked.py --server ${aviary_server_name}
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


# auth api endpoint
auth_endpoint = 'api/v1/auth/sign_in'

# chunk size
CHUNK_SIZE = 100000000

#
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', required=True, help='Servername.')
    return parser.parse_args()


# initialize a session with API endpoint
def init_session(args):
    username = input('Username:')
    password = getpass('Password:')

    session = requests.Session()
    session.auth = (username, password)

    response = session.post(
        urljoin(args.server, auth_endpoint),
        json={'email': username, 'password': password},
        headers={'Content-Type': 'application/json'}
    )
    response.raise_for_status()

    # aviary headers for auth:
    # https://www.aviaryplatform.com/api/v1/documentation#jump-Authorization-Authorization_3A_2Fapi_2Fv1_2Fauth_2Fsignin
    auth = {
        'access-token': response.headers['access-token'],
        'client': response.headers['client'],
        'token-type': response.headers['token-type'],
        'uid': response.headers['uid']
    }
    session.headers.update(auth)
    return session


# https://stackoverflow.com/questions/50994218/post-large-file-using-requests-toolbelt-to-vk
def put_media_item(args, session, item):
    content_name = os.path.basename(item['filepath']) 
    content_size = os.stat(item['filepath']).st_size
    url = urljoin(args.server, 'api/v1/media_files'),
    index = 0
    offet = 0

    print(f"Uploading: [{item['filepath']}] with size [{content_size}]")

    print(str(datetime.datetime.now()) + " #################################################")
    try:
        f = open(item['filepath'], 'rb')
        while chunk := f.read(CHUNK_SIZE):
            offset = index + len(chunk)
            params = {
                "collection_resource_id" : item['resource_id'],
                "access" : item['access'],
                "is_360" : item['is_360'],
                "display_name" : item['display_name'],
                }
            files = {"media_file" : (content_name, chunk) } # set filename (default is media_file when chunked or filename from path if not); filename used to populate display_name if not set???
            headers = {
                'Content-Range' : 'bytes %s-%s/%s' % (index, offset-1, content_size)
                }
            print(f"Uploading: [{item['filepath']}] with Content-Range[{headers['Content-Range']}]")
            response = session.post(
                urljoin(args.server, 'api/v1/media_files'),
                params = params,
                files = files,
                headers = headers,
                timeout=120,
                verify=False
            )
            print(f"{response.request.url}") 
            print(response.__dict__)
            index = offset
            response.raise_for_status()
    except Exception as e:
        print("ERROR (begin): #################################################")
        print(e)
        print("#################################################")
        print(response.__dict__)
        print("#################################################")
        print(traceback.format_exc())
        print("ERROR (end): #################################################")

    print(str(datetime.datetime.now()) + " #################################################")


# hard coded test
def get_media_item(args, session, media_id):
    response = session.get(
        urljoin(args.server, 'api/v1/media_files/'.media_id)
    )
    print(f"{response.request.url}") 
    print(response.__dict__)


#
def process(args, session):

  # get_media_item(args, session, "")
  
  media_item_90m = {
    "resource_id" : "75072",
    "filepath" : "testsrc_7200.mp4",
    "access" : "true",
    "is_360" : "false",
    "title" : "ztestz $ title",
    "display_name" : "ztestz $ title"
  }
  put_media_item(args, session, media_item_90m)

#
def main():
    args = parse_args()
    session = init_session(args)

    process(args, session)


if __name__ == "__main__":
    main()
