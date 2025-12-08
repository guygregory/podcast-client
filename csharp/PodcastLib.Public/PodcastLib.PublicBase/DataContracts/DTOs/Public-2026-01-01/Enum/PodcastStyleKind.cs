//
// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE.md file in the project root for full license information.
//

namespace Microsoft.SpeechServices.Cris.Http.DTOs.Public.Podcast.Public20260101Preview;

// Put DTO enum in Common.Client due to it need be referenced DB properties to store user original input.
public enum PodcastStyleKind
{
    // Neutral
    Default = 0,

    // Professional and Casual are shown in Copilot podcast UI.
    Professional,

    Casual,
}
