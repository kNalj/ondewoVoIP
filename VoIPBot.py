from threading import Event
from application.notification import NotificationCenter
from application.python import Null
from sipsimple.configuration.settings import SIPSimpleSettings

from sipsimple.session import Session
from sipsimple.account import Account, AccountManager, BonjourAccount
from sipsimple.application import SIPApplication
from application.notification import NotificationCenter, NotificationData
from sipsimple.audio import WavePlayer
from sipsimple.storage import FileStorage
from sipsimple.configuration import ConfigurationManager
from sipsimple.threading.green import run_in_green_thread
from sipsimple.util import user_info, execute_once



class VoIPBot(SIPApplication):
	def __init__(self):
		"""

		"""
		print("Building VoIP bot . . .")

		super(SIPApplication, self).__init__()
		
		self.account = None
		self.session = None
		self.wave_file = None  # This will be played to the user requesting something
		self.player = None
		self.ended = Event()

		notification_center = NotificationCenter()
		notification_center.add_observer(self)

	##############################################################
	########################### EVENTS ###########################
	##############################################################

	@run_in_green_thread
	def _NH_SIPApplicationDidStart(self, notification):
		"""
		"""
		self.player = WavePlayer(SIPApplication.voice_audio_mixer, self.wave_file, loop_count=1)
		# self.session = Session(self.account)

		print('SIP application started')

	def _NH_SIPSessionDidStart(self, notification):
		"""
		This method should start a new session, and also create AudioBridge to pass the incoming stream to the STT processor.
		"""
		print('Session started!')


	def _NH_SIPSessionDidFail(self, notification):
		"""
		Cleanup whatever you started
		"""
		print('Failed to connect')
		# self.session = None

	def _NH_SIPSessionDidEnd(self, notification):
		"""
		Cleanup Session and AudioBridge
		"""
		print('Session ended')
		# self.session = None

	def _NH_SIPSessionNewIncoming(self, notification):
		"""
		
		"""
		print("Incoming call . . .")
		print(notification.sender)
		self.session = notification.sender
		self.session.accept(notification.data.streams)

	##############################################################
	########################## HELPERS ###########################
	##############################################################
	@execute_once
	def prepare(self):
		"""
		
		"""
		print("Preparing VoIP bot . . .")
		self.start(FileStorage("config"))

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
		settings.audio.input_device = "system_dafault"
		settings.audio.output_device = "system_default"
		settings.save()

	def cleanup(self):
		"""
		
		"""
		self.stop()

	def handle_notification(self, notification):
		handler = getattr(self, '_NH_%s' % notification.name, Null)
		handler(notification)


def main():
	bot = VoIPBot()
	bot.prepare()

	input()

	if bot.session:
		bot.session.end()
	bot.ended.wait()


if __name__ == "__main__":
	main()