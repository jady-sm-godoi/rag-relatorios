import math
import os
import shutil
from datetime import datetime
from pathlib import Path
from pprint import pprint

import speech_recognition as sr
from pydub import AudioSegment


class Audio2Text:
    def __init__(self, input_path):
        self.input_path = input_path
        self.audio_name = str(input_path).split("/")[-1].split(".")[0]
        self.chunk_length_ms = 30_000
        self.chunk_paths = self.split_audio()
        self.full_text = ""

    def split_audio(self):
        audio = AudioSegment.from_file(self.input_path)
        total_length = len(audio)

        output_folder = f"audios/chunks/{self.audio_name}"
        os.makedirs(output_folder, exist_ok=True)

        num_chunks = math.ceil(total_length / self.chunk_length_ms)
        chunk_paths = []

        for i in range(num_chunks):
            start = i * self.chunk_length_ms
            end = min(start + self.chunk_length_ms, total_length)
            chunk = audio[start:end]
            chunk_path = os.path.join(output_folder, f"chunk_{i:03d}.wav")
            chunk.export(chunk_path, format="wav")
            chunk_paths.append(chunk_path)

        return chunk_paths

    def transcribe(self):
        recognizer = sr.Recognizer()

        print(f"- {self.audio_name} ", end="", flush=True)

        for path in self.chunk_paths:
            print(".", end="", flush=True)

            with sr.AudioFile(path) as source:
                audio = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio, language="pt-BR")
                self.full_text += text + " "
            except sr.UnknownValueError:
                self.full_text += "[inaudível] "
            except sr.RequestError as e:
                self.full_text += f"[erro: {e}] "

        print()
        return self.full_text

    def write_to_file(self, text_file_path):
        with open(text_file_path, "a") as f:
            f.write(f"{self.full_text}\n\n")


# def get_unique_filename(filepath: str) -> Path:
#     """
#     Returns a unique path.
#     If the file already exists, it adds numbering (_1, _2, etc.).
#     """
#     path = Path(filepath)
#     parent = path.parent
#     stem = path.stem
#     suffix = path.suffix

#     if not path.exists():
#         return path

#     counter = 1
#     while True:
#         new_name = f"{stem}_{counter}{suffix}"
#         new_path = parent / new_name

#         if not new_path.exists():
#             return new_path

#         counter += 1


def run_transcription(audio_folder="audios", title=None) -> dict:
    """
    Transcribe all audio files inside the 'audios' folder
    and return the transcriptions
    """
    mom_title = (
        f"{title}.txt"
        if title
        else f"{datetime.isoformat(datetime.now())}.txt"
    )
    text_file_path = Path(f"docs/{mom_title}")

    if text_file_path.exists():
        with open(text_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        parts = content.strip().split(" \n\n")

        return {"file": str(text_file_path), "content": " | ".join(parts)}

    text_file_path.parent.mkdir(parents=True, exist_ok=True)
    text_file_path.touch(exist_ok=True)

    audio_files = [
        file
        for file in os.listdir(audio_folder)
        if os.path.isfile(os.path.join(audio_folder, file))
    ]

    parts = []

    for file in audio_files:
        text = Audio2Text(f"{audio_folder}/{file}")
        transcription = text.transcribe()
        text.write_to_file(str(text_file_path))
        parts.append(transcription.strip())

    if os.path.exists("audios/chunks"):
        shutil.rmtree("audios/chunks")

    return {"file": str(text_file_path), "content": " | ".join(parts)}


def main():
    result = run_transcription()
    pprint(result)


if __name__ == "__main__":
    main()
