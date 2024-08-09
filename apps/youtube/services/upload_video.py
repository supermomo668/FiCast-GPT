"""
YouTube Video Uploader Script

This script uploads a video to YouTube using the YouTube Data API. It includes
retry logic for certain errors and uses environment variables for configuration.

Ensure you have a .env file with the following variables:
    CLIENT_SECRETS_FILE=<client secret file path>
    YOUTUBE_API_SERVICE_NAME="youtube"
    YOUTUBE_API_VERSION="v3"
    YOUTUBE_SCOPES="https://www.googleapis.com/auth/youtube.upload"
"""

import os
import random
import time
import pathlib
import argparse
from typing import Optional, List
from dotenv import load_dotenv

import httplib2
from google_auth_oauthlib.flow import Flow

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# Load environment variables from .env file
load_dotenv()

# Environment variable setup
CLIENT_SECRETS_FILE = pathlib.Path(os.getenv("CLIENT_SECRETS_FILE", "client_secret.json")).expanduser()
SCOPES = [
    os.getenv("YOUTUBE_SCOPES", 'https://www.googleapis.com/auth/youtube.upload')
]
API_SERVICE_NAME = os.getenv("YOUTUBE_API_SERVICE_NAME", 'youtube')
API_VERSION = os.getenv("YOUTUBE_API_VERSION", 'v3')
REDIRECT_URI = os.getenv("REDIRECT_URI", 'http://localhost:3000')

httplib2.RETRIES = 1
MAX_RETRIES = 10
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

def get_authenticated_service():
    """
    Authenticate and return a service object for the YouTube API.
    """
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES,
        redirect_uri = REDIRECT_URI
    )
        # Tell the user to go to the authorization URL.
    auth_url, _ = flow.authorization_url(prompt='consent')

    print('Please go to this URL: {}'.format(auth_url))

    # The user will get an authorization code. This code is used to get the
    # access token.
    code = input('Enter the authorization code: ')
    flow.fetch_token(code=code)

    # You can use flow.credentials, or you can just get a requests session
    # using flow.authorized_session.
    session = flow.authorized_session()
    print(session.get('https://www.googleapis.com/userinfo/v2/me').json())
    return session

def initialize_upload(youtube, file_path: str, title: str, description: str, category: str, keywords: str, privacy_status: str):
    """
    Initialize and start the upload process.
    """
    tags = keywords.split(',') if keywords else None

    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': category,
        },
        'status': {
            'privacyStatus': privacy_status
        }
    }

    insert_request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
    )
    resumable_upload(insert_request)

def resumable_upload(request):
    """
    Perform a resumable upload with retry logic for certain errors.
    """
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print('Uploading file...')
            status, response = request.next_chunk()
            if response:
                if 'id' in response:
                    print(f'Video id "{response["id"]}" was successfully uploaded.')
                else:
                    raise Exception(f'The upload failed with an unexpected response: {response}')
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = f'A retriable HTTP error {e.resp.status} occurred:\n{e.content}'
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = f'A retriable error occurred: {e}'

        if error:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                raise Exception('No longer attempting to retry.')

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print(f'Sleeping {sleep_seconds} seconds and then retrying...')
            time.sleep(sleep_seconds)

def main():
    """
    Parse command-line arguments and initiate the YouTube video upload.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True, default="data/samples/david_sinclair-20240805103612560.mp4", help='Video file to upload')
    parser.add_argument('--title', help='Video title', default='Test Title')
    parser.add_argument('--description', help='Video description', default='Test Description')
    parser.add_argument('--category', default='22', help='Numeric video category. See https://developers.google.com/youtube/v3/docs/videoCategories/list')
    parser.add_argument('--keywords', help='Video keywords, comma separated', default='')
    parser.add_argument('--privacyStatus', choices=['public', 'private', 'unlisted'], default='private', help='Video privacy status.')
    args = parser.parse_args()

    youtube = get_authenticated_service()

    try:
        initialize_upload(youtube, args.file, args.title, args.description, args.category, args.keywords, args.privacyStatus)
    except HttpError as e:
        print(f'An HTTP error {e.resp.status} occurred:\n{e.content}')

if __name__ == '__main__':
    main()
