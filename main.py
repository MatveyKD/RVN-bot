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
WORKSHEET_BUYERS = sh.get_worksheet(1)
WORKSHEET_FEEDBACKS = sh.get_worksheet(2)

# Data
BRANDS = []
BUYERS = []
CHOSEN_BUYER = ""

# States
DATA = {}


def startup(bot, event):
    global DATA
    DATA[event.from_chat] = {}
    DATA[event.from_chat]["BRAND_WRT"] = False

    print("FCF was COME")  # ------BOT-STARTED----------
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
    global DATA
    if not DATA.get(event.from_chat):
        startup(bot, event)
    elif DATA[event.from_chat].get("BRAND_WRT"):
        choose_brand(bot, event)
    elif DATA[event.from_chat].get("QUESTMINMAX_WRT"):
        DATA[event.from_chat]["QUESTMINMAX_WRT"] = False
        questionminmax_send(bot, event)
    elif DATA[event.from_chat].get("QUEST_WRT"):
        DATA[event.from_chat]["QUEST_WRT"] = False
        question_send(bot, event)
    elif DATA[event.from_chat].get("CLAIM_WRT"):
        DATA[event.from_chat]["CLAIM_WRT"] = False
        claim_send(bot, event)
    elif DATA[event.from_chat].get("COMMEND_WRT"):
        DATA[event.from_chat]["COMMEND_WRT"] = False
        commendation_send(bot, event)
    else:
        startup(bot, event)


def formanager(bot, event):
    global DATA
    default_markup = [
        [{"text": "Назад", "callbackData": "startup"}],
    ]
    bot.send_text(
        chat_id=event.from_chat,
        text="Введите название бренда и нажмите ввод⤵",
        inline_keyboard_markup=json.dumps(default_markup)
    )
    DATA[event.from_chat]["BRAND_WRT"] = True


def choose_brand(bot, event):
    global DATA
    DATA[event.from_chat]["BRAND_WRT"] = False
    print("PH was triggered...")
    # bot.answer_callback_query(
    #     query_id=event.data['queryId'],
    #     text='Поставщики'
    # )
    br = event.data["text"]
    values_list = WORKSHEET_MAIN.col_values(1)
    DATA[event.from_chat]["BRANDS"] = []
    for i, v in enumerate(values_list):
        if br.lower() in v.lower() or v.lower() in br.lower():
            print(i + 1, 1)
            print(WORKSHEET_MAIN.cell(i + 1, 2).value)
            DATA[event.from_chat]["BRANDS"].append((v, i+1))
            if len(DATA[event.from_chat]["BRANDS"]) >= 5:
                break
    default_markup = []
    if len(DATA[event.from_chat]["BRANDS"]) == 0:
        default_markup.append([{"text": "Уточнить бренд", "callbackData": f"formanager"}])
        bot.send_text(
            chat_id=event.from_chat,
            text="По данному запросу не найдено брендов. Уточните поиск.",
            inline_keyboard_markup=json.dumps(default_markup)
        )
        return  # leave func
    for i, brand in enumerate(DATA[event.from_chat]["BRANDS"][0:5]):
        default_markup.append([{"text": brand[0], "callbackData": f"gotbrand{i+1}"}],)
    default_markup.append([{"text": "Уточнить бренд", "callbackData": f"formanager"}], )

    if len(DATA[event.from_chat]['BRANDS'][0:5]) >= 5:  # окончание слова
        text = f"Найдено {len(DATA[event.from_chat]['BRANDS'][0:5])} брендов."
    elif len(DATA[event.from_chat]['BRANDS'][0:5]) > 1:  # окончание слова
        text = f"Найдено {len(DATA[event.from_chat]['BRANDS'][0:5])} бренда."
    else:
        text = f"Найден 1 бренд"
    bot.send_text(
        chat_id=event.from_chat,
        text=text,
        inline_keyboard_markup=json.dumps(default_markup)
    )


def gotbrand1(bot, event):
    manager = WORKSHEET_MAIN.cell(DATA[event.from_chat]['BRANDS'][0][1], 2).value
    default_markup = [
        [{"text": "Написать сообщение", "callbackData": "sendmsg"}],
        [{"text": "Проверить другой бренд", "callbackData": "formanager"}],
        [{"text": "В меню", "callbackData": "startup"}],
    ]
    bot.send_text(
        chat_id=event.from_chat,
        text=f"Ответственный за бренд {DATA[event.from_chat]['BRANDS'][0][0]}: {manager}",
        inline_keyboard_markup=json.dumps(default_markup)
    )


def gotbrand2(bot, event):
    manager = WORKSHEET_MAIN.cell(DATA[event.from_chat]['BRANDS'][1][1], 2).value
    default_markup = [
        [{"text": "Написать сообщение", "callbackData": "sendmsg"}],
        [{"text": "Проверить другой бренд", "callbackData": "formanager"}],
        [{"text": "В меню", "callbackData": "startup"}],
    ]
    bot.send_text(
        chat_id=event.from_chat,
        text=f"Ответственный за бренд {DATA[event.from_chat]['BRANDS'][1][0]}: {manager}",
        inline_keyboard_markup=json.dumps(default_markup)
    )


def gotbrand3(bot, event):
    manager = WORKSHEET_MAIN.cell(DATA[event.from_chat]['BRANDS'][2][1], 2).value
    default_markup = [
        [{"text": "Написать сообщение", "callbackData": "sendmsg"}],
        [{"text": "Проверить другой бренд", "callbackData": "formanager"}],
        [{"text": "В меню", "callbackData": "startup"}],
    ]
    bot.send_text(
        chat_id=event.from_chat,
        text=f"Ответственный за бренд {DATA[event.from_chat]['BRANDS'][2][0]}: {manager}",
        inline_keyboard_markup=json.dumps(default_markup)
    )


def gotbrand4(bot, event):
    manager = WORKSHEET_MAIN.cell(DATA[event.from_chat]['BRANDS'][3][1], 2).value
    default_markup = [
        [{"text": "Написать сообщение", "callbackData": "sendmsg"}],
        [{"text": "Проверить другой бренд", "callbackData": "formanager"}],
        [{"text": "В меню", "callbackData": "startup"}],
    ]
    bot.send_text(
        chat_id=event.from_chat,
        text=f"Ответственный за бренд {DATA[event.from_chat]['BRANDS'][3][0]}: {manager}",
        inline_keyboard_markup=json.dumps(default_markup)
    )


def gotbrand5(bot, event):
    manager = WORKSHEET_MAIN.cell(DATA[event.from_chat]['BRANDS'][4][1], 2).value
    default_markup = [
        [{"text": "Написать сообщение", "callbackData": "sendmsg"}],
        [{"text": "Проверить другой бренд", "callbackData": "formanager"}],
        [{"text": "В меню", "callbackData": "startup"}],
    ]
    bot.send_text(
        chat_id=event.from_chat,
        text=f"Ответственный за бренд {DATA[event.from_chat]['BRANDS'][4][0]}:\n{manager}",
        inline_keyboard_markup=json.dumps(default_markup)
    )


def questionminmax(bot, event):
    global DATA
    default_markup = [
        [{"text": "Назад", "callbackData": "startup"}],
    ]
    bot.send_text(
        chat_id=event.from_chat,
        text=f"Введите сообщение и нажмите отправить",
        inline_keyboard_markup=json.dumps(default_markup)
    )
    DATA[event.from_chat]["QUESTMINMAX_WRT"] = True


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
    global DATA
    default_markup = [
        [{"text": "Назад", "callbackData": "startup"}],
    ]
    bot.send_text(
        chat_id=event.from_chat,
        text=f"Введите сообщение и нажмите отправить",
        inline_keyboard_markup=json.dumps(default_markup)
    )
    DATA[event.from_chat]["QUEST_WRT"] = True


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
    global DATA
    default_markup = [
        [{"text": "Назад", "callbackData": "startup"}],
    ]
    bot.send_text(
        chat_id=event.from_chat,
        text=f"Введите сообщение и нажмите отправить",
        inline_keyboard_markup=json.dumps(default_markup)
    )
    DATA[event.from_chat]["CLAIM_WRT"] = True


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


def commendation(bot, event):
    global DATA
    default_markup = []

    DATA[event.from_chat]["BUYERS"] = WORKSHEET_BUYERS.col_values(1)[1:]  # without column name
    for i, buyer in enumerate(DATA[event.from_chat]["BUYERS"]):
        default_markup.append([{"text": buyer, "callbackData": f"buyer{i+1}"}])
    default_markup.append([{"text": "Назад", "callbackData": "startup"}])

    bot.send_text(
        chat_id=event.data['message']['chat']['chatId'],
        text="Выберите закупщика из списка",
        inline_keyboard_markup=json.dumps(default_markup)
    )


def ch_buyer1(bot, event):
    global DATA
    DATA[event.from_chat]["CHOSEN_BUYER"] = DATA[event.from_chat]["BUYERS"][0]
    buyer_chd(bot, event)


def ch_buyer2(bot, event):
    global DATA
    DATA[event.from_chat]["CHOSEN_BUYER"] = DATA[event.from_chat]["BUYERS"][1]
    buyer_chd(bot, event)


def ch_buyer3(bot, event):
    global DATA
    DATA[event.from_chat]["CHOSEN_BUYER"] = DATA[event.from_chat]["BUYERS"][2]
    buyer_chd(bot, event)


def ch_buyer4(bot, event):
    global DATA
    DATA[event.from_chat]["CHOSEN_BUYER"] = DATA[event.from_chat]["BUYERS"][3]
    buyer_chd(bot, event)


def ch_buyer5(bot, event):
    global DATA
    DATA[event.from_chat]["CHOSEN_BUYER"] = DATA[event.from_chat]["BUYERS"][4]
    buyer_chd(bot, event)


def ch_buyer6(bot, event):
    global DATA
    DATA[event.from_chat]["CHOSEN_BUYER"] = DATA[event.from_chat]["BUYERS"][5]
    buyer_chd(bot, event)


def ch_buyer7(bot, event):
    global DATA
    DATA[event.from_chat]["CHOSEN_BUYER"] = DATA[event.from_chat]["BUYERS"][6]
    buyer_chd(bot, event)


def ch_buyer8(bot, event):
    global DATA
    DATA[event.from_chat]["CHOSEN_BUYER"] = DATA[event.from_chat]["BUYERS"][7]
    buyer_chd(bot, event)


def ch_buyer9(bot, event):
    global DATA
    DATA[event.from_chat]["CHOSEN_BUYER"] = DATA[event.from_chat]["BUYERS"][8]
    buyer_chd(bot, event)


def ch_buyer10(bot, event):
    global DATA
    DATA[event.from_chat]["CHOSEN_BUYER"] = DATA[event.from_chat]["BUYERS"][9]
    buyer_chd(bot, event)


def buyer_chd(bot, event):
    global DATA
    default_markup = [
        [{"text": "Назад", "callbackData": "commendation"}],
    ]
    bot.send_text(
        chat_id=event.from_chat,
        text=f"Введите сообщение и нажмите отправить",
        inline_keyboard_markup=json.dumps(default_markup)
    )
    DATA[event.from_chat]["COMMEND_WRT"] = True


def commendation_send(bot, event):
    global DATA
    default_markup = [
        [{"text": "В меню", "callbackData": "startup"}],
    ]

    cur_row = len(WORKSHEET_FEEDBACKS.col_values(1)) + 1

    # Add row with question to Gsheet
    WORKSHEET_FEEDBACKS.update_cell(cur_row, 1, cur_row)
    WORKSHEET_FEEDBACKS.update_cell(cur_row, 2, str(datetime.datetime.now()))
    WORKSHEET_FEEDBACKS.update_cell(cur_row, 3, event.data['from']['userId'])
    WORKSHEET_FEEDBACKS.update_cell(cur_row, 4, f"{event.data['from']['firstName']} {event.data['from']['lastName']}")
    WORKSHEET_FEEDBACKS.update_cell(cur_row, 6, event.data['msgId'])
    WORKSHEET_FEEDBACKS.update_cell(cur_row, 7, 'Похвала')  # тип обращения
    WORKSHEET_FEEDBACKS.update_cell(cur_row, 8, event.data['text'])
    WORKSHEET_FEEDBACKS.update_cell(cur_row, 9, DATA[event.from_chat]["CHOSEN_BUYER"])

    bot.send_text(
        chat_id=event.from_chat,
        text=f"Ваша похвала была отправлена",
        inline_keyboard_markup=json.dumps(default_markup)
    )


def main():
    # TG bot
    bot_token = os.getenv("BOT_TOKEN")
    bot = Bot(token=bot_token)
    bot.dispatcher.add_handler(StartCommandHandler(callback=startup))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=startup, filters=Filter.callback_data("startup")))
    bot.dispatcher.add_handler(MessageHandler(filters=Filter.text, callback=wrote_text))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=questionminmax, filters=Filter.callback_data("questionminmax")))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=question, filters=Filter.callback_data("question")))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=claim, filters=Filter.callback_data("claim")))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=formanager, filters=Filter.callback_data("formanager")))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=gotbrand1, filters=Filter.callback_data("gotbrand1")))  # got brands (max 5)
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=gotbrand2, filters=Filter.callback_data("gotbrand2")))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=gotbrand3, filters=Filter.callback_data("gotbrand3")))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=gotbrand4, filters=Filter.callback_data("gotbrand4")))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=gotbrand5, filters=Filter.callback_data("gotbrand5")))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=commendation, filters=Filter.callback_data("commendation")))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=ch_buyer1, filters=Filter.callback_data("buyer1")))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=ch_buyer2, filters=Filter.callback_data("buyer2")))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=ch_buyer3, filters=Filter.callback_data("buyer3")))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=ch_buyer4, filters=Filter.callback_data("buyer4")))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=ch_buyer5, filters=Filter.callback_data("buyer5")))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=ch_buyer6, filters=Filter.callback_data("buyer6")))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=ch_buyer7, filters=Filter.callback_data("buyer7")))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=ch_buyer8, filters=Filter.callback_data("buyer8")))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=ch_buyer9, filters=Filter.callback_data("buyer9")))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=ch_buyer10, filters=Filter.callback_data("buyer10")))

    print("CCH started polling... Updating begin...")
    bot.start_polling()


if __name__ == '__main__':
    main()
