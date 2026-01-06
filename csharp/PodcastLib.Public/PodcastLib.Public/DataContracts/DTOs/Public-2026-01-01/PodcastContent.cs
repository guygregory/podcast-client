//
// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE.md file in the project root for full license information.
//

namespace Microsoft.SpeechServices.Cris.Http.DTOs.Public.Podcast.Public20260101Preview;

using System;
using System.ComponentModel.DataAnnotations;

public class PodcastContent
{
    public Uri Url { get; set; }

    public string Text { get; set; }

    public string Base64Text { get; set; }

    public string TempFileId { get; set; }

    public ContentFileFormatKind? FileFormat { get; set; }

    // TODO: Delete after 2026/1/19
    // public string Kind { get; set; }
}
