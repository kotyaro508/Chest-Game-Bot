import telebot


bot_link = '<BOT LINK>'

def bot_init(bot_link):
    global bot
    bot = telebot.TeleBot(bot_link)