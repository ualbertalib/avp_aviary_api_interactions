##############################################################################################
# desc: exploratory script to download files attached to Aviary content (audio/video only NOT transcripts, index, and supplemental files)
#       exploratory / proof-of-concept code
# usage:
#       python3 aviary_api_experimental_media_download_v2024-11-08.py --server ${SERVER_URL} --output_dir /tmp/  --media_id ${ID}
#       * [Create API Key and store](https://coda.aviaryplatform.com/edit-user-profile-83#_luHGN)
#           * export AVIARY_API_KEY=string_from step above
#           * export AVIARY_API_ORGANIZATION_ID=128
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
    parser.add_argument('--force_download',
                        action=argparse.BooleanOptionalAction,
                        help='Modifies to allow downloads when is_downloadable is False.')
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

def get_media_item(session, args):

    try:
        item_json = None
        item = aviaryApi.get_media_item(args, session, args.media_id)
        item_json = json.loads(item)
        if "errors" in item_json['data']:
            logging.error(f"Media lookup error for ID: {args.media_id} with error {item_json}")
        logging.info(f"Media : {item_json}")
    except Exception as e:
        logging.error(f"Media id: {args.media_id} Exception: {e}")
        traceback.print_exc()
    finally:
        return item_json

def download_media(session, args, item_json):
    url = item_json['data']['media_download_url']
    filename = url.rsplit('/', 1)[-1].split('?')[0]
    # or use item_json['data']['display_name']
    aviaryUtilities.download_file(session, url, filename, args.output_dir)


def download_media_simple(session, args, item_json):
    if item_json['data']['is_downloadable'] is True:
        download_media(session, args, item_json)
    else:
        logging.error(f"Media id: {args.media_id} is not downloadable without changing 'is_downloadable'.")


def download_media_with_downloadable_reset(session, args, item_json):
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
        logging.info(f"Media before is_downloadable change: {item_json}")
        if original_is_downloadable is False:
            item = update_media_downloadable(session, args.server, args.media_id, True)
            item_json = json.loads(item)
            logging.info(f"Media after is_downloadable set: {item_json}")
            current_is_downloadable = item_json['data']['is_downloadable']

        download_media(session, args, item_json)

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

        item_json = get_media_item(session, args)
        if args.force_download is True:
            text = input("Use with SANDBOX items only!!! Code may modify permissions (is_downloadable). Continue (Y/n)?")
            if (text == "Y"):
                print("Downloading media with is_downloadable reset.")
                download_media_with_downloadable_reset(session, args, item_json)
        else:
            download_media_simple(session, args, item_json)


#
def main():

    args = parse_args()

    logging.getLogger().setLevel(args.logging_level)

    session = aviaryApi.init_session_api_key(args.server)

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    process(args, session)


if __name__ == "__main__":
    main()
