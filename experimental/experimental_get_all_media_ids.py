# Try to gather all the media items
# this exists because the `resource` API only list max 10 media IDs and the WebUI export doesnt' contain IDs as of 2023-05-30

# Proof-of-concept only

from getpass import getpass
from time import sleep
import argparse
from bs4 import BeautifulSoup
import csv
import json
import logging
import requests
import os
import sys
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aviary import api as aviaryApi
from aviary import utilities as aviaryUtilities


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', required=True, help='Servername.')
    parser.add_argument('--output', required=True, help='Location to store CSV output file.')
    parser.add_argument('--session_cookie', required=True, help='The session cookie from an active .')
    parser.add_argument('--wait', required=False, help='Time to wait between API calls.', default=1.0)
    parser.add_argument('--logging_level', required=False, help='Logging level.', default=logging.WARNING)
    return parser.parse_args()


def process(args, session, headers, report_csv):
    more_pages = True
    start = 0
    length = 100
    while more_pages is True:
        try:
            # `order` is required along with start and length -- unsuer about the others
            data = {
                # "draw": 2,
                # "columns[0][data]": 0,
                # "columns[0][name]": "",
                # "columns[0][searchable]": "true",
                # "columns[0][orderable]": "true",
                # "columns[0][search][value]": "true",
                # "columns[0][search][regex]": "true",
                "order[0][column]": 1,
                "order[0][dir]": "asc",
                "start": start,
                "length": length,
                "search[value]": "",
                "search[regex]": "false",
                "called_from": ""
            }
            logging.info(data)
            response = session.post(
                args.server + "collection_resource_files/data_table.json",
                headers=headers,
                data=data
            )
            response.raise_for_status()
            start = start + length
            print(f" {start} ", end="", flush=True)
            sleep(args.wait)
            logging.debug(response)
            response_json = json.loads(response.content)
            logging.debug(response_json)
            for item in response_json['data']:
                logging.info(item)
                report_csv.writerow({
                    "media_id": item[1],
                    "collection_title": item[6],
                    "resource_id": item[7],
                    "resource_title": item[8],
                })
            if (start + length > response_json['recordsFiltered']):
                logging.info(f"Total: {response_json['recordsFiltered']}")
                more_pages = False
        except BaseException as e:
            more_pages = False
            print(f"{e}")
            traceback.print_exc()

    print(f"\n")


def build_session_header(args, input_file, session):
    # get the x-csrf-token
    headers = {"cookie": input_file.read().rstrip("\n")}
    response = session.get(
        args.server + "collection_resource_files",
        headers=headers,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.content, features="lxml")
    csrf_token = soup.find('meta', {'name': 'csrf-token'})['content']
    headers = {
        "cookie": headers['cookie'],
        "x-csrf-token": csrf_token
    }
    logging.info(headers)
    return headers

#
def main():
    args = parse_args()

    logging.getLogger().setLevel(args.logging_level)

    # copy the cookie from an authenticated Aviary Web UI session (via the browser dev tools -> network)
    # write to a file (this will be the input file)
    # todo: replace with a python auth script that can handle the MFA request
    with open(args.session_cookie, 'r', encoding="utf-8", newline='') as input_file:
        session = requests.Session()
        headers = build_session_header(args, input_file, session)
        with open(args.output, 'wt', encoding="utf-8", newline='') as output_file:
            report_csv = csv.DictWriter(output_file, fieldnames={"media_id", "collection_title", "resource_id", "resource_title"})
            report_csv.writeheader()
            process(args, session, headers, report_csv)


if __name__ == "__main__":
    main()
