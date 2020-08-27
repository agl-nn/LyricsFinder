import os
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters
from lyrics_finder import LyricsFinder

ARTIST, TRACK = range(2)


def start(update, context):
    user = update.message.from_user['first_name']
    update.message.reply_text(f"ok, {user}! \nlet's get it started! type artist name for search")
    return ARTIST


def get_artist(update, context):
    artist = update.message.text
    update.message.reply_text(f'the artist you looking for is {artist.title()}')
    update.message.reply_text('and now type track name for search')
    context.user_data.update({'artist': artist})
    return TRACK


def get_track(update, context):
    track = update.message.text
    context.user_data.update({'track': track})

    token = os.getenv('GENIUS_COM_API_KEY')
    finder = LyricsFinder(token)

    artist = context.user_data['artist']
    track = context.user_data['track']

    answer = finder.get_lyrics(artist, track)
    update.message.reply_text(answer)
    return ConversationHandler.END


def cancel(update, context):
    update.message.reply_text('canceled')
    return ConversationHandler.END


def main():
    updater = Updater(token=os.getenv('TELEGRAM_BOT_API_KEY'), use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={ARTIST: [MessageHandler(Filters.text & ~Filters.command, get_artist)],
                TRACK: [MessageHandler(Filters.text & ~Filters.command, get_track)],
                },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    return


if __name__ == '__main__':
    main()
