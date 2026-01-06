//
// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE.md file in the project root for full license information.
//

namespace Microsoft.SpeechServices.Podcast.ApiSampleCode;

using Azure;
using CommandLine;
using Flurl.Http;
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
        var tempFileClient = new TempFileClient(httpConfig);

        switch (baseOptions)
        {
            case UploadTempFileOptions options:
                {
                    var responseString = await tempFileClient.UploadTempFileAsync(
                        options.FilePath,
                        options.ExpiresAfterInMins == 0 ? null : options.ExpiresAfterInMins)
                        .ReceiveString().ConfigureAwait(false);
                    Console.WriteLine(responseString);
                    break;
                }

            case ListTempFilesOptions options:
                {
                    var tempFiles = await tempFileClient.ListTempFilesAsync(
                        top: 2,
                        skip: 1,
                        maxPageSize: 2).ConfigureAwait(false);
                    Console.WriteLine(JsonConvert.SerializeObject(
                        tempFiles,
                        Formatting.Indented,
                        CommonPublicConst.Json.WriterSettings));
                    break;
                }

            case GetTempFileOptions options:
                {
                    var tempFile = await tempFileClient.GetTempFileAsync(options.Id).ConfigureAwait(false);
                    Console.WriteLine(JsonConvert.SerializeObject(
                        tempFile,
                        Formatting.Indented,
                        CommonPublicConst.Json.WriterSettings));
                    break;
                }

            case DeleteTempFileOptions options:
                {
                    var response = await tempFileClient.DeleteTempFileAsync(options.Id).ConfigureAwait(false);
                    Console.WriteLine(response.StatusCode);
                    Console.WriteLine(JsonConvert.SerializeObject(
                        await response.GetStringAsync().ConfigureAwait(false),
                        Formatting.Indented,
                        CommonPublicConst.Json.WriterSettings));
                    break;
                }

            case CreateGenerationAndWaitUntilTerminatedOptions options:
                {
                    string plainText = null;
                    string base64Text = null;
                    string tempFileId = null;
                    Uri url = null;
                    ContentFileFormatKind? format = null;
                    var uploadByTempFile = false;

                    if (!string.IsNullOrEmpty(options.ContentFileAzureBlobUrl?.OriginalString))
                    {
                        url = options.ContentFileAzureBlobUrl;
                    }
                    else if (!string.IsNullOrWhiteSpace(options.TempFileId))
                    {
                        tempFileId = options.TempFileId;
                    }
                    else if (!string.IsNullOrEmpty(options.ContentFilePath))
                    {
                        if (options.UploadWithTempFile)
                        {
                            uploadByTempFile = true;
                        }
                        else if (options.ContentFilePath.EndsWith(".txt", StringComparison.OrdinalIgnoreCase))
                        {
                            var filePlainText = await File.ReadAllTextAsync(options.ContentFilePath).ConfigureAwait(false);
                            if ((filePlainText?.Length ?? 0) <= PodcastPublicConst.DataValidation.MaxPlainTextLength)
                            {
                                plainText = filePlainText;
                            }
                            else
                            {
                                uploadByTempFile = true;
                            }
                        }
                        else if (options.ContentFilePath.EndsWith(".pdf", StringComparison.OrdinalIgnoreCase))
                        {
                            format = ContentFileFormatKind.Pdf;
                            var bytes = await File.ReadAllBytesAsync(options.ContentFilePath).ConfigureAwait(false);
                            if (bytes.Length <= PodcastPublicConst.DataValidation.MaxBaser64TextLength)
                            {
                                var fileBase64Text = Convert.ToBase64String(bytes);
                                if (fileBase64Text.Length <= PodcastPublicConst.DataValidation.MaxBaser64TextLength)
                                {
                                    base64Text = fileBase64Text;
                                }
                            }

                            if (string.IsNullOrWhiteSpace(base64Text) &&
                                bytes.Length <= PodcastPublicConst.DataValidation.MaxContentFileSize)
                            {
                                uploadByTempFile = true;
                            }
                            else
                            {
                                throw new NotSupportedException($"Input content file too large, should not exceed exceed 50MB.");
                            }
                        }
                        else
                        {
                            throw new InvalidDataException($"Unsupported file format for content file path: {options.ContentFilePath}");
                        }

                        if (uploadByTempFile)
                        {
                            Console.WriteLine($"Uploading content file: {options.ContentFilePath}");
                            var response = await tempFileClient.UploadTempFileAsync(
                                localFilePath: options.ContentFilePath,
                                expiresAfterInMins: (int)TimeSpan.FromHours(2).TotalMinutes)
                                .ReceiveJson<TempFile>().ConfigureAwait(false);
                            Console.WriteLine(JsonConvert.SerializeObject(
                                response,
                                Formatting.Indented,
                                CommonPublicConst.Json.WriterSettings));
                            Console.WriteLine($"Succesfully uploaded content file!");
                            tempFileId = response.Id;
                        }
                    }
                    else
                    {
                        throw new InvalidDataException($"Please specify contentLocalFilePath or contentFileAzureBlobUrl");
                    }

                    try
                    {
                        var generation = new PodcastGeneration()
                        {
                            Id = string.IsNullOrWhiteSpace(options.Id) ?
                                Guid.NewGuid().ToString() : options.Id,
                            DisplayName = options.Id,
                            Description = options.Id,
                            Locale = options.TargetLocale,
                            Host = options.Host == PodcastHostKind.None ? null : options.Host,
                            Content = new PodcastContent()
                            {
                                TempFileId = tempFileId,
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
                    }
                    finally
                    {
                        if (!string.IsNullOrWhiteSpace(tempFileId) && uploadByTempFile)
                        {
                            Console.WriteLine($"Deleting temp file with ID: {tempFileId}");
                            var response = await tempFileClient.DeleteTempFileAsync(tempFileId).ConfigureAwait(false);
                            Console.WriteLine($"Succesfully deleted temp file with response status code {response.StatusCode}!");
                        }
                    }

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
