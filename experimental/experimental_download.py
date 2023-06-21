# Given a type and ID, download the attached file 

# Proof-of-concept only

from urllib.parse import urljoin
from getpass import getpass
from time import sleep
import argparse
from bs4 import BeautifulSoup
import json
import logging
import os
import requests
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aviary import api as aviaryApi
from aviary import utilities as aviaryUtilities
from aviary import ui as aviaryUI


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', required=True, help='Servername.')
    parser.add_argument('--id', required=True, help='id.')
    parser.add_argument('--type', required=True, help='One letter character for type [m]edia, [t]ranscript, [i]ndex, [s]upplemental file.')
    parser.add_argument('--wait', required=False, help='Time to wait between API calls.', default=1.0)
    parser.add_argument('--logging_level', required=False, help='Logging level.', default=logging.INFO)
    parser.add_argument('--session_cookie', required=False, help='File containing an auth cookie from the WebUI (temporary).')
    return parser.parse_args()


def download_file(session, url, filename='tmp', path="/tmp/", headers=""):
    logging.info(f"URL: {url}")
    local_file_path = path + '/' + filename 
    with session.get(url, stream=True, headers=headers) as response:
        logging.info(f"Response: {response.request.url}")
        response.raise_for_status()
        with open(local_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    logging.info(f"Stored: {local_file_path}")

    return local_file_path 

def update_media_downloadable(session, server, id, value):
    url = urljoin(server, 'api/v1/media_files/' + str(id))
    value = 'true' if (value is True) else 'false'
    params = {
        #'is_downloadable': 'true' 
        'is_downloadable': value
    }
    response = session.put(url, params=params)
    logging.info(f"{response.request.url}")
    logging.info(f"{response.content}")
    return response.content

def update_resource_access(session, server, id, value):
    url = urljoin(server, 'api/v1/resources/' + str(id))
    params = {
        'access': value
    }
    response = session.put(url, params=params)
    logging.info(f"{response.request.url}")
    logging.info(f"{response.content}")
    return response.content


def download_media(session, args):
    item = aviaryApi.get_media_item(args, session, args.id)
    item_json = json.loads(item)
    logging.info(f"Media: {item_json}")


    # set resource private before enabling download link
    # Todo: error check
    #resource_id = item_json['data']['collection_resource_id'] 
    #resource = aviaryApi.get_media_item(args, session, resource_id)
    #resource_json = json.loads(item)
    #original_resource_access = resource_json['data']['access']
    #current_resource_access = resource_json['data']['access']
    #if (original_resource_access != 'private'):
    #    resource_json = update_resource_access(session, args.server, resource_id, 'private')
    #    resource_json = json.loads(item)
    #    current_resource_access = resource_json['data']['access']

    # Need is_downloadable to be true to allow downloads
    # Todo: error check
    original_is_downloadable = item_json['data']['is_downloadable']
    current_is_downloadable = False
    if original_is_downloadable == False:
        item = update_media_downloadable(session, args.server, args.id, True)
        item_json = json.loads(item)
        logging.info(f"Media: {item_json}")
        current_is_downloadable = item_json['data']['is_downloadable']

    url = item_json['data']['media_download_url']
    filename = url.rsplit('/',1)[-1].split('?')[0]
    download_file(session, url, filename)
    
    # Need is_downloadable to be set to the original value
    if original_is_downloadable != current_is_downloadable: 
        update_media_downloadable(session, args.server, args.id, original_is_downloadable)
        item = aviaryApi.get_media_item(args, session, args.id)
        item_json = json.loads(item)

    # todo what if fails before? 
    #if (original_resource_access != current_resource_access):
    #    resource_json = update_resource_access(session, args.server, resource_id, original_resrouce_access)








def process(args, session, headers=""):
    if args.type == 's':
        item = aviaryApi.get_supplemental_files_item(args, session, args.id)
        item_json = json.loads(item)
        logging.info(f"Supplemental File: {item_json}")
        download_file(session, item_json['data']['file'], item_json['data']['associated_file_file_name'])
    elif args.type == 't':
        url = urljoin(args.server, '/transcripts/export/webvtt/' + str(args.id))
        filename = args.id + '.webvtt'
        download_file(session, url, filename, headers=headers)
    elif args.type == 'i':
        url = urljoin(args.server, '/indexes/export//' + str(args.id))
        filename = args.id + '.webvtt'
        download_file(session, url, filename, headers=headers)
    elif args.type == 'm':
        text = input("SANDBOX item only!!! Code modifies permissions. Continue (Y/n)?")
        if (text == "Y"):
            download_media(session, args)
        
#
def main():
    args = parse_args()

    logging.getLogger().setLevel(args.logging_level)

    username = input('Username:')
    password = getpass('Password:')

    if args.type == 't':
        # todo: replace with a python auth script that can handle the MFA request
        if (args.session_cookie):
            session_ui = requests.Session()
            token = aviaryUI.get_auth_from_file(args)
            headers = aviaryUI.build_session_header(args, token, '/transcripts', session_ui)
        else:
            otp_attempt = getpass('MFA OTP:')
            session_ui = aviaryUI.init_session(args, username, password, otp_attempt)
            headers = {}
        process(args, session_ui, headers)
    elif args.type == 'i':
        # todo: replace with a python auth script that can handle the MFA request
        if (args.session_cookie):
            session_ui = requests.Session()
            token = aviaryUI.get_auth_from_file(args)
            headers = aviaryUI.build_session_header(args, token, '/indexes', session_ui)
        else:
            otp_attempt = getpass('MFA OTP:')
            session_ui = aviaryUI.init_session(args, username, password, otp_attempt)
            headers = {}
        process(args, session_ui, headers)
    else:
        session = aviaryApi.init_session(args, username, password)
        process(args, session)



if __name__ == "__main__":
    main()
