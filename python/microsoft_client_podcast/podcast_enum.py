# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.

from enum import Enum


class ContentSourceKind(str, Enum):
    AzureStorageBlobPublicUrl = 'AzureStorageBlobPublicUrl'
    PlainText = 'PlainText'
    FileBase64 = 'FileBase64'

class PodcastHostKind(str, Enum):
    OneHost = 'OneHost'
    TwoHosts = 'TwoHosts'

class ContentFileFormatKind(str, Enum):
    Txt = 'Txt'
    Pdf = 'Pdf'

class PodcastLengthKind(str, Enum):
    VeryShort = 'VeryShort'
    Short = 'Short'
    Medium = 'Medium'
    Long = 'Long'
    VeryLong = 'VeryLong'

class PodcastStyleKind(str, Enum):
    Default = 'Default' # Neutral
    Professional = 'Professional'
    Casual = 'Casual'

class PodcastGenderPreferenceKind(str, Enum):
    Female = 'Female'
    Male = 'Male'