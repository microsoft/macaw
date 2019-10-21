import logging
import os
from pydub import AudioSegment
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import tempfile
import traceback

from code import util
from code.util.msg import Message
from code.interface.interface import Interface


class TelegramBot(Interface):
    def __init__(self, params):
        super().__init__(params)
        # Enable logging
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        """Start the bot."""
        # Create the Updater and pass it your bot's token.
        # Make sure to set use_context=True to use the new context based callbacks
        # Post version 12 this will no longer be necessary
        # self.updater = Updater("920831379:AAFt_jr7bK4sFuv4FJ1hWIWqABoEa9w9708", use_context=True)
        self.updater = Updater(self.params['bot_token'], use_context=True)
        # Get the dispatcher to register handlers
        self.dp = self.updater.dispatcher

        # on different commands - answer in Telegram
        self.dp.add_handler(CommandHandler("start", self.start))
        self.dp.add_handler(CommandHandler("help", self.help))

        # on noncommand i.e message - echo the message on Telegram
        self.dp.add_handler(MessageHandler(Filters.text, self.request_handler))
        self.dp.add_handler(MessageHandler(Filters.voice, self.voice_request_handler))
        self.dp.add_handler(CallbackQueryHandler(self.button_click_handler))

        # log all errors
        self.dp.add_error_handler(self.error)

    # Define a few command handlers. These usually take the two arguments bot and
    # update. Error handlers also receive the raised TelegramError object in error.
    def start(self, update, context):
        """Send a message when the command /start is issued."""
        update.message.reply_text('Hi!')

    def help(self, update, context):
        """Send a message when the command /help is issued."""
        update.message.reply_text('Help!')

    def request_handler(self, update, context):
        try:
            print(update.message)
            user_info = {'first_name': update.message.chat.first_name,
                         'last_name': update.message.chat.last_name,
                         'is_bot': update._effective_user.is_bot
            }
            msg_info = {'msg_id': update.message.message_id,
                        'msg_type': 'text',
                        'msg_source': 'user'}
            msg = Message(user_interface='telegram',
                          user_id=update.message.chat.id,
                          user_info=user_info,
                          msg_info=msg_info,
                          text=update.message.text,
                          timestamp=util.current_time_in_milliseconds())
            output = self.params['live_request_handler'](msg)
            self.result_presentation(output, {'update': update})
        except Exception as ex:
            traceback.print_exc()

    def voice_request_handler(self, update, context):
        """Echo the user message."""
        try:
            ogg_file = tempfile.NamedTemporaryFile(delete=True)
            update.message.voice.get_file().download(ogg_file.name)
            text = self.params['asr'].speech_to_text(ogg_file.name)
            ogg_file.close()
            # update.message.text = text
            update.message.reply_text('Macaw heard: ' + text)

            user_info = {'first_name': update.message.chat.first_name,
                         'last_name': update.message.chat.last_name,
                         'is_bot': update._effective_user.is_bot
                         }
            msg_info = {'msg_id': update.message.message_id,
                        'msg_type': 'voice',
                        'msg_source': 'user'}
            msg = Message(user_interface='telegram',
                          user_id=update.message.chat.id,
                          user_info=user_info,
                          msg_info=msg_info,
                          text=text,
                          timestamp=util.current_time_in_milliseconds())
            output = self.params['live_request_handler'](msg)
            self.result_presentation(output, {'update': update})
        except Exception as ex:
            traceback.print_exc()

    def button_click_handler(self, update, context):
        try:
            print(update)
            user_info = {'first_name': update.callback_query.message.chat.first_name,
                         'last_name': update.callback_query.message.chat.last_name,
                         'is_bot': update._effective_user.is_bot
                         }
            msg_info = {'msg_id': update.callback_query.message.message_id,
                        'msg_type': 'command',
                        'msg_source': 'user'}
            msg = Message(user_interface='telegram',
                          user_id=update.callback_query.message.chat.id,
                          user_info=user_info,
                          msg_info=msg_info,
                          text=update.callback_query.data,
                          timestamp=util.current_time_in_milliseconds())
            output = self.params['live_request_handler'](msg)
            # print(output)
            # query.message.reply_text(output[:4096])
            self.result_presentation(output, {'update': update})
        except Exception as ex:
            traceback.print_exc()

    def result_presentation(self, response_msg, params):
        try:
            update = params['update']
            if response_msg.msg_info['msg_type'] == 'text':
                if update.message is not None:
                    update.message.reply_text(response_msg.text[:4096])
                elif update.callback_query.message is not None:
                    update.callback_query.message.reply_text(response_msg.text[:4096])
            elif response_msg.msg_info['msg_type'] == 'voice':
                ogg_file_name = self.params['asg'].text_to_speech(response_msg.text[:4096])
                # update.message.reply_voice(voice=open(ogg_file_name, 'rb'))
                self.updater.bot.send_voice(chat_id=update.message.chat.id, voice=open(ogg_file_name, 'rb'))
                # update.message.reply_voice(voice=open('/mnt/e/example.ogg', 'rb'))
                os.remove(ogg_file_name)
                # raise Exception('Not implemented yet!')
            elif response_msg.msg_info['msg_type'] == 'options':
                keyboard = [[InlineKeyboardButton(option_text[:30], callback_data=option_data)]
                            for (option_text, option_data, output_score) in response_msg.msg_info['options']]
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text(response_msg.text[:4096], reply_markup=reply_markup)
            elif response_msg.msg_info['msg_type'] == 'error':
                error_msg = 'ERROR: NO RESULT!'
                if update.message is not None:
                    update.message.reply_text(error_msg)
                elif update.callback_query.message is not None:
                    update.callback_query.message.reply_text(error_msg)
            else:
                raise Exception('The msg_type is not recognized:', response_msg.msg_info['msg_type'])
        except Exception as ex:
            traceback.print_exc()

    def error(self, update, context):
        """Log Errors caused by Updates."""
        self.logger.warning('Update "%s" caused error "%s"', update, context.error)

    def run(self):
        # Start the Bot
        self.updater.start_polling()
        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        self.updater.idle()
from os import path

