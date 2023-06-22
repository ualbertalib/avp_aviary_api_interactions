# set of tools to interact with the Aviary Web UI

import logging
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup


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
