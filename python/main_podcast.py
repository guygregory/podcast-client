# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.

import argparse
import json
import dataclasses
import uuid
import urllib3
from datetime import datetime
from termcolor import colored
from microsoft_client_podcast.podcast_client import PodcastClient
from microsoft_client_podcast.tempfile_client import TempFileClient

ARGUMENT_HELP_CONTENT_FILE_AZURE_BLOB_URL = (
    'Input file url, supported formats are .pdf and .txt. '
    'The file should be publicly accessible or accessible with a SAS token.')

ARGUMENT_HELP_CONTENT_FILE_PATH = (
    'Path to a file containing the podcast content, the file will be uploaded by API, supported files: .pdf, .txt'
    'If this argument is provided, the content will be read from the specified file instead of using a URL.'
)

ARGUMENT_HELP_EXPIRES_AFTER_IN_MINS = (
    'The expiration time in minutes for the uploaded temp file. '
    'If not specified, the default expiration time will be applied.'
)

ARGUMENT_HELP_CONTENT_FILE_TEMP_FILE_ID = (
    'The temp file ID containing the podcast content, supported formats are .pdf and .txt. '
    'If this argument is provided, the content will be read from the specified temp file instead of using a URL.'
)

ARGUMENT_HELP_UPLOAD_TEMP_FILE = (
    'Flag indicating whether to upload the content file as a temp file. '
    'If set to true, the content will be uploaded as a temp file instead of using a URL.'
)

ARGUMENT_HELP_BASE64_CONTENT_FILE_PATH = (
    'Path to a file containing the base64-encoded content for the podcast, the file will be uploaded by Base64Text property with base64-encoded content. '
    'If this argument is provided, the content will be read from the specified file instead of using a URL.'
)

ARGUMENT_HELP_TARGET_LOCALE = (
    'The locale of the podcast. Locale code follows BCP-47. You can find the text to speech locale list '
    'here https://learn.microsoft.com/azure/ai-services/speech-service/language-support?tabs=tts.'
)

ARGUMENT_HELP_ADDITIONAL_INSTRUCTIONS = (
    'The focus of the podcast, which can help guide the content generation. '
    'For example, you can specify "technology" or "health".'
)

ARGUMENT_HELP_VOICE_NAME = (
    'The voice name to be used for TTS synthesis. You can find the voice name list '
    'here https://learn.microsoft.com/azure/ai-services/speech-service/voice-list?tabs=tts.'
)

ARGUMENT_HELP_MULTI_TALKER_VOICE_SPEAKER_NAMES = (
    'The multi-talker voice speaker names, separated by comma, to be used for TTS synthesis.'
)

ARGUMENT_HELP_GENDER_PREFERENCE = (
    'Gender preference of the podcast voice. Possible values are Female/Male.'
)

ARGUMENT_HELP_LENGTH = (
    'The length of the podcast. Possible values are VeryShort/Short/Medium/Long/VeryLong.'
)

ARGUMENT_HELP_HOST = (
    'The host configuration of the podcast. Possible values are OneHost/TwoHosts.'
)

ARGUMENT_HELP_STYLE = (
    'The style of the podcast. Possible values are Default/Professional/Casual.'
)

def handle_create_generation_and_wait_until_terminated(args):

    tempfile_client = TempFileClient(
        region=args.region,
        sub_key=args.sub_key,
        api_version=args.api_version,
    )

    content_file_temp_file_id = None
    if args.content_file_temp_file_id is not None:
        content_file_temp_file_id = args.content_file_temp_file_id
    elif args.upload_with_temp_file:
        if args.content_file_path is None:
            raise ValueError("Please provide a content file path when uploading with temp file.")
        success, error, temp_file = tempfile_client.request_upload_temp_file(
            file_path=args.content_file_path)
        if not success:
            print(colored(f"Failed to upload temp file from path {args.content_file_path} with error: {error}", 'red'))
            return False, error, None
        content_file_temp_file_id = temp_file.id

    # If base64_content_file_path is provided, use it as content_file_path for base64 upload
    content_file_path = args.content_file_path
    if args.base64_content_file_path is not None:
        content_file_path = args.base64_content_file_path

    podcast_client = PodcastClient(
        region=args.region,
        sub_key=args.sub_key,
        api_version=args.api_version,
    )

    success, error, generation = podcast_client.create_generation_and_wait_until_terminated(
        target_locale=args.target_locale,
        content_file_azure_blob_url=args.content_file_azure_blob_url,
        content_file_path=content_file_path,
        content_file_temp_file_id=content_file_temp_file_id,
        voice_name=args.voice_name,
        multi_talker_voice_speaker_names=args.multi_talker_voice_speaker_names,
        gender_preference=args.gender_preference,
        length=args.length,
        host=args.host,
        style=args.style,
        additional_instructions=args.additional_instructions
    )
    if not success:
        return
    print(colored("successfull generated podcast.", "green"))
    if args.upload_with_temp_file:
        tempfile_client.request_delete_temp_file(file_id=content_file_temp_file_id)

def handle_request_get_generation_api(args):
    client = PodcastClient(
        region=args.region,
        sub_key=args.sub_key,
        api_version=args.api_version,
    )

    success, error, generation = client.request_get_generation(
        generation_id=args.id,
    )
    if not success:
        print(colored(f"Failed to request get translation API with error: {error}", 'red'))
        return
    if generation is None:
        print(colored("Generation not found", 'yellow'))
    else:
        print(colored("succesfully get generation:", 'green'))
        json_formatted_str = json.dumps(dataclasses.asdict(generation), indent=2)
        print(json_formatted_str)

def handle_request_list_generations_api(args):
    client = PodcastClient(
        region=args.region,
        sub_key=args.sub_key,
        api_version=args.api_version,
    )

    success, error, generations = client.request_list_generations()
    if not success:
        print(colored(f"Failed to request list generation API with error: {error}", 'red'))
        return
    print(colored("succesfully list generations:", 'green'))
    json_formatted_str = json.dumps(dataclasses.asdict(generations), indent=2)
    print(json_formatted_str)

def handle_request_delete_generation_api(args):
    client = PodcastClient(
        region=args.region,
        sub_key=args.sub_key,
        api_version=args.api_version,
    )

    success, error = client.request_delete_generation(args.id)
    if not success:
        print(colored(f"Failed to request delete generation API with error: {error}", 'red'))
        return
    print(colored("succesfully delete generation.", 'green'))

def handle_upload_temp_file(args):
    client = TempFileClient(
        region=args.region,
        sub_key=args.sub_key,
        api_version=args.api_version,
    )

    success, error, temp_file = client.request_upload_temp_file(
        file_path=args.file_path,
        expires_after_in_mins=args.expires_after_in_mins
    )
    if not success:
        print(colored(f"Failed to upload temp file with error: {error}", 'red'))
        return
    
    print(colored("Successfully uploaded temp file:", 'green'))
    json_formatted_str = json.dumps(dataclasses.asdict(temp_file), indent=2)
    print(json_formatted_str)

def handle_list_temp_files(args):
    client = TempFileClient(
        region=args.region,
        sub_key=args.sub_key,
        api_version=args.api_version,
    )

    success, error, temp_files = client.request_list_temp_files()
    if not success:
        print(colored(f"Failed to list temp files with error: {error}", 'red'))
        return
    
    print(colored("Successfully listed temp files:", 'green'))
    json_formatted_str = json.dumps(dataclasses.asdict(temp_files), indent=2)
    print(json_formatted_str)

def handle_get_temp_file(args):
    client = TempFileClient(
        region=args.region,
        sub_key=args.sub_key,
        api_version=args.api_version,
    )

    success, error, temp_file = client.request_get_temp_file(
        file_id=args.id
    )
    if not success:
        print(colored(f"Failed to get temp file with error: {error}", 'red'))
        return
    if temp_file is None:
        print(colored("Temp file not found", 'yellow'))
    else:
        print(colored("Successfully retrieved temp file:", 'green'))
        json_formatted_str = json.dumps(dataclasses.asdict(temp_file), indent=2)
        print(json_formatted_str)

def handle_delete_temp_file(args):
    client = TempFileClient(
        region=args.region,
        sub_key=args.sub_key,
        api_version=args.api_version,
    )

    success, error = client.request_delete_temp_file(file_id=args.id)
    if not success:
        print(colored(f"Failed to delete temp file with error: {error}", 'red'))
        return
    print(colored("Successfully deleted temp file.", 'green'))

root_parser = argparse.ArgumentParser(
    prog='main_podcast.py',
    description='Generate podcast audio/video from text input using Microsoft Podcast API.',
    epilog='Microsoft Podcast Generation Sample'
)

root_parser.add_argument("--region", required=True, help="specify speech resource region.")
root_parser.add_argument("--sub_key", required=True, help="specify speech resource subscription key.")
root_parser.add_argument("--api_version", required=True, help="specify API version.")
sub_parsers = root_parser.add_subparsers(required=True, help='subcommand help')

podcast_parser = sub_parsers.add_parser(
    'create_generation_and_wait_until_terminated',
    help='Create podcast generation with pdf/txt file blob url.')
podcast_parser.add_argument('--content_file_azure_blob_url', required=False, type=str, help=ARGUMENT_HELP_CONTENT_FILE_AZURE_BLOB_URL)
podcast_parser.add_argument('--content_file_path', required=False, type=str, help=ARGUMENT_HELP_CONTENT_FILE_PATH)
podcast_parser.add_argument('--base64_content_file_path', required=False, type=str, help=ARGUMENT_HELP_BASE64_CONTENT_FILE_PATH)
podcast_parser.add_argument('--upload_with_temp_file', required=False, type=bool, help=ARGUMENT_HELP_UPLOAD_TEMP_FILE)
podcast_parser.add_argument('--content_file_temp_file_id', required=False, type=str, help=ARGUMENT_HELP_CONTENT_FILE_TEMP_FILE_ID)
podcast_parser.add_argument('--target_locale', required=False, type=str, help=ARGUMENT_HELP_TARGET_LOCALE)
podcast_parser.add_argument('--voice_name', required=False, type=str, help=ARGUMENT_HELP_VOICE_NAME)
podcast_parser.add_argument('--multi_talker_voice_speaker_names', required=False, type=str, help=ARGUMENT_HELP_MULTI_TALKER_VOICE_SPEAKER_NAMES)
podcast_parser.add_argument('--gender_preference', required=False, type=str, help=ARGUMENT_HELP_GENDER_PREFERENCE)
podcast_parser.add_argument('--length', required=False, type=str, help=ARGUMENT_HELP_LENGTH)
podcast_parser.add_argument('--host', required=False, type=str, help=ARGUMENT_HELP_HOST)
podcast_parser.add_argument('--style', required=False, type=str, help=ARGUMENT_HELP_STYLE)
podcast_parser.add_argument('--additional_instructions', required=False, type=str, help=ARGUMENT_HELP_ADDITIONAL_INSTRUCTIONS)
podcast_parser.set_defaults(func=handle_create_generation_and_wait_until_terminated)

podcast_parser = sub_parsers.add_parser('get', help='Request get generation API.')
podcast_parser.add_argument('--id', required=True, type=str, help='Generation ID.')
podcast_parser.set_defaults(func=handle_request_get_generation_api)

podcast_parser = sub_parsers.add_parser('list', help='Request list generations API.')
podcast_parser.set_defaults(func=handle_request_list_generations_api)

podcast_parser = sub_parsers.add_parser('delete', help='Request delete generation API.')
podcast_parser.add_argument('--id', required=True, type=str, help='Generation ID.')
podcast_parser.set_defaults(func=handle_request_delete_generation_api)

# Add these command parsers before "args = root_parser.parse_args()"
podcast_parser = sub_parsers.add_parser('upload_temp_file', help='Upload a temp file.')
podcast_parser.add_argument('--file_path', required=True, type=str, help=ARGUMENT_HELP_CONTENT_FILE_PATH)
podcast_parser.add_argument('--expires_after_in_mins', required=False, type=int, help=ARGUMENT_HELP_EXPIRES_AFTER_IN_MINS)
podcast_parser.set_defaults(func=handle_upload_temp_file)

podcast_parser = sub_parsers.add_parser('list_temp_files', help='List all temp files.')
podcast_parser.set_defaults(func=handle_list_temp_files)

podcast_parser = sub_parsers.add_parser('get_temp_file', help='Get details of a specific temp file.')
podcast_parser.add_argument('--id', required=True, type=str, help="Temp file ID")
podcast_parser.set_defaults(func=handle_get_temp_file)

podcast_parser = sub_parsers.add_parser('delete_temp_file', help='Delete a temp file.')
podcast_parser.add_argument('--id', required=True, type=str, help="Temp file ID")
podcast_parser.set_defaults(func=handle_delete_temp_file)

args = root_parser.parse_args()
args.func(args)
