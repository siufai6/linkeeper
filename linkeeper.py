import sqlite3
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.ext import MessageHandler, filters
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
    try:
        bkm = data.search_by_exact_url(url)
        if len(bkm) > 0:
            logger.info(f'Bookmark already exists. {bkm[0][0]} {bkm[0][1]} {bkm[0][4]}')
            # remove old bookmarks
            data.delete_bookmark_by_id(bkm[0][0])
            await update.message.reply_text('The Bookmark already exists, it has been updated.')
        else:
            logger.info(f"Adding bookmark with url {url} and tags {tags}")
        # Adjust the save_bookmark call according to how many tags you found
        if len(tags) == 0:
            data.save_bookmark(url=url)
        else:
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

async def handle_reply_command(update: Update, context):
    command = update.message.text  # This will be the command
    original_message = update.message.reply_to_message
    logger.info(f"Received command: {command}")
    if original_message:
        original_text = original_message.text
        response = f"You used the command '{command}' in reply to '{original_text}'"
        await update.message.reply_text(response)
        match = re.search(r'ID:(\d+):', original_text)
        if match:
            logger.info(f"Matched ID: {match.group(1)}")
            id_2_remove = match.group(1)  # This will be '9' for "ID:9:bla bla.."
            if command.startswith('/rm'):
                logger.info(f"Removing bookmark with id {id_2_remove}")
                data.delete_bookmark_by_id(id=id_2_remove)
                await update.message.reply_text(f'Bookmark with ID {id_2_remove} removed.')
            else:
                logger.info(f"Message not recognized: {original_text}")
                await update.message.reply_text('Sorry I am not sure what I should do with this command.')
    else:
        await rm_bookmark(update, context)



async def search_bookmark(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) == 0:
        await update.message.reply_text('Please provide an URL to search.')
        return
        
    url_pattern = args[0]

    bookmarks = data.search_by_url_pattern(url_pattern)
    if bookmarks:
        await update.message.reply_text('Here are the bookmarks matching your search.')
        i=0
        for bookmark in bookmarks:
            i+=1
            tags=''
            print(bookmark)
            if bookmark[4] is not None:
                tags_arr = bookmark[4].split('|')
                tags = ' '.join([f'#{tag}' for tag in tags_arr])
            await update.message.reply_text(f'ID:{bookmark[0]}: {bookmark[1]} {tags}')
    else:
        await update.message.reply_text('No matching bookmarks.')


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
            await update.message.reply_text(f'ID:{bookmark[0]}: {bookmark[1]} {tags}')
    else:
        await update.message.reply_text('You have no bookmarks saved.')


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # You can access the text of the message with [`update.message.text`](command:_github.copilot.openSymbolFromReferences?%5B%7B%22%24mid%22%3A1%2C%22path%22%3A%22%2Fc%3A%2Fworking%2Flinkeeper%2Flinkeeper.py%22%2C%22scheme%22%3A%22file%22%7D%2C%7B%22line%22%3A30%2C%22character%22%3A23%7D%5D "../linkeeper/linkeeper.py")
    text = update.message.text
    if is_url(text):
        await update.message.reply_text(f"URL detected: {text}")
        add_bookmark(update, context)
    else:
        await update.message.reply_text(f"Not an URL. Nothing to do")




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
    #application.add_handler(CommandHandler("rm", rm_bookmark))
    application.add_handler(CommandHandler("rm", handle_reply_command, filters=filters.REPLY))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_error_handler(error)

    application.run_polling()


if __name__ == '__main__':
    main()