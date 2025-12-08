//
// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE.md file in the project root for full license information.
//

namespace Microsoft.SpeechServices.Cris.Http.DTOs.Public.Podcast.Public20260101Preview;

using System.ComponentModel.DataAnnotations;
using System.Globalization;

public partial class PodcastTtsConfig
{
    public string VoiceName { get; set; }

    public PodcastGenderPreferenceKind? GenderPreference { get; set; }

    public string MultiTalkerVoiceSpeakerNames { get; set; }
}
