import sqlite3
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

import asyncio
import data as data 
import re
import os

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "Welcome to Linkeeper! 📚✨\n\n"
        "I'm here to help you store and organize your bookmarks. "
        "Here are some basic instructions:\n\n"
        "• Use /add [URL] to save a new bookmark\n"
        "• Use /ls to see all your saved bookmarks\n"        
        "• Use /se [tag] [keyword] to search for bookmark\n\n"
        "• Use /rm [n]  to delete bookmark with id n \n\n"
        "Happy bookmarking!"
    )
    await update.message.reply_text(welcome_message)

async def add_bookmark(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # add code to add bookmark to database
    args = context.args
    if len(args) == 0:
        await update.message.reply_text('No URL provided. e.g to add google.com, type /add google.com.')
        return
        
    url = args[0]
    tags_arr = re.findall(r'#(\w+)', ' '.join(args[1:]))  # This regex finds all words preceded by a '#'
    tags = "|".join(tags_arr)  
    print(url,tags)
    try:
        # Adjust the save_bookmark call according to how many tags you found
        if len(tags) == 0:
            data.save_bookmark(url=url)
        else:
            print('here')
            data.save_bookmark(url=url, title=None, description=None, tags=tags)

        await update.message.reply_text('Bookmark added!')
    except Exception as e:
        logger.error(f"Failed to add bookmark: {e}")
        await update.message.reply_text('Sorry, there was an error adding your bookmark.')


async def rm_bookmark(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # add code to add bookmark to database
    args = context.args
    if len(args) == 0:
        await update.message.reply_text('No ID provided. e.g use /ls to list bookmarks, take note of the ID, type /rm [ID] to remove.')
        return
        
    id = args[0]
    logger.info(f"Removing bookmark with id {id}")
    try:
        data.delete_bookmark_by_id(id=id)

        await update.message.reply_text('Bookmark removed!')
    except Exception as e:
        logger.error(f"Failed to remove bookmark: {e}")
        await update.message.reply_text('Sorry, there was an error removing your bookmark.')


async def list_bookmarks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Placeholder for listing bookmarks from the database
    bookmarks = data.list_bookmarks()
    if bookmarks:
        await update.message.reply_text('Here are your bookmarks...')
        i=0
        for bookmark in bookmarks:
            i+=1
            tags=''
            print(bookmark)
            if bookmark[4] is not None:
                tags_arr = bookmark[4].split('|')
                tags = ' '.join([f'#{tag}' for tag in tags_arr])
            await update.message.reply_text(f'{i}: {bookmark[1]} {tags} id={bookmark[0]}')
    else:
        await update.message.reply_text('You have no bookmarks saved.')

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    data.init_db()
    # Replace 'YOUR_TOKEN' with your bot's token
    token = os.getenv('TG_TOKEN')  # Assuming the environment variable is named 'TELEGRAM_BOT_TOKEN'
    if not token:
        raise ValueError("No token provided. Please set the TG_TOKEN environment variable.")

    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_bookmark))
    application.add_handler(CommandHandler("ls", list_bookmarks))
    application.add_handler(CommandHandler("rm", rm_bookmark))

    application.add_error_handler(error)

    application.run_polling()


if __name__ == '__main__':
    main()