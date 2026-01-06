//
// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE.md file in the project root for full license information.
//

namespace Microsoft.SpeechServices.Cris.Http.DTOs.Public.Podcast.Public20260101Preview;

using System;

public class TempFile : ResourceBase
{
    public string Name { get; set; }

    public DateTime CreatedDateTime { get; set; }

    public DateTime ExpiresDateTime { get; set; }

    public long SizeInBytes { get; set; }
}
