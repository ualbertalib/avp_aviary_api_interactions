"""
aviary.api
~~~~~~~~~~

this module implements the AVP Aviary API client.

"""

from urllib.parse import urljoin
from requests.adapters import HTTPAdapter, Retry

import datetime
import json
import logging
import os
import requests
import traceback

# ToDo: Refine from quick proof-of-concept code
# * replace args in function definitions




class MissingEnvironmentVariable(Exception):
    def __init__(self, variable_name):
        self.variable_name = variable_name
        self.message = f"The environment variable '{self.variable_name}' is missing."
        super().__init__(self.message)


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


# initialize a session with API endpoint
def init_session_api_key(server, organization_id=None):

    retry_strategy = Retry(
        total=5,
        backoff_factor=1, # Time between retries will be 2^(retry count) * backoff_factor status
        status_forcelist=[429, 500, 502, 503, 504], # Retry on these status codes
        #allowed_methods=["HEAD", "GET", "OPTIONS"] # Methods to retry
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)

    if 'AVIARY_API_KEY' not in os.environ:
        raise MissingEnvironmentVariable('AVIARY_API_KEY')

    session = requests.Session()
    
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    auth_endpoint = 'api/v1/auth/sign_in'

    response = session.post(
        urljoin(server, auth_endpoint),
        headers={'Content-Type': 'application/json', 'Authorization': os.getenv('AVIARY_API_KEY')}
    )
    response.raise_for_status()

    # aviary headers for auth:
    # assumes first org in the list and user only belongs to one org
    # https://www.aviaryplatform.com/api/v1/documentation#jump-Authorization-Authorization_3A_2Fapi_2Fv1_2Fauth_2Fsignin
    if organization_id is None:
        logging.debug(f"Session response: {response.json()}")
        if 'AVIARY_API_ORGANIZATION_ID' in os.environ:
            organization_id = os.getenv('AVIARY_API_ORGANIZATION_ID')
        else:
            organization_id = f"{response.json()['data']['organizations'][0]['id']}"
            # raise MissingEnvironmentVariable('AVIARY_API_OEGANIZATION_ID')
    auth = {
        'Authorization': os.getenv('AVIARY_API_KEY'),
        'organization-id': organization_id
    }
    session.headers.update(auth)
    return session


#
def get_collection_list(args, session, page_number=1, page_size=10):
    query_string = f"?page_number={page_number}&page_size={page_size}"
    response = session.get(
        urljoin(args.server, 'api/v1/collections' + query_string)
    )
    logging.info(f"{response.request.url}")
    logging.debug(response.__dict__)
    # print(response.content)
    response.raise_for_status()
    return response.content


#
def get_collection_metadata(args, session, id):
    response = session.get(
        urljoin(args.server, 'api/v1/collections/' + id + "/metadata")
    )
    logging.info(f"{response.request.url}")
    logging.debug(response.__dict__)
    # print(response.content)
    response.raise_for_status()
    return response.content



# https://www.aviaryplatform.com/api/v1/documentation
# Page numbers start at 1 (not 0) and max page size is 100
def get_collection_resources(args, session, id, page_number=1, page_size=100):
    query_string = f"?page_number={page_number}&page_size={page_size}"
    response = session.get(
        urljoin(args.server, 'api/v1/collections/' + str(id) + '/resources'+ query_string)
    )
    logging.info(f"{response.request.url}")
    logging.debug(response.__dict__)
    # print(response.content)
    response.raise_for_status()
    return response.content


#
def get_resource_item(args, session, id):
    response = session.get(
        urljoin(args.server, 'api/v1/resources/' + str(id))
    )
    logging.info(f"{response.request.url}")
    logging.debug(response.__dict__)
    # print(response.content)
    response.raise_for_status()
    return response.content


#
def get_media_item(args, session, id):
    response = session.get(
        urljoin(args.server, 'api/v1/media_files/' + str(id))
    )
    logging.info(f"{response.request.url}")
    logging.debug(response.__dict__)
    # logging.debug(response.content)
    response.raise_for_status()
    return response.content


#
def get_transcripts_item(args, session, id):
    response = session.get(
        urljoin(args.server, 'api/v1/transcripts/' + str(id))
    )
    logging.info(f"{response.request.url}")
    # print(response.__dict__)
    # print(response.content)
    response.raise_for_status()
    return response.content


# Deprecated: 2024-03-25
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
    response.raise_for_status()
    return response.content

#
def get_supplemental_files_item(args, session, id):
    response = session.get(
        urljoin(args.server, 'api/v1/supplemental_files/' + str(id))
    )
    logging.info(f"{response.request.url}")
    # print(response.__dict__)
    # print(response.content)
    response.raise_for_status()
    return response.content


#
def download_indexes_item(session, index, path):

    if 'export' not in index['data'] :
        logging.error(f"JSON key {index} {path}")
    else:
        for key, value in index['data']['export'].items() :

            if ( 'file_name' in value ):
                file_name = value['file_name']
            else:
                # file_name sometimes "null" / "None"
                file_name = f"{index['data']['id']}.webvtt"
                logging.warning(f"Missing index file name in metadata {index}: assigning a default name {file_name}")

            if ( 'file' in value ):
                local_file_path = os.path.join(path, file_name)
                url = value['file']

                logging.info(f"{file_name} {value['file_content_type']}")

                export_file(session, url, local_file_path)
            else:
                logging.error(f"Missing index file in metadata {index}")


#
def download_supplemental(session, supplemental_file, path):

    file_name = supplemental_file['data'].get(
        'associated_file_file_name',
        f"{supplemental_file['data']['id']}"
        )
    if 'associated_file_file_name' not in supplemental_file['data']:
        logging.error(f"Missing file name in metadata {supplemental_file}")

    local_file_path = os.path.join(path, file_name)
    url = supplemental_file['data']['file']

    logging.info(f"{local_file_path} {supplemental_file}")

    export_file(session, url, local_file_path) 


#
def download_transcript(session, transcript, path):
    
    for key, value in transcript['data']['export'].items():

        file_name = value.get('file_name', f"{transcript['data']['id']}.{key}")
        if 'file_name' not in value:
            logging.warning(f"Missing file name in metadata {transcript}")

        local_file_path = os.path.join(path, file_name)
        url = value['file']
    
        logging.info(f"{local_file_path} {value}")

        export_file(session, url, local_file_path) 


#
def export_file(session, url, local_file_path):
    logging.info(f"Download URL: {url}")

    with session.get(url, stream=True) as response:
        response.raise_for_status()
        with open(local_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

    logging.info(f"Stored: {local_file_path}")
