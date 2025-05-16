def attributes_init():
    # Game attributes (nominals, suits, counts) for cards, messages and buttons
    global nominals, nominal_to_name

    nominals = ["2", "3", "4", "5", "6", "7", "8", "9", "1", "J", "Q", "K", "A"]
    nominal_to_name = {                                 # "1" is for 10s, 0 is added to create button later
        "2": "Двойки",
        "3": "Тройки",
        "4": "Четвёрки",
        "5": "Пятёрки",
        "6": "Шестёрки",
        "7": "Семёрки",
        "8": "Восьмёрки",
        "9": "Девятки",
        "1": "Десятки",
        "J": "Валеты",
        "Q": "Дамы",
        "K": "Короли",
        "A": "Тузы"
    }


    global suits, suit_to_name

    suits = ["S", "H", "C", "D"]
    suit_to_name = {                                    # suit names (without endnames that are depended on nominal)
        "S": "Пиков",
        "H": "Червов",
        "C": "Крестов",
        "D": "Бубнов"
    }


    global card_to_num, num_to_card

    card_to_num = {}
    num_to_card = ["" for _ in range(52)]

    for i, nominal in enumerate(nominals):
        for j, suit in enumerate(suits):
            card = nominal + suit
            num = 4 * i + j
            card_to_num[card] = num
            num_to_card[num] = card


    global count_to_name, count_to_suits

    count_to_name = {}

    for nominal in nominals:
        if nominal in ("J", "K", "A"):
            count_to_name[nominal] = ['Один', 'Два', 'Три']
        else:
            count_to_name[nominal] = ['Одна', 'Две', 'Три']


    count_to_suits = [
        (
            ('♠️', 'S'),
            ('♥️', 'H'),
            ('♣️', 'C'),
            ('♦️', 'D')
        ),
        (
            ('♠️♥️', 'SH'),
            ('♠️♣️', 'SC'),
            ('♠️♦️', 'SD'),
            ('♥️♣️', 'HC'),
            ('♥️♦️', 'HD'),
            ('♣️♦️', 'CD')
        ),
        (
            ('♥️♣️♦️', 'HCD'),
            ('♠️♣️♦️', 'SCD'),
            ('♠️♥️♦️', 'SHD'),
            ('♠️♥️♣️', 'SHC')
        )
    ]


    global suit_to_endname

    suit_to_endname = {}

    for nominal in nominals:
        if nominal in ("J", "K", "A"):                              # suit endnames are added later
            suit_to_endname[nominal] = "ый"
        else:
            suit_to_endname[nominal] = "ая"


    # Text used for commands
    global bot_info_text, guest_text, owner_text

    bot_info_text = "\nОткрыть правила игры /rules.\n"
    bot_info_text += "Открыть свою комнату /open.\n"
    bot_info_text += "Подключиться к чужой комнате /join.\n"
    bot_info_text += "Посмотреть имя и статистику /personal.\n"
    bot_info_text += "Изменить имя и фамилию /rename."

    guest_text = "Покинуть комнату /leave."

    owner_text = "Закрыть комнату /close."
    owner_text += "\nНачать игру /play."

    # Dicts for users and rooms is used continuously
    global user_dict, room_dict

    user_dict = {}
    room_dict = {}