//
// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE.md file in the project root for full license information.
//

namespace Microsoft.SpeechServices.Podcast.ApiSampleCode;

using CommandLine;

[Verb("getTempFile", HelpText = "Get a temporary file by ID.")]
public partial class GetTempFileOptions : BaseOptions
{
    [Option("id", Required = false, HelpText = "Temp file ID.")]
    public string Id { get; set; }
}
