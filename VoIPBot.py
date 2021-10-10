from threading import Event

from application.notification import NotificationCenter
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
		TODO: Write documentation
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
		TODO: Write documentation

		:param notification: [description]
		:type notification: [type]
		"""
		self.player = WavePlayer(SIPApplication.voice_audio_mixer, self.wave_file, loop_count=1)
		print('SIP application started')

	def _NH_SIPSessionDidStart(self, notification):
		"""
		This method should start a new session, and also create AudioBridge to pass the incoming stream to the STT processor.

		:param notification: [description]
		:type notification: [type]
		"""
		print('Session started!')
		self.session = notification.sender
		self.recognizer.speech_recognition_from_mic()

	def _NH_SIPSessionDidFail(self, notification):
		"""
		TODO: Write documentation

		:param notification: [description]
		:type notification: [type]
		"""
		print('Failed to connect')
		self.session = None
		self.player.stop()
		self.recognizer.recognizer.stop_continuous_recognition()

	def _NH_SIPSessionDidEnd(self, notification):
		"""
		TODO: Write documentation

		:param notification: [description]
		:type notification: [type]
		"""
		print('Session ended . . .')
		self.session = None
		self.player.stop()
		self.recognizer.recognizer.stop_continuous_recognition()

	def _NH_SIPSessionNewIncoming(self, notification):
		"""
		TODO: Write documentation

		:param notification: [description]
		:type notification: [type]
		"""
		print("Incoming call . . .")
		session = notification.sender
		session.send_ring_indication()
		# Maybe some kind of accept/decline (not needed for now)
		session.accept(notification.data.streams)

	def _NH_PlaySongRequested(self, notification):
		"""[summary]

		:param notification: [description]
		:type notification: [type]
		"""
		self.add_media_to_session("./media/sounds/PinkPanther60.wav")

	def _NH_PlayJokeRequested(self, notification):
		"""[summary]

		:param notification: [description]
		:type notification: [type]
		"""
		print("This should play a joke")

	def _NH_TestRequested(self, notification):
		"""[summary]

		:param notification: [description]
		:type notification: [type]
		"""
		print("test notification triggered")

	##############################################################
	########################## HELPERS ###########################
	##############################################################
	@execute_once
	def prepare(self):
		"""
		TODO: Write documentation
		"""
		print("Preparing VoIP bot . . .")
		self.start(FileStorage("config"))

		# This is obviously not the ideal way of loging into an account
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
			" want to hear a joke": "PlayJokeRequested",
			"test": "TestRequested"
		}
		self.recognizer = STTEngine(self.triggers, self.notification_center)

	def cleanup(self):
		"""
		TODO: Write documentation
		"""
		self.stop()

	def handle_notification(self, notification):
		"""
		TODO: Write documentation

		:param notification: [description]
		:type notification: [type]
		"""
		handler = getattr(self, '_NH_%s' % notification.name, Null)
		if notification.name in [self.triggers.values()]:
			print("{} will be called".format(notification.name))
		handler(notification)

	def add_media_to_session(self, relative_location):
		"""
		TODO: Write documentation

		:param relative_location: [description]
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