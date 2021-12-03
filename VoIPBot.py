from threading import Event, Thread

from application.notification import NotificationCenter, Notification
from application.python import Null
from sipsimple.configuration.settings import SIPSimpleSettings

from sipsimple.account import Account, AccountManager
from sipsimple.application import SIPApplication
from sipsimple.audio import WavePlayer
from sipsimple.storage import FileStorage
from sipsimple.threading.green import run_in_green_thread
from sipsimple.util import execute_once

from SpeechEngine import STTEngine


class VoIPBot(SIPApplication):
	def __init__(self):
		"""
		Constructor for the VoIPBot class.  Creates empty member variables, and 
		subscribes itself to a notification center.
		"""
		print("Building VoIP bot . . .")

		super(SIPApplication, self).__init__()

		self.account = None
		self.session = None  # This allways gonna be the current ongoing session, if any
		self.wave_file = None  # This will be played to the user requesting something
		self.player = None  # Wave player that will play the requested file
		self.ended = Event()

		self.speech_sub = None
		self.speech_region = None
		self.sepeech_language = None
		self.recognizer = None
		self.triggers = {}

		self.notification_center = NotificationCenter()
		self.notification_center.add_observer(self)

	##############################################################
	########################### EVENTS ###########################
	##############################################################

	@run_in_green_thread
	def _NH_SIPApplicationDidStart(self, notification):
		"""
		SIPApplication will fire this event as soon as it starts.

		Once the application started, create and configure the wave player.
		This could be done in some other place as well.

		:param notification: Any data that the notification sender might pass
		:type notification: Notification
		"""
		self.player = WavePlayer(
			SIPApplication.voice_audio_mixer, 
			self.wave_file, 
			loop_count=1
		)
		print('SIP application started')

	def _NH_SIPSessionDidStart(self, notification):
		"""
		SIPApplication will fire this event as soon as a new session starts.

		When a new session has started, make sure to save the proposed session 
		and start the recognizer

		:param notification: Any data that the notification sender might pass
		:type notification: Notification
		"""
		print('Session started!')
		self.session = notification.sender
		self.recognizer.recognizer.start_continuous_recognition()

	def _NH_SIPSessionDidFail(self, notification):
		"""
		SIPApplication will fire this event in case a session fails.

		In case that the session fails, cleanup by stoping the player if it is
		running, and stopping the recognizer.

		:param notification: Any data that the notification sender might pass
		:type notification: Notification
		"""
		print('Failed to connect')
		self.session = None
		self.player.stop()
		self.recognizer.recognizer.stop_continuous_recognition()

	def _NH_SIPSessionDidEnd(self, notification):
		"""
		SIPApplication will fire this event when a session ends.

		Whan a session ends, cleanup by stoping the player if it is running, 
		and stopping the recognizer.

		:param notification: Any data that the notification sender might pass
		:type notification: Notification
		"""
		print('Session ended . . .')
		self.session = None
		self.player.stop()
		self.recognizer.recognizer.stop_continuous_recognition()

	def _NH_SIPSessionNewIncoming(self, notification):
		"""
		SIPApplication will fire this event when another SIP client proposes
		a new session to it (for example on incoming call).

		:param notification: Any data that the notification sender might pass
		:type notification: Notification
		"""
		print("Incoming call . . .")
		session = notification.sender
		session.send_ring_indication()
		# Maybe some kind of accept/decline (not needed for now)
		session.accept(notification.data.streams)

	def _NH_PlaySongRequested(self, notification):
		"""
		Recognizer will fire this event once a certain phrase matching this 
		action is recognized.

		:param notification: Any data that the notification sender might pass
		:type notification: Notification
		"""
		self.add_media_to_session("./media/sounds/song.wav")

	def _NH_PlayJokeRequested(self, notification):
		"""
		Recognizer will fire this event once a certain phrase matching this 
		action is recognized.

		:param notification: Any data that the notification sender might pass
		:type notification: Notification
		"""
		self.add_media_to_session("./media/sounds/joke.wav")

	def _NH_TestRequested(self, notification):
		"""
		Used for testing the notification system.

		:param notification: Any data that the notification sender might pass
		:type notification: Notification
		"""
		print("test notification triggered")

	##############################################################
	########################## HELPERS ###########################
	##############################################################
	@execute_once
	def prepare(self):
		"""
		This is a helper method that that prepares things needed for this class
		 to function properly. Start the app with the specified config file.
		 To make sure that correct data is written in the config file write it
		 all in the file anyway. This includes account data, and audio 
		 configuration.

		 Finnaly create a dictionary containing all the trigger phrases that
		 this bot should respond to, and create a speech to text engine to 
		 which that dictionary is passed.
		"""
		print("Preparing VoIP bot . . .")
		self.start(FileStorage("config"))

		# This is obviously not the ideal way of loging into an account,
		acc_manager = AccountManager()
		if not acc_manager.has_account("ondewo@sip2sip.info"):
			acc = Account("ondewo@sip2sip.info")
			acc.auth.password = "ondewo12"
			acc.display_name = "SIP on Virtual Machine"
			acc.enabled = True
			acc.save()

		settings = SIPSimpleSettings()
		settings.default_account = "ondewo@sip2sip.info"
		self.account = acc_manager.default_account
		settings.audio.alert_device = "system_default"
		settings.audio.input_device = None
		settings.audio.output_device = "system_default"
		settings.save()

		self.triggers = {
			"i want to listen to a song": "PlaySongRequested",
			"i want to hear a joke": "PlayJokeRequested",
			"test": "TestRequested"
		}
		self.recognizer = STTEngine(self.triggers, self.notification_center)

	def cleanup(self):
		"""
		TODO: Write documentation

		Not even sure i will need this one
		"""
		# do stuff
		self.stop()

	def handle_notification(self, notification: Notification):
		"""
		A helper method that catches events and calls appropriate handle method
		 based on the data passed in the notification.

		:param notification: Any data that the notification sender might pass
		:type notification: Notification
		"""
		handler = getattr(self, '_NH_%s' % notification.name, Null)
		handler(notification)

	def add_media_to_session(self, relative_location):
		"""
		Helper method that adds a player to the current session. The player 
		will play the file passed to this method.

		:param relative_location: Relative location of the file to play
		:type relative_location: str
		"""
		audio_stream = self.session.streams[0]
		audio_stream.bridge.add(self.player)
		self.player.filename = relative_location
		self.player.play()


def main():
	bot = VoIPBot()
	bot.prepare()

	input()

	if bot.session:
		bot.session.end()
	bot.ended.wait()


if __name__ == "__main__":
	main()