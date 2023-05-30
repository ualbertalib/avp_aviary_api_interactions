##############################################################################################
# desc: connect to the Aviary API and get media item metadata
#       exploritory / proof-of-concept code
# usage: python3 aviary_media_api_get.py --server ${aviary_server_name} --media_id ${media_id}
# license: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication
# date: June 15, 2022
##############################################################################################

# Proof-of-concept only

from getpass import getpass
import argparse
from aviary import api as aviaryApi


#
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', required=True, help='Servername.')
    parser.add_argument('--media_id', required=True, help='Media id.')
    return parser.parse_args()


#
def process(args, session):
    item = aviaryApi.get_media_item(args, session, args.media_id)
    print(item)


#
def main():
    args = parse_args()

    username = input('Username:')
    password = getpass('Password:')

    session = aviaryApi.init_session(args, username, password)

    process(args, session)


if __name__ == "__main__":
    main()
