from base64 import b64decode
from typing import Optional, Dict

from application.notification import IObserver, NotificationCenter, NotificationData, Notification
from application.python import Null
from azure.cognitiveservices.speech.speech import EventSignal
from zope.interface import implementer

import azure.cognitiveservices.speech as STT


@implementer(IObserver)
class STTEngine():
    def __init__(self, triggers: Dict, notification_center: NotificationCenter):
        """
        Constructor for STTEngine class. Subscribe self to the notification 
        center passed to it. This allows it to send and recieve notifications 
        from SIPApplication which instantiates it.

        TODO: Figure out if NotificationCenter is singleton, maybe i dont even 
        need to pass it to the constructor

        :param triggers: Keys are the exact phrases that the recognizer will be 
        looking for, and the values are the event names that will be fired when 
        those phrases are recognized.
        :type triggers: Dict
        :param notification_center: Pass a notification center to this class in 
        order to be able to notify other classes about recognizing phrases.
        :type notification_center: NotificationCenter
        """

        self.notification_center = notification_center
        self.notification_center.add_observer(self)

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
        self.connect_signals()

    ##############################################################
    ########################### EVENTS ###########################
    ##############################################################
    def evt_session_started(self, evt: EventSignal):
        """
        Event handler for SpeechRecognizers SessionStarted signal. Currently 
        used only to check if the recognizer started properly.

        :param evt: SpeechRecognizer class fires this event when its initially 
        started
        :type evt: EventSignal
        """
        print("Session started: {}".format(evt))

    def evt_session_ended(self, evt: EventSignal):
        """
        Event handler for SpeechRecognizers SessionEnded signal. Makes a call 
        to stop_callback() method. This method does any necessary cleanup after 
        the recognizer is done.

        :param evt: SpeechRecognizer class fires this event when the session 
        ends
        :type evt: EventSignal
        """
        print("Session ended: {}".format(evt))
        self.stop_callback(evt)

    def evt_canceled(self, evt: EventSignal):
        """
        Event handler for SpeechRecognizers SessionCancel signal. Makes a call 
        to stop_callback() method. This method does any necessary cleanup after 
        the recognizer is done.

        :param evt: SpeechRecognizer class fires this event when recognizer 
        gets cancelled.
        :type evt: EventSignal
        """
        print("Canceled {}".format(evt))
        self.stop_callback(evt)

    def evt_recognizing(self, evt: EventSignal):
        """
        Event handler for SpeechRecognizers Recognizing signal. Makes a call 
        to stop_callback() method. Currently used only to check if the 
        recognizer is registering input.

        :param evt: SpeechRecognizer class fires this event when input comes 
        through and it is being processed.
        :type evt: EventSignal
        """
        return
        print("Recognizing {}".format(evt))

    def evt_recognized(self, evt: EventSignal):
        """
        Use this signal to check if the recognized phrase fits any of the 
        phrases that were passed to the constructor, and in case that it does 
        fire an event to notify other listeners about it.

        :param evt: SpeechRecognizer class fires this event when an input gets 
        recognized.
        :type evt: EventSignal
        """
        text = evt.result.text
        text_lower = text.lower().strip(".")
        if text_lower in self.triggers:
            print("Recognized command: {}".format(text))
            self.notify(text_lower)

    def _NH_SIPSessionDidStart(self, notification):
        """
        SIPApplication will fire this event as soon as a new session starts.

        When a new session has started, make sure to save the proposed session 
        and start the recognizer

        :param notification: Any data that the notification sender might pass
        :type notification: Notification
        """
        print('Session started!')
        # self.recognizer.start_continuous_recognition()

    def _NH_SIPSessionDidFail(self, notification):
        """
        SIPApplication will fire this event in case a session fails.

        In case that the session fails, cleanup by stoping the player if it is
        running, and stopping the recognizer.

        :param notification: Any data that the notification sender might pass
        :type notification: Notification
        """
        print('Failed to connect')
        # self.recognizer.stop_continuous_recognition()

    def _NH_SIPSessionDidEnd(self, notification):
        """
        SIPApplication will fire this event when a session ends.

        Whan a session ends, cleanup by stoping the player if it is running, 
        and stopping the recognizer.

        :param notification: Any data that the notification sender might pass
        :type notification: Notification
        """
        print('Session ended . . .')
        # self.recognizer.stop_continuous_recognition()

    ##############################################################
    ########################## HELPERS ###########################
    ##############################################################

    def handle_notification(self, notification):
        """
        A helper method that catches events and calls appropriate handle method
            based on the data passed in the notification.

        :param notification: Any data that the notification sender might pass
        :type notification: Notification
        """
        handler = getattr(self, '_NH_%s' % notification.name, Null)
        handler(notification)
        
    def connect_signals(self):
        """
        Helper method to connect all of the recognizers signals to appropriate 
        methods.
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

    def stop_callback(self, evt: EventSignal):
        """
        A helper method to cleanup after the reconizer has been stopped or 
        cancelled.

        :param event: The same event that has been passed to the method that is 
        calling this method.
        :type event: EventSignal
        """
        self.found = True
        print("Speech recognition finished.")

    def notify(self, trigger):
        """
        A helper method to send a notification to all listeners of the 
        notification center passed to the constructor of this class.

        :param trigger: [description]
        :type trigger: [type]
        """
        print("Sending notification: {}".format(self.triggers[trigger]))
        self.notification_center.post_notification(
                    self.triggers[trigger], 
                    self.recognizer, 
                    data=NotificationData()
                )
