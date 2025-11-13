# text_program/audio_record.py
import speech_recognition as sr
import sys

def record(file_path):
    recognizer = sr.Recognizer()

    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)

        try:
            text = recognizer.recognize_google(audio, language='en-US')
            print(text)
        except sr.UnknownValueError:
            print('Can not understand audio')
        except sr.RequestError as e:
            print(f"Identification service error: {e}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        record(file_path)