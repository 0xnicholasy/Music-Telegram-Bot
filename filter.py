from telegram import Message
from telegram.ext import filters

class YoutubePlaylistFilter(filters.BaseFilter):
    def filter(self, message: Message) -> bool:
        # This method should return True if the message passes the filter and False otherwise
        return message.text.startswith('https://www.youtube.com/playlist?')

# You can then use this filter in a MessageHandler:

