import pyaudio
import speech_recognition as sr
import pyttsx3
import time


def short_Command(message="Recording"):
    #Short command is 4 seconds
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        #text_to_Speech("Adjusting noise.")
        recognizer.adjust_for_ambient_noise(source, duration=.5)
        text_to_Speech(message)
        print("listening")
        recorded_audio = recognizer.listen(source,phrase_time_limit=2, timeout=5)
    try:
        text = recognizer.recognize_google(
            recorded_audio,
            language="en-US"
        )
        return text
    except Exception as exception:
        print(exception)

def text_to_Speech(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 145) 
    engine.say(text)
    engine.runAndWait()
    engine.stop()

def always_listening():
    #listens for hotword
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        #Maybe use snowboy for hotword detection
        print("Beginning listening, say the keyphrase")
        audio = recognizer.listen(source, timeout=None)
        #print(audio, type(audio))
    try:
        text = recognizer.recognize_google(
            audio,
            language="en-US"
        )
        print(f"text:{text}")
        if text == "Alfred" or text == "alfred":
            return True
    except Exception as exception:
        print(exception)
    return False



