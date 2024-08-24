import requests
from datetime import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, JobQueue
import logging

# Replace 'YOUR_TOKEN' with your actual bot token
TOKEN = 'YOUR_TOKEN'

# Replace 'YOUR_MOVIE_API_KEY' with your actual API key for the movie database
MOVIE_API_KEY = 'YOUR_MOVIE_API_KEY' 
MOVIE_API_URL = f'https://api.themoviedb.org/3/movie/now_playing?api_key={MOVIE_API_KEY}'
MOVIE_POSTER_BASE_URL = 'https://image.tmdb.org/t/p/w500'

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hello! I am your movie bot. I will notify you about new movie releases.')

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Stopping the bot...')
    await context.application.stop()

def get_new_releases():
    response = requests.get(MOVIE_API_URL)
    if response.status_code == 200:
        movies = response.json().get('results', [])
        return movies
    return []

async def notify_new_releases(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    movies = get_new_releases()
    if movies:
        message = 'New Movie Releases:\n'
        for movie in movies:
            title = movie['title']
            release_date = movie['release_date']
            poster_path = movie['poster_path']
            poster_url = f"{MOVIE_POSTER_BASE_URL}{poster_path}"

            message += f"{title}\n (Release Date: {release_date})\n\n"

            await context.bot.send_photo(chat_id=chat_id, photo=poster_url, caption=message, parse_mode='Markdown')      
    else:
        await context.bot.send_message(chat_id=chat_id, text='No new releases found.')

async def set_notification(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    context.application.job_queue.run_daily(
        notify_new_releases, 
        time=time(9, 0), 
        data=chat_id   
    )
    await update.message.reply_text('Daily notifications set for new movie releases at 9 AM.')

def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("new", notify_new_releases))
    application.add_handler(CommandHandler("notify", set_notification))
    application.add_handler(CommandHandler("stop", stop))

    application.run_polling()

if __name__ == '__main__':
    main()
