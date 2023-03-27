"""
aviary.api
~~~~~~~~~~

this module implements the AVP Aviary API client.

"""

from urllib.parse import urljoin
import requests

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
    print(f"{response.request.url}")
    #print(response.__dict__)
    #print(response.content)
    return response.content


#
def get_collection_resources(args, session, id):
    response = session.get(
        urljoin(args.server, 'api/v1/collections/' + str(id) + '/resources')
    )
    print(f"{response.request.url}")
    #print(response.__dict__)
    #print(response.content)
    return response.content


#
def get_resource_item(args, session, id):
    response = session.get(
        urljoin(args.server, 'api/v1/resources/' + str(id))
    )
    print(f"{response.request.url}")
    #print(response.__dict__)
    #print(response.content)
    return response.content


#
def get_media_item(args, session, id):
    response = session.get(
        urljoin(args.server, 'api/v1/media_files/' + str(id))
    )
    print(f"{response.request.url}")
    #print(response.__dict__)
    #print(response.content)
    return response.content

