import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.ext import MessageHandler, filters
import asyncio
import data as data 
import re
import os
import parser as parser
from config import logger, TAG_DELIMITER

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "Welcome to Linkeeper! 📚✨\n\n"
        "I'm here to help you store and organize your bookmarks. "
        "Here are some basic instructions:\n\n"
        "• Use /add [URL] to save a new bookmark or just paste a link to add\n"
        "• Use /ls to see all your saved bookmarks\n"        
        "• Use /se [tag] [keyword] to search for bookmark\n\n"
        "• Use /rm [n]  to delete bookmark with id n \n\n"
        "• You can also reply to a message with /rm to delete the bookmark\n\n"
        "Happy bookmarking!"
    )
    await update.message.reply_text(welcome_message)


def extract_url_and_tags(input_string):
    # Pattern to match URLs with or without protocol
    url_pattern = r'(https?:\/\/)?([www\.]?[^\s]+\.[a-z]{2,})(\/[^\s#?]*)?(\?[^#\s]*)?(?=#|\s|$)'
    
    # Pattern to match hashtags
    tag_pattern = r'#(\w+)'
    
    # Extract URL
    url_match = re.search(url_pattern, input_string)
    url = url_match.group().rstrip('/') if url_match else None
    
    # Extract tags
    tags = re.findall(tag_pattern, input_string)
    
    return (url, tags)


def get_tags_for_save(tags_arr, delimiter=TAG_DELIMITER):
    return delimiter.join(tags_arr) if len(tags_arr)>0 else ''

async def add_bookmark(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    this function will handle the /add command to add a bookmark
    """
    args = context.args
    text = ' '.join(args)
    url, tags_arr = extract_url_and_tags(text)
    tags=get_tags_for_save(tags_arr)
    if url is None:
        await update.message.reply_text('No URL provided. e.g to add google.com, type /add google.com.')
    try:
        await process_bookmark(update, url, tags)
    except Exception as e:
        logger.error(f"Failed to add bookmark: {e}")
        await update.message.reply_text('Sorry, there was an error adding your bookmark.')


async def rm_bookmark(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    this function will handle the /rm command to remove a bookmark
    """
    # add code to add bookmark to database
    args = context.args
    if len(args) == 0:
        await update.message.reply_text('No ID provided. e.g use /ls to list bookmarks, take note of the ID, type /rm [ID] to remove.')
        return
        
    ids = args[0:]
    logger.info(f"Removing bookmark with id {ids}")
    try:
        data.delete_bookmark_by_id(ids=ids)
        await update.message.reply_text('Bookmark removed!')
    except Exception as e:
        logger.error(f"Failed to remove bookmark: {e}")
        await update.message.reply_text('Sorry, there was an error removing your bookmark.')


async def handle_reply_command(update: Update, context):
    """
    this function will handle the command when it is a reply to a message, e.g. when the user sends /rm in reply to a message
    """
    command = update.message.text  # This will be the command
    print(command)
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


#def get_url(text):
#    match = re.search(r'^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$', text) is not None
#    if match:
#        return match.group(0)  # Return the matched URL
#    else:
#        return None

def format_tags(tag_string, delimiter=TAG_DELIMITER):
    if tag_string is None:
        return ''
    tags_arr = tag_string.split(delimiter)
    return ' '.join([f'#{tag}' for tag in tags_arr])

async def search_bookmark(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) == 0:
        await update.message.reply_text('Please provide URL or tags to search.')
        return
    args_str=' '.join(args)
    url, tags_arr = extract_url_and_tags(args_str)
    
    bookmarks = data.search_by_url_pattern(url,tags_arr)
    if bookmarks:
        await update.message.reply_text('Here are the bookmarks matching your search.')
        i=0
        for bookmark in bookmarks:
            i+=1
            tags=''
            if bookmark[4] is not None:
                tags = format_tags(bookmark[4])
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
            if bookmark[4] is not None:
                tags = format_tags(bookmark[4])
                #tags_arr = bookmark[4].split('|')
                #tags = ' '.join([f'#{tag}' for tag in tags_arr])
            await update.message.reply_text(f'ID:{bookmark[0]}: {bookmark[1]} {bookmark[2]}  {tags}')
    else:
        await update.message.reply_text('You have no bookmarks saved.')


async def process_non_command_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
        this function will handle the text when it is not a command, e.g. when the user sends a URL
    """
    # You can access the text of the message with [`update.message.text`](command:_github.copilot.openSymbolFromReferences?%5B%7B%22%24mid%22%3A1%2C%22path%22%3A%22%2Fc%3A%2Fworking%2Flinkeeper%2Flinkeeper.py%22%2C%22scheme%22%3A%22file%22%7D%2C%7B%22line%22%3A30%2C%22character%22%3A23%7D%5D "../linkeeper/linkeeper.py")
    text = update.message.text
    url, tags_arr = extract_url_and_tags(text)
    logger.info(f"{url} {tags_arr}")

    tags=get_tags_for_save(tags_arr)
    if url is not None:
        await process_bookmark(update, url, tags)



async def process_bookmark(update, url, tags):
    title=parser.fetch_page_title(url)
    logger.info(f"URL detected: {url} {title}")
    existing_bookmark = data.search_by_exact_url(url)
    if len(existing_bookmark) > 0:
        bookmark_id, _, _, _, existing_tags = existing_bookmark[0]
        logger.info(f'Bookmark already exists. {bookmark_id} {url} {existing_tags}')
        # remove old bookmarks
        data.delete_bookmark_by_id([bookmark_id])
        message="Bookmark already exists and  updated."
    else:
        message="Bookmark added."
        logger.info(f"Adding bookmark with url {url} and tags {tags}")
        # Adjust the save_bookmark call according to how many tags you found
    if len(tags) == 0:
        data.save_bookmark(url=url,title=title,description=None,tags=None)
    else:
        data.save_bookmark(url=url, title=title, description=None, tags=tags)

    await update.message.reply_text(message)



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
    application.add_handler(CommandHandler("se", search_bookmark))
    # the following handles both /rm 1 2 3 4 and also reply and /rm case
    application.add_handler(CommandHandler("rm", handle_reply_command, filters=filters.ChatType.PRIVATE))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_non_command_text))
    application.add_error_handler(error)

    application.run_polling()


if __name__ == '__main__':
    main()