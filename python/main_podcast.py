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


ARGUMENT_HELP_CONTENT_FILE_AZURE_BLOB_URL = (
    'Input file url, supported formats are .pdf and .txt. '
    'The file should be publicly accessible or accessible with a SAS token.')

ARGUMENT_HELP_PLAIN_TEXT_CONTENT_FILE_PATH = (
    'Path to a plain text file containing the podcast content, the file will be uploaded  by Text property with plain text. '
    'If this argument is provided, the content will be read from the specified file instead of using a URL.'
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
    client = PodcastClient(
        region=args.region,
        sub_key=args.sub_key,
        api_version=args.api_version,
    )

    success, error, generation = client.create_generation_and_wait_until_terminated(
        target_locale=args.target_locale,
        content_file_azure_blob_url=args.content_file_azure_blob_url,
        plain_text_content_file_path=args.plain_text_content_file_path,
        base64_content_file_path=args.base64_content_file_path,
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
    print(colored("success", "green"))

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


root_parser = argparse.ArgumentParser(
    prog='main_podcast.py',
    description='Generate podcast audio/video from text input using Microsoft Podcast API.',
    epilog='Microsoft Podcast Generation Sample'
)

root_parser.add_argument("--region", required=True, help="specify speech resource region.")
root_parser.add_argument("--sub_key", required=True, help="specify speech resource subscription key.")
root_parser.add_argument("--api_version", required=True, help="specify API version.")
sub_parsers = root_parser.add_subparsers(required=True, help='subcommand help')

translate_parser = sub_parsers.add_parser(
    'create_generation_and_wait_until_terminated',
    help='Create podcast generation with pdf/txt file blob url.')
translate_parser.add_argument('--content_file_azure_blob_url', required=False, type=str, help=ARGUMENT_HELP_CONTENT_FILE_AZURE_BLOB_URL)
translate_parser.add_argument('--plain_text_content_file_path', required=False, type=str, help=ARGUMENT_HELP_PLAIN_TEXT_CONTENT_FILE_PATH)
translate_parser.add_argument('--base64_content_file_path', required=False, type=str, help=ARGUMENT_HELP_BASE64_CONTENT_FILE_PATH)
translate_parser.add_argument('--target_locale', required=False, type=str, help=ARGUMENT_HELP_TARGET_LOCALE)
translate_parser.add_argument('--voice_name', required=False, type=str, help=ARGUMENT_HELP_VOICE_NAME)
translate_parser.add_argument('--multi_talker_voice_speaker_names', required=False, type=str, help=ARGUMENT_HELP_MULTI_TALKER_VOICE_SPEAKER_NAMES)
translate_parser.add_argument('--gender_preference', required=False, type=str, help=ARGUMENT_HELP_GENDER_PREFERENCE)
translate_parser.add_argument('--length', required=False, type=str, help=ARGUMENT_HELP_LENGTH)
translate_parser.add_argument('--host', required=False, type=str, help=ARGUMENT_HELP_HOST)
translate_parser.add_argument('--style', required=False, type=str, help=ARGUMENT_HELP_STYLE)
translate_parser.add_argument('--additional_instructions', required=False, type=str, help=ARGUMENT_HELP_ADDITIONAL_INSTRUCTIONS)
translate_parser.set_defaults(func=handle_create_generation_and_wait_until_terminated)

translate_parser = sub_parsers.add_parser('get', help='Request get generation API.')
translate_parser.add_argument('--id', required=True, type=str, help='Generation ID.')
translate_parser.set_defaults(func=handle_request_get_generation_api)

translate_parser = sub_parsers.add_parser('list', help='Request list generations API.')
translate_parser.set_defaults(func=handle_request_list_generations_api)

translate_parser = sub_parsers.add_parser('delete', help='Request delete generation API.')
translate_parser.add_argument('--id', required=True, type=str, help='Generation ID.')
translate_parser.set_defaults(func=handle_request_delete_generation_api)

args = root_parser.parse_args()
args.func(args)
