##############################################################################################
# desc: exploratory script to test the resource public access URL - https://weareavp.aviaryplatform.com/collections/41/collection_resources/32667/file/101487
#       as a means to download content and recover from unknown problems.
#       exploritory / proof-of-concept code
# usage:
#       python3 experimental/experimental_resource_public_access_url.py --server ${SERVER_URL} --collection_id ${C_ID} --resource_id ${R_ID} --id {MEDIA_ID}
# license: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication
# date: June 22, 2023
#       Update 2025 July, likely fails with the latest Aviary UI changes
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
    parser.add_argument('--id', required=True, help='id.')
    parser.add_argument('--collection_id', required=False, help='Collection id.', default="1797")
    parser.add_argument('--resource_id', required=False, help='Resource id.', default="96596")
    parser.add_argument('--type', required=True, help='One letter character for type [m]edia, [t]ranscript, [i]ndex, [s]upplemental file.')
    parser.add_argument('--wait', required=False, help='Time to wait between API calls.', default=1.0)
    parser.add_argument('--logging_level', required=False, help='Logging level.', default=logging.INFO)
    parser.add_argument('--session_cookie', required=False, help='File containing an auth cookie from the WebUI (temporary).')
    return parser.parse_args()


def download_media_by_resource_public_access_url(session, server, collection_id, resource_id, media_id):
    # May faile with 2025 bot mitigations (Cloudflare turnstile)
    # get duration of the expireing public access URL
    duration = aviaryUI.resource_public_access_duration()
    logging.info(f"Start/end: {duration}")

    # Start: resource view & media player hover menu "share" --> Resource Public Access URL --> expiring url
    #   * https://ualberta.aviaryplatform.com/collections/1797/collection_resources/96596
    # To add expiring download URL
    #   * https://ualberta.aviaryplatform.com/encrypted_info?action=encryptedInfo&collection_resource_id=96596&duration=06-26-2023+00%3A00+-+06-26-2023+00%3A05
    #       &auto_play=false&start_time=&start_time_status=false&end_time=00%3A00%3A00&end_time_status=false&downloadable=1&type=limited_access_url
    # The resulting URL (needs the `access` portion otherwise will not display the download link on the media player):
    #   * https://ualberta.aviaryplatform.com/r/mk6542km08?access=jZ-jHl9T6Wem5cyFWC3qSg==
    url = aviaryUI.download_media_setup_expiring(session, server, collection_id, resource_id, duration)
    logging.info(f"Expiring URL: {url}")

    # Load URL (this should gather the credentials)
    # download like in the media player dropdown
    #   * /download_media/192882?
    #       * check which parts of the header are needed
    #   * redirects to S3 storage & returns file
    #       * check which parts of the header are needed
    # Todo: Do for all media attached to a resource
    aviaryUI.resource_public_access_download_media(session, url, server, media_id, path="/tmp/")

    # Delete expiring URL (cleanup)
    aviaryUI.resource_public_access_delete(session, server, resource_id, duration)


def process(args, session, headers=""):
   if args.type == 'x':
        download_media_by_resource_public_access_url(session, args.server, args.collection_id, args.resource_id, args.id)


#
def main():
    args = parse_args()

    logging.getLogger().setLevel(args.logging_level)

    username = input('Username:')
    password = getpass('Password:')

    otp_attempt = getpass('MFA OTP:')
    session_ui = aviaryUI.init_session(args, username, password, otp_attempt)
    headers = {}

    process(args, session_ui, headers)


if __name__ == "__main__":
    main()
