//
// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE.md file in the project root for full license information.
//

namespace Microsoft.SpeechServices.Podcast;

using Flurl.Http;
using Microsoft.SpeechServices.CommonLib.Util;
using Microsoft.SpeechServices.Cris.Http.DTOs.Public.Podcast.Public20260101Preview;
using Microsoft.SpeechServices.DataContracts;
using System.Threading.Tasks;

public class GenerationClient : CurlHttpStatefulClientBase<PodcastGeneration>
{
    public GenerationClient(HttpSpeechClientConfigBase config)
        : base(config)
    {
    }

    public override string ControllerName => "generations";

    public async Task<IFlurlResponse> DeleteGenerationAsync(string generationId)
    {
        return await this.DeleteByIdAsync(generationId);
    }

    public async Task<PodcastGeneration> GetGenerationAsync(string generationId)
    {
        return await this.GetTypedDtoAsync(generationId);
    }

    public async Task<PaginatedResources<PodcastGeneration>> ListGenerationsAsync(
        int? top = null,
        int? skip = null,
        int? maxPageSize = null)
    {
        return await this.ListTypedDtosAsync(
            top: top,
            skip: skip,
            maxPageSize: maxPageSize).ConfigureAwait(false);
    }

    public async Task<PodcastGeneration> CreateGenerationAndWaitUntilTerminatedAsync(
        PodcastGeneration generation)
    {
        return await this.CreateDtoAndWaitUntilTerminatedAsync(generation).ConfigureAwait(false);
    }
}
