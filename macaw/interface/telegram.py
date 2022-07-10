"""
The Telegram bot (supports interactive multi-modal interactions with different devices).

Authors: Hamed Zamani (hazamani@microsoft.com), George Wei (gzwei@umass.edu)
"""

import os
import tempfile
import traceback
import urllib.parse
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
)

from macaw.core.interaction_handler.msg import Message
from macaw.interface.interface import Interface


class TelegramBot(Interface):
    def __init__(self, params):
        """
        A Telegram bot interface for Macaw.

        Args:
            params(dict): A dict of parameters. The params 'logger' and 'bot_token' are mandatory.
        """
        super().__init__(params)
        self.logger = self.params["logger"]

        self.MAX_MSG_LEN = (
            1000  # maximum number of characters in each response message.
        )
        self.MAX_OPTION_LEN = (
            30  # maximum number of characters in each clickable option text.
        )

        # Starting the bot by creating the Updater.
        # Make sure to set use_context=True to use the new context based callbacks
        # If you don't have a bot_token, add 'botfather' to your personal Telegram account and follow the instructions
        # to get a token for your bot.
        self.updater = Updater(self.params["bot_token"], use_context=True)
        self.dp = self.updater.dispatcher

        # Telegram command handlers (e.g., /start)
        self.dp.add_handler(CommandHandler("start", self.start))
        self.dp.add_handler(CommandHandler("help", self.help))

        # Telegram message handlers
        self.dp.add_handler(MessageHandler(Filters.text, self.request_handler))
        self.dp.add_handler(MessageHandler(Filters.voice, self.voice_request_handler))
        self.dp.add_handler(CallbackQueryHandler(self.button_click_handler))

        # logging all errors
        self.dp.add_error_handler(self.error)

    def start(self, update, context):
        """Send a message when the command /start is issued."""
        update.message.reply_text(
            "Hi, welcome to Macaw! Macaw is an open-source extensible framework for "
            "conversational information seeking. Visit: https://github.com/microsoft/macaw"
        )

    def help(self, update, context):
        """Send a message when the command /help is issued."""
        update.message.reply_text(
            "Macaw should be able to answer your questions. Just ask a question!"
        )

    def request_handler(self, update, context):
        """This method handles all text messages, and asks result_presentation to send the response to the user."""
        try:
            self.logger.info(update.message)
            user_info = {
                "first_name": update.message.chat.first_name,
                "last_name": update.message.chat.last_name,
                "is_bot": update._effective_user.is_bot,
            }
            msg_info = {
                "msg_id": update.message.message_id,
                "msg_type": "text",
                "msg_source": "user",
            }
            msg = Message(
                user_interface="telegram",
                user_id=update.message.chat.id,
                user_info=user_info,
                msg_info=msg_info,
                text=update.message.text,
                timestamp=datetime.utcnow(),
            )
            output = self.params["live_request_handler"](msg)
            self.result_presentation(output, {"update": update})
        except Exception:
            traceback.print_exc()

    def voice_request_handler(self, update, context):
        """This method handles all voice messages, and asks result_presentation to send the response to the user."""
        try:
            ogg_file = tempfile.NamedTemporaryFile(delete=True)
            update.message.voice.get_file().download(ogg_file.name)
            text = self.params["asr"].speech_to_text(ogg_file.name)
            ogg_file.close()
            update.message.reply_text("Macaw heard: " + text)

            user_info = {
                "first_name": update.message.chat.first_name,
                "last_name": update.message.chat.last_name,
                "is_bot": update._effective_user.is_bot,
            }
            msg_info = {
                "msg_id": update.message.message_id,
                "msg_type": "voice",
                "msg_source": "user",
            }
            msg = Message(
                user_interface="telegram",
                user_id=update.message.chat.id,
                user_info=user_info,
                msg_info=msg_info,
                text=text,
                timestamp=datetime.utcnow(),
            )
            output = self.params["live_request_handler"](msg)
            self.result_presentation(output, {"update": update})
        except Exception:
            traceback.print_exc()

    def button_click_handler(self, update, context):
        """This method handles clicks, and asks result_presentation to send the response to the user."""
        try:
            self.logger.info(update)
            user_info = {
                "first_name": update.callback_query.message.chat.first_name,
                "last_name": update.callback_query.message.chat.last_name,
                "is_bot": update._effective_user.is_bot,
            }
            msg_info = {
                "msg_id": update.callback_query.message.message_id,
                "msg_type": "command",
                "msg_source": "user",
            }
            msg = Message(
                user_interface="telegram",
                user_id=update.callback_query.message.chat.id,
                user_info=user_info,
                msg_info=msg_info,
                text=update.callback_query.data,
                timestamp=datetime.utcnow(),
            )
            output = self.params["live_request_handler"](msg)
            self.result_presentation(output, {"update": update})
        except Exception as ex:
            traceback.print_exc()

    def result_presentation(self, response_msg, additional_params):
        """This method produces an appropriate response to be sent to the client."""
        try:
            if response_msg is None:
                return
            update = additional_params["update"]
            if response_msg.msg_info["msg_type"] == "text":
                if update.message is not None:
                    update.message.reply_text(response_msg.text[: self.MAX_MSG_LEN])
                elif update.callback_query.message is not None:
                    update.callback_query.message.reply_text(
                        response_msg.text[: self.MAX_MSG_LEN]
                    )
            elif response_msg.msg_info["msg_type"] == "voice":
                ogg_file_name = self.params["asg"].text_to_speech(
                    response_msg.text[: self.MAX_MSG_LEN]
                )
                self.updater.bot.send_voice(
                    chat_id=update.message.chat.id, voice=open(ogg_file_name, "rb")
                )
                os.remove(ogg_file_name)  # removing audio files for privacy reasons.
            elif response_msg.msg_info["msg_type"] == "options":
                keyboard = [
                    [
                        InlineKeyboardButton(
                            option_text[: self.MAX_OPTION_LEN],
                            callback_data=urllib.parse.unquote(option_data),
                        )
                    ]
                    for (
                        option_text,
                        option_data,
                        output_score,
                    ) in response_msg.msg_info["options"]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text(
                    response_msg.text[: self.MAX_MSG_LEN], reply_markup=reply_markup
                )
            elif response_msg.msg_info["msg_type"] == "error":
                error_msg = "ERROR: NO RESULT!"
                if update.message is not None:
                    update.message.reply_text(error_msg)
                elif update.callback_query.message is not None:
                    update.callback_query.message.reply_text(error_msg)
            else:
                raise Exception(
                    "The msg_type is not recognized:", response_msg.msg_info["msg_type"]
                )
        except Exception:
            traceback.print_exc()

    def error(self, update, context):
        """Log Errors caused by Updates."""
        self.logger.warning('Update "%s" caused error "%s"', update, context.error)

    def send_msg(self, chat_id, msg_text):
        """This method is used for sending a message to a user. It can be used for mixed-initiative interactions, as
        well as Wizard of Oz settings."""
        self.updater.bot.sendMessage(chat_id=chat_id, text=msg_text)

    def run(self):
        """Starting the bot!"""
        self.logger.info("Running the Telegram bot!")
        self.updater.start_polling()
        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        self.updater.idle()
