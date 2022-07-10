"""
Speech recognition and generation and some utility functions.

Authors: Hamed Zamani (hazamani@microsoft.com)
"""

import os
import tempfile
from abc import ABC, abstractmethod

import speech_recognition as sr
from google.cloud import texttospeech
from pydub import AudioSegment


def mp3_to_ogg(input_file_name):  # caller should delete the file afterwards.
    ogg_file = tempfile.NamedTemporaryFile(delete=False)
    AudioSegment.from_mp3(input_file_name).export(
        ogg_file.name, format="ogg", parameters=["-acodec", "libopus"]
    )
    ogg_file.close()
    return ogg_file.name


def ogg_to_wav(input_file_name):  # caller should delete the file afterwards.
    wav_file = tempfile.NamedTemporaryFile(delete=False)
    AudioSegment.from_ogg(input_file_name).export(wav_file.name, format="wav")
    wav_file.close()
    return wav_file.name


class ASR(ABC):  # Automatic Speech Recognition
    def __init__(self, params):
        self.params = params

    @abstractmethod
    def speech_to_text(self, file_path):
        pass


class ASG(ABC):  # Automatic Speech Generation
    def __init__(self, params):
        self.params = params

    @abstractmethod
    def text_to_speech(self, text):
        pass


class GoogleASR(ASR):
    def __init__(self, params):
        super().__init__(params)
        self.asr = sr.Recognizer()

    def speech_to_text(self, file_path):
        print(file_path)
        wav_file_name = ogg_to_wav(file_path)
        with sr.AudioFile(wav_file_name) as source:
            audio = self.asr.record(source)
        try:
            text = self.asr.recognize_google(audio)
            os.remove(wav_file_name)
            return text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(
                "Could not request results from Google Speech Recognition service; {0}".format(
                    e
                )
            )


class GoogleText2Speech(ASG):
    def __init__(self, params):
        super().__init__(params)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.params[
            "google-speech-to-text-credential-file"
        ]
        # Instantiates a client
        self.client = texttospeech.TextToSpeechClient()
        # Build the voice request, select the language code ("en-US") and the ssml
        # voice gender ("neutral")
        self.voice = texttospeech.types.VoiceSelectionParams(
            language_code="en-US",
            ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL,
        )
        # Select the type of audio file you want returned
        self.audio_config = texttospeech.types.AudioConfig(
            audio_encoding=texttospeech.enums.AudioEncoding.MP3
        )

    def text_to_speech(self, text):
        # Set the text input to be synthesized
        synthesis_input = texttospeech.types.SynthesisInput(text=text)

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        response = self.client.synthesize_speech(
            synthesis_input, self.voice, self.audio_config
        )

        mp3_file = tempfile.NamedTemporaryFile(delete=True)
        mp3_file.write(response.audio_content)
        ogg_file_name = mp3_to_ogg(mp3_file.name)
        mp3_file.close()
        return ogg_file_name
