"""
aviary.api
~~~~~~~~~~

this module implements the AVP Aviary API client.

"""

from urllib.parse import urljoin
import requests
import datetime
import json
import logging
import os
import requests
import traceback

# ToDo: Refine from quick proof-of-concept code
# * replace args in function definitions


# chunk size
CHUNK_SIZE = 90000000


# initialize a session with API endpoint
def init_session(args, username, password):

    session = requests.Session()
    session.auth = (username, password)

    auth_endpoint = 'api/v1/auth/sign_in'

    response = session.post(
        urljoin(args.server, auth_endpoint),
        json={'email': username, 'password': password},
        headers={'Content-Type': 'application/json'}
    )
    response.raise_for_status()

    # aviary headers for auth:
    # https://www.aviaryplatform.com/api/v1/documentation#jump-Authorization-Authorization_3A_2Fapi_2Fv1_2Fauth_2Fsignin
    auth = {
        'access-token': response.headers['access-token'],
        'client': response.headers['client'],
        'token-type': response.headers['token-type'],
        'uid': response.headers['uid']
    }
    session.headers.update(auth)
    return session


#
def get_collection_list(args, session):
    response = session.get(
        urljoin(args.server, 'api/v1/collections')
    )
    logging.info(f"{response.request.url}")
    logging.debug(response.__dict__)
    # print(response.content)
    return response.content


#
def get_collection_resources(args, session, id):
    response = session.get(
        urljoin(args.server, 'api/v1/collections/' + str(id) + '/resources')
    )
    logging.info(f"{response.request.url}")
    logging.debug(response.__dict__)
    # print(response.content)
    return response.content


#
def get_resource_item(args, session, id):
    response = session.get(
        urljoin(args.server, 'api/v1/resources/' + str(id))
    )
    logging.info(f"{response.request.url}")
    logging.debug(response.__dict__)
    # print(response.content)
    return response.content


#
def get_media_item(args, session, id):
    response = session.get(
        urljoin(args.server, 'api/v1/media_files/' + str(id))
    )
    logging.info(f"{response.request.url}")
    logging.debug(response.__dict__)
    # logging.debug(response.content)
    return response.content


# https://stackoverflow.com/questions/50994218/post-large-file-using-requests-toolbelt-to-vk
def put_media_item(args, session, item):
    content_name = os.path.basename(item['filepath'])
    content_size = os.stat(item['filepath']).st_size
    url = urljoin(args.server, 'api/v1/media_files'),
    index = 0
    offet = 0

    print(f"Uploading: [{item['filepath']}] with size [{content_size}]")

    print(str(datetime.datetime.now()) + " #################################################")
    try:
        f = open(item['filepath'], 'rb')
        while chunk := f.read(CHUNK_SIZE):
            offset = index + len(chunk)
            params = {
                "collection_resource_id": item['resource_id'],
                "access": item['access'],
                "is_360": item['is_360'],
                "filename": content_name,
                # "display_name" : item['display_name'],
            }
            files = {"media_file": chunk}
            headers = {
                'Content-Range': 'bytes %s-%s/%s' % (index, offset - 1, content_size)
            }
            print(f"Uploading: [{item['filepath']}] with Content-Range[{headers['Content-Range']}]")
            response = session.post(
                urljoin(args.server, 'api/v1/media_files'),
                params=params,
                files=files,
                headers=headers,
                timeout=120,
                verify=False
            )
            response_content = json.loads(response.content)
            if "errors" in response_content:
                print(f"ERROR: {response_content['errors']}")
                print(f"{response.request.url}")
            print(response.__dict__)
            index = offset
            response.raise_for_status()
    except Exception as e:
        print("ERROR (begin): #################################################")
        print(e)
        print("#################################################")
        print(response.__dict__)
        print("#################################################")
        print(traceback.format_exc())
        print("ERROR (end): #################################################")

    print(str(datetime.datetime.now()) + " #################################################")


# from AVP Aviary Documentation for uploading media <https://www.aviaryplatform.com/api/v1/documentation#jump-MediaFiles-_2Fapi_2Fv1_2Fmediafiles>
def read_in_chunks(file_object, CHUNK_SIZE):
    while True:
        data = file_object.read(CHUNK_SIZE)
        if not data:
            break
        yield data


# from AVP Aviary Documentation for uploading media <https://www.aviaryplatform.com/api/v1/documentation#jump-MediaFiles-_2Fapi_2Fv1_2Fmediafiles>
def upload_based_on_avp_documentation(args, session, item):

    file = item["filepath"]
    url = urljoin(args.server, 'api/v1/media_files')

    content_name = str(file)
    content_path = os.path.abspath(file)
    content_size = os.stat(content_path).st_size

    print(content_name, content_path, content_size)

    f = open(content_path, 'rb')

    index = 0
    offset = 0
    headers = {}

    for chunk in read_in_chunks(f, CHUNK_SIZE):
        offset = index + len(chunk)
        headers['Content-Range'] = "bytes %s-%s/%s" % (index, offset - 1, content_size)
        index = offset
        try:
            files = {"media_file": chunk}
            params = {
                "collection_resource_id": item['resource_id'],
                "access": item['access'],
                "is_360": item['is_360'],
                "filename": content_name,
                # "display_name" : item['display_name'],
            }
            r = session.post(url=url, files=files, params=params, headers=headers)
            print(r.json())
            print("r: %s, Content-Range: %s" % (r, headers['Content-Range']))
        except Exception as e:
            print(e)
            traceback.print_exc()


#
def get_transcripts_item(args, session, id):
    response = session.get(
        urljoin(args.server, 'api/v1/transcripts/' + str(id))
    )
    logging.info(f"{response.request.url}")
    # print(response.__dict__)
    # print(response.content)
    return response.content


# The HTTP GET request is not supported as of 2023-05-26; see https://www.aviaryplatform.com/api/v1/documentation#Indexes
# The following is a workaround - id is the media id as the media APi includes the index json
def get_indexes_item(args, session, id):
    # response = session.get(
    #    urljoin(args.server, 'api/v1/indexes/' + str(id))
    # )
    # logging.info(f"{response.request.url}")
    # print(response.__dict__)
    # print(response.content)
    media = get_media_item(args, session, id)
    media_json = json.loads(media)
    if ('data' in media_json):
        return media_json['data']['indexes']
    else:
        logging.error(f"media id:[{id}] - {media_json}")

# The GET HTTP request may now be supported: 2024-03-25
def get_indexes_item_v2(args, session, id):
    response = session.get(
        urljoin(args.server, 'api/v1/indexes/' + str(id))
    )
    logging.info(f"{response.request.url}")
    # print(response.__dict__)
    # print(response.content)
    return response.content

#
def get_supplemental_files_item(args, session, id):
    response = session.get(
        urljoin(args.server, 'api/v1/supplemental_files/' + str(id))
    )
    logging.info(f"{response.request.url}")
    # print(response.__dict__)
    # print(response.content)
    return response.content
