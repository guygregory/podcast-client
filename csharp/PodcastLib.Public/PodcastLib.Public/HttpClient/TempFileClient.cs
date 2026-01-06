//
// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE.md file in the project root for full license information.
//

namespace Microsoft.SpeechServices.Podcast;

using Flurl.Http;
using Microsoft.SpeechServices.CommonLib;
using Microsoft.SpeechServices.CommonLib.Util;
using Microsoft.SpeechServices.Cris.Http.DTOs.Public.Podcast.Public20260101Preview;
using Microsoft.SpeechServices.DataContracts;
using System;
using System.Globalization;
using System.IO;
using System.Net;
using System.Threading.Tasks;

public class TempFileClient : CurlHttpClientBase<TempFile>
{
    public TempFileClient(HttpSpeechClientConfigBase config)
        : base(config)
    {
    }

    public override string ControllerName => "tempfiles";

    public async Task<IFlurlResponse> DeleteTempFileAsync(string tempFileId)
    {
        return await this.DeleteByIdAsync(tempFileId);
    }

    public async Task<TempFile> GetTempFileAsync(string tempFileId)
    {
        return await this.GetTypedDtoAsync(tempFileId);
    }

    public async Task<PaginatedResources<TempFile>> ListTempFilesAsync(
        int? top = null,
        int? skip = null,
        int? maxPageSize = null)
    {
        return await this.ListTypedDtosAsync(
            top: top,
            skip: skip,
            maxPageSize: maxPageSize).ConfigureAwait(false);
    }

    public async Task<IFlurlResponse> UploadTempFileAsync(string localFilePath, int? expiresAfterInMins)
    {
        var operationId = Guid.NewGuid().ToString();
        var tempFileId = Guid.NewGuid().ToString();

        var url = await this.BuildRequestBaseAsync().ConfigureAwait(false);

        // Use operation ID to void duplicate uploads in case of retries.
        url = url.AppendPathSegment(tempFileId)
            .WithHeader(CommonPublicConst.Http.Headers.OperationId, operationId);
        var fileInfo = new FileInfo(localFilePath);
        if (fileInfo.Length > PodcastPublicConst.DataValidation.MaxContentFileSize)
        {
            throw new NotSupportedException($"File size {fileInfo.Length} exceeds maximum allowed size {PodcastPublicConst.DataValidation.MaxContentFileSize}.");
        }

        return await RequestWithRetryAsync(async () =>
        {
            try
            {
                return await url.PostMultipartAsync(mp =>
                {
                    if (expiresAfterInMins != null)
                    {
                        mp.AddString(
                            nameof(TempFileCreation.ExpiresAfterInMins),
                            expiresAfterInMins.Value.ToString(CultureInfo.InvariantCulture));
                    }

                    mp.AddFile("file", localFilePath, fileName: Path.GetFileName(localFilePath));
                }).ConfigureAwait(false);

            }
            catch (FlurlHttpException ex)
            {
                if (ex.StatusCode == (int)HttpStatusCode.NotFound)
                {
                    return null;
                }

                Console.Write($"Response failed with error: {await ex.GetResponseStringAsync().ConfigureAwait(false)}");
                throw;
            }
        }).ConfigureAwait(false);
    }
}
