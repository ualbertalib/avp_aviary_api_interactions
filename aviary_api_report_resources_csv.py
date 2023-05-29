##############################################################################################
# desc: connect to the Aviary API and get media item metadata
#       Missing 2023-03-27: pagination (no documentation) thus result only contains 100 of `N` items per collection
#       exploritory / proof-of-concept code
# usage: python3 aviary_api_report_resources_csv.py --server ${aviary_server_name} --output ${output_path}
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
import requests
from aviary import api as aviaryApi
from aviary import utilities as aviaryUtilities


#
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', required=True, help='Servername.')
    parser.add_argument('--output', required=True, help='Location to store CSV output file.')
    parser.add_argument('--wait', required=False, help='Time to wait between API calls.', default=0.1)
    return parser.parse_args()


#
def process(args, session, report_csv):
    # Get list of collections
    collections = aviaryApi.get_collection_list(args, session)
    collection_list = json.loads(collections)
    for collection in collection_list['data']:
        # Get list of resources attached to a given collection
        # Todo: this fails due to no documentated pagination in the Avairy API 2023-05-27
        resources = aviaryApi.get_collection_resources(args, session, collection['id'])
        resource_list = json.loads(resources)
        for resource in resource_list['data']:
            if ('resource_id' in resource):
                # Get resource details
                item = aviaryApi.get_resource_item(args, session, resource['resource_id'])
                report_csv.writerow(aviaryUtilities.processResourceJSON(item, resource['title']))
            else:
                print(resource)
            sleep(args.wait)
        print("Test only - pagination FAILS 2023 April due to no upstream documentation on how to paginate")


#
def main():
    args = parse_args()

    username = input('Username:')
    password = getpass('Password:')

    session = aviaryApi.init_session(args, username, password)

    with open(args.output, 'wt', encoding="utf-8", newline='') as output_file:
        report_csv = csv.DictWriter(output_file, fieldnames=aviaryUtilities._resource_csv_fieldnames)
        report_csv.writeheader()
        process(args, session, report_csv)


if __name__ == "__main__":
    main()
