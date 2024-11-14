##############################################################################################
# desc: exploratory script to download files attached to Aviary content (audio/video only NOT transcripts, index, and supplemental files)
#       exploritory / proof-of-concept code
# usage:
#       python3 aviary_api_experimental_media_download_v2024-11-08.py --server ${SERVER_URL} --output_dir /tmp/  --media_id ${ID}
# license: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication
# date: June 22, 2022
##############################################################################################

# Given a Media ID, download the attached file

# Proof-of-concept only

from urllib.parse import urljoin

import argparse
import json
import logging
import os
import sys
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aviary import api as aviaryApi
from aviary import utilities as aviaryUtilities


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', required=True, help='Server name.')
    parser.add_argument('--media_id', required=True, help='Media id.')
    parser.add_argument('--output_dir', required=True, help='Directory to store output.')
    parser.add_argument('--logging_level', required=False, help='Logging level.', default=logging.INFO)
    return parser.parse_args()


def update_media_downloadable(session, server, id, value):
    url = urljoin(server, 'api/v1/media_files/' + str(id))
    value = 'true' if (value is True) else 'false'
    params = {
        'is_downloadable': value
    }
    response = session.put(url, params=params)
    logging.info(f"{response.request.url}")
    logging.debug(f"Media change response: {response.content}")

    return response.content


def download_media(session, args):

    try:
        item = aviaryApi.get_media_item(args, session, args.media_id)
        item_json = json.loads(item)
        if "errors" in item_json['data']:
            logging.error(f"Media lookup error for ID: {args.media_id} with error {item_json}")
        logging.info(f"Media before is_downloadable change: {item_json}")
    except Exception as e:
        logging.error(f"Media id: {args.media_id} Exception: {e}")
        traceback.print_exc()

    # From https://docs.google.com/document/d/1PSr6mpO3gWr9cxp2RAKJ2jjtVCfTrmsjjWMtXnhx8_Y/edit?tab=t.0
    # Question:  Accessing downloadable files (e.g. the audio/video or supplemental file or transcript) if the item is not public and marked as not downloadable.
    # Answer from vendor:
    #   * 2 step process: not tied to permissions, is a parameter tied to a media file (y/n).
    #   * PUT for time limited download status change,
    #   * GET wasabi direct URL, Kevin recommends doing one by one.
    #   * **SILR** collection should be **excluded** from this process

    # Need is_downloadable to be true to allow present the download URL in the metadata and allow downloads
    #   * **SILR** collection should be **excluded** from this process
    # Todo: error check
    try:
        current_is_downloadable = original_is_downloadable = item_json['data']['is_downloadable']
        if original_is_downloadable is False:
            item = update_media_downloadable(session, args.server, args.media_id, True)
            item_json = json.loads(item)
            logging.info(f"Media after is_downloadable set: {item_json}")
            current_is_downloadable = item_json['data']['is_downloadable']

        url = item_json['data']['media_download_url']
        filename = url.rsplit('/', 1)[-1].split('?')[0]
        # or use item_json['data']['display_name']
        aviaryUtilities.download_file(session, url, filename, args.output_dir)

    except Exception as e:
        logging.error(f"Media id: {args.media_id} Exception: {e}")
        traceback.print_exc()

    finally:
        # todo what if exception occurs during download or after media is_download change?
        # Need is_downloadable to be set to the original value even if exception occurs
        if original_is_downloadable != current_is_downloadable:
            update_media_downloadable(session, args.server, args.media_id, original_is_downloadable)
            item = aviaryApi.get_media_item(args, session, args.media_id)
            item_json = json.loads(item)
            logging.info(f"Media after is_downloadable reset : {item_json}")

#
def process(args, session, headers=""):

    text = input("SANDBOX item only!!! Code modifies permissions. Continue (Y/n)?")
    if (text == "Y"):
        download_media(session, args)

#
def main():

    args = parse_args()

    logging.getLogger().setLevel(args.logging_level)

    session = aviaryApi.init_session_api_key(args)
  
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    process(args, session)


if __name__ == "__main__":
    main()
