//
// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE.md file in the project root for full license information.
//

namespace Microsoft.SpeechServices.CommonLib;

public static class PodcastPublicConst
{
    public static class DataValidation
    {
        public const int MaxPlainTextLength = 1024 * 1024;

        // For 8M base64(about 5M pdf) can handle 80% of real world pdf.
        public const int MaxBaser64TextLength = 8 * 1024 * 1024;
        public const int MaxContentFileSize = 50 * 1024 * 1025;
        public const int AdditionalInstructionsMaxLength = 200;

        public const long MaxExpiresAfterInMins = 60 * 24;
    }

    public static class ArgumentDescription
    {
        public const string GenerationId = "Specify generation ID.";

        public const string ContentFileAzureBlobUrl = "Content file Azure blob URL, this parameter is conflict with ContentFilePath.";

        public const string ContentFilePath = "Content file path, this parameter is conflict with ContentFileAzureBlobUrl.";

        public const string Locale = "Podcast target generated podcast locale.";

        public const string AdditionalInstructions = "Podcast dialog generation additional instructions.";

        public const string VoiceName = "Specify neural voice for one host or multi talker voice for two hosts: en-US-MultiTalker-Ava-Andrew:DragonHDLatestNeural, en-US-MultiTalker-Ava-Steffan:DragonHDLatestNeural";

        public const string Length = "Podcast length: VeryShort/Short/Medium(default)/Long/VeryLong";

        public const string GenderPreference = "Podcast gender preference: Male/Female";

        public const string MultiTalkerVoiceSpeakerNames = "Podcast multi-talker voice speaker names: ada/andrew/ava/brian/davis/emma/jane/steffan";

        public const string Host = "Podcast host: OneHost(default)/TwoHosts";

        public const string Style = "Podcast style: Default(default)/Professional/Casual";
    }
}
