# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.

import urllib3
import orjson
import uuid
import requests
import locale
import json
import dataclasses
from termcolor import colored
from datetime import datetime
from urllib3.util import Url
from microsoft_speech_client_common.client_common_const import (
    HTTP_HEADERS_OPERATION_LOCATION
)
from microsoft_speech_client_common.client_common_enum import (
    OperationStatus
)
from microsoft_client_podcast.podcast_enum import (
    ContentSourceKind,
    PodcastHostKind,
    PodcastGenderPreferenceKind,
    PodcastLengthKind,
    PodcastStyleKind,
    ContentFileFormatKind,
)
from microsoft_client_podcast.podcast_dataclass import (
    ContentSourceKind,
    PodcastScriptGenerationConfig,
)
from microsoft_client_podcast.podcast_const import (
    MAX_PLAIN_TEXT_LENGTH,
    MAX_BASE64_TEXT_LENGTH,
    MAX_CONTENT_FILE_SIZE,
)
from microsoft_speech_client_common.client_common_dataclass import (
    OperationDefinition
)

from microsoft_speech_client_common.client_common_util import (
    dict_to_dataclass, append_url_args
)
from microsoft_speech_client_common.client_common_client_base import (
    SpeechLongRunningTaskClientBase
)
from microsoft_client_podcast.podcast_dataclass import (
    PodcastGenerationDefinition, PodcastContent, PodcastGenerationOutput, PodcastTtsConfig, PagedGenerationDefinition
)
import time
import base64
import os


class PodcastClient(SpeechLongRunningTaskClientBase):
    URL_PATH_ROOT = "podcast"
    URL_SEGMENT_NAME_GENERATIONS = "generations"

    def __init__(self, region, sub_key, api_version):
        super().__init__(
            region=region,
            sub_key=sub_key,
            api_version=api_version,
            service_url_segment_name=self.URL_PATH_ROOT,
            long_running_tasks_url_segment_name=self.URL_SEGMENT_NAME_GENERATIONS
        )

    def create_generation_and_wait_until_terminated(
        self,
        target_locale: locale,
        content_file_azure_blob_url: Url,
        content_file_path: str = None,
        content_file_temp_file_id: str = None,
        voice_name: str = None,
        multi_talker_voice_speaker_names: str = None,
        gender_preference: str = None,
        length: str = None,
        host: str = None,
        style: str = None,
        additional_instructions: str = None
    ) -> tuple[bool, str, PodcastGenerationDefinition]:
        if target_locale is None:
            raise ValueError("Target locale must be provided")
        if content_file_azure_blob_url is None and content_file_path is None:
            raise ValueError("At least one content source must be provided")

        now = datetime.now()
        nowString = now.strftime("%m%d%Y%H%M%S")
        generation_id = f"{nowString}_{target_locale}"

        request_body = self.create_generation_creation_body(
            content_file_azure_blob_url=content_file_azure_blob_url,
            content_file_path=content_file_path,
            content_file_temp_file_id = content_file_temp_file_id,
            target_locale=target_locale,
            voice_name=voice_name,
            multi_talker_voice_speaker_names=multi_talker_voice_speaker_names,
            gender_preference=gender_preference,
            length=length,
            host=host,
            style=style,
            additional_instructions=additional_instructions
        )

        success, error, response_generation, operation_location = self.request_create_generation(
            generation_id=generation_id,
            request_body=request_body)
        if not success:
            print(colored(f"Failed to create generation with ID {generation_id} with error: {error}",
                          'red'))
            return False, error, None

        self.request_operation_until_terminated(operation_location)

        success, error, response_generation = self.request_get_generation(generation_id)
        if not success:
            print(colored(f"Failed to query generation {generation_id} with error: {error}", 'red'))
            return False, error, None
        generation = json.dumps(dataclasses.asdict(response_generation), indent=2)
        if response_generation.status != OperationStatus.Succeeded:
            print(colored(f"Generation creation failed with error: {error}", 'red'))
            print(generation)
            return False, response_generation.FailureReason, None
        else:
            print(colored(f"Succesfully generated podcast:", 'green'))
            print(generation)

        return True, None, response_generation

    def request_get_generation(self,
                                generation_id: str) -> tuple[bool, str, PodcastGenerationDefinition]:
        success, error, response = self.request_get_long_running_task(generation_id)
        if not success:
            return False, error, None
        response_translation_json = response.json()
        response_translation = dict_to_dataclass(
            data=response_translation_json,
            dataclass_type=PodcastGenerationDefinition)
        return True, None, response_translation
    
    def request_list_generations(self,
                                  top: int = None,
                                  skip: int = None,
                                  maxPageSize: int = None) -> tuple[bool, str, PagedGenerationDefinition]:

        success, error, response = self.request_list_long_running_tasks(
            top=top,
            skip=skip,
            maxPageSize=maxPageSize)
        if not success:
            return False, error, None
        
        response_generations_json = response.json()
        response_generations = dict_to_dataclass(
            data=response_generations_json,
            dataclass_type=PagedGenerationDefinition)
        return True, None, response_generations

    def request_delete_generation(self,
                                   generation_id: str) -> tuple[bool, str]:
        return self.request_delete_long_running_task(generation_id)

    def create_generation_creation_body(
            self,
            target_locale: locale,
            content_file_azure_blob_url: Url,
            content_file_path: str = None,
            content_file_temp_file_id: str = None,
            voice_name: str = None,
            multi_talker_voice_speaker_names: str = None,
            gender_preference: str = None,
            length: str = None,
            host: str = None,
            style: str = None,
            additional_instructions: str = None,
            ) -> PodcastGenerationDefinition:
        if target_locale is None:
            raise ValueError
        if content_file_azure_blob_url is None and content_file_path is None and content_file_temp_file_id is None:
            raise ValueError("At least one content source must be provided")

        create_request_body=PodcastGenerationDefinition(
            displayName="Generation Name",
            description="Generation Description",
            locale=target_locale,
            host=host,
            content=PodcastContent(),
            scriptGeneration=PodcastScriptGenerationConfig(
                additionalInstructions=additional_instructions,
                length=length,
                style=style),
            tts=PodcastTtsConfig(
                voiceName=voice_name,
                genderPreference=gender_preference,
                multiTalkerVoiceSpeakerNames=multi_talker_voice_speaker_names),
        )

        # API also support proivde text directly, then not specify url argument, instead using the "text" argument as below:
        #   kind=ContentSourceKind.PlainText,
        #   text="your text content"
        if content_file_azure_blob_url is not None:
            create_request_body.content.kind=ContentSourceKind.AzureStorageBlobPublicUrl
            create_request_body.content.url=content_file_azure_blob_url
        elif content_file_temp_file_id is not None:
            create_request_body.content.tempFileId = content_file_temp_file_id
        elif content_file_path is not None:
            file_extension = os.path.splitext(content_file_path)[1].lower()
            if file_extension == '.txt':
                with open(content_file_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                    if (len(text_content) <= MAX_PLAIN_TEXT_LENGTH):
                        create_request_body.content.kind=ContentSourceKind.PlainText
                        create_request_body.content.fileFormat = ContentFileFormatKind.Txt
                        create_request_body.content.text = text_content
                    else:
                        raise ValueError("Please upload by temp file.")
            elif file_extension == '.pdf':
                create_request_body.content.fileFormat = ContentFileFormatKind.Pdf
                with open(content_file_path, 'rb') as f:
                    file_binary = f.read()
                    if len(file_binary) <= MAX_BASE64_TEXT_LENGTH:
                        base64_content = base64.b64encode(file_binary).decode('utf-8')
                        if (len(base64_content) <= MAX_BASE64_TEXT_LENGTH):
                            create_request_body.content.kind = ContentSourceKind.FileBase64
                            create_request_body.content.base64Text = base64_content
                        else:
                            raise ValueError("Input content file too large, should not exceed exceed 50M.")
                    else:
                        raise ValueError("Input content file too large, should not exceed exceed 50M.")
            else:
                raise ValueError(f"Unsupported file extension: {file_extension}. Only .pdf and .txt are supported for base64 content.")
        else:
            raise ValueError("At least one content source must be provided")

        return create_request_body

    def request_create_generation(
            self,
            generation_id: str,
            request_body: PodcastGenerationDefinition,
            ) -> tuple[bool, str, PodcastGenerationDefinition, Url]:
        if generation_id is None:
            raise ValueError

        success, error, response, operation_location_url = self.request_create_long_running_task_with_id(
            id=generation_id,
            creation_body=request_body)
        if not success:
            return False, error, None, None
        
        response_generation_json = response.json()
        response_generation = dict_to_dataclass(
            data=response_generation_json,
            dataclass_type=PodcastGenerationDefinition)
        return True, None, response_generation, operation_location_url