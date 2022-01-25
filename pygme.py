import pygame
import win32api
import win32con
import win32gui
import ch
import time
import html
from configparser import ConfigParser
from ctypes import windll

class Message:
    def __init__(self, msg_username, message, name_color, msg_color):
        self.username = msg_username
        self.message = message
        self.nameColor = name_color
        self.msgColor = msg_color



pygame.init()
pygame.font.init()
global chatcount
global chatstore
global ESC
ESC = False

config_object = ConfigParser()
try:
    config_object.read("config.ini")
    parameters = config_object["Parameters"]
    font_size = int(parameters["Font size"])
    overlay_height = int(parameters["Overlay height"])
    overlay_width = int(parameters["Overlay width"])
    always_focused = bool(parameters["Always on top"])

    chatangoDetails = config_object["Chatango bot"]
    rooms = [chatangoDetails["Room"]]
    username = chatangoDetails["Username"]
    password = chatangoDetails["Password"]
except:
    print("config not found")
    config_object = ConfigParser()
    config_object["Parameters"] = {
        "Font size": "30",
        "Overlay height": "400",
        "Overlay width": "700",
        "Always on top": "True",
        }
    config_object["Chatango bot"] = {
        "Username": "botstero",
        "Password": "123qwe",
        "Room": "vidyatendency",
        }

    with open('config.ini', 'w') as conf:
        config_object.write(conf)

    config_object.read("config.ini")
    parameters = config_object["Parameters"]
    font_size = int(parameters["Font size"])
    overlay_height = int(parameters["Overlay height"])
    overlay_width = int(parameters["Overlay width"])
    always_focused = bool(parameters["Always on top"])

    chatangoDetails = config_object["Chatango bot"]
    rooms = [chatangoDetails["Room"]]
    username = chatangoDetails["Username"]
    password = chatangoDetails["Password"]

myfont = pygame.font.SysFont('Arial Bold', font_size)
pygame.display.set_caption('chatango overlay')
chatstore = []
chatcount = 0  # message counter
shadow_color = (128, 128, 128)
shadow_y_offset = 2
shadow_x_offset = 1

screen = pygame.display.set_mode((overlay_width, overlay_height),pygame.NOFRAME)  
fuchsia = (255, 0, 128)  # Transparency color
dark_red = (139, 0, 0)
screen.fill(fuchsia)  # Transparent background

# Create layered window
hwnd = pygame.display.get_wm_info()["window"]
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                       win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
# Set window transparency color
win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*fuchsia), 0, win32con.LWA_COLORKEY)
win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 600, 300, 0, 0, win32con.SWP_NOSIZE)


class bot(ch.RoomManager):
    def onMessage(self, room, user, message):
        global chatcount
        global chatstore
        ctext = "{0}: {1}".format(user.name.title(), message.body)
        # shift everything in chat table to make room for new message
        print(ctext)
        chatstore.append(Message(
            html.unescape(user.name.title()),
            html.unescape(message.body),
            self.convert_chatango_colors(message.nameColor),
            self.convert_chatango_colors(message.fontColor)
        ))

        screen.fill(fuchsia)
        messageIndex = len(chatstore) - 1
        output_y = overlay_height
        # draw everything in chat table
        while messageIndex >= 0:
            current_message = chatstore[messageIndex]
            message_lines = bot.create_message_lines_array(current_message, overlay_width)
            message_height = bot.get_message_height(message_lines)
            bot.render_message(
                current_message.username,
                current_message.nameColor,
                message_lines,
                current_message.msgColor,
                output_y
            )
            messageIndex -= 1
            output_y -= message_height
            if output_y <= 0:
                bot.purge_old_chat(messageIndex)

            pygame.display.update()

    # every bot tick update the GUI
    def _tick(self):
         pygame.event.get()
         x,y = win32gui.GetCursorPos()
         x2 = int(x-overlay_width/2)
         y2 = int(y-overlay_height/2)
         b = win32gui.GetWindowRect(hwnd)
         if win32api.GetKeyState(0x01) < -1 and b[2] >= x >= b[0] and b[3] >= y >= b[1]:
             win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, x2, y2, overlay_height, overlay_width, win32con.SWP_NOSIZE)
         pygame.display.update()
         if win32api.GetKeyState(0x1B) < -1 and b[2] >= x >= b[0] and b[3] >= y >= b[1]:
             global ESC
             ESC = True
             exit()
    def onDisconnect(self, room):
     print("bot disconnected")
     if ESC == False:
      bot.stop(self)
      bot.easy_start(rooms, username, password)
    def onPMDisconnect(self, pm):
     print("PMbot disconnected")
     if ESC == False:
      bot.stop(self)
      bot.easy_start(rooms, username, password)

    @staticmethod
    def convert_chatango_colors(color):
        colorR, colorG, colorB = 0, 0, 0

        if len(color) == 3:
            colorR = int(str(color[0]) + str(color[0]), 16)
            colorG = int(str(color[1]) + str(color[1]), 16)
            colorB = int(str(color[2]) + str(color[2]), 16)
        if len(color) == 6:
            colorR = int(str(color[0:2]), 16)
            colorG = int(str(color[2:4]), 16)
            colorB = int(str(color[4:6]), 16)

        if colorR == 0 and colorG == 0 and colorB == 0:
            return 255, 255, 255
        return colorR, colorG, colorB

    @staticmethod
    def create_message_lines_array(message, line_width) -> list[str]:
        name_surface = myfont.render(message.username + ": ", False, shadow_color)
        first_line_width = line_width - name_surface.get_width()

        leftover_message = message.message
        lines = []
        i = 0
        while leftover_message:
            if len(lines) == 0:
                width = first_line_width
            else:
                width = line_width

            while myfont.size(leftover_message[:i])[0] < width and i < len(leftover_message):
                i += 1

            # if we've wrapped the text, then adjust the wrap to the last word
            if i < len(leftover_message):
                i = leftover_message.rfind(" ", 0, i) + 1
            if i == 0:
                i = len(leftover_message)
            lines.append(leftover_message[:i])

            leftover_message = leftover_message[i:]

        return lines

    @staticmethod
    def get_message_height(message_lines:list[str]):
        return font_size * len(message_lines)

    @staticmethod
    def render_message(username:str, nameColor, message_lines:list[str], msgColor, bottom_y):
        message_height = bot.get_message_height(message_lines)
        message_top_y = bottom_y - message_height

        #blit name
        name_surface = myfont.render(username + ": ", False, shadow_color)
        name_width = name_surface.get_width()
        screen.blit(name_surface, (shadow_x_offset, message_top_y + shadow_y_offset))
        name_surface = myfont.render(username + ": ", False, nameColor)
        screen.blit(name_surface, (0, message_top_y))

        #blit first line
        message_surface = myfont.render(message_lines[0], False, shadow_color)
        screen.blit(message_surface, (name_width + shadow_x_offset, message_top_y + shadow_y_offset))
        message_surface = myfont.render(message_lines[0], False, msgColor)
        screen.blit(message_surface, (name_width, message_top_y))

        #blit rest of the message
        i = 1
        for i in range(1, len(message_lines)):
            image = myfont.render(message_lines[i], False, shadow_color)
            screen.blit(image, (0 + shadow_x_offset, message_top_y + i * font_size + shadow_y_offset))
            image = myfont.render(message_lines[i], False, msgColor)
            screen.blit(image, (0, message_top_y + i * font_size))

    @staticmethod
    def purge_old_chat(offscreen_message_index):
        for purged_messages in range(0, offscreen_message_index):
            purged_message = chatstore.pop(0)
            print(purged_message.message)

    
pygame.draw.rect(screen, (0,0,255), (0,0,overlay_width,overlay_height), 0)
pygame.draw.rect(screen, fuchsia, (2,2,overlay_width-4,overlay_height-4), 0)

bot.easy_start(rooms, username, password)
