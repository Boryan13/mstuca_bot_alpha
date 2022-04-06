import openpyxl, re, datetime, pytz, os
from replit import db

from telegram import Update, ReplyKeyboardMarkup #upm package(python-telegram-bot)
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext  #upm package(python-telegram-bot)

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
	return render_template("index.html")

day = {0: "Понедельник", 1: "Вторник", 2: "Среда", 3: "Четверг", 4: "Пятница", 5: "Суббота", 6: "Воскресенье"}

wb = openpyxl.load_workbook("Расписание.xlsx")

wb = wb.worksheets[1]

def check_merged(cell):
    cell = re.split(r'(\d+)', cell)[:-1]
    for i in db["lesson_merged"]:
        i = re.split(r'(\d+)', i)[:-1]
        if (ord(cell[0]) >= ord(i[0])) and (ord(cell[0]) <= ord(i[2][1:])) and (int(cell[1]) == int(i[1])):
            return db["lesson_merged"]["".join(i)]

    return wb["".join(cell)].value

def result(update):
    if datetime.datetime.now(pytz.timezone('Europe/Moscow')).weekday() == 6:
        db["now"] += 7
    
    for i in range(6):
        add = ""
        for j in range(68, 75):
            check = check_merged(chr(j) + str(db["now"] + i))
            if check != None:
                add += str(j - 67) + " Пара - " + " ".join(check.split()) + "\n"
            else:
                add += str(j - 67) + " Пара - " + "Нет занятий" + "\n"

        update.message.reply_text(day[i] + "\n" +  add)

def echo(update: Update, context: CallbackContext) -> None:
    custom_keyboard = [["Расписание на неделю"]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
    result(update)
    update.message.reply_text("Воскресенье - Отдых", reply_markup = reply_markup)

def command(update: Update, context: CallbackContext) -> None:
    custom_keyboard = [["Расписание на неделю"]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
    update.message.reply_text("Здравствуйте!", reply_markup = reply_markup)

def telegram_bot():
    updater = Updater(os.getenv("token"))
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    dispatcher.add_handler(CommandHandler("start", command))

    updater.start_polling()
	
def main():
    telegram_bot()
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
	main()