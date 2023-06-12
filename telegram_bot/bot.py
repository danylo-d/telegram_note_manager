import os

from dotenv import load_dotenv
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware

load_dotenv(".env")
API_TOKEN = os.getenv("API_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    """
    Handler for the /start command.
    Sends a welcome message to the user.
    """
    await message.reply(
        "Hi, I'm a bot for note management."
        "For a list of available commands, type /help."
    )


@dp.message_handler(commands=["help"])
async def send_help(message: types.Message):
    """
    Handler for the /help command.
    Sends a help message with the list of available commands.
    """
    help_message = """
    List of available commands:
    /create <title> <content> - create a new note.
    /list - display a list of all notes.
    /view <note_id> - view a specific note by its identifier.
    /update <note_id> <new_content> - update the contents of the note.
    /delete <note_id> - delete the note.
    """
    await message.reply(help_message)


@dp.message_handler(commands=["create"])
async def create_handler(message: types.Message):
    """
    Handler for the /create command.
    Creates a new note with the provided title and content.
    """
    command_args = message.get_args()
    if not command_args:
        await message.reply(
            "Please provide title and content. Example: /create <title> <content>"
        )
        return

    args = command_args.split(maxsplit=1)
    if len(args) != 2:
        await message.reply("Invalid format. Example: /create <title> <content>")
        return

    title, content = args
    response = requests.post(API_BASE_URL, json={"title": title, "content": content})

    if response.status_code == 201:
        await message.reply("Note created successfully!")
    else:
        await message.reply("Failed to create note.")


@dp.message_handler(commands=["list"])
async def list_handler(message: types.Message):
    """
    Handler for the /list command.
    Retrieves and displays a list of all notes.
    """
    response = requests.get(API_BASE_URL)

    if response.status_code == 200:
        notes = response.json()
        if notes:
            notes_list = "\n".join(f"{note['id']}. {note['title']}" for note in notes)
            await message.reply(f"Notes:\n{notes_list}")
        else:
            await message.reply("No notes found.")
    else:
        await message.reply("Failed to retrieve notes.")


@dp.message_handler(commands=["view"])
async def view_handler(message: types.Message):
    """
    Handler for the /view command.
    Retrieves and displays the details of a specific note.
    """
    command_args = message.get_args()
    if not command_args:
        await message.reply("Please provide note ID. Example: /view <note_id>")
        return

    note_id = command_args.strip()
    response = requests.get(f"{API_BASE_URL}{note_id}/")

    if response.status_code == 200:
        note = response.json()
        await message.reply(
            f'Note ID: {note["id"]}\nTitle: {note["title"]}\nContent: {note["content"]}'
        )
    elif response.status_code == 404:
        await message.reply("Note not found.")
    else:
        await message.reply("Failed to retrieve note.")


@dp.message_handler(commands=["update"])
async def update_handler(message: types.Message):
    """
    Handler for the /update command.
    Updates the contents of a specific note.
    """
    command_args = message.get_args()
    if not command_args:
        await message.reply(
            "Please provide note ID and new content. Example: /update <note_id> <new_content>"
        )
        return

    args = command_args.split(maxsplit=1)
    if len(args) != 2:
        await message.reply("Invalid format. Example: /update <note_id> <new_content>")
        return

    note_id, new_content = args
    response = requests.patch(
        f"{API_BASE_URL}{note_id}/", json={"content": new_content}
    )

    if response.status_code == 200:
        await message.reply("Note updated successfully!")
    elif response.status_code == 404:
        await message.reply("Note not found.")
    else:
        await message.reply("Failed to update note.")


@dp.message_handler(commands=["delete"])
async def delete_handler(message: types.Message):
    """
    Handler for the /delete command.
    Deletes a specific note.
    """
    command_args = message.get_args()
    if not command_args:
        await message.reply("Please provide note ID. Example: /delete <note_id>")
        return

    note_id = command_args.strip()
    response = requests.delete(f"{API_BASE_URL}{note_id}/")

    if response.status_code == 204:
        await message.reply("Note deleted successfully!")
    elif response.status_code == 404:
        await message.reply("Note not found.")
    else:
        await message.reply("Failed to delete note.")


if __name__ == "__main__":
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)
