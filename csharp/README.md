# Podcast generation

Podcast generation client tool and API sample code

# Supported OS
## Windows prerequisite:
   Install [dotnet 8.0](https://dotnet.microsoft.com/download/dotnet/8.0)

   Run tool: PodcastSample.exe [verb] [arguments]

## Linux prerequisite:
   Install [dotnet 8.0](https://dotnet.microsoft.com/download/dotnet/8.0)

   Run tool: dotnet PodcastSample.dll [verb] [arguments]

# Work Flow

   1. Upload input content file(.pdf, .txt) to Azure storage blob.

   2. Create generation and wait until terminated with below command:

   > PodcastSample createGenerationAndWaitUntilTerminated --region [RegionIdentifier] --subscriptionKey [YourSpeechResourceKey] --apiVersion [ApiVersion] --targetLocales [TargetLocale] -contentFileAzureBlobUrl [ContentFileAzureBlobUrl]

# Solution:
   [PodcastSample.sln](PodcastSample.sln)

## Authentication withh Subscription key
The endpoint (and key) could be got from the Keys and Endpoint page in the Speech service resource.

Run the tool with argument:

      --subscriptionKey [YourSpeechResourceKey]

# API sample:

## Usage:
   For RESTful API usage reference below API core library class.

## RESTful API core library:
   Generation API core library: [GenerationClient.cs](PodcastLib.Public/HttpClient/GenerationClient.cs)

   Operation API core library: [OperationClient.cs](CommonLib.Public/HttpClient/OperationClient.cs)

# For project CommonLib
   Do not upgrade Flurl to version 4.0 because it does not support NewtonJson for ReceiveJson.

# Command Line Usage
   | Description | Command line arguments |
   | ------------ | -------------- |
   | Create podcast and wait until terminated. | createGenerationAndWaitUntilTerminated --region [RegionIdentifier] --subscriptionKey [YourSpeechResourceKey] --apiVersion [ApiVersion] --targetLocales [TargetLocale]  --contentFileAzureBlobUrl [ContentFileAzureBlobUrl] |
   | Query the generations. | list --region [RegionIdentifier] --subscriptionKey [YourSpeechResourceKey] --apiVersion [ApiVersion] |
   | Query the generation by ID. | get --region [RegionIdentifier] --subscriptionKey [YourSpeechResourceKey] --apiVersion [ApiVersion] --id [Id] |
   | Delete the generation by ID. | delete --region [RegionIdentifier] --subscriptionKey [YourSpeechResourceKey] --apiVersion [ApiVersion] --id [Id] |

# Command line tool arguments
   | Argument | Is Required | Supported Values Sample | Description |
   | -------- | -------- | ---------------- | ----------- |
   | --region  | True | eastus | Provide the region of the API request. |
   | --subscriptionKey | True | | Provide your speech resource key. |
   | --apiVersion | True | 2024-05-20-preview | Provide the version of the API request. |
   | --targetLocales | True | en-US | Target locale of the translation. |
   | --id | True | MyEnUSGeneration2024050601 | Generation ID. |
   | --contentFileAzureBlobUrl | True | URL | Please proivde input content file URL, with or without SAS, which is hosted in an Azure storage blob. |

# Argument definitions
## Supported regions
   https://learn.microsoft.com/azure/ai-services/speech-service/regions

   Use region identifier for the region argument.

## Supported API versions:
* 2026-01-01-preview


# Best practice
## Escape char for URL arguments in Windows
   For arguments:  --contentFileAzureBlobUrl
   If you run a client sample tool in a Windows shell and there is an & in the URL arguments (for example, a SAS token in an Azure blob URL), the & needs to be converted to ^& to escape it.

   For example, if the actual URL for the argument contentFileAzureBlobUrl is https://a/b?c&d, then when you run the command in the Windows shell, you need to run the command like this:

      --contentFileAzureBlobUrl "https://a/b?c^&d"

## How to retry?
   If you initiate a command to create a generation job and subsequently restart Windows, the job will continue to run on the server side. To check the status of the generation job, you can use the query generation tool command or the API, providing the specific generation ID.

