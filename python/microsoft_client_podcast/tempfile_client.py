# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.

import urllib3
import os
from termcolor import colored
from urllib3.util import Url
import uuid
from microsoft_speech_client_common.client_common_client_base import (
    SpeechLongRunningTaskClientBase
)
from microsoft_speech_client_common.client_common_util import (
    dict_to_dataclass, append_url_args
)
from microsoft_client_podcast.podcast_dataclass import (
    TempFile, PagedTempFileDefinition
)


class TempFileClient(SpeechLongRunningTaskClientBase):
    """Client for managing temporary files in the Podcast API."""
    
    URL_PATH_ROOT = "podcast"
    URL_SEGMENT_NAME_TEMP_FILES = "tempfiles"

    def __init__(self, region, sub_key, api_version):
        super().__init__(
            region=region,
            sub_key=sub_key,
            api_version=api_version,
            service_url_segment_name=self.URL_PATH_ROOT,
            long_running_tasks_url_segment_name=self.URL_SEGMENT_NAME_TEMP_FILES
        )

    def build_temp_files_path(self) -> str:
        """Build the path for temp files collection."""
        return f"{self.URL_PATH_ROOT}/{self.URL_SEGMENT_NAME_TEMP_FILES}"

    def build_temp_file_path(self, file_id: str) -> str:
        """Build the path for a specific temp file."""
        if file_id is None:
            raise ValueError("File ID is required")
        temp_files_path = self.build_temp_files_path()
        return f"{temp_files_path}/{file_id}"

    def build_temp_files_url(self) -> Url:
        """Build the URL for temp files collection."""
        path = self.build_temp_files_path()
        return self.build_url(path)

    def build_temp_file_url(self, file_id: str) -> Url:
        """Build the URL for a specific temp file."""
        if file_id is None:
            raise ValueError("File ID is required")
        path = self.build_temp_file_path(file_id)
        return self.build_url(path)

    def request_upload_temp_file(
        self,
        file_path: str,
        expires_after_in_mins: int = None,
    ) -> tuple[bool, str, TempFile]:
        """
        Upload a file to temp storage.
        
        Args:
            file_path: Local path to the file to upload
            file_name: Optional custom name for the file
            
        Returns:
            Tuple of (success, error_message, temp_file)
        """
        if file_path is None:
            raise ValueError("File path is required")
        
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}", None
        
        file_name = os.path.basename(file_path)
        
        file_id = str(uuid.uuid4())
        url = self.build_temp_file_url(file_id)
        headers = self.build_request_header()
        
        # Create multipart form data
        # Read file content as bytes
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        fields = {
            'file': (file_name, file_content, 'application/octet-stream')
        }
        if expires_after_in_mins is not None:
            fields['expiresAfterInMins'] = str(expires_after_in_mins)
        
        print(f"Uploading file to: {url}")
        response = self.http.request(
            "POST",
            url.url,
            headers=headers,
            fields=fields
        )

        if response.status not in [200, 201]:
            error = response.data.decode('utf-8')
            return False, error, None
        
        response_json = response.json()
        temp_file = dict_to_dataclass(
            data=response_json,
            dataclass_type=TempFile
        )
        return True, None, temp_file

    def request_list_temp_files(
        self,
        top: int = None,
        skip: int = None,
        max_page_size: int = None
    ) -> tuple[bool, str, PagedTempFileDefinition]:
        """
        List all temp files.
        
        Args:
            top: Maximum number of items to return
            skip: Number of items to skip
            max_page_size: Maximum page size
            
        Returns:
            Tuple of (success, error_message, paged_temp_files)
        """
        url = self.build_temp_files_url()
        args = {}
        if top is not None:
            args["top"] = top
        if skip is not None:
            args["skip"] = skip
        if max_page_size is not None:
            args["maxPageSize"] = max_page_size
        
        url = append_url_args(url, args)
        headers = self.build_request_header()
        
        print(f"Requesting http GET: {url}")
        response = self.http.request("GET", url.url, headers=headers)
        
        if response.status != 200:
            error = response.data.decode('utf-8')
            return False, error, None
        
        response_json = response.json()
        paged_files = dict_to_dataclass(
            data=response_json,
            dataclass_type=PagedTempFileDefinition
        )
        return True, None, paged_files

    def request_get_temp_file(
        self,
        file_id: str
    ) -> tuple[bool, str, TempFile]:
        """
        Get details of a specific temp file.
        
        Args:
            file_id: ID of the temp file
            
        Returns:
            Tuple of (success, error_message, temp_file)
        """
        if file_id is None:
            raise ValueError("File ID is required")
        
        url = self.build_temp_file_url(file_id)
        headers = self.build_request_header()
        
        print(f"Requesting http GET: {url}")
        response = self.http.request("GET", url.url, headers=headers)
        
        if response.status == 200:
            response_json = response.json()
            temp_file = dict_to_dataclass(
                data=response_json,
                dataclass_type=TempFile
            )
            return True, None, temp_file
        elif response.status == 404:
            return True, None, None
        
        error = response.data.decode('utf-8')
        return False, error, None

    def request_delete_temp_file(
        self,
        file_id: str
    ) -> tuple[bool, str]:
        """
        Delete a temp file.
        
        Args:
            file_id: ID of the temp file to delete
            
        Returns:
            Tuple of (success, error_message)
        """
        if file_id is None:
            raise ValueError("File ID is required")
        
        url = self.build_temp_file_url(file_id)
        headers = self.build_request_header()
        
        print(f"Requesting http DELETE: {url}")
        response = self.http.request("DELETE", url.url, headers=headers)
        
        if response.status not in [204]:
            error = response.data.decode('utf-8')
            return False, error
        
        return True, None
