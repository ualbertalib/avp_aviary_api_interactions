##############################################################################################
# desc: connect to the Aviary API and get item (collection resource, resource, media) metadata
#       exploritory / proof-of-concept code
# usage: python3 aviary_api_get_by_id.py --server ${aviary_server_name} --id ${resource_id} --type r
# license: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication
# date: June 15, 2022
##############################################################################################

# Proof-of-concept only

from getpass import getpass
import argparse
import logging

from aviary import api as aviaryApi


#
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', required=True, help='Servername.')
    parser.add_argument('--id', required=True, help='id.')
    parser.add_argument('--type', required=True, help='One letter character for type [c]ollection resources, [r]esource, [m]edia.')
    parser.add_argument('--logging_level', required=False, help='Logging level.', default=logging.DEBUG)

    return parser.parse_args()


#
def process(args, session):
    if args.type == 'c':
        item = aviaryApi.get_collection_resources(args, session, args.id)
    elif args.type == 'r':
        item = aviaryApi.get_resource_item(args, session, args.id)
    elif args.type == 'm':
        item = aviaryApi.get_media_item(args, session, args.id)
    print(item)


#
def main():
    args = parse_args()

    logging.basicConfig(level=args.logging_level)

    username = input('Username:')
    password = getpass('Password:')

    session = aviaryApi.init_session(args, username, password)

    process(args, session)


if __name__ == "__main__":
    main()
