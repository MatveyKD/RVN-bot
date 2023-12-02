import logging
import gspread
import json
import os
import datetime
from bot.bot import Bot
from bot.handler import MessageHandler, BotButtonCommandHandler, StartCommandHandler
from bot.filter import Filter
from dotenv import load_dotenv

from gsheets_tools import get_brands, get_manager_info, send_feedback, get_all_buyers

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

    # ------BOT-STARTED----------
    default_markup = [
        [{"text": "Кто ведет бренд?ℹ", "callbackData": "formanager"}],
        [{"text": "Вопрос по мин-макс📦", "callbackData": "questionminmax"}],
        [{"text": "Другой вопрос🤔", "callbackData": "question"}],
        [{"text": "Пожаловаться🤬", "callbackData": "claim"}],
        [{"text": "Похвалить закупщика♥", "callbackData": "commendation"}],
    ]
    first_message_text = "*HELP-DESK Отдела Закупок RVN-Group*"
    with open("Holodnyj-zvonok.jpg", 'rb') as file:
        bot.send_file(
            chat_id=event.from_chat,
            caption=first_message_text,
            file=file,
            inline_keyboard_markup=json.dumps(default_markup),
            parse_mode='MarkdownV2'
        )


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

    DATA[event.from_chat]["BRANDS"] = get_brands(event.data["text"], WORKSHEET_MAIN)

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

    text = f"Результаты поиска: {len(DATA[event.from_chat]['BRANDS'])}."
    if len(DATA[event.from_chat]['BRANDS']) > 5:
        text += "\nВывожу первые 5"

    bot.send_text(
        chat_id=event.from_chat,
        text=text,
        inline_keyboard_markup=json.dumps(default_markup)
    )


def gotbrand1(bot, event): brand_got(bot, event, 0)
def gotbrand2(bot, event): brand_got(bot, event, 1)
def gotbrand3(bot, event): brand_got(bot, event, 2)
def gotbrand4(bot, event): brand_got(bot, event, 3)
def gotbrand5(bot, event): brand_got(bot, event, 4)


def brand_got(bot, event, manager_ind):
    manager, nickname, phonenumber = get_manager_info(DATA[event.from_chat]['BRANDS'][manager_ind][1], WORKSHEET_MAIN, WORKSHEET_BUYERS)
    default_markup = [
        [{"text": "Проверить другой бренд", "callbackData": "formanager"}],
        [{"text": "В меню", "callbackData": "startup"}],
    ]
    text = f"Ответственный за бренд {DATA[event.from_chat]['BRANDS'][manager_ind][0]}: {manager}"
    if nickname or phonenumber: text += "\n"
    if nickname:
        text += f"@{nickname}"
        if phonenumber: text += ", "
    if phonenumber: text += phonenumber
    bot.send_text(
        chat_id=event.from_chat,
        text=text,
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

    send_feedback(WORKSHEET_BUYERS, WORKSHEET_FEEDBACKS, event.data["from"], event.data["msgId"], event.data["text"], "Вопрос по мин-макс")

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

    send_feedback(WORKSHEET_BUYERS, WORKSHEET_FEEDBACKS, event.data["from"], event.data["msgId"], event.data["text"], "Другой вопрос")

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

    send_feedback(WORKSHEET_BUYERS, WORKSHEET_FEEDBACKS, event.data["from"], event.data["msgId"], event.data["text"], "Жалоба")

    bot.send_text(
        chat_id=event.from_chat,
        text=f"Ваша жалоба была отправлена",
        inline_keyboard_markup=json.dumps(default_markup)
    )


def commendation(bot, event):
    global DATA
    default_markup = []

    DATA[event.from_chat]["BUYERS"] = get_all_buyers(WORKSHEET_BUYERS)
    for i, buyer in enumerate(DATA[event.from_chat]["BUYERS"]):
        default_markup.append([{"text": buyer, "callbackData": f"buyer{i + 1}"}])
    default_markup.append([{"text": "Назад", "callbackData": "startup"}])

    bot.send_text(
        chat_id=event.data['message']['chat']['chatId'],
        text="Выберите закупщика из списка",
        inline_keyboard_markup=json.dumps(default_markup)
    )


def ch_buyer1(bot, event): buyer_chd(bot, event, 0)
def ch_buyer2(bot, event): buyer_chd(bot, event, 1)
def ch_buyer3(bot, event): buyer_chd(bot, event, 2)
def ch_buyer4(bot, event): buyer_chd(bot, event, 3)
def ch_buyer5(bot, event): buyer_chd(bot, event, 4)
def ch_buyer6(bot, event): buyer_chd(bot, event, 5)
def ch_buyer7(bot, event): buyer_chd(bot, event, 6)
def ch_buyer8(bot, event): buyer_chd(bot, event, 7)
def ch_buyer9(bot, event): buyer_chd(bot, event, 8)
def ch_buyer10(bot, event): buyer_chd(bot, event, 9)


def buyer_chd(bot, event, buyer_ind):
    global DATA
    DATA[event.from_chat]["CHOSEN_BUYER"] = DATA[event.from_chat]["BUYERS"][buyer_ind]
    default_markup = [
        [{"text": "Назад", "callbackData": "commendation"}],
    ]
    bot.send_text(
        chat_id=event.from_chat,
        text=f"Введите сообщение и нажмите отправить",
        inline_keyboard_markup=json.dumps(default_markup)
    )
    DATA[event.from_chat]["COMMEND_WRT"] = True
    DATA[event.from_chat]["CHOSEN_BUYER"] = DATA[event.from_chat]["BUYERS"][buyer_ind]


def commendation_send(bot, event):
    global DATA
    default_markup = [
        [{"text": "В меню", "callbackData": "startup"}],
    ]

    send_feedback(
        WORKSHEET_BUYERS, WORKSHEET_FEEDBACKS, event.data["from"], event.data["msgId"],
        event.data["text"], "Похвала", DATA[event.from_chat]["CHOSEN_BUYER"]
    )

    bot.send_text(
        chat_id=event.from_chat,
        text=f"Ваша похвала была отправлена",
        inline_keyboard_markup=json.dumps(default_markup)
    )


def main():
    # ICQ bot
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

    bot.start_polling()


if __name__ == '__main__':
    main()
