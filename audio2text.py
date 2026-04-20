import math
import os
import tempfile
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
        self.chunk_paths = []
        self.full_text = ""

    def split_audio(self, output_folder):
        audio = AudioSegment.from_file(self.input_path)
        total_length = len(audio)

        os.makedirs(output_folder, exist_ok=True)

        num_chunks = math.ceil(total_length / self.chunk_length_ms)
        self.chunk_paths = []

        for i in range(num_chunks):
            start = i * self.chunk_length_ms
            end = min(start + self.chunk_length_ms, total_length)
            chunk = audio[start:end]
            chunk_path = os.path.join(output_folder, f"chunk_{i:03d}.wav")
            chunk.export(chunk_path, format="wav")
            self.chunk_paths.append(chunk_path)

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


def run_transcription(audio_folder="audios", title=None) -> dict:
    """
    Transcreve todos os arquivos de áudio dentro da pasta 'audios'
    e retorna as transcrições consolidadas.
    """
    audio_dir = Path(audio_folder)
    if not audio_dir.exists() or not audio_dir.is_dir():
        return {
            "file": "",
            "content": f"A pasta de áudio '{audio_folder}' não foi encontrada.",
        }

    mom_title = (
        f"{title}.txt"
        if title
        else f"transcricao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    )
    text_file_path = Path(f"docs/{mom_title}")

    if text_file_path.exists():
        with open(text_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        parts = content.strip().split(" \n\n")

        return {"file": str(text_file_path), "content": " | ".join(parts)}

    audio_files = [f for f in audio_dir.iterdir() if f.is_file()]
    if not audio_files:
        return {
            "file": "",
            "content": "Nenhum arquivo de áudio para transcrever na pasta.",
        }

    text_file_path.parent.mkdir(parents=True, exist_ok=True)
    text_file_path.touch(exist_ok=True)

    parts = []

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        for file in audio_files:
            text = Audio2Text(file)
            chunks_dir = temp_path / text.audio_name
            text.split_audio(chunks_dir)

            transcription = text.transcribe()
            text.write_to_file(str(text_file_path))
            parts.append(transcription.strip())

    return {"file": str(text_file_path), "content": " | ".join(parts)}


def main():
    result = run_transcription()
    pprint(result)


if __name__ == "__main__":
    main()
