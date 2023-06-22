##############################################################################################
# desc: exploratory script to download files attached to Aviary content (audio/video, transcripts, index, and supplemental files)
#       exploritory / proof-of-concept code
# usage:
#       python3 experimental/experimental_download.py --server ${SERVER_URL}  --id ${ID} --type ${TYPE}
#       python3 experimental/experimental_download.py --server ${SERVER_URL}  --id 53122 --type i
# license: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication
# date: June 22, 2022
##############################################################################################


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
    parser.add_argument('--input_file', required=True, help='Input file with a list of IDs.')
    parser.add_argument('--output_path', required=True, help='Output file path')
    parser.add_argument('--type', required=True, help='One letter character for type [m]edia, [t]ranscript, [i]ndex, [s]upplemental file.')
    parser.add_argument('--wait', required=False, help='Time to wait between API calls.', default=1.0)
    parser.add_argument('--logging_level', required=False, help='Logging level.', default=logging.INFO)
    parser.add_argument('--session_cookie', required=False, help='File containing an auth cookie from the WebUI (temporary).')
    return parser.parse_args()


def process(args, session, headers=""):

    with open(args.input_file, 'r', encoding="utf-8", newline='') as input_file:
        for id in input_file:
            id = id.rstrip("\n")
            logging.info(f"ID: {id}")
            try:
                if args.type == 's':
                    item = aviaryApi.get_supplemental_files_item(args, session, str(id))
                    item_json = json.loads(item)
                    logging.info(f"Supplemental File: {item_json}")
                    aviaryUtilities.download_file(session, item_json['data']['file'], item_json['data']['associated_file_file_name'])
                    # todo: test if a proper export or an html page
                elif args.type == 't':
                    aviaryUI.download_transcript(args, session, id)
                elif args.type == 'i':
                    aviaryUI.download_index(args, session, id)
            except requests.exceptions.HTTPError as e:
                logging.error(f"ID:{id} - {e}")
            finally:
                sleep(int(args.wait))


#
def main():
    args = parse_args()

    logging.getLogger().setLevel(args.logging_level)

    username = input('Username:')
    password = getpass('Password:')

    if args.type == 't' or args.type == 'i':
        # todo: replace with a python auth script that can handle the MFA request
        otp_attempt = getpass('MFA OTP:')
        session_ui = aviaryUI.init_session(args, username, password, otp_attempt)
        headers = {}
        process(args, session_ui, headers)
    else:
        session = aviaryApi.init_session(args, username, password)
        process(args, session)


if __name__ == "__main__":
    main()
