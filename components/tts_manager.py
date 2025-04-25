## components/tts_manager.py

import os
import time

import edge_tts
import pyttsx3
import soundfile as sf
from pedalboard import Chorus, Pedalboard, Reverb
from pygame import mixer

from components.utils import log

# Config.py
from config import (
    TTS_EDGE_PITCH,
    TTS_EDGE_RATE,
    TTS_EDGE_VOICE,
    TTS_EDGE_VOLUME,
    TTS_EFFECTS,
    TTS_TYPE,
    TTS_WINDOWS_LIST,
    TTS_WINDOWS_RATE,
    TTS_WINDOWS_VOICE,
    TTS_WINDOWS_VOLUME,
)


async def send_text_to_voice(text):
    if TTS_TYPE == "WINDOWS":
        send_local_text_to_voice(text)
    else:
        await send_edge_text_to_voice(text)


# Text-to-Speech functions, using Windows TTS
def send_local_text_to_voice(text):
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")

    # List available voices
    if "TTS_WINDOWS_LIST" in globals() and TTS_WINDOWS_LIST:
        for index, voice in enumerate(voices):
            if voice.name == TTS_WINDOWS_VOICE:
                log("info", f"Voice {index}: {voice.name} < selected")
            else:
                log("info", f"Voice {index}: {voice.name}")

    for index, voice in enumerate(voices):
        if voice.name == TTS_WINDOWS_VOICE:
            break
    else:
        index = None

    if index is not None:
        try:
            engine.setProperty("voice", voices[index].id)
            engine.setProperty("rate", TTS_WINDOWS_RATE)
            engine.setProperty("volume", TTS_WINDOWS_VOLUME)

            # Save to temporary file instead of speaking directly
            temp_file = "./tts-temp.mp3"
            engine.save_to_file(text, temp_file)
            engine.runAndWait()

            # Add effects if enabled
            if TTS_EFFECTS:
                add_audio_effects(temp_file)

            # Play with pygame mixer
            mixer.init()
            mixer.music.load(temp_file)
            mixer.music.play()

            while mixer.music.get_busy():
                time.sleep(0.1)

            mixer.music.unload()
            mixer.quit()

            # Cleanup
            os.remove(temp_file)

        except Exception as e:
            log("error", f"Windows TTS error: {str(e)}")
    else:
        log("error", "Specified TTS voice not found.")


# Text-to-Speech functions, using Edge TTS
async def send_edge_text_to_voice(text):
    try:
        voice = TTS_EDGE_VOICE
        rate = TTS_EDGE_RATE
        volume = TTS_EDGE_VOLUME
        pitch = TTS_EDGE_PITCH
        communicate = edge_tts.Communicate(
            text, voice, rate=rate, volume=volume, pitch=pitch
        )

        temp_file = "./tts-temp.mp3"
        await communicate.save(temp_file)

        # Add effects to the audio file
        if TTS_EFFECTS:
            add_audio_effects(temp_file)

        # Play with pygame mixer
        mixer.init()
        mixer.music.load(temp_file)
        mixer.music.play()

        while mixer.music.get_busy():
            time.sleep(0.1)

        mixer.music.unload()
        mixer.quit()

        # Cleanup
        os.remove(temp_file)

    except Exception as e:
        log("error", f"Edge TTS error: {str(e)}")
        # Optionally fall back to Windows TTS
        if TTS_TYPE != "WINDOWS":
            log("info", "Falling back to Windows TTS")
            send_local_text_to_voice(text)


def add_audio_effects(audio):
    # Load the audio file
    audio, sample_rate = sf.read("./tts-temp.mp3")

    # Create an effects board
    board = Pedalboard(
        [
            Reverb(room_size=0.1, wet_level=0.1),
            Chorus(rate_hz=2.0, depth=0.25),  # Add chorus effect
        ]
    )

    # Apply effects
    effected = board(audio, sample_rate)

    # Save the processed audio
    sf.write("./tts-temp.mp3", effected, sample_rate)
