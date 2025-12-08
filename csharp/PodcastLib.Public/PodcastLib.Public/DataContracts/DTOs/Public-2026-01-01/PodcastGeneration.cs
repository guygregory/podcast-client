//
// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE.md file in the project root for full license information.
//

namespace Microsoft.SpeechServices.Cris.Http.DTOs.Public.Podcast.Public20260101Preview;

using System.ComponentModel.DataAnnotations;
using System.Globalization;

public partial class PodcastGeneration : StatefulResourceBase
{
    public string Locale { get; set; }

    // Default is PodcastHostKindExtension.DefaultHostKind: TwoHosts
    public PodcastHostKind? Host { get; set; }

    public PodcastScriptGenerationConfig ScriptGeneration { get; set; }

    public PodcastTtsConfig Tts { get; set; }

    public PodcastGenerationOutput Output { get; set; }

    public PodcastGenerationContent Content { get; set; }

    public string FailureReason { get; set; }
}
