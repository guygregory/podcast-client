# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.

import locale
from datetime import datetime
from dataclasses import dataclass
from urllib3.util import Url
from typing import Optional

from microsoft_speech_client_common.client_common_enum import (
    OperationStatus, OneApiState
)

from microsoft_client_podcast.podcast_enum import (
    ContentFileFormatKind, ContentSourceKind, PodcastHostKind, PodcastLengthKind, PodcastStyleKind, PodcastGenderPreferenceKind
)

from microsoft_speech_client_common.client_common_dataclass import (
    StatelessResourceBaseDefinition, StatefulResourceBaseDefinition
)


@dataclass(kw_only=True)
class PodcastContent:
    url: Optional[Url] = None
    text: Optional[str] = None
    base64Text: Optional[str] = None
    tempFileId: Optional[str] = None
    # TODO: Delete after 2026/1/19
    kind: Optional[ContentSourceKind] = None
    fileFormat: Optional[ContentFileFormatKind] = None

@dataclass(kw_only=True)
class PodcastScriptGenerationConfig:
    additionalInstructions: Optional[str] = None
    length: Optional[PodcastLengthKind] = None
    style: Optional[PodcastStyleKind] = None

@dataclass(kw_only=True)
class PodcastGenerationOutput:
    audioFileUrl: Url

@dataclass(kw_only=True)
class PodcastTtsConfig:
    voiceName: str = None
    genderPreference: Optional[PodcastGenderPreferenceKind] = None
    multiTalkerVoiceSpeakerNames: str = None # for example: ava,steffan

@dataclass(kw_only=True)
class PodcastGenerationDefinition(StatefulResourceBaseDefinition):
    displayName: Optional[str] = None
    description: Optional[str] = None
    locale: locale
    host: Optional[PodcastHostKind] = None
    content: PodcastContent = None
    scriptGeneration: Optional[PodcastScriptGenerationConfig] = None
    tts: Optional[PodcastTtsConfig] = None
    output: PodcastGenerationOutput = None
    failureReason: Optional[str] = None

@dataclass(kw_only=True)
class PagedGenerationDefinition:
    value: list[PodcastGenerationDefinition]
    nextLink: Optional[Url] = None

@dataclass(kw_only=True)
class TempFile:
    id: str
    name: Optional[str] = None
    createdDateTime: Optional[datetime] = None
    expiresDateTime: Optional[datetime] = None
    sizeInBytes: Optional[int] = None

@dataclass(kw_only=True)
class PagedTempFileDefinition:
    value: list[TempFile]
    nextLink: Optional[Url] = None