import logging
import gspread
import json
import os
from bot.bot import Bot
from bot.handler import MessageHandler, BotButtonCommandHandler, StartCommandHandler
from bot.filter import Filter
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y.%m.%d %I:%M:%S %p', level=logging.DEBUG)

# GSheets
gc = gspread.service_account(filename=os.getenv("GSHEETSAPI_FILENAME"))
WORKSHEET = gc.open("БД чат-бота").sheet1

# Data
BRANDS = []

# States
BRAND_WRT = False


def startup(bot, event):
    print("FCF")
    default_markup = [
        [
            {"text": "Кто ведет бренд?", "callbackData": "formanager"},
            {"text": "Пожаловаться❗", "callbackData": "claim"}
        ],
        [
            {"text": "Задать вопрос❓", "callbackData": "question"},
            {"text": "Похвалить закупщика❤", "callbackData": "commendation"}
        ],
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
    print("C")
    # bot.send_text(
    #     chat_id=event.from_chat,
    #     text=first_message_text,
    #     inline_keyboard_markup=json.dumps(default_markup)
    # )


def wrote_text(bot, event):
    global BRAND_WRT
    if BRAND_WRT:
        BRAND_WRT = False
        choose_brand(bot, event)
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
    print("CH")
    # bot.answer_callback_query(
    #     query_id=event.data['queryId'],
    #     text='Поставщики'
    # )
    br = event.data["text"]
    values_list = WORKSHEET.col_values(1)
    BRANDS = []
    for i, v in enumerate(values_list):
        if br.lower() in v.lower() or v.lower() in br.lower():
            print(i + 1, 1)
            print(WORKSHEET.cell(i + 1, 2).value)
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
    manager = WORKSHEET.cell(BRANDS[0][1], 2).value
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
    manager = WORKSHEET.cell(BRANDS[1][1], 2).value
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
    manager = WORKSHEET.cell(BRANDS[2][1], 2).value
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
    manager = WORKSHEET.cell(BRANDS[3][1], 2).value
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
    manager = WORKSHEET.cell(BRANDS[4][1], 2).value
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
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=feedback, filters=Filter.callback_data("feedback")))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=gotbrand1, filters=Filter.callback_data("gotbrand1")))  # got brands (max 5)
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=gotbrand2, filters=Filter.callback_data("gotbrand2")))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=gotbrand3, filters=Filter.callback_data("gotbrand3")))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=gotbrand4, filters=Filter.callback_data("gotbrand4")))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=gotbrand5, filters=Filter.callback_data("gotbrand5")))
    print("CCH")
    bot.start_polling()


if __name__ == '__main__':
    main()
