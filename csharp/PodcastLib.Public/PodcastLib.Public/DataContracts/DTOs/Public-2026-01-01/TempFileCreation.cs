//
// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE.md file in the project root for full license information.
//

namespace Microsoft.SpeechServices.Cris.Http.DTOs.Public.Podcast.Public20260101Preview;

public class TempFileCreation
{
    // Supported range from 1 to maximum value is 1440 (1 day)
    public int? ExpiresAfterInMins { get; set; }
}
