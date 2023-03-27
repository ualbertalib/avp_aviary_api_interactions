##############################################################################################
# desc: connect to the Aviary API and get media item metadata 
#       exploritory / proof-of-concept code
# usage: python3 aviary_api_report_resources.py --server ${aviary_server_name} --output ${output_path}
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

#
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', required=True, help='Servername.')
    parser.add_argument('--output', required=True, help='Locaiton to store CSV output file.')
    return parser.parse_args()


# initialize a session with API endpoint
def init_session(args):
    #username = input('Username:')
    username = 'jeffery.antoniuk@ualberta.ca'
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

# 
def get_collection_list(args, session):
    response = session.get(
        urljoin(args.server, 'api/v1/collections')
    )
    print(f"{response.request.url}") 
    #print(response.__dict__)
    #print(response.content)
    return response.content

 
def get_collection_resources(args, session, id):
    response = session.get(
        urljoin(args.server, 'api/v1/collections/' + str(id) + '/resources')
    )
    print(f"{response.request.url}") 
    #print(response.__dict__)
    #print(response.content)
    return response.content



# 
def get_resource_item(args, session, id):
    response = session.get(
        urljoin(args.server, 'api/v1/resources/' + str(id))
    )
    print(f"{response.request.url}") 
    #print(response.__dict__)
    #print(response.content)
    return response.content



# 
def get_media_item(args, session, id):
    response = session.get(
        urljoin(args.server, 'api/v1/media_files/' + str(id))
    )
    print(f"{response.request.url}") 
    #print(response.__dict__)
    #print(response.content)
    return response.content


#
def process(args, session):
  collections = get_collection_list(args, session)
  collection_list = json.loads(collections)
  for collection in collection_list['data'] :
    resources = get_collection_resources(args, session, collection['id'])
    resource_list = json.loads(resources)
    for resource in resource_list['data'] :
        item = get_resource_item(args, session, resource['resource_id'])
        print(item.content)

        # for media_id in resource['media_file_id'] :
            # media = get_media_item(args, session, media_id)
            # media = json.loads(media)
            # print(media['id'])

        break


#
def main():
    args = parse_args()
    session = init_session(args)

    process(args, session)


if __name__ == "__main__":
    main()
