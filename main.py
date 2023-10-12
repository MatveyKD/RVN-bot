import logging
import gspread
import json
import os
import datetime
from bot.bot import Bot
from bot.handler import MessageHandler, BotButtonCommandHandler, StartCommandHandler
from bot.filter import Filter
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y.%m.%d %I:%M:%S %p', level=logging.DEBUG)

# GSheets
gc = gspread.service_account(filename=os.getenv("GSHEETSAPI_FILENAME"))
sh = gc.open("БД чат-бота")
WORKSHEET_MAIN = sh.get_worksheet(0)
WORKSHEET_FEEDBACKS = sh.get_worksheet(2)

# Data
BRANDS = []

# States
BRAND_WRT = False
QUESTMINMAX_WRT = False
QUEST_WRT = False
CLAIM_WRT = False


def startup(bot, event):
    print("FCF was COME")
    default_markup = [
        [{"text": "Кто ведет бренд?", "callbackData": "formanager"}],
        [{"text": "Вопрос по мин-макс❓", "callbackData": "questionminmax"}],
        [{"text": "Другой вопрос", "callbackData": "question"}],
        [{"text": "Пожаловаться", "callbackData": "claim"}],
        [{"text": "Похвалить закупщика❤", "callbackData": "commendation"}],
    ]
    first_message_text = "*HELP-DESK Отдела Закупок*"
    with open("Holodnyj-zvonok.jpg", 'rb') as file:
        bot.send_file(
            chat_id=event.from_chat,
            caption=first_message_text,
            file=file,
            inline_keyboard_markup=json.dumps(default_markup),
            parse_mode='MarkdownV2'
        )
    print("C STARTED BOT")


def wrote_text(bot, event):
    global BRAND_WRT, QUESTMINMAX_WRT, QUEST_WRT, CLAIM_WRT
    if BRAND_WRT:
        BRAND_WRT = False
        choose_brand(bot, event)
    elif QUESTMINMAX_WRT:
        QUESTMINMAX_WRT = False
        questionminmax_send(bot, event)
    elif QUEST_WRT:
        QUEST_WRT = False
        question_send(bot, event)
    elif CLAIM_WRT:
        CLAIM_WRT = False
        claim_send(bot, event)
    else:
        startup(bot, event)


def formanager(bot, event):
    global BRAND_WRT
    default_markup = [
        [{"text": "Назад", "callbackData": "startup"}],
    ]
    bot.send_text(
        chat_id=event.from_chat,
        text="Введите название бренда и нажмите ввод⤵",
        inline_keyboard_markup=json.dumps(default_markup)
    )
    BRAND_WRT = True


def choose_brand(bot, event):
    global BRANDS
    print("PH was triggered...")
    # bot.answer_callback_query(
    #     query_id=event.data['queryId'],
    #     text='Поставщики'
    # )
    br = event.data["text"]
    values_list = WORKSHEET_MAIN.col_values(1)
    BRANDS = []
    for i, v in enumerate(values_list):
        if br.lower() in v.lower() or v.lower() in br.lower():
            print(i + 1, 1)
            print(WORKSHEET_MAIN.cell(i + 1, 2).value)
            BRANDS.append((v, i+1))
    default_markup = []
    if len(BRANDS) == 0:
        default_markup.append([{"text": "Уточнить бренд", "callbackData": f"formanager"}])
        bot.send_text(
            chat_id=event.from_chat,
            text="По данному запросу не найдено брендов. Уточните поиск.",
            inline_keyboard_markup=json.dumps(default_markup)
        )
        return  # leave func
    for i, brand in enumerate(BRANDS[0:5]):
        default_markup.append([{"text": brand[0], "callbackData": f"gotbrand{i+1}"}],)
    default_markup.append([{"text": "Уточнить бренд", "callbackData": f"formanager"}], )

    if len(BRANDS[0:5]) >= 5:  # окончание
        text = f"Найдено {len(BRANDS[0:5])} брендов."
    elif len(BRANDS[0:5]) > 1:  # окончание
        text = f"Найдено {len(BRANDS[0:5])} бренда."
    else:
        text = f"Найден 1 бренд"
    bot.send_text(
        chat_id=event.from_chat,
        text=text,
        inline_keyboard_markup=json.dumps(default_markup)
    )


def gotbrand1(bot, event):
    manager = WORKSHEET_MAIN.cell(BRANDS[0][1], 2).value
    default_markup = [
        [{"text": "Написать сообщение", "callbackData": "sendmsg"}],
        [{"text": "Проверить другой бренд", "callbackData": "formanager"}],
        [{"text": "В меню", "callbackData": "startup"}],
    ]
    bot.send_text(
        chat_id=event.from_chat,
        text=f"Ответсвенный за бренд {BRANDS[0][0]}: {manager}",
        inline_keyboard_markup=json.dumps(default_markup)
    )


def gotbrand2(bot, event):
    manager = WORKSHEET_MAIN.cell(BRANDS[1][1], 2).value
    default_markup = [
        [{"text": "Написать сообщение", "callbackData": "sendmsg"}],
        [{"text": "Проверить другой бренд", "callbackData": "formanager"}],
        [{"text": "В меню", "callbackData": "startup"}],
    ]
    bot.send_text(
        chat_id=event.from_chat,
        text=f"Ответсвенный за бренд {BRANDS[1][0]}: {manager}",
        inline_keyboard_markup=json.dumps(default_markup)
    )


def gotbrand3(bot, event):
    manager = WORKSHEET_MAIN.cell(BRANDS[2][1], 2).value
    default_markup = [
        [{"text": "Написать сообщение", "callbackData": "sendmsg"}],
        [{"text": "Проверить другой бренд", "callbackData": "formanager"}],
        [{"text": "В меню", "callbackData": "startup"}],
    ]
    bot.send_text(
        chat_id=event.from_chat,
        text=f"Ответсвенный за бренд {BRANDS[2][0]}: {manager}",
        inline_keyboard_markup=json.dumps(default_markup)
    )


def gotbrand4(bot, event):
    manager = WORKSHEET_MAIN.cell(BRANDS[3][1], 2).value
    default_markup = [
        [{"text": "Написать сообщение", "callbackData": "sendmsg"}],
        [{"text": "Проверить другой бренд", "callbackData": "formanager"}],
        [{"text": "В меню", "callbackData": "startup"}],
    ]
    bot.send_text(
        chat_id=event.from_chat,
        text=f"Ответсвенный за бренд {BRANDS[3][0]}: {manager}",
        inline_keyboard_markup=json.dumps(default_markup)
    )


def gotbrand5(bot, event):
    manager = WORKSHEET_MAIN.cell(BRANDS[4][1], 2).value
    default_markup = [
        [{"text": "Написать сообщение", "callbackData": "sendmsg"}],
        [{"text": "Проверить другой бренд", "callbackData": "formanager"}],
        [{"text": "В меню", "callbackData": "startup"}],
    ]
    bot.send_text(
        chat_id=event.from_chat,
        text=f"Ответсвенный за бренд {BRANDS[4][0]}:\n{manager}",
        inline_keyboard_markup=json.dumps(default_markup)
    )


def questionminmax(bot, event):
    global QUESTMINMAX_WRT
    default_markup = [
        [{"text": "Назад", "callbackData": "startup"}],
    ]
    bot.send_text(
        chat_id=event.from_chat,
        text=f"Введите сообщение и нажмите отправить",
        inline_keyboard_markup=json.dumps(default_markup)
    )
    QUESTMINMAX_WRT = True


def questionminmax_send(bot, event):
    default_markup = [
        [{"text": "В меню", "callbackData": "startup"}],
    ]

    cur_row = len(WORKSHEET_FEEDBACKS.col_values(1))+1

    # Add row with question to Gsheet
    WORKSHEET_FEEDBACKS.update_cell(cur_row, 1, cur_row)
    WORKSHEET_FEEDBACKS.update_cell(cur_row, 2, str(datetime.datetime.now()))
    WORKSHEET_FEEDBACKS.update_cell(cur_row, 3, event.data['from']['userId'])
    WORKSHEET_FEEDBACKS.update_cell(cur_row, 4, f"{event.data['from']['firstName']} {event.data['from']['lastName']}")
    WORKSHEET_FEEDBACKS.update_cell(cur_row, 6, event.data['msgId'])
    WORKSHEET_FEEDBACKS.update_cell(cur_row, 7, 'Вопрос по мин-макс')  # тип обращения
    WORKSHEET_FEEDBACKS.update_cell(cur_row, 8, event.data['text'])

    bot.send_text(
        chat_id=event.from_chat,
        text=f"Ваш вопрос был отправлен",
        inline_keyboard_markup=json.dumps(default_markup)
    )


def question(bot, event):
    global QUEST_WRT
    default_markup = [
        [{"text": "Назад", "callbackData": "startup"}],
    ]
    bot.send_text(
        chat_id=event.from_chat,
        text=f"Введите сообщение и нажмите отправить",
        inline_keyboard_markup=json.dumps(default_markup)
    )
    QUEST_WRT = True


def question_send(bot, event):
    default_markup = [
        [{"text": "В меню", "callbackData": "startup"}],
    ]

    cur_row = len(WORKSHEET_FEEDBACKS.col_values(1))+1

    # Add row with question to Gsheet
    WORKSHEET_FEEDBACKS.update_cell(cur_row, 1, cur_row)
    WORKSHEET_FEEDBACKS.update_cell(cur_row, 2, str(datetime.datetime.now()))
    WORKSHEET_FEEDBACKS.update_cell(cur_row, 3, event.data['from']['userId'])
    WORKSHEET_FEEDBACKS.update_cell(cur_row, 4, f"{event.data['from']['firstName']} {event.data['from']['lastName']}")
    WORKSHEET_FEEDBACKS.update_cell(cur_row, 6, event.data['msgId'])
    WORKSHEET_FEEDBACKS.update_cell(cur_row, 7, 'Другой вопрос')  # тип обращения
    WORKSHEET_FEEDBACKS.update_cell(cur_row, 8, event.data['text'])

    bot.send_text(
        chat_id=event.from_chat,
        text=f"Ваш вопрос был отправлен",
        inline_keyboard_markup=json.dumps(default_markup)
    )


def claim(bot, event):
    global CLAIM_WRT
    default_markup = [
        [{"text": "Назад", "callbackData": "startup"}],
    ]
    bot.send_text(
        chat_id=event.from_chat,
        text=f"Введите сообщение и нажмите отправить",
        inline_keyboard_markup=json.dumps(default_markup)
    )
    CLAIM_WRT = True


def claim_send(bot, event):
    default_markup = [
        [{"text": "В меню", "callbackData": "startup"}],
    ]

    cur_row = len(WORKSHEET_FEEDBACKS.col_values(1))+1

    # Add row with question to Gsheet
    WORKSHEET_FEEDBACKS.update_cell(cur_row, 1, cur_row)
    WORKSHEET_FEEDBACKS.update_cell(cur_row, 2, str(datetime.datetime.now()))
    WORKSHEET_FEEDBACKS.update_cell(cur_row, 3, event.data['from']['userId'])
    WORKSHEET_FEEDBACKS.update_cell(cur_row, 4, f"{event.data['from']['firstName']} {event.data['from']['lastName']}")
    WORKSHEET_FEEDBACKS.update_cell(cur_row, 6, event.data['msgId'])
    WORKSHEET_FEEDBACKS.update_cell(cur_row, 7, 'Жалоба')  # тип обращения
    WORKSHEET_FEEDBACKS.update_cell(cur_row, 8, event.data['text'])

    bot.send_text(
        chat_id=event.from_chat,
        text=f"Ваша жалоба была отправлена",
        inline_keyboard_markup=json.dumps(default_markup)
    )


def feedback(bot, event):
    bot.answer_callback_query(
        query_id=event.data['queryId'],
        text='Отзывы'
    )

    bot.send_text(
        chat_id=event.data['message']['chat']['chatId'],
        text="Менеджерам платят много...",
        # inline_keyboard_markup=json.dumps(buttons)
    )


def main():
    # TG bot
    bot_token = os.getenv("BOT_TOKEN")
    bot = Bot(token=bot_token)
    bot.dispatcher.add_handler(StartCommandHandler(callback=startup))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=startup, filters=Filter.callback_data("startup")))
    bot.dispatcher.add_handler(MessageHandler(filters=Filter.text, callback=wrote_text))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=formanager, filters=Filter.callback_data("formanager")))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=questionminmax, filters=Filter.callback_data("questionminmax")))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=question, filters=Filter.callback_data("question")))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=claim, filters=Filter.callback_data("claim")))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=gotbrand1, filters=Filter.callback_data("gotbrand1")))  # got brands (max 5)
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=gotbrand2, filters=Filter.callback_data("gotbrand2")))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=gotbrand3, filters=Filter.callback_data("gotbrand3")))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=gotbrand4, filters=Filter.callback_data("gotbrand4")))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=gotbrand5, filters=Filter.callback_data("gotbrand5")))
    print("CCH started polling... Updating begin...")
    bot.start_polling()


if __name__ == '__main__':
    main()
