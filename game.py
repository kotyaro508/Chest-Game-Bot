from bot_init import bot_init, bot_link
from game_attributes import attributes_init

if __name__ == '__main__':
    bot_init(bot_link)
    attributes_init()

from bot_init import bot

from telebot import types

from game_attributes import user_dict, room_dict
from game_attributes import nominal_to_name, count_to_name, count_to_suits, suit_to_name, suit_to_endname
from game_attributes import bot_info_text, guest_text, owner_text

from classes import User, Room



# Start bot
@bot.message_handler(commands=['start'])
def send_welcome(message):

    if message.chat.id not in user_dict:                # initial bot launch
        user = User(message.from_user.username)
        user_dict[message.chat.id] = user
        
        text = "Привет!\nНапиши, пожалуйста, свою <b>фамилию</b>."

        msg = bot.send_message(message.chat.id, text, parse_mode='html', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, process_last_name_step)
    
    else:                                               # return to the bot
        user = user_dict[message.chat.id]
        if not user.current_room_id:
            text = f"С возвращением, {user.first_name}.\nХочешь сыграть с друзьями?"
            text += bot_info_text
            bot.send_message(message.chat.id, text, parse_mode='html')
        else:                                                   # command denied if user is in some room
            bot.delete_message(message.chat.id, message.message_id)


# Initial last name input
def process_last_name_step(message):
    user_dict[message.chat.id].setLastName(message.text)
    text = "Хорошо!\nТеперь напиши своё <b>имя</b>."
    msg = bot.send_message(message.chat.id, text, parse_mode='html')
    bot.register_next_step_handler(msg, process_first_name_step)


# Initial first name input and bot introduction
def process_first_name_step(message):
    user_dict[message.chat.id].setFirstName(message.text)
    room = Room(message.chat.id)
    room_dict[message.chat.id] = room

    text = "Отлично! Теперь расскажу о себе.\n"
    text += "Я &#8212; многопользовательский бот, созданный для карточной игры &#171;Сундучки&#187;. "
    text += "Если не знаешь, что это за игра, можешь ознакомиться с правилами. "
    text += "Если знаешь, то расскажу подробнее про свой формат.\n"
    text += "Игры происходят в так называемых <b>комнатах</b>. "
    text += "Комната создаётся для каждого пользователя сразу после регистрации. "
    text += "Для участия в игре пользователь может:\n"
    text += "\t1. Открыть свою комнату и поделиться её идентификатором с друзьями.\n"
    text += "\t2. Присоединиться в комнату другого пользователя по идентификатору.\n"
    text += "Для каждого пользователя я веду статистику за всё время взаимодействия, "
    text += "включающую количество игр, количество побед и общее число набранных сундучков.\n"
    text += bot_info_text

    bot.send_message(message.chat.id, text, parse_mode='html')


# Rules description
@bot.message_handler(commands=['rules'])
def getRules(message):
    user = user_dict[message.chat.id]

    if not user.current_room_id:
        text = "<u><b>Правила игры &#171;Сундучки&#187;</b></u>\n\n"
        text += "<b>Состав игры</b>.\nКолода из 52 карт.\n\n"
        text += "<b>Цель игры</b>.\nСобрать как можно больше <b>сундучков</b> &#8212; "
        text += "наборов из 4-х карт одного номинала (двойки, пятёрки, валеты, тузы, ...).\n\n"
        text += "<b>Начало игры</b>.\nКаждому игроку раздаются по 4 карты. "
        text += "Остаток колоды кладётся на центр стола. "
        text += "Игроки сами выбирают того, кто будет ходит первым.\n\n"
        text += "<b>Ход игры</b>.\nИгрок выбирает соперника, у которого хочет попробовать украсть карты. "
        text += "Чтобы это осуществить, игрок выбирает один из номиналов карт, которые есть у него на руке, "
        text += "и начинает последовательно задавать сопернику следующие вопросы:\n"
        text += "\t\t1. <b>Номинал</b>. Например, <i>Есть ли у тебя четвёрки?</i>.\n"
        text += "\t\t2. <b>Количество</b>. Например, <i>Их две?</i>.\n"
        text += "\t\t3. <b>Масти</b>. Например, <i>Это червовая и крестовая четвёрки?</i>.\n"
        text += "Если в процессе на любой из этих вопросов был получен ответ <i>Нет</i>, "
        text += "то игрок немедленно берёт одну карту из стопки в центре стола "
        text += "(если её ещё не разобрали) , и ход переходит к следующему по кругу игроку. "
        text += "Если же на все три вопроса был получен ответ <i>Да</i>, то игрок забирает "
        text += "карты спрашиваемого номинала у соперника, после чего продолжает свой ход, "
        text += "пробуя осуществить новую кражу.\n"
        text += "Когда на руке у любого игрока оказываются 4 карты, образующие сундучок, "
        text += "он выкладывает их перед собой лицевой стороной вверх "
        text += "(здесь вместо 4 карт на столе появится кружок с символом номинала). "
        text += "Теперь этот сундучок принадлежит данному игроку и проносит ему 1 балл.\n"
        text += "Когда игрок получает ход, но не имеет карт на руке, он должен взять карту из стопки. "
        text += "Если на данный момент в стопке уже нет карт, "
        text += "игрок больше не может продолжать игру."
        
        bot.send_message(message.chat.id, text, parse_mode='html')
    
    else:                                                       # command denied if user is in some room
        bot.delete_message(message.chat.id, message.message_id)


# Open user's personal room
@bot.message_handler(commands=['open'])
def chooseGame(message):
    user = user_dict[message.chat.id]

    if not user.current_room_id:
        room = room_dict[message.chat.id]
        room.openRoom()

        text = f"Комната успешно открыта!\nИдентификатор: `{message.chat.id}`.\n"
        text += "Подожди, когда войдут твои друзья, и начинай игру.\n\n"
        text += owner_text

        bot.send_message(message.chat.id, text, parse_mode='Markdown')
    
    else:                                                       # command denied if user is in some room
        bot.delete_message(message.chat.id, message.message_id)


# Join another user's room
@bot.message_handler(commands=['join'])
def joinRoom(message):
    user = user_dict[message.chat.id]

    if not user.current_room_id:
        text = "Введи идентификатор комнаты, к которой хочешь подключиться:"
        msg = bot.send_message(message.chat.id, text, parse_mode='html')
        bot.register_next_step_handler(msg, add_user_to_room)

    else:                                                       # command denied if user is in some room
        bot.delete_message(message.chat.id, message.message_id)


# Input another user's room link
def add_user_to_room(message):
    user = user_dict[message.chat.id]
    link = int(message.text)

    if link in room_dict:
        if room_dict[link].is_opened:                   # the room is open
            if room_dict[link].users_count < 6:                 # the maximum number of users in the room has not been exceeded
                room = room_dict[link]

                end = "а" if room.users_count < 4 else "ов"             # owner notification
                room_info = f"\n{room.users_count + 1} игрок" + end + " ждут начала."
                text = f"Успешное подключение  <code>{user.username}</code> к комнате." + room_info

                bot.send_message(link, text, parse_mode='html')
                
                for user_id in room.user_ids:                           # other users notifications
                    bot.send_message(user_id, text, parse_mode='html')
                
                room.addUser(message.chat.id)

                text = f"Успешное подключение!" + room_info + "\n\n"    # new user notification
                text += guest_text

            else:                                               # the maximum number of users in the room has been exceeded
                text = "В данной комнате уже находится 6 человек.\n"
                text += bot_info_text
            
        else:                                           # the room is closed
            text = "Эта комната в данный момент закрыта.\n"
            text += "Попробуй зайти позже или убедись, что вводишь нужный идентификатор.\n"
            text += bot_info_text
    
    else:                                       # invalid room link
        text = "Данной комнаты не существует.\nПроверь, что вводишь нужный идентификатор.\n"
        text += bot_info_text
    
    bot.send_message(message.chat.id, text, parse_mode='html')


# Show personal info
@bot.message_handler(commands=['personal'])
def personalInfo(message):
    user = user_dict[message.chat.id]

    if not user.current_room_id:
        text = "Имя: " + f"<b>{user.first_name}</b>\n"
        text += "Фамилия: " + f"<b>{user.last_name}</b>\n\n"
        text += "Количество игр: " + f"<b>{user.games}</b>\n"
        text += "Количество побед: " + f"<b>{user.victories}</b>\n"
        text += "Количество сундучков: " + f"<b>{user.chests}</b>\n"
        bot.send_message(message.chat.id, text, parse_mode='html')
    
    else:                                                       # command denied if user is in some room
        bot.delete_message(message.chat.id, message.message_id)


# Rename user
@bot.message_handler(commands=['rename'])
def changeName(message):
    user = user_dict[message.chat.id]

    if not user.current_room_id:
        text = "Введи новое <b>имя</b>:"
        msg = bot.send_message(message.chat.id, text, parse_mode='html')
        bot.register_next_step_handler(msg, set_first_name)
    
    else:                                                       # command denied if user is in some room
        bot.delete_message(message.chat.id, message.message_id)


# Secondary first name input
def set_first_name(message):
    user_dict[message.chat.id].setFirstName(message.text)
    text = "Введи новую <b>фамилию</b>:"
    msg = bot.send_message(message.chat.id, text, parse_mode='html')
    bot.register_next_step_handler(msg, set_last_name)


# Secondary last name input
def set_last_name(message):
    user_dict[message.chat.id].setLastName(message.text)
    text = "Данные успешно изменены.\n"
    bot.send_message(message.chat.id, text, parse_mode='html')


# Leave another user's room
@bot.message_handler(commands=['leave'])
def leaveRoom(message):
    user = user_dict[message.chat.id]
    room = room_dict[user.current_room_id]

    if user.current_room_id and user.current_room_id != message.chat.id:
        
        text = ""
        add_owner_text = ""
        add_guest_text = ""

        if room.players:                                        # a game is running in the room with the user
            for player_id, message_id in room.round_to_delete:          # delete the last round
                bot.delete_message(player_id, message_id)
            room.clearMessagesToDelete(is_round=True)

            for player_id, message_id in room.message_to_delete:        # delete the last message
                bot.delete_message(player_id, message_id)
            room.clearMessagesToDelete()

            room.finishGame()                                           # finish the game and delete the game data

            text = "Игра прервана.\n"
            add_owner_text = owner_text
            add_guest_text = guest_text

        room.removeUser(message.chat.id)

        text += f"<code>{user.username}</code> покидает комнату."       # text of notification
        end = ""
        if room.users_count > 4:
            end = "ов"
        elif room.users_count > 1:
            end = "а"
        text += f"\n{room.users_count} игрок" + end + " в комнате."
                                                                        # owner notification
        bot.send_message(room.owner_id, text + add_owner_text, parse_mode='html')

        for user_id in room.user_ids:                                   # other users notifications
            bot.send_message(user_id, text + add_guest_text, parse_mode='html')
        
        text = "Успешный выход из комнаты.\n"                           # leaving user notification
        text += "Возвращайся к игре в любой момент."
        bot.send_message(message.chat.id, text, parse_mode='html')

    else:                                                       # command denied if user is not in a room
        bot.delete_message(message.chat.id, message.message_id) # or the room is the user's personal room


# Close user's personal room
@bot.message_handler(commands=['close'])
def closeRoom(message):
    room = room_dict[message.chat.id]

    if user_dict[message.chat.id].current_room_id == message.chat.id:
        
        text = ""

        if room.players:                                        # a game is running in the user's room
            for player_id, message_id in room.round_to_delete:          # delete the last round
                bot.delete_message(player_id, message_id)
            room.clearMessagesToDelete(is_round=True)

            for player_id, message_id in room.message_to_delete:        # delete the last message
                bot.delete_message(player_id, message_id)
            room.clearMessagesToDelete()

            room.finishGame()                                           # finish the game and delete the game data

            text = "Игра прервана.\n"
        
        text += "Комната закрыта владельцем."                           # other users notifications
        for user_id in room.user_ids:
            bot.send_message(user_id, text, parse_mode='html')
        
        room.closeRoom()

        text = "Комната успешно закрыта."                              # owner notification
        bot.send_message(message.chat.id, text, parse_mode='html')
    
    else:                                                       # command denied if user is not in a room
        bot.delete_message(message.chat.id, message.message_id) # or the room is not the user's personal room


# Play the game in an open room with 2 to 6 players
@bot.message_handler(commands=['play'])
def playGame(message):
    room = room_dict[message.chat.id]

    if user_dict[message.chat.id].current_room_id == message.chat.id and not room.players:
        if room.users_count > 1:                        # number of users is valid
            room.startGame()
            players = room.players
            
            text = "Игра началась!"
            if len(players) > 2:                        # text of the game order if there are 3 or more users
                name_len = 0
                for player_id in players:
                    name_len = max(name_len, len(players[player_id].name))

                order = "```"
                for player_id in players:
                    name = players[player_id].name
                    delta_left = (name_len - len(name)) // 2
                    order += '\n-> ' + name.ljust(len(name) + delta_left).rjust(name_len) + ' ->'

                text += f"\n\nУстановлен порядок:{order}```\n\n"
            add_text = "Владелец комнаты должен выбрать первого игрока."

            message_to_delete = []                      # message links about choosing the first player
            message_id = message.message_id + 3
            markup = types.InlineKeyboardMarkup()

            for player_id in players:
                bot.send_message(player_id, text, parse_mode='Markdown')    # message with the game order

                name = players[player_id].name                              # message about choosing the first player (to other users)
                if player_id == message.chat.id:
                    name += " (Я)"
                else:
                    bot.send_message(player_id, add_text, parse_mode='html')
                    message_to_delete.append((player_id, message_id))
                    message_id += 2
                
                callback_data = "first" if len(players) > 2 else "player"
                callback_data += str(player_id)
                button = types.InlineKeyboardButton(text=name, callback_data=callback_data)
                markup.add(button)
            
            add_text = "Выбери игрока, который будет ходить первым."        # message about choosing the first player (to the owner)
            bot.send_message(message.chat.id, add_text, parse_mode='html', reply_markup=markup)
            message_to_delete.append((message.chat.id, message_id - 1))

            room.addMessagesToDelete(message_to_delete)             # save messages links to delete them later
        
        else:                                           # no one connected except the owner
            text = "В комнату пока никто не подключился, кроме тебя.\nПодожди друзей."
            bot.send_message(message.chat.id, text, parse_mode='html')
    
    else:                                                       # command denied if user is in another user's room
        bot.delete_message(message.chat.id, message.message_id) # or a game is running in the room with the user



# Game commands
@bot.callback_query_handler(func=lambda _: True)
def response(function_call):
    message = function_call.message

    if message:
        data = function_call.data           # basic objects
        room_id = user_dict[message.chat.id].current_room_id
        room = room_dict[room_id]
        players = room.players
        
        '''
            `ask_id` - player asking questions
            `answer_id` - player answering questions
        '''

        # set the first asking player and choose an answering player  (3 or more players)
        if data[:5] == 'first':

            ask_id = int(data[5:])

            room.setQueue(ask_id)

            for player_id, message_id in room.message_to_delete:    # delete previous message
                bot.delete_message(player_id, message_id)
            room.clearMessagesToDelete()

            message_to_delete = []                                  # start storing messages to delete them later
            round_to_delete = []
            message_id = message.message_id + 1

            markup = types.InlineKeyboardMarkup()
            text = f"<code>бот</code>\nХодит {players[ask_id].name}"

            for player_id in players:                               # send messages to non-asking players
                if player_id != ask_id:
                    image = room.drawPlayerRoom(player_id, face_id=ask_id)  # send initial room image
                    bot.send_photo(player_id, image)
                    round_to_delete.append((player_id, message_id))         # image will be deleted at the end of the round

                    bot.send_message(player_id, text, parse_mode='html')    # player notification
                    message_to_delete.append((player_id, message_id + 1))   # message will be deleted in the next step
                    message_id += 2

                    name = players[player_id].name                          # create name button for the asking player
                    callback_data = 'player' + str(player_id)
                    button = types.InlineKeyboardButton(text=name, callback_data=callback_data)
                    markup.add(button)
            
            image = room.drawPlayerRoom(ask_id)                     # send initial room image to the asking player
            bot.send_photo(ask_id, image)
            round_to_delete.append((ask_id, message_id))            # image will be deleted at the end of the round

            room.addMessagesToDelete(round_to_delete, is_round=True)    # save image links until the end of the round

            if players[ask_id].num_list:                            # choose an answering player
                text = "<code>бот</code>\nВыбери, у кого хочешь спросить карты"     # ask the asking player to choose an answering player
                bot.send_message(ask_id, text, parse_mode='html', reply_markup=markup)

                room.addMessagesToDelete(message_to_delete)                         # save message links to delete in the next step
            
            else:                                                   # take card from the stack if the initial cards formed a chest
                room.takeCards(ask_id, is_stack=True)

                markup = types.InlineKeyboardMarkup()                               # create button to pass the turn to the next player
                callback_data = "next" + str(room.updateQueue())                    # get the next player
                button = types.InlineKeyboardButton(text="Передать ход", callback_data=callback_data)
                markup.add(button)

                text = "<code>бот</code>\nУ тебя пустая рука.\nВозьми карту из колоды и передай ход."
                bot.send_message(ask_id, text, parse_mode='html', reply_markup=markup)

                message_to_delete.append((ask_id, message_id))                      # save message links to delete in the next step
                room.addMessagesToDelete(message_to_delete, is_round=True)          # the whole round will be deleted at once
        
        # choose asked nominal
        elif data[:6] == 'player':

            if len(players) > 2:                    # just ask the asking player to choose nominal  (3 or more players)
                answer_id_str = data[6:]

                text = "<code>бот</code>\nВыбери номинал"
                markup = types.InlineKeyboardMarkup()

                for nominal in players[message.chat.id].card_dict:          # create nominal buttons
                    if not players[message.chat.id].card_dict[nominal]:
                        continue

                    callback_data = 'nominal' + nominal + answer_id_str

                    if nominal == "1":                                              # add missing '0' for 10
                        nominal += "0"
                    
                    button = types.InlineKeyboardButton(text=nominal, callback_data=callback_data)
                    markup.add(button)
                
                bot.send_message(message.chat.id, text, parse_mode='html', reply_markup=markup)

                room.addMessagesToDelete([(message.chat.id, message.message_id + 1)])   # save link of the message with choosing nominal

                bot.delete_message(message.chat.id, message.message_id)     # delete the message with choosing an answering player

            else:                                   # additional information before choosing nominal  (2 players)
                ask_id = int(data[6:])

                if room.queue[0] == ask_id:                                 # set order
                    room.setQueue(ask_id)
                answer_id = room.queue[0]

                image = room.drawPlayerRoom(answer_id, face_id=ask_id)      # send photo to both players
                bot.send_photo(answer_id, image)
                image = room.drawPlayerRoom(ask_id)
                bot.send_photo(ask_id, image)

                text = f"<code>бот</code>\nХодит {players[ask_id].name}"    # answering player notification
                bot.send_message(answer_id, text, parse_mode='html')

                if players[ask_id].num_list:                                # ask the asking player to choose nominal if he has cards
                    text = "<code>бот</code>\nВыбери номинал"
                    markup = types.InlineKeyboardMarkup()

                    for nominal in players[ask_id].card_dict:                   # create nominal buttons
                        if not players[ask_id].card_dict[nominal]:
                            continue

                        callback_data = 'nominal' + nominal + str(answer_id)

                        if nominal == "1":                                          # add missing '0' for 10
                            nominal += "0"
                        
                        button = types.InlineKeyboardButton(text=nominal, callback_data=callback_data)
                        markup.add(button)
                    
                    bot.send_message(ask_id, text, parse_mode='html', reply_markup=markup)
                
                else:                                                       # take card from the stack if the asking player has no cards
                    room.takeCards(ask_id, is_stack=True)

                    markup = types.InlineKeyboardMarkup()                           # create button to pass the turn to the next player
                    callback_data = "player" + str(answer_id)
                    button = types.InlineKeyboardButton(text="Передать ход", callback_data=callback_data)
                    markup.add(button)

                    text = "<code>бот</code>\nУ тебя пустая рука.\nВозьми карту из колоды и передай ход."
                    bot.send_message(ask_id, text, parse_mode='html', reply_markup=markup)
                
                for player_id, message_id in room.round_to_delete:                  # delete the previous round
                    bot.delete_message(player_id, message_id)
                room.clearMessagesToDelete(is_round=True)

                for player_id, message_id in room.message_to_delete:                # delete the previous message
                    bot.delete_message(player_id, message_id)
                room.clearMessagesToDelete()

                room.addMessagesToDelete(
                    [
                        (answer_id, message.message_id + 1),                        # save image links until the end of the round
                        (ask_id, message.message_id + 2)
                    ],
                    is_round=True
                )
                room.addMessagesToDelete(
                    [
                        (answer_id, message.message_id + 3),                        # save message links to delete in the next step
                        (ask_id, message.message_id + 4)
                    ]
                )
        
        # ask about the chosen nominal
        elif data[:7] == 'nominal':
            
            ask_nominal = data[7]
            answer_id = int(data[8:])

            round_to_delete = []                                        # start storing messages to delete them later
            message_id = message.message_id + 1

            text = f"<code>{players[message.chat.id].name}</code>\n"    # text of the question about the chosen nominal
            text += f"<b>{players[answer_id].name}</b>, "
            text += f"есть ли у тебя <b><i>{nominal_to_name[ask_nominal]}</i></b>?"

            for player_id in players:                                   # send the question to non-answering players
                if player_id != answer_id:
                    bot.send_message(player_id, text, parse_mode='html')
                    round_to_delete.append((player_id, message_id))             # question will be deleted at the end of the round
                    message_id += 1
            
            markup = types.InlineKeyboardMarkup()

            if players[answer_id].card_dict[ask_nominal]:               # check if the answering player has the chosen nominal
                callback_data = "yesnominal" + ask_nominal + str(message.chat.id)       # create a positive response button
                button = types.InlineKeyboardButton(text="Да", callback_data=callback_data)
            
            else:
                callback_data = "fail1" + str(message.chat.id)                          # create a negative response button
                button = types.InlineKeyboardButton(text="Нет", callback_data=callback_data)
            
            markup.add(button)                                          # send the question with button to the answering player
            bot.send_message(answer_id, text, parse_mode='html', reply_markup=markup)
            
            room.addMessagesToDelete(round_to_delete, is_round=True)    # save question links until the end of the round

            for player_id, message_id in room.message_to_delete:        # delete the message with the round start
                bot.delete_message(player_id, message_id)
            room.clearMessagesToDelete()
        
        # answer positively about the chosen nominal and choose the count of the asked nominal
        elif data[:10] == 'yesnominal':

            ask_nominal = data[10]
            ask_id = int(data[11:])

            text = f"<code>{players[ask_id].name}</code>\n"             # send a copy of the previous message to the answering player
            text += f"<b>{players[message.chat.id].name}</b>, "
            text += f"есть ли у тебя <b><i>{nominal_to_name[ask_nominal]}</i></b>?"
            bot.send_message(message.chat.id, text, parse_mode='html')  # without button

            bot.delete_message(message.chat.id, message.message_id)     # delete the previous message from the answering player

            round_to_delete = [(message.chat.id, message.message_id + 1)]
            message_id = message.message_id + 2                         # start storing messages to delete them later

            text = f"<code>{players[message.chat.id].name}</code>\nДа"

            for player_id in players:                                   # send the answer to each player
                bot.send_message(player_id, text, parse_mode='html')
                round_to_delete.append((player_id, message_id))                 # answer will be deleted at the end of the round
                message_id += 1
            
            room.addMessagesToDelete(round_to_delete, is_round=True)    # save question links until the end of the round
            
            markup = types.InlineKeyboardMarkup()

            for count in range(1, 4):                                   # create count buttons
                callback_data = 'count' + ask_nominal + str(count) + str(message.chat.id)
                button = types.InlineKeyboardButton(text=str(count), callback_data=callback_data)
                markup.add(button)
            
            bot.send_message(ask_id, "Выбери количество", parse_mode='html', reply_markup=markup)
        
        # ask about the chosen count
        elif data[:5] == 'count':
            
            ask_nominal = data[5]
            ask_count = int(data[6])
            answer_id = int(data[7:])

            round_to_delete = []                                        # start storing messages to delete them later
            message_id = message.message_id + 1

            text = f"<code>{players[message.chat.id].name}</code>\n"    # text of the question about the chosen count 
            text += f"<b><i>{count_to_name[ask_nominal][ask_count - 1]}</i></b>?"
            
            for player_id in players:                                   # send the question to non-answering players
                if player_id != answer_id:
                    bot.send_message(player_id, text, parse_mode='html')
                    round_to_delete.append((player_id, message_id))             # question will be deleted at the end of the round
                    message_id += 1
            
            room.addMessagesToDelete(round_to_delete, is_round=True)    # save question links until the end of the round

            markup = types.InlineKeyboardMarkup()
                                                                        # check if the answering player has the right count of the asked nominal
            if len(players[answer_id].card_dict[ask_nominal]) == ask_count:
                callback_data = "yescount" + ask_nominal + str(message.chat.id)         # create a positive response button
                button = types.InlineKeyboardButton(text="Да", callback_data=callback_data)
            
            else:
                callback_data = "fail2" + str(message.chat.id)                          # create a negative response button
                button = types.InlineKeyboardButton(text="Нет", callback_data=callback_data)
            
            markup.add(button)                                          # send the question with button to the answering player
            bot.send_message(answer_id, text, parse_mode='html', reply_markup=markup)

            bot.delete_message(message.chat.id, message.message_id)     # delete the message with count choosing
        
        # answer positively about the chosen count and choose the suit of the asked nominal
        elif data[:8] == 'yescount':

            ask_nominal = data[8]
            ask_id = int(data[9:])
            ask_count = len(players[message.chat.id].card_dict[ask_nominal])

            text = f"<code>{players[ask_id].name}</code>\n"             # send a copy of the previous message to the answering player
            add_text = message.text.split('\n')[1][:-1]
            text += f"<b><i>{add_text}</i></b>?"
            bot.send_message(message.chat.id, text, parse_mode='html')  # without button

            bot.delete_message(message.chat.id, message.message_id)     # delete the previous message from the answering player

            round_to_delete = [(message.chat.id, message.message_id + 1)]
            message_id = message.message_id + 2                         # start storing messages to delete them later

            text = f"<code>{players[message.chat.id].name}</code>\nДа"

            for player_id in players:                                   # send the answer to each player
                bot.send_message(player_id, text, parse_mode='html')
                round_to_delete.append((player_id, message_id))                 # answer will be deleted at the end of the round
                message_id += 1
            
            room.addMessagesToDelete(round_to_delete, is_round=True)    # save question links until the end of the round

            markup = types.InlineKeyboardMarkup()

            for syms, suit in count_to_suits[ask_count - 1]:           # create suit buttons
                callback_data = 'suit' + ask_nominal + str(ask_count) + suit + str(message.chat.id)
                button = types.InlineKeyboardButton(text=syms, callback_data=callback_data)
                markup.add(button)
            
            end = 'ь' if ask_count == 1 else 'и'                        # end of the message depends on the count
            bot.send_message(ask_id, "Выбери маст" + end, parse_mode='html', reply_markup=markup)
        
        # ask about the chosen suits
        elif data[:4] == 'suit':

            ask_nominal = data[4]
            ask_count = int(data[5])
            ask_suits = data[6:6+ask_count]
            answer_id = int(data[6+ask_count:])

            round_to_delete = []                                        # start storing messages to delete them later
            message_id = message.message_id + 1
                                                                        # text of the question about the chosen suits 
            text_suits = ', '.join([suit_to_name[suit] + suit_to_endname[ask_nominal] for suit in ask_suits])
            text = f"<code>{players[message.chat.id].name}</code>\n<b><i>{text_suits}</i></b>?"

            for player_id in players:                                   # send the question to non-answering players
                if player_id != answer_id:
                    bot.send_message(player_id, text, parse_mode='html')
                    round_to_delete.append((player_id, message_id))             # question will be deleted at the end of the round
                    message_id += 1
            
            room.addMessagesToDelete(round_to_delete, is_round=True)    # save question links until the end of the round

            markup = types.InlineKeyboardMarkup()

            for suit in ask_suits:                                      # check if the answering player has the right suits of the asked nominal
                card = ask_nominal + suit
                if card not in players[answer_id].card_dict[ask_nominal]:       # create a negative response button
                    callback_data = "fail3" + str(message.chat.id)
                    button = types.InlineKeyboardButton(text="Нет", callback_data=callback_data)
                    break
            
            else:                                                               # create a positive response button
                callback_data = "yessuit" + ask_nominal + str(message.chat.id)
                button = types.InlineKeyboardButton(text="Да", callback_data=callback_data)
            
            markup.add(button)                                          # send the question with button to the answering player
            bot.send_message(answer_id, text, parse_mode='html', reply_markup=markup)

            bot.delete_message(message.chat.id, message.message_id)     # delete the message with suit choosing
        
        # send images of the tranferred cards in case of positive response
        elif data[:7] == 'yessuit':
            
            ask_nominal = data[7]
            ask_id = int(data[8:])
            
            text = f"<code>{players[ask_id].name}</code>\n"             # send a copy of the previous message to the answering player
            add_text = message.text.split('\n')[1][:-1]
            text += f"<b><i>{add_text}</i></b>?"
            bot.send_message(message.chat.id, text, parse_mode='html')  # without button

            bot.delete_message(message.chat.id, message.message_id)     # delete the previous message from the answering player

            round_to_delete = [(message.chat.id, message.message_id + 1)]
            message_id = message.message_id + 2                         # start storing messages to delete them later

            ask_nums = room.giveCards(ask_nominal, message.chat.id)     # take cards from the answering player

            for player_id in players:                                   # send final room image to non-asking players
                if player_id != ask_id:
                    image = room.drawPlayerRoom(player_id, smile_id=ask_id, rage_id=message.chat.id, ask_nums=ask_nums)
                    bot.send_photo(player_id, image)
                    round_to_delete.append((player_id, message_id))             # image will be deleted at the end of the round (the next step)
                    message_id += 1
            
            markup = types.InlineKeyboardMarkup()

            if len(players) > 2:
                if room.cards_count > 4:                                # too many cards not in chests to finish the game
                    button_text = "Принять"
                    callback_data = "continue"
                elif len(ask_nums) + len(players[ask_id].num_list) < 4: # the asking player doesn't get all the cards to form the last chest
                    button_text = "Принять"                                 # because there are other players with the asked nominal in hand
                    callback_data = "continue"
                else:                                                   # the asking player gets all the cards to form the last chest
                    button_text = "Завершить игру"                          # because only the answering player has not left the game yet
                    callback_data = "endgame"
            
            else:
                if room.cards_count > 4:                                # too many cards not in chests to finish the game
                    button_text = "Принять"
                    callback_data = "player" + str(ask_id)
                else:                                                   # the asking player gets all the cards to form the last chest
                    button_text = "Завершить игру"                           # because there is no other players except the answering player
                    callback_data = "endgame"

            button = types.InlineKeyboardButton(text=button_text, callback_data=callback_data)
            markup.add(button)
            image = room.drawPlayerRoom(ask_id, smile_id=ask_id, rage_id=message.chat.id, ask_nums=ask_nums)
            bot.send_photo(ask_id, image, reply_markup=markup)          # send final room image with button to the asking player
            round_to_delete.append((ask_id, message_id))

            room.addMessagesToDelete(round_to_delete, is_round=True)    # save image links until the end of the round (the next step)

            room.takeCards(ask_id, nums=ask_nums)                       # give cards to the asking player
        
        # answer negatively and ask the asking player to pass the turn to the next player
        elif data[:4] == 'fail':

            questions_count = int(data[4])
            ask_id = int(data[5:])

            if questions_count == 1:                                    # send a copy of the previous message to the answering player
                text = f"<code>{players[ask_id].name}</code>\n"                 # nominal has complex question structure
                text += f"<b>{players[message.chat.id].name}</b>, "
                text += f"есть ли у тебя "
                nominal_text = message.text.split("есть ли у тебя ")[1][:-1]
                text += f"<b><i>{nominal_text}</i></b>?"
            else:
                text = f"<code>{players[ask_id].name}</code>\n"                 # count and suits have simple question structure
                add_text = message.text.split('\n')[1][:-1]
                text += f"<b><i>{add_text}</i></b>?"
            bot.send_message(message.chat.id, text, parse_mode='html')

            bot.delete_message(message.chat.id, message.message_id)     # delete the previous message from the answering player

            round_to_delete = [(message.chat.id, message.message_id + 1)]
            message_id = message.message_id + 2                         # start storing messages to delete them later

            text = f"<code>{players[message.chat.id].name}</code>\nНет"

            for player_id in players:                                   # send the answer to non-ansking players
                if player_id != ask_id:
                    bot.send_message(player_id, text, parse_mode='html')
                    round_to_delete.append((player_id, message_id))             # answer will be deleted at the end of the round (the next step)
                    message_id += 1

            next_id = room.updateQueue()                                # update the game order and get the next asking player
            
            markup = types.InlineKeyboardMarkup()

            if room.stack:                                              # take a card from the stack if it is not empty
                room.takeCards(ask_id, is_stack=True)
                if room.cards_count > 0:                                        # pass the turn to the next player
                    button_text = "Взять карту и передать ход"                      # because there are cards not in chests
                    callback_data = "next" if len(players) > 2 else "player"
                    callback_data += str(next_id)
                else:                                                           # finish the game
                    button_text = "Завершить игру"
                    callback_data = "endgame"

            else:                                                       # pass the turn to the next player with cards in hand
                while not players[next_id].num_list:
                    next_id = room.updateQueue()                                # get the first next player with cards in hand
                button_text = "Передать ход"
                callback_data = "next" if len(players) > 2 else "player"        # to choose the answering player (3 or more players)
                callback_data += str(next_id)                                       # to choose nominal (2 players)

            button = types.InlineKeyboardButton(text=button_text, callback_data=callback_data)
            markup.add(button)                                          # send the answer with button to the asking player
            bot.send_message(ask_id, text, parse_mode='html', reply_markup=markup)
            round_to_delete.append((ask_id, message_id))

            room.addMessagesToDelete(round_to_delete, is_round=True)    # save answer links until the end of the round (the next step)
        
        # delete previous round and choose an answering player  (3 or more players)
        elif data == 'continue' or data[:4] == 'next':

            for player_id, message_id in room.round_to_delete:          # delete the previous round
                bot.delete_message(player_id, message_id)
            room.clearMessagesToDelete(is_round=True)

            message_to_delete = []                                      # start storing messages to delete them later
            round_to_delete = []
            message_id = message.message_id + 1

            if data == 'continue':                                              # asking player is the same
                ask_id = message.chat.id
                text = f"<code>бот</code>\nПродолжает ходить {players[ask_id].name}"
            else:                                                               # asking player is new
                ask_id = int(data[4:])
                text = f"<code>бот</code>\nХодит {players[ask_id].name}"
            
            markup = types.InlineKeyboardMarkup()

            for player_id in players:                                   # send messages to non-asking players
                if player_id != ask_id:
                    image = room.drawPlayerRoom(player_id, face_id=ask_id)      # send initial round image
                    bot.send_photo(player_id, image)
                    round_to_delete.append((player_id, message_id))             # image will be deleted at the end of the round

                    bot.send_message(player_id, text, parse_mode='html')        # player notification
                    message_to_delete.append((player_id, message_id + 1))       # message will be deleted in the next step
                    message_id += 2
                    
                    if players[player_id].num_list:                             # skip players with no cards in hand
                        name = players[player_id].name                                  # create name button for the asking player
                        callback_data = 'player' + str(player_id) 
                        button = types.InlineKeyboardButton(text=name, callback_data=callback_data)
                        markup.add(button)
            
            image = room.drawPlayerRoom(ask_id)                         # send initial round image to the asking player
            bot.send_photo(ask_id, image)
            round_to_delete.append((ask_id, message_id))                # image will be deleted at the end of the round

            room.addMessagesToDelete(round_to_delete, is_round=True)    # save image links until the end of the round

            if players[ask_id].num_list:                                # choose an answering player
                text = "<code>бот</code>\nВыбери, у кого хочешь спросить карты"     # ask the asking player to choose an answering player
                bot.send_message(ask_id, text, parse_mode='html', reply_markup=markup)

                room.addMessagesToDelete(message_to_delete)                         # save message links to delete in the next step
            
            else:                                                       # pass the turn if the asking player has no cards in hand
                next_id = room.updateQueue()                                        # get the next player

                if room.stack:                                                      # take card from the stack if it is not empty
                    room.takeCards(ask_id, is_stack=True)
                    button_text = "Взять карту и передать ход"
                    text = "<code>бот</code>\nУ тебя пустая рука.\nВозьми карту из колоды и передай ход."
                
                else:                                                               # the asking player cannot continue the game
                    while not players[next_id].num_list:                                    # get the first next player with cards in hand
                        next_id = room.updateQueue()
                    button_text = "Передать ход"
                    text = "<code>бот</code>\nТы больше не можешь собирать сундучки."
                
                callback_data = "next" + str(next_id)                               # ask the asking player to pass the turn
                markup = types.InlineKeyboardMarkup()
                button = types.InlineKeyboardButton(text=button_text, callback_data=callback_data)
                markup.add(button)
                bot.send_message(ask_id, text, parse_mode='html', reply_markup=markup)

                message_to_delete.append((ask_id, message_id + 1))                  # save message links to delete in the next step
                room.addMessagesToDelete(message_to_delete, is_round=True)          # the whole round will be deleted at once
        
        # write the game results and statistics ofthe users
        elif data == 'endgame':
            
            for player_id, message_id in room.round_to_delete:          # delete the last round
                bot.delete_message(player_id, message_id)
            room.clearMessagesToDelete(is_round=True)

            chests = {}                                                 # game info attributes
            win_count = 0
            winners = []
            name_len = 0

            for player_id in players:                                   # attributes caltulation
                cnt = players[player_id].chest_count
                name_len = max(name_len, len(players[player_id].name))
                chests[player_id] = cnt
                if cnt > win_count:
                    win_count = cnt
                    winners = [players[player_id].name]
                elif cnt == win_count:
                    winners.append(players[player_id].name)
                                                                        # text of the game results
            text = "*Игра окончена!*🎉🎉🎉\n\n*Победител"                       # headline text
            text += 'ь' if len(winners) == 1 else 'и'
            text += "*: " + ', '.join(winners) + ".\n\n```\n"

            line = '-' * (name_len + 35) + '\n'                                 # horizontal line of the result table

            text += line                                                        # names of the result table columns
            text += '|' + "Имя".ljust(name_len + 2) + '|' + "Игры".ljust(6) + '|' + "Победы".ljust(9) + '|' + "Сундучки".ljust(13) + '|\n'
            text += line

            for player_id, player in players.items():                           # lines with statistics of each player
                user = user_dict[player_id]
                victory = int(bool(player.name in winners))
                user.updateScore(victory, chests[player_id])                            # update user's score
                text += '|' + str(player.name).ljust(name_len + 2) + '|' + str(user.games).rjust(6) + '|'
                text += (str(user.victories) + " (+" + str(victory) + ')').rjust(9) + '|'
                text += (str(user.chests) + " (+" + str(chests[player_id]) + ')').rjust(13) + '|\n'
            
            text += line                                                        # result table end
            text += "```"
                                                                        # additional guest text
            add_text = "Можешь остаться в комнате, если хочешь сыграть ещё раз в той же компании.\n\n"
            add_text += guest_text

            for player_id in players:                                   # send final messages
                image = room.drawPlayerRoom(player_id)
                bot.send_photo(player_id, image)                                # final image
                bot.send_message(player_id, text, parse_mode='Markdown')        # game results

                if player_id != room.owner_id:                                  # remind the command to leave the room
                    bot.send_message(player_id, add_text, parse_mode='html')
                                                                        # additional owner text
            add_text = "Можешь остаться в своей комнате, если хочешь провести ещё одну игру в той же компании.\n\n"
            add_text += owner_text
                                                                        # remind commands for the owner
            bot.send_message(room.owner_id, add_text, parse_mode='html')

            room.finishGame()                                           # finish the game and delete the game data



if __name__ == '__main__':
    bot.infinity_polling()