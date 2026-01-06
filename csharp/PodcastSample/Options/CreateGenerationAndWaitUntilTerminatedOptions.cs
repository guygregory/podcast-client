//
// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE.md file in the project root for full license information.
//

namespace Microsoft.SpeechServices.Podcast.ApiSampleCode;

using CommandLine;
using Microsoft.SpeechServices.CommonLib;
using Microsoft.SpeechServices.Cris.Http.DTOs.Public.Podcast.Public20260101Preview;
using System;
using System.Globalization;

[Verb("createGenerationAndWaitUntilTerminated", HelpText = "Create generation and wait until terminated.")]
public partial class CreateGenerationAndWaitUntilTerminatedOptions : BaseOptions
{
    [Option("id", Required = false, HelpText = PodcastPublicConst.ArgumentDescription.GenerationId)]
    public string Id { get; set; }

    [Option("contentFileAzureBlobUrl", Required = false, HelpText = PodcastPublicConst.ArgumentDescription.ContentFileAzureBlobUrl)]
    public Uri ContentFileAzureBlobUrl { get; set; }

    [Option("contentFilePath", Required = false, HelpText = PodcastPublicConst.ArgumentDescription.ContentFilePath)]
    public string ContentFilePath { get; set; }

    // Not use CultureInfo due to it not support dialet like: zh-HeNan-CN
    [Option("targetLocale", Required = false, HelpText = PodcastPublicConst.ArgumentDescription.Locale)]
    public string TargetLocale { get; set; }

    [Option("voiceName", Required = false, HelpText = PodcastPublicConst.ArgumentDescription.VoiceName)]
    public string VoiceName { get; set; }

    [Option("multiTalkerVoiceSpeakerNames", Required = false, HelpText = PodcastPublicConst.ArgumentDescription.MultiTalkerVoiceSpeakerNames)]
    public string MultiTalkerVoiceSpeakerNames { get; set; }

    [Option("uploadWithTempFile", Required = false, HelpText = "Upload with temp file.")]
    public bool UploadWithTempFile { get; set; }

    [Option("tempFileId", Required = false, HelpText = "Temp file ID of input content file.")]
    public string TempFileId { get; set; }

    [Option("genderPreference", Required = false, Default = PodcastGenderPreferenceKind.None, HelpText = PodcastPublicConst.ArgumentDescription.GenderPreference)]
    public PodcastGenderPreferenceKind GenderPreference { get; set; }

    [Option("length", Required = false, Default = PodcastLengthKind.None, HelpText = PodcastPublicConst.ArgumentDescription.Length)]
    public PodcastLengthKind Length { get; set; }

    [Option("host", Required = false, Default = PodcastHostKind.None,
    HelpText = PodcastPublicConst.ArgumentDescription.Host)]
    public PodcastHostKind Host { get; set; }

    [Option("style", Required = false, Default = PodcastStyleKind.Default, HelpText = PodcastPublicConst.ArgumentDescription.Style)]
    public PodcastStyleKind Style { get; set; }

    [Option("additionalInstructions", Required = false, HelpText = PodcastPublicConst.ArgumentDescription.AdditionalInstructions)]
    public string AdditionalInstructions { get; set; }
}

