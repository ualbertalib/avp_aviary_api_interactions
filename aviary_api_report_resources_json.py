##############################################################################################
# desc: connect to the Aviary API and get media item metadata 
#       exploritory / proof-of-concept code
# usage: python3 aviary_api_report_resources_json.py --server ${aviary_server_name} --output ${output_path}
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
import json
import requests
from aviary import api as aviaryApi

#
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', required=True, help='Servername.')
    parser.add_argument('--output', required=True, help='Location to store JSON (like) output file.')
    parser.add_argument('--wait', required=False, help='Time to wait between API calls.', type=float, default=0.1)
    return parser.parse_args()

#
def process(args, session, output_file):

  collections = aviaryApi.get_collection_list(args, session)
  collection_list = json.loads(collections)
  for collection in collection_list['data'] :
    resources = aviaryApi.get_collection_resources(args, session, collection['id'])
    #resources = aviaryApi.get_collection_resources(args, session, 2226)
    #resources = aviaryApi.get_collection_resources(args, session, 1787)
    resource_list = json.loads(resources)
    for resource in resource_list['data'] :
        if ('resource_id' in resource):
            item = aviaryApi.get_resource_item(args, session, resource['resource_id'])
            output_file.write(json.dumps(json.loads(item)))
            output_file.write("\n")
        else:
            output_file.write(json.dumps(resource))
            output_file.write("\n")
            print(resource) #error
        sleep(args.wait)


#
def main():
    args = parse_args()
    
    username = input('Username:')
    password = getpass('Password:')
    
    session = aviaryApi.init_session(args, username, password)

    with open(args.output, 'wt', encoding="utf-8", newline='') as output_file:
        process(args, session, output_file)


if __name__ == "__main__":
    main()
