import logging
import gspread
import json
import os
import time
import datetime
from bot.bot import Bot
from bot.handler import MessageHandler, BotButtonCommandHandler, StartCommandHandler
from bot.filter import Filter
from dotenv import load_dotenv


# Универсален, отправляет и в TG, и в ICQ, просто добавить еще мессенджер
# Загрузка из Гугл Таблицы также в отдельном скрипте

load_dotenv()

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y.%m.%d %I:%M:%S %p', level=logging.DEBUG)

# GSheets
gc = gspread.service_account(filename=os.getenv("GSHEETSAPI_FILENAME"))
sh = gc.open("БД чат-бота")
WORKSHEET_FEEDBACKS = sh.get_worksheet(2)


def main():
    bot_token = os.getenv("BOT_TOKEN")
    bot = Bot(token=bot_token)
    checking_delay = int(os.getenv("CHECKING_DELAY"))
    while True:
        values_list = WORKSHEET_FEEDBACKS.col_values(11)
        for row, value in enumerate(values_list):
            if value == 'TRUE' and WORKSHEET_FEEDBACKS.cell(row+1, 12).value == 'FALSE':
                chat_id = WORKSHEET_FEEDBACKS.cell(row+1, 3).value
                msg_id = WORKSHEET_FEEDBACKS.cell(row+1, 6).value
                responsible = WORKSHEET_FEEDBACKS.cell(row+1, 9).value
                answer = WORKSHEET_FEEDBACKS.cell(row+1, 10).value
                if responsible and answer:
                    WORKSHEET_FEEDBACKS.update_cell(row + 1, 12, 'TRUE')
                    feedback_type = WORKSHEET_FEEDBACKS.cell(row+1, 7).value
                    if feedback_type == 'Вопрос по мин-макс' or feedback_type == 'Другой вопрос':
                        text = f'''На ваш вопрос ответил {responsible}:
{answer}'''
                    elif feedback_type == 'Жалоба':
                        text = f'''На вашу жалобу ответил {responsible}:
{answer}'''
                    else:
                        continue
                    bot.send_text(chat_id=chat_id, text=text, reply_msg_id=msg_id)
                    WORKSHEET_FEEDBACKS.update_cell(row+1, 13, str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
        time.sleep(checking_delay)


if __name__ == "__main__":
    main()
