from random import shuffle
from PIL import Image, ImageDraw, ImageFont
import numpy as np

import game_attributes
if __name__ == '__main__':
    game_attributes.attributes_init()

from game_attributes import user_dict
from game_attributes import nominals, num_to_card, card_to_num


# Object of User class is created immediately after user registration
class User:
    def __init__(self, username, first_name=None, last_name=None):
        self.username = username            # user's account name
        self.first_name = first_name
        self.last_name = last_name
        self.current_room_id = None         # link to the room the user is in
        self.games = 0
        self.victories = 0
        self.chests = 0
    
    def setFirstName(self, new_first_name):
        self.first_name = new_first_name
    
    def setLastName(self, new_last_name):
        self.last_name = new_last_name
    
    def joinRoom(self, room_id):
        self.current_room_id = room_id
    
    def leaveRoom(self):
        self.current_room_id = None
    
    def updateScore(self, victory, chest):
        self.games += 1                     # update user stats after each game
        self.victories += victory
        self.chests += chest


# Object of Room class is created for each user immediately after registration
class Room:
    def __init__(self, owner_id):
        self.owner_id = owner_id            # owner link is equal to room link
        self.is_opened = False
        self.users_count = 0
        self.user_ids = []                  # list of users (in open room)
        self.players = {}                   # players are created from user list after the game start
        self.queue = []                     # game order
        self.deck = list(range(52))
        self.stack = []                     # rest of the deck lying in the center of the table
        self.cards_count = 0                # number of cards not in chests (stack and players hands)
        self.first_names_dict = {}
        self.image = None
        self.round_to_delete = []           # message links of one round to be deleted after the round is finished
        self.message_to_delete = []         # message links of one bot message to be deleted after the message is answered
    

    def openRoom(self):
        self.is_opened = True
        self.users_count = 1
        user_dict[self.owner_id].joinRoom(self.owner_id)
    

    def closeRoom(self):
        user_dict[self.owner_id].leaveRoom()
        for user_id in self.user_ids:
            user_dict[user_id].leaveRoom()
        
        self.is_opened = False
        self.users_count = 0
        self.user_ids.clear()
    

    def addUser(self, user_id):
        self.user_ids.append(user_id)
        self.users_count += 1
        user_dict[user_id].joinRoom(self.owner_id)
    

    def removeUser(self, user_id):
        self.user_ids.remove(user_id)
        self.users_count -= 1
        user_dict[user_id].leaveRoom()
    

    def startGame(self):
        self.createPlayer(self.owner_id)                        # create Player object for each user in the room
        for user_id in self.user_ids:
            self.createPlayer(user_id)
        
        shuffle(self.deck)                                      # prepare cards for the game
        self.stack = self.deck.copy()

        for first_name in self.first_names_dict:                # set names for players
            if len(self.first_names_dict[first_name]) == 1:             # name is first name for players with unique first names
                user_id = self.first_names_dict[first_name][0]
                self.addPlayerParams(user_id, first_name)
                self.queue.append(user_id)
            else:                                                       # name is first and last name for players with non-unique names
                for user_id in self.first_names_dict[first_name]:
                    self.addPlayerParams(user_id, first_name + ' ' + user_dict[user_id].last_name)
                    self.queue.append(user_id)
        self.first_names_dict.clear()

        shuffle(self.queue)
        self.cards_count = 52
    

    def createPlayer(self, user_id):
        user = user_dict[user_id]
        player = Player(user.username)
        self.players[user_id] = player

        if user.first_name not in self.first_names_dict:        # add first name and user link to dict that is used to set player names later
            self.first_names_dict[user.first_name] = []
        self.first_names_dict[user.first_name].append(user_id)
    

    def addPlayerParams(self, player_id, name):
        self.players[player_id].setName(name)

        num_list = []                                           # take initial cards in hand
        for _ in range(4):
            num_list.append(self.stack.pop())
        nominal_id = self.players[player_id].takeCards(num_list)

        self.throwChest(player_id, nominal_id)
    

    def setQueue(self, first_player_id):
        player_id = self.queue[-1]
        while player_id != first_player_id:
            player_id = self.updateQueue()
    

    def addMessagesToDelete(self, messages, is_round=False):
        if is_round:
            self.round_to_delete.extend(messages)
        else:
            self.message_to_delete.extend(messages)
    

    def clearMessagesToDelete(self, is_round=False):
        if is_round:
            self.round_to_delete.clear()
        else:
            self.message_to_delete.clear()
    

    def giveCards(self, nominal, player_id):
        return self.players[player_id].removeNominal(nominal)

    
    def takeCards(self, player_id, is_stack=False, nums=None):
        nominal_id = None
        if is_stack:
            nominal_id = self.players[player_id].takeCards([self.stack.pop()])
        else:
            nominal_id = self.players[player_id].takeCards(nums)
        self.throwChest(player_id, nominal_id)
    

    def throwChest(self, player_id, nominal_id):
        if nominal_id is not None:                              # throw cards on the table if there is a chest
            self.cards_count -= 4
            self.drawChest(player_id, self.players[player_id].chest_count, nominal_id)


    def updateQueue(self):
        player_id = self.queue.pop(0)
        self.queue.append(player_id)
        return player_id
    

    def drawChest(self, front_id, chest_num, nominal_id):
        tmp = self.queue.index(front_id)                        # set order to draw the table
        order = self.queue[tmp:] + self.queue[:tmp]

        R = 300

        nums = list(range(4 * nominal_id, 4 * nominal_id + 4))  # set random order of chest cards
        shuffle(nums)

        for i, player_id in enumerate(order):                   # draw chest in front of chest owner for each player
            for k, num in enumerate(nums):
                alpha = 5 * (chest_num - 4)
                alpha -= i * 360 // self.users_count                    # i defines the owner's angle
                alpha -= (k - 1) / 2                                    # k defines the small shift angle for each card in chest
                path = 'Img/Small/' + str(num) + '.png'
                self.players[player_id].drawChestCard(path, alpha, R)


    def drawPlayerRoom(self, front_id, face_id=None, smile_id=None, rage_id=None, ask_nums=[]):
        '''
            `front_id` - front player
            `face_id` - active player
            `smile_id` - player receiving cards from another player
            `rage_id` - player giving cards to another player
            `ask_nums` - list of transferred cards

            `face_id` is necessary to draw the room at the beginning of the round to show the player asking questions.
            `smile_id`, `rage_id` and `ask_nums` is necessary to draw the room at the end of the round
                to show the winner, the loser and the transferred cards.
        '''
        self.image = self.players[front_id].image.copy()

        self.drawStack()

        tmp = self.queue.index(front_id)                        # set order to draw the table
        order = self.queue[tmp + 1:] + self.queue[:tmp]         # the front player will be added later (to draw emoji)

        R, r = 720, 320                                         # draw the front player's hand
        nums = self.players[front_id].num_list
        for j, num in enumerate(nums):
            beta = 2 * (len(nums) - 1 - 2 * j)
            path = 'Img/Cards/' + str(num) + '.png'
            self.drawCard(path, 0, beta, R, r)
        
        R, r = 720, 270                                         # draw opponents hands
        path = 'Img/back.png'
        for i, player_id in enumerate(order):
            alpha = -(i + 1) * 360 // self.users_count
            n_cards = len(self.players[player_id].num_list)
            for j in range(n_cards):
                beta = 5 * (n_cards - 1 - 2 * j) // 2
                self.drawCard(path, alpha, beta, R, r)
                        
        R = 300                                                 # draw players names
        delta_alpha = 15
        for i, player_id in enumerate(order):
            alpha = -(i + 1) * 360 // self.users_count
            alpha += delta_alpha
            self.drawName(player_id, alpha, R)
        
        R = 450                                                 # draw emoji
        order = [front_id] + order
        if face_id:                                                     # emoji of the player asking questions
            alpha = -order.index(face_id) * 360 // self.users_count
            self.drawEmoji("Img/slightly_smiling_face.png", alpha, R)
        if smile_id:                                                    # emoji of the players receiving cards from another player
            alpha = -order.index(smile_id) * 360 // self.users_count
            self.drawEmoji("Img/smiley.png", alpha, R)
        if rage_id:                                                     # emoji of the player giving cards to another player
            alpha = -order.index(rage_id) * 360 // self.users_count
            self.drawEmoji("Img/rage.png", alpha, R)
        
        for i, num in enumerate(ask_nums):                    # draw transferred cards
            R = 100 * abs(2 * i + 1 - len(ask_nums))
            alpha = -90 * ((4 - len(ask_nums)) * i + 1)
            path = 'Img/Cards/' + str(num) + '.png'
            self.drawCard(path, alpha, -alpha, R, 0)
        
        image = self.image.copy()
        self.image = None

        return image


    def drawCard(self, path, alpha, beta, R, r):
        '''
            `path` - link to the card file
            `alpha` - player's angle
            `beta` - card angle in a player's hand
            `R` - radius from the room center
            `r` - radius of a player's hand
        '''
        card = Image.open(path)                                 # card loading and rotation
        width, height = card.size
        card = card.rotate(angle, expand=1)

        angle = alpha + beta                                    # total angle of a card rotation
        
        mask_card = Image.new("L", (width, height), 0)          # mask creation and rotation
        draw = ImageDraw.Draw(mask_card)
        draw.rounded_rectangle((0, 0, width, height), radius=(width / 10 - 1), fill=255)
        mask_card = mask_card.rotate(angle, expand=1)

        alpha = alpha / 180 * np.pi
        angle = angle / 180 * np.pi

        pos_x = self.image.size[0] / 2                                  # room center
        pos_y = self.image.size[1] / 2
        pos_x += R * np.sin(alpha)                                      # player's hand center
        pos_y += R * np.cos(alpha)
        pos_x -= r * np.sin(angle)                                      # card location in a player's hand
        pos_y -= r * np.cos(angle)
        pos_x -= (width * np.abs(np.cos(angle)) + height * np.abs(np.sin(angle))) / 2   # correction for card size and rotation
        pos_y -= (width * np.abs(np.sin(angle)) + height * np.abs(np.cos(angle))) / 2
        pos_x = np.round(pos_x).astype('int')
        pos_y = np.round(pos_y).astype('int')

        self.image.paste(card, (pos_x, pos_y), mask_card)
    

    def drawStack(self):
        n_cards = len(self.stack)
        path = 'Img/back.png'
        for i in range(n_cards):                                # card stack is rotated to show number of cards
            alpha = 180 * (i + 1) // n_cards
            self.drawCard(path, alpha, 0, 0, 0)
    

    def drawName(self, player_id, alpha, R, delta_height=-40, font_size=30, stroke_width=1, fill='orange'):
        '''
            `player_id` - player
            `alpha` - player's angle
            `R` - radius from the room center
            `delta_height` - vertical shift to avoid intersections with other components of the table
        '''
        font = ImageFont.truetype("Img/arial.ttf", font_size)       # set text format
        drawer = ImageDraw.Draw(self.image)

        text = self.players[player_id].name                     # name could consist of two words
        words = text.split()

        width = max(font.getmask(word).getbbox()[2] for word in words)  # width is equal to the longest word in the name
        height = font.getmask(text).getbbox()[3]

        alpha = alpha / 180 * np.pi

        pos_x = self.image.size[0] / 2                                  # room center
        pos_y = self.image.size[1] / 2 + delta_height
        pos_x += R * np.sin(alpha)                                      # place before the player's hand
        pos_y += R * np.cos(alpha)
        pos_x -= width // 2                                             # correction for name size
        pos_y -= height // 2
        pos_x = np.round(pos_x).astype('int')
        pos_y = np.round(pos_y).astype('int')

        drawer.text(
            (pos_x, pos_y),
            '\n'.join(words),
            font=font,
            fill=fill,
            stroke_width=stroke_width,
            align="center"
        )
    

    def drawEmoji(self, path, alpha, R):
        emoji = Image.open(path)                                # emoji loading
        width, height = emoji.size

        mask = Image.new("L", (width, height), 0)               # mask creation
        draw = ImageDraw.Draw(mask)
        draw.ellipse((1, 1, width - 1, height - 1), fill='white')

        alpha = alpha / 180 * np.pi

        pos_x = self.image.size[0] / 2                                  # room center
        pos_y = self.image.size[1] / 2
        pos_x += R * np.sin(alpha)                                      # player's hand
        pos_y += R * np.cos(alpha)
        pos_x -= width / 2                                              # correction for emoji size
        pos_y -= height / 2
        pos_x = np.round(pos_x).astype('int')
        pos_y = np.round(pos_y).astype('int')

        self.image.paste(emoji, (pos_x, pos_y), mask)
    

    def finishGame(self):
        self.players.clear()
        self.queue.clear()
        self.cards_count = 0


# Object of Player class is created immediately after the game starts
class Player:
    def __init__(self, username):
        self.username = username
        self.name = None
        self.num_list = []                  # list of card numbers (used to sort cards in player's hand and get links to files)
        self.card_dict = {}                 # dict of card names (used for asking questions and checking cards in another player's hand)
        self.chest_count = 0
        self.image = Image.open('Img/room.png') # empty round
    

    def setName(self, name):
        self.name = name
    

    def removeNominal(self, nominal):
        nums = []                                               # give cards to another player
        for card in self.card_dict.pop(nominal):
            num = card_to_num[card]
            self.num_list.remove(num)
            nums.append(num)
        return nums


    def takeCards(self, nums):
        self.num_list.extend(nums)
        self.num_list.sort()

        for num in nums:
            nominal = nominals[num // 4]
            if nominal not in self.card_dict:
                self.card_dict[nominal] = []
            self.card_dict[nominal].append(num_to_card[num])

            if len(self.card_dict[nominal]) == 4:               # throw a chest if the player gets one in his hand
                _ = self.removeNominal(nominal)
                self.chest_count += 1
                return nominals.index(nominal)
        return None
    

    def drawChestCard(self, path, alpha, R):
        '''
            `path` - link to the card file
            `alpha` - player's angle
            `R` - radius from the room center
        '''
        card = Image.open(path)                                 # card loading and rotation
        width, height = card.size
        card = card.rotate(alpha, expand=1)

        mask_card = Image.new("L", (width, height), 0)          # mask creation and rotation
        draw = ImageDraw.Draw(mask_card)
        draw.rounded_rectangle((0, 0, width, height), radius=(width / 10 - 1), fill=255)
        mask_card = mask_card.rotate(alpha, expand=1)

        alpha = alpha / 180 * np.pi

        pos_x = self.image.size[0] / 2                                  # room center
        pos_y = self.image.size[1] / 2
        pos_x += R * np.sin(alpha)                                      # place before the player's hand
        pos_y += R * np.cos(alpha)
        pos_x -= (width * np.abs(np.cos(alpha)) + height * np.abs(np.sin(alpha))) / 2   # correction for card size and rotation
        pos_y -= (width * np.abs(np.sin(alpha)) + height * np.abs(np.cos(alpha))) / 2
        pos_x = np.round(pos_x).astype('int')
        pos_y = np.round(pos_y).astype('int')

        self.image.paste(card, (pos_x, pos_y), mask_card)
