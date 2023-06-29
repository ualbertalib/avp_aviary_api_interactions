# set of tools to interact with the Aviary Web UI

import filetype
import json
import logging
import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime as dt
from datetime import timedelta as timedelta
from urllib.parse import urljoin

from aviary import utilities as aviaryUtilities


def get_auth_from_file(args):
    # copy the cookie from an authenticated Aviary Web UI session (via the browser dev tools -> network --> request --> cookie)
    # write to a file (this will be the input file)
    # todo: replace with a python auth script that can handle the MFA request
    with open(args.session_cookie, 'r', encoding="utf-8", newline='') as input_file:
        return input_file.read().rstrip("\n")


# assume the auth cookie is captured from a browser session (kludge) and stored in a file
# this is required to authenticate with the Web UI (different from the API)
def build_session_header(args, token, url_path, session):
    # get the x-csrf-token
    headers = {"cookie": token}
    response = session.get(
        args.server + url_path,
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


# Auth via the Web UI username/password form and subsequent two-factor authentication form
def init_session(args, username, password, otp_attempt):
    session = requests.Session()
    response = session.get(args.server)
    logging.info(f"URL: {response.request.url}")
    logging.info(f"Status: {response.status_code}")
    # logging.info(f"Content: {response.content}")
    logging.info(f"Headers: {response.headers}")
    soup = BeautifulSoup(response.content, features="lxml")
    authenticity_token = soup.find('input', {'name': 'authenticity_token'})['value']
    data = {
        'authenticity_token': authenticity_token,
        'user[email]': username,
        'user[password]': password,
        'user[remember_me]': '0',
        'site_url': args.server,
        'commit': "Sign in"
    }
    url = urljoin(args.server, 'users/sign_in')
    response = session.post(
        url=urljoin(args.server, 'users/sign_in'),
        data=data
    )
    logging.info(f"URL: {response.request.url}")
    logging.info(f"Status: {response.status_code}")
    # logging.info(f"Body: {response.request.body}")
    # logging.info(f"Headers: {response.headers}")
    # logging.info(f"Content: {response.content}")
    # /html/body/div[2]/div[4]/div/main/div/div[3]/div/div[1]/div[2]/form/input
    soup = BeautifulSoup(response.content, features="lxml")
    authenticity_token_elements = soup.find_all('input', {'name': 'authenticity_token'})
    for token_element in authenticity_token_elements:
        logging.info(f"{token_element['value']}")
    # find the authenticity_token in the correct form
    # todo: add durability / error handling
    # uncertain if [2] will be the correct token - works at present
    authenticity_token = soup.find_all('input', {'name': 'authenticity_token'})[2]['value']
    data = {
        'authenticity_token': authenticity_token,
        'user[otp_attempt]': otp_attempt,
        'commit': "Login"
    }
    response = session.post(
        url=urljoin(args.server, 'users/sign_in'),
        data=data
    )
    logging.info(f"URL: {response.request.url}")
    logging.info(f"Status: {response.status_code}")
    # logging.info(f"Body: {response.request.body}")
    # logging.info(f"Headers: {response.headers}")
    # logging.info(f"Content: {response.content}")

    return session


#
def download_transcript(args, session, id, headers=''):
    url = urljoin(args.server, '/transcripts/export/webvtt/' + str(id))
    filename = id + '.webvtt'
    aviaryUtilities.download_file(session, url, filename, path=args.output_path, headers=headers)
    # todo: test if a proper export or an html page


def download_index(args, session, id, headers=''):
    url = urljoin(args.server, '/indexes/export//' + str(id))  # double slash is intentional; match Web UI
    filename = id + '.webvtt'
    aviaryUtilities.download_file(session, url, filename, path=args.output_path, headers=headers)
    # todo: test if a proper export or an html page


# retieve CSRF token
def build_resource_public_access_urls_index_header(session, url):
    # get the x-csrf-token
    response = session.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, features="lxml")
    csrf_tokens = soup.find_all('meta', {'name': 'csrf-token'})
    for token_element in csrf_tokens:
        logging.info(f"{token_element['content']}")
    csrf_token = soup.find('meta', {'name': 'csrf-token'})['content']
    headers = {
        "X-Csrf-Token": csrf_token,
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/json, text/javascript, */*; q=0.01"
    }
    logging.info(headers)
    return headers


# Start: resource view & media player hover menu "share" --> Resource Public Access URL --> expiring url
#   * https://ualberta.aviaryplatform.com/collections/1797/collection_resources/96596
# To add expiring download URL
#   * https://ualberta.aviaryplatform.com/encrypted_info?action=encryptedInfo&collection_resource_id=96596&duration=06-26-2023+00%3A00+-+06-26-2023+00%3A05
#       &auto_play=false&start_time=&start_time_status=false&end_time=00%3A00%3A00&end_time_status=false&downloadable=1&type=limited_access_url
# The resulting URL (needs the `access` portion otherwise will not display the download link on the media player):
#   * https://ualberta.aviaryplatform.com/r/mk6542km08?access=jZ-jHl9T6Wem5cyFWC3qSg==#
def download_media_setup_expiring(session, server, collection_id, collection_resource_id, duration):
    url = urljoin(server, f"collections/{collection_id}/collection_resources/{collection_resource_id}")
    response = session.get(url)
    logging.info(f"Resource: {response}")
    url = urljoin(server, 'encrypted_info')
    params = {
        "action": "encryptedInfo",
        "collection_resource_id": collection_resource_id,
        # "duration": "06-26-2023 00:00 - 06-29-2023 00:05",
        "duration": str(duration),
        "auto_play": "false",
        "start_time": "",
        "start_time_status": "false",
        "end_time": "00:00:00",
        "end_time_status": "false",
        "downloadable": "1",
        "type": "limited_access_url"
    }
    logging.info(f"Create expiring request: {params}")
    response = session.get(url, params=params)
    logging.info(f"Create expiring request: {response.request.url}")
    logging.info(f"Create expiring link: {response}")
    logging.info(f"Create expiring link: {response.content}")
    # logging.info(f"Create expiring link: {response.headers}")
    resp = json.loads(response.content)['encrypted_data']
    return resp


# Build the duration of the expiry for the resource public access URL
def resource_public_access_duration():
    startObj = dt.now()
    # silently fails if 6 hours or less
    # change = timedelta(minutes=17)
    change = timedelta(minutes=361)
    endObj = startObj + change
    return f"{startObj.strftime('%m-%d-%Y %H:%M')} - {endObj.strftime('%m-%d-%Y %H:%M')}"


def resource_public_access_download_media(session, url, server, id, path):
    response = session.get(url)
    logging.info(f"Expiring URL response: {response}")
    url = urljoin(server, f"download_media/{id}?")
    logging.info(f"Download URL: {url}")
    with session.get(url, stream=True) as response:
        logging.info(f"Status: [{response.status_code}] Response URL: [{response.request.url}]")
        response.raise_for_status()
        filename = response.request.url.rsplit('/', 1)[-1]
        logging.info(f"Remove URL start: {filename}")
        filename = filename.split('?')[0]
        logging.info(f"Remove URL end: {filename}")
        local_file_path = os.path.join(path, filename)
        logging.info(f"Local file path: [{local_file_path}]")
        with open(local_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8191):
                f.write(chunk)
        kind = filetype.guess(local_file_path)
        if kind.mime.split("/")[0] not in ['audio', 'video']:
            raise ValueError(f"Downloaded file [{local_file_path}] mime type [{kind.mime}] is not a media file type")

        logging.info(f"Type: {kind.mime}")
        logging.info(f"Stored: {local_file_path}")
        # aviaryUtilities.download_file(session, url, filename, headers=headers)
        # logging.info(f"Download response headers: {response.headers}")
        # logging.info(f"Download request headers: {response.request.headers}")


def resource_public_access_delete(session, server, resource_id, duration):
    # get CSRF token (HTTP GET)
    url = urljoin(server, f"resource_public_access_urls/index")
    headers = build_resource_public_access_urls_index_header(session, url)
    logging.info(f"Header: {headers}")

    # retrieve list of public access urls (HTTP POST) sorted by date
    data = {
        "draw": "3",
        "order[0][column]": 8,
        "order[0][dir]": "desc",
        "start": 0,
        "length": 25,
        "search[value]": "",
        "search[regex]": "false",
    }
    url = urljoin(server, f"resource_public_access_urls/index")
    logging.info(f"Download URL: {url}")
    response = session.post(url, data=data, headers=headers)
    logging.info(f"Index: {response.url}")
    # logging.info(f"Index: {response.content}")
    list = json.loads(response.content)

    # pick the correct resource public access URL ID to delete
    resource_public_access_urls_id = ""
    for i, item in enumerate(list['data'], start=1):
        logging.info(f"Table: {item[3]} {item[8]} {item[9]} {item[10]}")

        # extract the resoruce public access url ID from a column
        # <a class="btn-sm btn-success access-edit " data-url="/public_access_urls/edit/4834" data-type="limited_access_url" href="javascript://">Edit</a>
        # <a class="btn-sm btn-danger access-delete ml-1" data-id="4834" href="javascript://">Delete</a>
        # <a class="btn-sm btn-default access-view-resource ml-1" data-id="4834" href="/collections/1797/collection_resources/96596">View Resource</a>
        button_html = item[10]
        # test if found correct: duration in item doesn't have "-"
        if (f"/collection_resources/{resource_id}\"" in button_html) and item[3] == duration.replace(" - ", " "):
            logging.info(f"Contains id[{id}]: {item[10]}")
            match = re.search(r" data-id=\"(\d+)\"", button_html)
            if match:
                resource_public_access_urls_id = match.group(1)
            break
    # delete resource public access URL
    if resource_public_access_urls_id:
        logging.info(f"Resource public access: {resource_public_access_urls_id} for resource: {id}")
        url = urljoin(server, "public_access_urls/update_info")
        params = {
            "action_type": "delete_access",
            "id": resource_public_access_urls_id
        }
        logging.info(f"Remove: {url} {params}")
        response = session.get(url, params=params)
        logging.info(f"Remove: {response}")
