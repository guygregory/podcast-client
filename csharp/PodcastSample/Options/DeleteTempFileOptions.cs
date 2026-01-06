//
// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE.md file in the project root for full license information.
//

namespace Microsoft.SpeechServices.Podcast.ApiSampleCode;

using CommandLine;
using Microsoft.SpeechServices.CommonLib;

[Verb("deleteTempFile", HelpText = "Delete temp file by ID.")]
public partial class DeleteTempFileOptions : BaseOptions
{
    [Option("id", Required = false, HelpText = "Temp file ID.")]
    public string Id { get; set; }
}
