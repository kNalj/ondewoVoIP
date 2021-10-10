from threading import Thread
import time

from base64 import b64decode
from typing import Optional, Dict
from application.notification import Notification, NotificationCenter, NotificationData

import azure.cognitiveservices.speech as STT


OptionalStr = Optional[str]


class STTEngine():
    def __init__(self, triggers: Dict, notification_center: NotificationCenter):
        """[summary]

        :param triggers: [description]
        :type triggers: Dict
        """

        self.notification_center = notification_center

        self.speech_sub = b64decode("YTY5MDAyY2RhZWFmNDUzZWFjNWE4NDU3OWE3YTUzMmM=").decode("utf-8")
        self.speech_region = "westeurope"
        self.speech_language = "en-US"

        self.speech_config = STT.SpeechConfig(
            subscription=self.speech_sub,
            region=self.speech_region,
            speech_recognition_language=self.speech_language
        )

        self.triggers = triggers  # Sentences that trigger a command
        self.recognizer = STT.SpeechRecognizer(speech_config=self.speech_config)

        self.found = False  # Use this to stop continuous recognition
        self.event = None

    ##############################################################
    ########################### EVENTS ###########################
    ##############################################################
    def evt_session_started(self, evt):
        """[summary]

        :param evt: [description]
        :type evt: [type]
        """
        print("Session started: {}".format(evt))

    def evt_session_ended(self, evt):
        """[summary]

        :param evt: [description]
        :type evt: [type]
        """
        print("Session ended: {}".format(evt))
        self.stop_callback(evt)

    def evt_canceled(self, evt):
        """[summary]

        :param evt: [description]
        :type evt: [type]
        """
        print("Canceled {}".format(evt))
        self.stop_callback(evt)

    def evt_recognizing(self, evt):
        """[summary]

        :param evt: [description]
        :type evt: [type]
        """
        return
        print("Recognizing {}".format(evt))

    def evt_recognized(self, evt):
        """[summary]

        :param evt: [description]
        :type evt: [type]
        """
        text = evt.result.text
        text_lower = text.lower().strip(".")
        if text_lower in self.triggers:
            print("Recognized command: {}".format(text))
            self.found = True
            self.recognizer.stop_continuous_recognition()
        self.event = text_lower

    ##############################################################
    ########################## HELPERS ###########################
    ##############################################################

    def speech_recognition_from_mic(self):
        """[summary]
        """

        self.connect_signals()
        self.recognizer.start_continuous_recognition()

        while not self.found:
            time.sleep(.5)

        self.recognizer.stop_continuous_recognition()
        
    def connect_signals(self):
        """[summary]
        """
        # Let everyone know i started a session
        self.recognizer.session_started.connect(lambda evt: self.evt_session_started(evt))
        # Let everyone know the session ended
        self.recognizer.session_stopped.connect(lambda evt: self.evt_session_ended(evt))
        # I got canceled
        self.recognizer.canceled.connect(lambda evt: self.evt_canceled(evt))
        # I heard somethin; let me figure it out

        self.recognizer.recognizing.connect(lambda evt: self.evt_recognizing(evt))
        # This is what i heard, let me see if its a command
        self.recognizer.recognized.connect(lambda evt: self.evt_recognized(evt))

    def stop_callback(self, evt):
        """[summary]

        :param event: [description]
        :type event: [type]
        """
        self.found = True
        print("Speech recognition finished.")
        self.notify(self.event)

    def notify(self, trigger):
        """[summary]

        :param trigger: [description]
        :type trigger: [type]
        """
        print("Sending notification: {}".format(self.triggers[trigger]))
        self.notification_center.post_notification(
                    self.triggers[trigger], 
                    self.recognizer, 
                    data=NotificationData()
                )
