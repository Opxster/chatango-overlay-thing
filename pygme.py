import pygame
import win32api
import win32con
import win32gui
import ch
import time
import html
from ctypes import windll

class Message:
    def __init__(self, msg_username, message, name_color, msg_color):
        self.username = msg_username
        self.message = message
        self.nameColor = name_color
        self.msgColor = msg_color

font_size = 50
overlay_height = 600
overlay_width = 800

pygame.init()
pygame.font.init()
myfont = pygame.font.SysFont('Arial Bold', font_size)
pygame.display.set_caption('ghetto ass overlay')
global chatcount
global chatstore

chatstore = [
    Message("test", "1", (0, 255, 0), (0, 255, 0)),
    Message("tes", "2", (0, 255, 0), (0, 255, 0)),
    Message("te", "3", (0, 255, 0), (0, 255, 0)),
    Message("t", "4", (0, 255, 0), (0, 255, 0))
]
chatcount = 0  # message counter
shadow_color = (128, 128, 128)
shadow_y_offset = 2
shadow_x_offset = 1
font_size = 50

screen = pygame.display.set_mode((overlay_width, overlay_height))  # For borderless, use pygame.NOFRAME

done = False
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
        chatstore[0] = chatstore[1]
        chatstore[1] = chatstore[2]
        chatstore[2] = chatstore[3]
        chatstore[3] = Message(
            html.unescape(user.name.title()),
            html.unescape(message.body),
            self.convert_chatango_colors(message.nameColor),
            self.convert_chatango_colors(message.fontColor)
        )

        screen.fill(fuchsia)
        lineNumber = 0
        messageIndex = 0
        # draw everything in chat table
        while messageIndex < len(chatstore):
            current_message = chatstore[messageIndex]
            name_surface = myfont.render(current_message.username + ": ", False, current_message.nameColor)
            screen.blit(name_surface, (0, font_size * messageIndex))

            leftover_message = current_message.message
            messageBounds = pygame.Rect(
                name_surface.get_width(),
                font_size * lineNumber,
                overlay_width - name_surface.get_width(),
                overlay_height - font_size * lineNumber,
            )
            i = 1
            y = messageBounds.top
            lineSpacing = -2
            while leftover_message:
                while myfont.size(leftover_message[:i])[0] < messageBounds.width and i < len(leftover_message):
                    i += 1
                    

                # if we've wrapped the text, then adjust the wrap to the last word
                if i < len(leftover_message):
                    i = leftover_message.rfind(" ", 0, i) + 1
                if i == 0:
                 i = len(leftover_message)                 
                image = myfont.render(leftover_message[:i], False, shadow_color)
                screen.blit(image, (messageBounds.left + shadow_x_offset, y + shadow_y_offset))
                image = myfont.render(leftover_message[:i], False, current_message.msgColor)
                screen.blit(image, (messageBounds.left, y))
                y += font_size + lineSpacing

                leftover_message = leftover_message[i:]
                lineNumber = lineNumber + 1

            messageIndex += 1

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
rooms = ["fontsizeparam"]
username = "botstero"
password = "123qwe"
bot.easy_start(rooms, username, password)
