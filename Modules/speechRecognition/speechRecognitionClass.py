import pyaudio
import speech_recognition as sr

class voiceRecognition:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def getCommand(self):
        with sr.Microphone() as source:
            print("Adjusting noise ")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Recording for 4 seconds")
            self.recorded_audio = self.recognizer.listen(source, timeout=4)
            print("Done recording")
        self.recognizeAudio()
    
    def recognizeAudio(self):
        try:
            print("Recognizing the text")
            text = self.recognizer.recognize_google(
                    self.recorded_audio,
                    language="en-US"
                    )
            print("Decoded Text : {}".format(text))
        except Exception as ex:
            print(ex)


voice = voiceRecognition()
voice.getCommand()