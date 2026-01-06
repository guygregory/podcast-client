//
// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE.md file in the project root for full license information.
//

namespace Microsoft.SpeechServices.Podcast.ApiSampleCode;

using CommandLine;

[Verb("uploadTempFile", HelpText = "Upload a temporary file.")]
public partial class UploadTempFileOptions : BaseOptions
{
    [Option("filePath", Required = true, HelpText = "Local file path to upload.")]
    public string FilePath { get; set; }

    [Option("expiresAfterInMins", Required = false, Default = 0, HelpText = "Expiration time in minutes.")]
    public int ExpiresAfterInMins { get; set; }
}
