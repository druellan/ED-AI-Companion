import os
import time
import pyttsx3
import edge_tts
from pygame import mixer
from pedalboard import Pedalboard, Reverb, Chorus
import soundfile as sf
from components.utils import output
from components.constants import COLOR

# Config.py
from config import (
    TTS_WINDOWS_VOICE,
    TTS_WINDOWS_RATE,
    TTS_WINDOWS_VOLUME,
    TTS_WINDOWS_LIST,
    TTS_EDGE_VOICE,
    TTS_EDGE_RATE,
    TTS_EDGE_VOLUME,
    TTS_EDGE_PITCH,
    TTS_TYPE,
    TTS_EFFECTS,
)


def send_text_to_voice(text):
    if TTS_TYPE == "WINDOWS":
        send_local_text_to_voice(text)
    else:
        send_edge_text_to_voice(text)


# Text-to-Speech functions, using Windows TTS
def send_local_text_to_voice(text):
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")

    # List available voices
    if "TTS_WINDOWS_LIST" in globals() and TTS_WINDOWS_LIST:
        for index, voice in enumerate(voices):
            if voice.name == TTS_WINDOWS_VOICE:
                output(f"Voice {index}: {voice.name} < selected", COLOR.BRIGHT_WHITE)
            else:
                output(f"Voice {index}: {voice.name}")

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
            output(f"Windows TTS error: {str(e)}", COLOR.RED)
    else:
        output("Specified TTS voice not found.", COLOR.RED)


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
        output(f"Edge TTS error: {str(e)}", COLOR.RED)
        # Optionally fall back to Windows TTS
        if TTS_TYPE != "WINDOWS":
            output("Falling back to Windows TTS", COLOR.YELLOW)
            await send_local_text_to_voice(text)


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
