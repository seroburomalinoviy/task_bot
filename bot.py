import os
from dotenv import load_dotenv
import sqlite3
import logging

from telegram.ext import Application, ConversationHandler, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import Update, ReplyKeyboardMarkup
from telegram.constants import ParseMode

load_dotenv()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

TASK_NUM, TASK_NEXT = 0, 1


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введи номер задачи")
    return TASK_NUM


async def task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = int(update.message.text)
    context.user_data['number'] = number

    kb = [["Назад", "Следующая"]]
    connection = sqlite3.connect('tasks.db')
    cursor = connection.cursor()
    cursor.execute(
        """
            select task, answer from Tasks where number= ?
        """,
        (number,)
    )
    result = cursor.fetchall()

    # logging.info(result)

    task = result[0][0]
    answer = result[0][1]

    await update.message.reply_text(
        "Задача №{number}\n{task}\n||{answer}||".format(
            number=number,
            task=task.replace('.', '''\.'''),
            answer=answer.replace('.', '''\.''')
        ),
        reply_markup=ReplyKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN_V2
    )
    return TASK_NEXT


async def task_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [["Назад", "Следующая"]]
    number = context.user_data.get('number')
    if update.message.text == "Следующая":
        if number < 1002:
            number += 1
    else:
        if number > 1:
            number += -1

    context.user_data['number'] = number
    connection = sqlite3.connect('tasks.db')
    cursor = connection.cursor()
    cursor.execute(
        """
            select task, answer from Tasks where number= ?
        """,
        (number,)
    )
    result = cursor.fetchall()

    # logging.info(result)

    task = result[0][0]
    answer = result[0][1]

    await update.message.reply_text(
        "Задача №{number}\n{task}\n||{answer}||".format(
            number=number,
            task=task.replace('.', '''\.'''),
            answer=answer.replace('.', '''\.''')
        ),
        reply_markup=ReplyKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN_V2
    )
    return TASK_NEXT


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Пока"
    )
    return ConversationHandler.END


def main():
    application = Application.builder().token(os.environ.get("TOKEN")).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            TASK_NUM: [MessageHandler(filters.Regex("\d+"), task)],
            TASK_NEXT: [MessageHandler(filters.Regex("^(Назад|Следующая)$"), task_next)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    application.add_handler(conv_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()