//
// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE.md file in the project root for full license information.
//

namespace Microsoft.SpeechServices.Podcast.ApiSampleCode;

using CommandLine;
using Microsoft.SpeechServices.CommonLib;
using Microsoft.SpeechServices.CommonLib.Public.Interface;
using Microsoft.SpeechServices.Cris.Http.DTOs.Public.Podcast.Public20260101Preview;
using Newtonsoft.Json;
using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;

internal partial class Program
{
    public static async Task<int> Main(string[] args)
    {
        var types = LoadVerbs();

        var exitCode = await Parser.Default.ParseArguments(args, types)
            .MapResult(
                options => RunAndReturnExitCodeAsync(options),
                _ => Task.FromResult(1));

        if (exitCode == 0)
        {
            Console.WriteLine("Process completed successfully.");
        }
        else
        {
            Console.WriteLine($"Failure with exit code: {exitCode}");
        }

        return exitCode;
    }

    private static async Task<int> RunAndReturnExitCodeAsync(object options)
    {
        var optionsBase = options as BaseOptions;
        ArgumentNullException.ThrowIfNull(optionsBase);
        try
        {
            return await DoRunAndReturnExitCodeAsync(optionsBase).ConfigureAwait(false);
        }
        catch (Exception e)
        {
            Console.WriteLine($"Failed to run with exception: {e.Message}");
            return CommonPublicConst.ExistCodes.GenericError;
        }
    }

    private static async Task<int> DoRunAndReturnExitCodeAsync(BaseOptions baseOptions)
    {
        ArgumentNullException.ThrowIfNull(baseOptions);
        var regionConfig = new ApimApiRegionConfig(baseOptions.Region);

        var httpConfig = new PodcastPublicPreviewHttpClientConfig(
            regionConfig: regionConfig,
            subKey: baseOptions.SubscriptionKey,
            customDomainName: baseOptions.CustomDomainName,
            managedIdentityClientId: baseOptions.ManagedIdentityClientId == Guid.Empty ? null : baseOptions.ManagedIdentityClientId)
        {
            ApiVersion = string.IsNullOrEmpty(baseOptions.ApiVersion) ?
                CommonPublicConst.ApiVersions.ApiVersion20260101Preview : baseOptions.ApiVersion,
        };

        var generationClient = new GenerationClient(httpConfig);

        switch (baseOptions)
        {
            case CreateGenerationAndWaitUntilTerminatedOptions options:
                {
                    ContentSourceKind? kind = null;
                    string plainText = null;
                    string base64Text = null;
                    Uri url = null;
                    ContentFileFormatKind? format = null;
                    if (!string.IsNullOrEmpty(options.ContentFileAzureBlobUrl?.OriginalString))
                    {
                        kind = ContentSourceKind.AzureStorageBlobPublicUrl;
                        url = options.ContentFileAzureBlobUrl;
                    }
                    else if (!string.IsNullOrEmpty(options.PlainTextContentFilePath))
                    {
                        kind = ContentSourceKind.PlainText;
                        plainText = await File.ReadAllTextAsync(options.PlainTextContentFilePath).ConfigureAwait(false);
                    }
                    else if (!string.IsNullOrEmpty(options.Base64ContentFilePath))
                    {
                        if (options.Base64ContentFilePath.EndsWith(".txt", StringComparison.OrdinalIgnoreCase))
                        {
                            format = ContentFileFormatKind.Txt;
                        }
                        else if (options.Base64ContentFilePath.EndsWith(".pdf", StringComparison.OrdinalIgnoreCase))
                        {
                            format = ContentFileFormatKind.Pdf;
                        }
                        else
                        {
                            throw new InvalidDataException($"Unsupported file format for base64 content file path: {options.Base64ContentFilePath}");
                        }

                        kind = ContentSourceKind.FileBase64;
                        var bytes = await File.ReadAllBytesAsync(options.Base64ContentFilePath).ConfigureAwait(false);
                        base64Text = Convert.ToBase64String(bytes);
                    }
                    else
                    {
                        throw new InvalidDataException($"Please specify contentLocalFilePath or contentFileAzureBlobUrl");
                    }

                    var generation = new PodcastGeneration()
                    {
                        Id = string.IsNullOrWhiteSpace(options.Id) ?
                            Guid.NewGuid().ToString() : options.Id,
                        DisplayName = options.Id,
                        Description = options.Id,
                        Locale = options.TargetLocale,
                        Host = options.Host == PodcastHostKind.None ? null : options.Host,
                        Content = new PodcastGenerationContent()
                        {
                            Kind = kind.Value,
                            Text = plainText,
                            Base64Text = base64Text,
                            FileFormat = format,
                            Url = url,
                        },
                        ScriptGeneration = new PodcastScriptGenerationConfig()
                        {
                            AdditionalInstructions = options.AdditionalInstructions,
                            Length = options.Length == PodcastLengthKind.None ? null : options.Length,
                            Style = options.Style == PodcastStyleKind.Default ? null : options.Style,
                        },
                        Tts = new PodcastTtsConfig()
                        {
                            VoiceName = options.VoiceName,
                            MultiTalkerVoiceSpeakerNames = options.MultiTalkerVoiceSpeakerNames,
                            GenderPreference = options.GenderPreference == PodcastGenderPreferenceKind.None ? null : options.GenderPreference,
                        },
                    };

                    generation = await generationClient.CreateGenerationAndWaitUntilTerminatedAsync(
                        generation: generation).ConfigureAwait(false);

                    Console.WriteLine();
                    Console.WriteLine("Created generation:");
                    Console.WriteLine(JsonConvert.SerializeObject(
                        generation,
                        Formatting.Indented,
                        CommonPublicConst.Json.WriterSettings));
                    break;
                }

            case ListOptions options:
                {
                    var translations = await generationClient.ListGenerationsAsync().ConfigureAwait(false);
                    Console.WriteLine(JsonConvert.SerializeObject(
                        translations,
                        Formatting.Indented,
                        CommonPublicConst.Json.WriterSettings));
                    break;
                }

            case GetOptions options:
                {
                    var translation = await generationClient.GetGenerationAsync(
                        options.Id).ConfigureAwait(false);
                    Console.WriteLine(JsonConvert.SerializeObject(
                        translation,
                        Formatting.Indented,
                        CommonPublicConst.Json.WriterSettings));
                    break;
                }

            case DeleteOptions options:
                {
                    var response = await generationClient.DeleteGenerationAsync(
                        options.Id).ConfigureAwait(false);
                    Console.WriteLine(response.StatusCode);
                    break;
                }

            default:
                throw new NotSupportedException();
        }

        return CommonPublicConst.ExistCodes.NoError;
    }

    //load all types using Reflection
    private static Type[] LoadVerbs()
    {
        return Assembly.GetExecutingAssembly().GetTypes()
            .Where(t => t.GetCustomAttribute<VerbAttribute>() != null).ToArray();
    }
}
