from tkinter import *
from time import *      #type: ignore
import os
from tkinter.ttk import Combobox
import cv2
#import mediapipe as mp


from PIL import Image, ImageTk, ImageDraw, ImageFont
import json
import webbrowser
import pyautogui as pag
import keyboard
import win32api
import win32con
import time
import threading
import copy
import win32com.client
import mediapipe as mp

import win32gui


# create all necessary path that are required
def remove_last_until_slash(string):
    while string and string[-1] != "\\":
        string = string[:-1]
    return string
current_file_path = os.path.abspath(__file__)
current_file_path_with_double_backslashes = current_file_path.replace(os.sep, '\\\\')
result = remove_last_until_slash(current_file_path_with_double_backslashes)
main_path = result + "assets\\\\"
picture_path = main_path + "pictures\\\\"
profiles_path = main_path + "profiles\\\\"


# base stuff camera and mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
#cap = cv2.VideoCapture(0)
#cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640 * 1)
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480 * 1)
font_path = "arial.ttf"  # Change this to the path of your font file
font_size = 24
font = ImageFont.truetype(font_path, font_size)

# global variables for execution of gestures
x_tmp_r = 0
x_tmp_l = 0
y_tmp_r = 0
y_tmp_l = 0

# Create base variables
resolution_gesture = 30
previos_time = time.time()
gesture_name = "None"
gesture_left = "None"
gesture_right = "None"
left_action = "None"
right_action = "None"
refresh_time = 0.5
start_time = time.time()
running = True
gesture_left_info = {}
gesture_right_info = {}
current_hand = "left"
running_actions = False
thread_running = False
w_pressed = False
a_pressed = False
s_pressed = False
d_pressed = False
camera_feed_visible = True
header_menu_shown = False
active_page = ""
gesture_functions = [
        "fist_gesture",
        "flat_hand_gesture_thumb_close",
        "flat_hand_gesture_thumb_stretched",
        "four_gesture",
        "index_gesture",
        "l_gesture",
        "measure_gesture",
        "middlefeinger_gesture",
        "peace_close_gesture",
        "peace_gesture",
        "pinky_gesture",
        "ring_gesture",
        "three_gesture",
        "thumb_index_middle_gesture",
        "thumbs_up_gesture"
    ]
empty_content = {
    "left": {
        "fist_gesture": "None",
        "flat_hand_gesture_thumb_close": "None",
        "flat_hand_gesture_thumb_stretched": "None",
        "four_gesture": "None",
        "index_gesture": "None",
        "l_gesture": "None",
        "measure_gesture": "None",
        "middlefeinger_gesture": "None",
        "peace_close_gesture": "None",
        "peace_gesture": "None",
        "pinky_gesture": "None",
        "ring_gesture": "None",
        "three_gesture": "None",
        "thumb_index_middle_gesture": "None",
        "thumbs_up_gesture": "None"
    },
    "right": {
        "fist_gesture": "None",
        "flat_hand_gesture_thumb_close": "None",
        "flat_hand_gesture_thumb_stretched": "None",
        "four_gesture": "None",
        "index_gesture": "None",
        "l_gesture": "None",
        "measure_gesture": "None",
        "middlefeinger_gesture": "None",
        "peace_close_gesture": "None",
        "peace_gesture": "None",
        "pinky_gesture": "None",
        "ring_gesture": "None",
        "three_gesture": "None",
        "thumb_index_middle_gesture": "None",
        "thumbs_up_gesture": "None"
    }
}
combo_values = [
    "Activate/deactivate quest or objective markers",
    "Aim down sights",
    "Attack with primary weapon",
    "Attack with secondary weapon",
    "Block/defend",
    "Change camera view/perspective",
    "Communicate with NPCs or other players",
    "Crafting system",
    "Crouch",
    "Customize character appearance/loadout",
    "Drop item",
    "Equip/unequip items",
    "Interact with objects",
    "Jump",
    "Move character backward",
    "Move character forward",
    "None",
    "Open inventory",
    "Open map",
    "Perform a melee attack",
    "Pick up item",
    "Reload weapon",
    "Save/load game progress",
    "Sprint",
    "Strafe left",
    "Strafe right",
    "Use a vehicle",
    "Use ability/special move",
    "Use flashlight/night vision",
    "Use item/consumable",
    "Use crafting system"
]
text_font = ("Inter", 16 * -1)
bg_white = "#FFFFFF"
bg_dark_blue = "#15153C"



#calculate gesture based on finger-coordintes
#region gestures
def similar(point1, point2, distance):
    return abs(point1 - point2) <= distance

def gesture_check(points):    
    if thumb_index_middle_gesture(points):
        return "thumb_index_middle_gesture"
    if four_gesture(points):
        return "four_gesture"
    if three_gesture(points):
        return "three_gesture"
    if l_gesture(points):
        return "l_gesture"
    if peace_gesture(points):
        return "peace_gesture"
    if peace_close_gesture(points):
        return "peace_close_gesture"  
    if fist_gesture(points):
        return "fist_gesture"
    if flat_hand_gesture_thumb_stretched(points):
        return "flat_hand_gesture_thumb_stretched"  
    if flat_hand_gesture_thumb_close(points):
        return "flat_hand_gesture_thumb_close"    
    if measure_gesture(points):        
        return "measure_gesture" 
    if thumbs_up_gesture(points):
        return "thumbs_up_gesture"
    if pinky_gesture(points):
        return "pinky_gesture"
    if ring_gesture(points):
        return "ring_gesture"
    if middlefeinger_gesture(points):
        return "middlefeinger_gesture"
    if index_gesture(points):
        return "index_gesture"
    return ""

def peace_gesture(points):
    # Sorting the dictionary based on the 'x' and 'y' value of its values
    y_sorted_points = dict(sorted(points.items(), key=lambda item: item[1].y))
    x_sorted_points = dict(sorted(points.items(), key=lambda item: item[1].x))
    
    mid_fingers = points.copy()
    mid_fingers.pop("middle")
    mid_fingers.pop("index")
    mid_fingers.pop("wrist")
    
    x_sorted_mid_fingers = dict(sorted(mid_fingers.items(), key=lambda item: item[1].x))
    x_sorted_mid_fingers_list = list(x_sorted_mid_fingers.items())    
    
    y_sorted_mid_fingers = dict(sorted(mid_fingers.items(), key=lambda item: item[1].y))
    y_sorted_mid_fingers_list = list(y_sorted_mid_fingers.items())
    
    if len(points) == 6:
        if (
            abs(points["index"].x - points["middle"].x) >= 2
            and abs(points["index"].y - points["middle"].y) <= 3
            and list(y_sorted_points.keys())[-1] == "wrist"
            and similar(x_sorted_mid_fingers_list[0][1].x, x_sorted_mid_fingers_list[-1][1].x, 2)
            and y_sorted_mid_fingers_list[0][1].y - points["index"].y > 3                 
        ):
            return True
    return False

def peace_close_gesture(points):
    # Sorting the dictionary based on the 'x' and 'y' value of its values
    y_sorted_points = dict(sorted(points.items(), key=lambda item: item[1].y))
    x_sorted_points = dict(sorted(points.items(), key=lambda item: item[1].x))
    
    mid_fingers = points.copy()
    mid_fingers.pop("middle")
    mid_fingers.pop("index")
    mid_fingers.pop("wrist")
    
    x_sorted_mid_fingers = dict(sorted(mid_fingers.items(), key=lambda item: item[1].x))
    x_sorted_mid_fingers_list = list(x_sorted_mid_fingers.items())    
    
    y_sorted_mid_fingers = dict(sorted(mid_fingers.items(), key=lambda item: item[1].y))
    y_sorted_mid_fingers_list = list(y_sorted_mid_fingers.items())
    
    
    if len(points) == 6:
        
        if (
            abs(points["index"].x - points["middle"].x) < 2
            and abs(points["index"].y - points["middle"].y) <= 3 
            and list(y_sorted_points.keys())[-1] == "wrist"
            and similar(x_sorted_mid_fingers_list[0][1].x, x_sorted_mid_fingers_list[-1][1].x, 2)
            and y_sorted_mid_fingers_list[0][1].y - points["index"].y > 3                 
        ):
            return True
    return False

def middlefeinger_gesture(points):
    y_sorted_points = dict(sorted(points.items(), key=lambda item: item[1].y))
    x_sorted_points = dict(sorted(points.items(), key=lambda item: item[1].x))
    
    mid_fingers = points.copy()
    mid_fingers.pop("middle")
    mid_fingers.pop("wrist")
    
    x_sorted_mid_fingers = dict(sorted(mid_fingers.items(), key=lambda item: item[1].x))
    x_sorted_mid_fingers_list = list(x_sorted_mid_fingers.items())  
    
    y_sorted_mid_fingers = dict(sorted(mid_fingers.items(), key=lambda item: item[1].y))
    y_sorted_mid_fingers_list = list(y_sorted_mid_fingers.items())
    
    if len(points) == 6:
        
        if (
            list(y_sorted_points.keys())[0] == "middle"
            and list(y_sorted_points.keys())[-1] == "wrist"
            and similar(y_sorted_mid_fingers_list[0][1].y, y_sorted_mid_fingers_list[-1][1].y, 3)
            and similar(x_sorted_mid_fingers_list[0][1].x, x_sorted_mid_fingers_list[-1][1].x, 6)
            and x_sorted_mid_fingers_list[-1][1].x - x_sorted_mid_fingers_list[-2][1].x < 2
            
            and abs(y_sorted_mid_fingers_list[0][1].y - points["middle"].y) > 1        
            and abs(y_sorted_mid_fingers_list[-1][1].y - points["wrist"].y) > 1             
        ):            
            return True
    return False

def index_gesture(points):
    y_sorted_points = dict(sorted(points.items(), key=lambda item: item[1].y))
    x_sorted_points = dict(sorted(points.items(), key=lambda item: item[1].x))
    
    mid_fingers = points.copy()
    mid_fingers.pop("index")
    mid_fingers.pop("wrist")
    
    x_sorted_mid_fingers = dict(sorted(mid_fingers.items(), key=lambda item: item[1].x))
    x_sorted_mid_fingers_list = list(x_sorted_mid_fingers.items())  
    
    y_sorted_mid_fingers = dict(sorted(mid_fingers.items(), key=lambda item: item[1].y))
    y_sorted_mid_fingers_list = list(y_sorted_mid_fingers.items())
    
    if len(points) == 6:
        
        if (
            list(y_sorted_points.keys())[0] == "index"
            and list(y_sorted_points.keys())[-1] == "wrist"
            and similar(y_sorted_mid_fingers_list[0][1].y, y_sorted_mid_fingers_list[-1][1].y, 3)
            and similar(x_sorted_mid_fingers_list[0][1].x, x_sorted_mid_fingers_list[-1][1].x, 6)
            and x_sorted_mid_fingers_list[0][1].x - x_sorted_mid_fingers_list[-1][1].x < 6
            
            and abs(y_sorted_mid_fingers_list[0][1].y - points["index"].y) > 1        
            and abs(y_sorted_mid_fingers_list[-1][1].y - points["wrist"].y) > 1   
            and abs(x_sorted_mid_fingers_list[1][1].x - x_sorted_mid_fingers_list[0][1].x < 2)          
        ):
            return True
    return False

def fist_gesture(points):
    y_sorted_points = dict(sorted(points.items(), key=lambda item: item[1].y))
    x_sorted_points = dict(sorted(points.items(), key=lambda item: item[1].x))
    
    mid_fingers = points.copy()
    mid_fingers.pop("wrist")
    
    x_sorted_mid_fingers = dict(sorted(mid_fingers.items(), key=lambda item: item[1].x))
    x_sorted_mid_fingers_list = list(x_sorted_mid_fingers.items())    
    
    y_sorted_mid_fingers = dict(sorted(mid_fingers.items(), key=lambda item: item[1].y))
    y_sorted_mid_fingers_list = list(y_sorted_mid_fingers.items())
    
    if len(points) == 6:
        if (            
            list(y_sorted_points.keys())[-1] == "wrist"
            and similar(y_sorted_mid_fingers_list[0][1].y, y_sorted_mid_fingers_list[-1][1].y, 4)
            and similar(x_sorted_mid_fingers_list[0][1].x, x_sorted_mid_fingers_list[-1][1].x, 7)
            #and x_sorted_mid_fingers_list[0][1].x <= points["wrist"].x <= x_sorted_mid_fingers_list[-1][1].x
            and abs(y_sorted_mid_fingers_list[-1][1].y - points["wrist"].y) > 2             
        ):
            return True
    return False

def thumbs_up_gesture(points):
    y_sorted_points = dict(sorted(points.items(), key=lambda item: item[1].y))
    x_sorted_points = dict(sorted(points.items(), key=lambda item: item[1].x))
    
    mid_fingers = points.copy()
    mid_fingers.pop("thumb")
    mid_fingers.pop("wrist")
    
    x_sorted_mid_fingers = dict(sorted(mid_fingers.items(), key=lambda item: item[1].x))
    x_sorted_mid_fingers_list = list(x_sorted_mid_fingers.items())  
    
    y_sorted_mid_fingers = dict(sorted(mid_fingers.items(), key=lambda item: item[1].y))
    y_sorted_mid_fingers_list = list(y_sorted_mid_fingers.items())
    
    if len(points) == 6:        
        if (
            list(y_sorted_points.keys())[0] == "thumb"
            and similar(x_sorted_mid_fingers_list[0][1].x, x_sorted_mid_fingers_list[-1][1].x, 3)
            and abs(y_sorted_mid_fingers_list[0][1].y - points["thumb"].y) > 4
            and similar(x_sorted_mid_fingers_list[0][1].x, points["wrist"].x, 5)     
        ):
            return True
    return False

def l_gesture(points):
    y_sorted_points = dict(sorted(points.items(), key=lambda item: item[1].y))
    x_sorted_points = dict(sorted(points.items(), key=lambda item: item[1].x))
    
    mid_fingers = points.copy()
    mid_fingers.pop("index")
    mid_fingers.pop("thumb")
    mid_fingers.pop("wrist")
    
    x_sorted_mid_fingers = dict(sorted(mid_fingers.items(), key=lambda item: item[1].x))
    x_sorted_mid_fingers_list = list(x_sorted_mid_fingers.items())  
    
    y_sorted_mid_fingers = dict(sorted(mid_fingers.items(), key=lambda item: item[1].y))
    y_sorted_mid_fingers_list = list(y_sorted_mid_fingers.items())
    
    if len(points) == 6:
        
        if (
            list(y_sorted_points.keys())[0] == "index"
            and list(y_sorted_points.keys())[-1] == "wrist"
            and abs(y_sorted_mid_fingers_list[0][1].y - points["index"].y) > 1        
            and abs(y_sorted_mid_fingers_list[-1][1].y - points["wrist"].y) >= 1 
            and (list(x_sorted_points.keys())[0] == "thumb" or list(x_sorted_points.keys())[-1] == "thumb")
            and (abs(points["thumb"].x - x_sorted_mid_fingers_list[0][1].x) > 2)     
        ):
            return True
    return False

def flat_hand_gesture_thumb_stretched(points):
    x_sorted_points = dict(sorted(points.items(), key=lambda item: item[1].x))    
    y_sorted_points = dict(sorted(points.items(), key=lambda item: item[1].y))
       
    if len(points) == 6:
        if (
            list(y_sorted_points.keys())[-1] == "wrist"
            and points["thumb"].x !=  points["index"].x !=  points["middle"].x !=  points["ring"].x !=  points["pinky"].x
            and (list(x_sorted_points.keys())[0] == "thumb" or list(x_sorted_points.keys())[-1] == "thumb")
            and abs(points["thumb"].x - points["index"].x) >= 2
            and abs(points["wrist"].y - points["index"].y) >= 4
            and abs(points["wrist"].y - points["middle"].y) >= 5
            and abs(points["wrist"].y - points["ring"].y) >= 6
        ):
            return True
    return False

def flat_hand_gesture_thumb_close(points):
    x_sorted_points = dict(sorted(points.items(), key=lambda item: item[1].x))    
    y_sorted_points = dict(sorted(points.items(), key=lambda item: item[1].y))
       
    if len(points) == 6:
        if (
            list(y_sorted_points.keys())[-1] == "wrist"
            and points["thumb"].x !=  points["index"].x !=  points["middle"].x !=  points["ring"].x !=  points["pinky"].x
            and (list(x_sorted_points.keys())[0] == "thumb" or list(x_sorted_points.keys())[-1] == "thumb")
            and abs(points["thumb"].x - points["index"].x) < 2
            and abs(points["wrist"].y - points["index"].y) >= 4
            and abs(points["wrist"].y - points["middle"].y) >= 5
            and abs(points["wrist"].y - points["ring"].y) >= 6
        ):
            return True
    return False

def pinky_gesture(points):
    y_sorted_points = dict(sorted(points.items(), key=lambda item: item[1].y))
    x_sorted_points = dict(sorted(points.items(), key=lambda item: item[1].x))
    
    mid_fingers = points.copy()
    mid_fingers.pop("pinky")
    mid_fingers.pop("wrist")
    
    x_sorted_mid_fingers = dict(sorted(mid_fingers.items(), key=lambda item: item[1].x))
    x_sorted_mid_fingers_list = list(x_sorted_mid_fingers.items())  
    
    y_sorted_mid_fingers = dict(sorted(mid_fingers.items(), key=lambda item: item[1].y))
    y_sorted_mid_fingers_list = list(y_sorted_mid_fingers.items())
    
    if len(points) == 6:
        if (
            list(y_sorted_points.keys())[0] == "pinky"
            and list(y_sorted_points.keys())[-1] == "wrist"
            and similar(y_sorted_mid_fingers_list[0][1].y, y_sorted_mid_fingers_list[-1][1].y, 3)
            and similar(x_sorted_mid_fingers_list[0][1].x, x_sorted_mid_fingers_list[-1][1].x, 6)
            and abs(y_sorted_mid_fingers_list[0][1].y - points["pinky"].y) > 1        
            and abs(y_sorted_mid_fingers_list[-1][1].y - points["wrist"].y) > 1 
        ):
            return True
    return False

def ring_gesture(points):
    y_sorted_points = dict(sorted(points.items(), key=lambda item: item[1].y))
    x_sorted_points = dict(sorted(points.items(), key=lambda item: item[1].x))
    
    mid_fingers = points.copy()
    mid_fingers.pop("ring")
    mid_fingers.pop("wrist")
    
    x_sorted_mid_fingers = dict(sorted(mid_fingers.items(), key=lambda item: item[1].x))
    x_sorted_mid_fingers_list = list(x_sorted_mid_fingers.items())  
    
    y_sorted_mid_fingers = dict(sorted(mid_fingers.items(), key=lambda item: item[1].y))
    y_sorted_mid_fingers_list = list(y_sorted_mid_fingers.items())
    
    if len(points) == 6:
        if (
            list(y_sorted_points.keys())[0] == "ring"
            and list(y_sorted_points.keys())[-1] == "wrist"
            and similar(y_sorted_mid_fingers_list[0][1].y, y_sorted_mid_fingers_list[-1][1].y, 3)
            and similar(x_sorted_mid_fingers_list[0][1].x, x_sorted_mid_fingers_list[-1][1].x, 6)
            and abs(y_sorted_mid_fingers_list[0][1].y - points["ring"].y) > 1        
            and abs(y_sorted_mid_fingers_list[-1][1].y - points["wrist"].y) > 1 
        ):
            return True
    return False

def thumb_index_middle_gesture(points):
    # Sorting the dictionary based on the 'x' and 'y' value of its values
    y_sorted_points = dict(sorted(points.items(), key=lambda item: item[1].y))
    x_sorted_points = dict(sorted(points.items(), key=lambda item: item[1].x))
    
    mid_fingers = points.copy()
    mid_fingers.pop("middle")
    mid_fingers.pop("index")
    mid_fingers.pop("thumb")
    mid_fingers.pop("wrist")
    
    x_sorted_mid_fingers = dict(sorted(mid_fingers.items(), key=lambda item: item[1].x))
    x_sorted_mid_fingers_list = list(x_sorted_mid_fingers.items())    
    
    y_sorted_mid_fingers = dict(sorted(mid_fingers.items(), key=lambda item: item[1].y))
    y_sorted_mid_fingers_list = list(y_sorted_mid_fingers.items())
    
    if len(points) == 6:
        if (
            similar(points["index"].y, points["middle"].y, 3)
            and list(y_sorted_points.keys())[-1] == "wrist"
            and similar(x_sorted_mid_fingers_list[0][1].x, x_sorted_mid_fingers_list[-1][1].x, 2)
            and (abs(x_sorted_mid_fingers_list[0][1].x - points["thumb"].x) > 3 or abs(x_sorted_mid_fingers_list[-1][1].x - points["thumb"].x) > 3)
            and y_sorted_mid_fingers_list[0][1].y - points["index"].y > 3        
        ):
            return True
    return False

def four_gesture(points):
    x_sorted_points = dict(sorted(points.items(), key=lambda item: item[1].x))    
    y_sorted_points = dict(sorted(points.items(), key=lambda item: item[1].y))
       
    if len(points) == 6:
        
        if (
            list(y_sorted_points.keys())[-1] == "wrist"
            and points["index"].x !=  points["middle"].x !=  points["ring"].x !=  points["pinky"].x
            and (points["index"].x < points["thumb"].x < points["pinky"].x) or (points["index"].x > points["thumb"].x > points["pinky"].x)
            and abs(points["pinky"].y - points["thumb"].y) > 2
            and abs(points["pinky"].x - points["thumb"].x) > 2
        ):
            return True
    return False

def three_gesture(points):
    x_sorted_points = dict(sorted(points.items(), key=lambda item: item[1].x))    
    y_sorted_points = dict(sorted(points.items(), key=lambda item: item[1].y))
    
    mid_fingers = points.copy()
    mid_fingers.pop("middle")
    mid_fingers.pop("index")
    mid_fingers.pop("ring")
    mid_fingers.pop("wrist")
    
    x_sorted_mid_fingers = dict(sorted(mid_fingers.items(), key=lambda item: item[1].x))
    x_sorted_mid_fingers_list = list(x_sorted_mid_fingers.items())    
    
    y_sorted_mid_fingers = dict(sorted(mid_fingers.items(), key=lambda item: item[1].y))
    y_sorted_mid_fingers_list = list(y_sorted_mid_fingers.items())
     
    if len(points) == 6:        
        if (
            list(y_sorted_points.keys())[-1] == "wrist"
            and list(y_sorted_points.keys())[0] == "middle"
            and (list(y_sorted_points.keys())[1] == "ring" or list(y_sorted_points.keys())[1] == "index")
            and (list(y_sorted_points.keys())[2] == "ring" or list(y_sorted_points.keys())[2] == "index")
            and points["index"].x !=  points["middle"].x !=  points["ring"].x
            and ((points["index"].x < x_sorted_mid_fingers_list[0][1].x <= points["ring"].x) or (points["index"].x > x_sorted_mid_fingers_list[0][1].x >= points["ring"].x))
            and ((points["index"].x < x_sorted_mid_fingers_list[-1][1].x <= points["ring"].x) or (points["index"].x > x_sorted_mid_fingers_list[-1][1].x >= points["ring"].x))
        ):
            return True
    return False

def measure_gesture(points):
    x_sorted_points = dict(sorted(points.items(), key=lambda item: item[1].x))    
    y_sorted_points = dict(sorted(points.items(), key=lambda item: item[1].y))
    
    mid_fingers = points.copy()
    mid_fingers.pop("thumb")
    mid_fingers.pop("index")
    mid_fingers.pop("wrist")
    
    x_sorted_mid_fingers = dict(sorted(mid_fingers.items(), key=lambda item: item[1].x))
    x_sorted_mid_fingers_list = list(x_sorted_mid_fingers.items())    
    
    y_sorted_mid_fingers = dict(sorted(mid_fingers.items(), key=lambda item: item[1].y))
    y_sorted_mid_fingers_list = list(y_sorted_mid_fingers.items())
     
    if len(points) == 6:        
        if (
            points["thumb"].x == points["index"].x
            and abs(x_sorted_mid_fingers_list[0][1].x - x_sorted_mid_fingers_list[-1][1].x) < 2
            and abs(y_sorted_mid_fingers_list[0][1].y - y_sorted_mid_fingers_list[-1][1].y) < 2
        ):
            return True
    return False

#endregion



#place and config header
#region header

def place_header():    
    global header_rectangle, header_logo_text_picture, header_logo_hand_picture
    
    header_rectangle = all_canvas.create_rectangle(
        0.0,
        0.0,
        1280.0,
        73.0,
        fill=bg_dark_blue,
        outline="")
    header_logo_text_picture = all_canvas.create_image(
        640.0,
        36.0,
        image=header_logo_text_image
    )
    header_logo_hand_picture = all_canvas.create_image(
        33.0,
        36.0,
        image=header_logo_hand_image
    )

    
    header_profile_button.place(
        x=1144.0,
        y=17.0,
        width=130.0,
        height=39.0
    )
    
def clear_header():
    global header_menu_shown
    header_profile_button.place_forget()
    
    all_canvas.delete(header_rectangle)
    all_canvas.delete(header_logo_text_picture)
    all_canvas.delete(header_logo_hand_picture)
    header_menu_shown = False
            
def header_menu_hide_show():
    global header_menu_shown    
    if header_menu_shown == False:
        place_header_menu()
    else:
        clear_header_menu()
     
def place_header_menu():
    global header_menu_bg, header_menu_shown      
    header_menu_bg = all_canvas.create_rectangle(
        1119.0,
        73.0,
        1280.0,
        130.0,
        fill=bg_dark_blue,
        outline="")
    header_menu_info_button.place(
        x=1129.0,
        y=72.0,
        width=119.0,
        height=25.0
    )
    header_menu_logout_button.place(
        x=1129.0,
        y=100.0,
        width=119.0,
        height=25.0
    )
    header_menu_shown = True

def clear_header_menu():
    global header_menu_shown
    
    all_canvas.delete(header_menu_bg)    
    header_menu_info_button.place_forget()
    header_menu_logout_button.place_forget()
    header_menu_shown = False

#endregion

#set menu for configuring profiles for the game
#region settings
def place_profile_info():
    global active_page, settings_canvas_left
    active_page = "Profile Info"
    swich_hand_to_left()
    
    settings_canvas_left.create_window(250, 550, anchor=W,window=settings_frame_left)
    settings_canvas_right.create_window(250, 550, anchor=W,window=settings_frame_right)
    
    settings_label_profile.place(x=680, y= 660)
    settings_label_profile_selection.place(x=750, y=660)
    settings_button_profile_reload.place(x=990, y=660)
    settings_button_profile_new.place(x=1055, y=660)
    settings_back_button.place(
        x=2.0,
        y=81.0,
        width=85.0,
        height=24.0
    )
    
    
    # Grid placement
    settings_label_left_1.grid(row=0, column=0, sticky='w', pady=15)
    settings_label_left_2.grid(row=1, column=0, sticky='w')
    settings_label_left_3.grid(row=2, column=0, sticky='w', pady=15)
    settings_label_left_4.grid(row=3, column=0, sticky='w')
    settings_label_left_5.grid(row=4, column=0, sticky='w', pady=15)
    settings_label_left_6.grid(row=5, column=0, sticky='w')
    settings_label_left_7.grid(row=6, column=0, sticky='w', pady=15)
    settings_label_left_8.grid(row=7, column=0, sticky='w')
    settings_label_left_9.grid(row=8, column=0, sticky='w', pady=15)
    settings_label_left_10.grid(row=9, column=0, sticky='w')
    settings_label_left_11.grid(row=10, column=0, sticky='w', pady=15)
    settings_label_left_12.grid(row=11, column=0, sticky='w')
    settings_label_left_13.grid(row=12, column=0, sticky='w', pady=15)
    settings_label_left_14.grid(row=13, column=0, sticky='w')
    settings_label_left_15.grid(row=14, column=0, sticky='w', pady=15)
    
    
    # Grid placement
    settings_combo_box_left_1.grid(row=0, column=1, sticky="e")
    settings_combo_box_left_2.grid(row=1, column=1, sticky="e")
    settings_combo_box_left_3.grid(row=2, column=1, sticky="e")
    settings_combo_box_left_4.grid(row=3, column=1, sticky="e")
    settings_combo_box_left_5.grid(row=4, column=1, sticky="e")
    settings_combo_box_left_6.grid(row=5, column=1, sticky="e")
    settings_combo_box_left_7.grid(row=6, column=1, sticky="e")
    settings_combo_box_left_8.grid(row=7, column=1, sticky="e")
    settings_combo_box_left_9.grid(row=8, column=1, sticky="e")
    settings_combo_box_left_10.grid(row=9, column=1, sticky="e")
    settings_combo_box_left_11.grid(row=10, column=1, sticky="e")
    settings_combo_box_left_12.grid(row=11, column=1, sticky="e")
    settings_combo_box_left_13.grid(row=12, column=1, sticky="e")
    settings_combo_box_left_14.grid(row=13, column=1, sticky="e")
    settings_combo_box_left_15.grid(row=14, column=1, sticky="e")
    
    # Grid placement
    settings_label_right_1.grid(row=0, column=0, sticky='w', pady=15)
    settings_label_right_2.grid(row=1, column=0, sticky='w')
    settings_label_right_3.grid(row=2, column=0, sticky='w', pady=15)
    settings_label_right_4.grid(row=3, column=0, sticky='w')
    settings_label_right_5.grid(row=4, column=0, sticky='w', pady=15)
    settings_label_right_6.grid(row=5, column=0, sticky='w')
    settings_label_right_7.grid(row=6, column=0, sticky='w', pady=15)
    settings_label_right_8.grid(row=7, column=0, sticky='w')
    settings_label_right_9.grid(row=8, column=0, sticky='w', pady=15)
    settings_label_right_10.grid(row=9, column=0, sticky='w')
    settings_label_right_11.grid(row=10, column=0, sticky='w', pady=15)
    settings_label_right_12.grid(row=11, column=0, sticky='w')
    settings_label_right_13.grid(row=12, column=0, sticky='w', pady=15)
    settings_label_right_14.grid(row=13, column=0, sticky='w')
    settings_label_right_15.grid(row=14, column=0, sticky='w', pady=15)
    

    # Grid placement
    settings_combo_box_right_1.grid(row=0, column=1, sticky="e")
    settings_combo_box_right_2.grid(row=1, column=1, sticky="e")
    settings_combo_box_right_3.grid(row=2, column=1, sticky="e")
    settings_combo_box_right_4.grid(row=3, column=1, sticky="e")
    settings_combo_box_right_5.grid(row=4, column=1, sticky="e")
    settings_combo_box_right_6.grid(row=5, column=1, sticky="e")
    settings_combo_box_right_7.grid(row=6, column=1, sticky="e")
    settings_combo_box_right_8.grid(row=7, column=1, sticky="e")
    settings_combo_box_right_9.grid(row=8, column=1, sticky="e")
    settings_combo_box_right_10.grid(row=9, column=1, sticky="e")
    settings_combo_box_right_11.grid(row=10, column=1, sticky="e")
    settings_combo_box_right_12.grid(row=11, column=1, sticky="e")
    settings_combo_box_right_13.grid(row=12, column=1, sticky="e")
    settings_combo_box_right_14.grid(row=13, column=1, sticky="e")
    settings_combo_box_right_15.grid(row=14, column=1, sticky="e")
        
    
    load_insert()


    settings_button_reset.place(x=659.0, y=608.0, width=142.52322387695312, height=39.0)
    settings_button_save.place(x=391.0, y=605.0, width=229.6397705078125, height=48.0)
 
def load_insert():
    global profiles_path
    try:
        file = open(profiles_path+settings_label_profile_selection.get(),"r")    
        data =json.loads(file.read())
        file = open(main_path+"settings.json","r")
        configuration = json.loads(file.read())
        configuration["profile_for_edit"] = settings_label_profile_selection.get()
        with open(main_path+"settings.json","w") as settings:
            json.dump(configuration, settings)
            settings.close()
        
        
            
        insert_settings(data)
        place_message("Profile Loaded") 
    except:
        place_message("Select a Profile") 
        
def reset_settings():
    profile = open(main_path+"settings.json","r")
    profile_name = json.loads(profile.read())["profile_for_edit"]
    settings = open(profiles_path+profile_name,"r")
    data = json.loads(settings.read())
    
    
    insert_settings(data)
    place_message("Data Reset") 
    

def save_profile():
    data = read_settings()
    file = open(main_path+"settings.json","r")
    profile = json.loads(file.read())["profile_for_edit"]
    with open(profiles_path+profile,"w") as old_profile:
            json.dump(data, old_profile)
            old_profile.close()
    place_message("Profile Saved") 
    
           
def load_base():
    settings = open(main_path + "settings.json","r")    
    data = json.loads(settings.read())
    profile = data["current_profile"]
    file = open(profiles_path+profile,"r")    
    data =json.loads(file.read())
    settings_label_profile_selection.set(profile)
    insert_settings(data)
    
  
def insert_settings(data):
    left = data["left"]
    right = data["right"]
    
    settings_combo_box_left_1.set(left["fist_gesture"])
    settings_combo_box_left_2.set(left["flat_hand_gesture_thumb_close"])
    settings_combo_box_left_3.set(left["flat_hand_gesture_thumb_stretched"])
    settings_combo_box_left_4.set(left["four_gesture"])
    settings_combo_box_left_5.set(left["index_gesture"])
    settings_combo_box_left_6.set(left["l_gesture"])
    settings_combo_box_left_7.set(left["measure_gesture"])
    settings_combo_box_left_8.set(left["middlefeinger_gesture"])
    settings_combo_box_left_9.set(left["peace_close_gesture"])
    settings_combo_box_left_10.set(left["peace_gesture"])
    settings_combo_box_left_11.set(left["pinky_gesture"])
    settings_combo_box_left_12.set(left["ring_gesture"])
    settings_combo_box_left_13.set(left["three_gesture"])
    settings_combo_box_left_14.set(left["thumb_index_middle_gesture"])
    settings_combo_box_left_15.set(left["thumbs_up_gesture"])
       
    
    settings_combo_box_right_1.set(right["fist_gesture"])
    settings_combo_box_right_2.set(right["flat_hand_gesture_thumb_close"])
    settings_combo_box_right_3.set(right["flat_hand_gesture_thumb_stretched"])
    settings_combo_box_right_4.set(right["four_gesture"])
    settings_combo_box_right_5.set(right["index_gesture"])
    settings_combo_box_right_6.set(right["l_gesture"])
    settings_combo_box_right_7.set(right["measure_gesture"])
    settings_combo_box_right_8.set(right["middlefeinger_gesture"])
    settings_combo_box_right_9.set(right["peace_close_gesture"])
    settings_combo_box_right_10.set(right["peace_gesture"])
    settings_combo_box_right_11.set(right["pinky_gesture"])
    settings_combo_box_right_12.set(right["ring_gesture"])
    settings_combo_box_right_13.set(right["three_gesture"])
    settings_combo_box_right_14.set(right["thumb_index_middle_gesture"])
    settings_combo_box_right_15.set(right["thumbs_up_gesture"])
    


def read_settings():
    data = {"left":{
        "fist_gesture":settings_combo_box_left_1.get(),
        "flat_hand_gesture_thumb_close":settings_combo_box_left_2.get(),
        "flat_hand_gesture_thumb_stretched":settings_combo_box_left_3.get(),
        "four_gesture":settings_combo_box_left_4.get(),
        "index_gesture":settings_combo_box_left_5.get(),
        "l_gesture":settings_combo_box_left_6.get(),
        "measure_gesture":settings_combo_box_left_7.get(),
        "middlefeinger_gesture":settings_combo_box_left_8.get(),
        "peace_close_gesture":settings_combo_box_left_9.get(),
        "peace_gesture":settings_combo_box_left_10.get(),
        "pinky_gesture":settings_combo_box_left_11.get(),
        "ring_gesture":settings_combo_box_left_12.get(),
        "three_gesture":settings_combo_box_left_13.get(),
        "thumb_index_middle_gesture":settings_combo_box_left_14.get(),
        "thumbs_up_gesture":settings_combo_box_left_15.get()
    
    },
    "right":{
        "fist_gesture":settings_combo_box_right_1.get(),
        "flat_hand_gesture_thumb_close":settings_combo_box_right_2.get(),
        "flat_hand_gesture_thumb_stretched":settings_combo_box_right_3.get(),
        "four_gesture":settings_combo_box_right_4.get(),
        "index_gesture":settings_combo_box_right_5.get(),
        "l_gesture":settings_combo_box_right_6.get(),
        "measure_gesture":settings_combo_box_right_7.get(),
        "middlefeinger_gesture":settings_combo_box_right_8.get(),
        "peace_close_gesture":settings_combo_box_right_9.get(),
        "peace_gesture":settings_combo_box_right_10.get(),
        "pinky_gesture":settings_combo_box_right_11.get(),
        "ring_gesture":settings_combo_box_right_12.get(),
        "three_gesture":settings_combo_box_right_13.get(),
        "thumb_index_middle_gesture":settings_combo_box_right_14.get(),
        "thumbs_up_gesture":settings_combo_box_right_15.get()
    
    }
    }
    return data

 
def swich_hand_to_left():
    global current_hand
    all_left = [settings_button_left_not,settings_button_right_selected,settings_frame_right,settings_canvas_right,settings_vbar_right]
    for element in all_left:
        element.place_forget()
    
    settings_canvas_left.place(x=0, y=130, width=1280, height=460)    
    settings_vbar_left.place(x=1260, y=130, height=460, width=30, anchor=N)
    
    settings_button_left_selected.place(
        x=337.0,
        y=85.0,
        width=229.6397705078125,
        height=43.0
    )
    settings_button_right_not.place(
        x=713.0,
        y=85.0,
        width=229.6397705078125,
        height=43.0
        )
    
def swich_hand_to_right():
    global current_hand
    all_right = [settings_button_left_selected,settings_button_right_not,settings_vbar_left,settings_canvas_left,settings_frame_left,]
    for element in all_right:
        element.place_forget()
   
    settings_canvas_right.place(x=0, y=130, width=1280, height=460)    
    settings_vbar_right.place(x=1260, y=130, height=460, width=30, anchor=N)
    
    settings_button_left_not.place(
        x=337.0,
        y=85.0,
        width=229.6397705078125,
        height=43.0
    )
    settings_button_right_selected.place(
        x=713.0,
        y=85.0,
        width=229.6397705078125,
        height=43.0
    )
    
def get_json_files():
    global profiles_path
    json_files = []
    for file_name in os.listdir(profiles_path):
        if file_name.endswith(".json"):
            json_files.append(file_name)
    #print(json_files) 
    return json_files

#set window for creating a new profile for the game 
def create_new_window_profile():
    global empty_content
    new_window = Toplevel(window)
    new_window.title("New Window")
    new_window.geometry("300x200")

    # Input box
    input_label = Label(new_window, text="Profile Name:")
    input_label.place(x=20, y=20)
    input_entry = Entry(new_window)
    input_entry.place(x=100, y=20)

    # Checkboxes
    checkbox_var1 = BooleanVar()
    checkbox_var2 = BooleanVar()
    checkbox1 = Checkbutton(new_window, text="Load Data instantly", variable=checkbox_var1)
    checkbox1.place(x=20, y=60)
    checkbox2 = Checkbutton(new_window, text="Select Profile", variable=checkbox_var2)
    checkbox2.place(x=20, y=80)

    def close_window():
        input_entry_content = input_entry.get()
        if not f"{input_entry_content}.json" in get_json_files() and input_entry_content != "":
            try:
                
                path = profiles_path + input_entry_content+ ".json"
                
                with open(path, "w") as json_file:
                    json.dump(empty_content, json_file)
                place_message("Profile Created") 
            except:
                place_message("Profile Creation Error") 
            if checkbox_var1.get():
                #load data
                file = open(main_path+"settings.json","r")
                configuration = json.loads(file.read())
                configuration["profile_for_edit"] = input_entry_content
                with open(main_path+"settings.json","w") as settings:
                    json.dump(configuration, settings)
                    settings.close()
                insert_settings(empty_content)
                settings_label_profile_selection.set(input_entry_content+".json")
                pass
            if checkbox_var2.get():
                file = open(main_path+"settings.json","r")
                configuration = json.loads(file.read())
                configuration["current_profile"] = input_entry_content+".json"
                with open(main_path+"settings.json","w") as settings:
                    json.dump(configuration, settings)
                    settings.close()
                game_menu_label_profile_selection.set(input_entry_content+".json")
            
            new_window.destroy()
        else:
            place_message("Profile Creation Error") 
        

    # Close button
    close_button = Button(new_window, text="Close Window", command=close_window)
    close_button.place(x=100, y=120)

def on_combobox_select(event):
    profile_list = get_json_files()
    #print(profile_list)
    settings_label_profile_selection.config(values=profile_list)
    game_menu_label_profile_selection.config(values=profile_list)
    
 
def on_mousewheel_left(event):
    settings_canvas_left.yview_scroll(int(-1*(event.delta/120)), "units")
    
def on_mousewheel_right(event):
    settings_canvas_right.yview_scroll(int(-1*(event.delta/120)), "units")
    
def disable_mouse_scroll(event):
    # Prevent the event from propagating further
    return "break"


    

def clear_profile_info():
    #global list_profile_info_combo_box_left, list_profile_info_combo_box_right, list_profile_info_label_left, list_profile_info_label_right
    list_profile_info_all_combo_box_label = list_settings_combo_box_left+list_settings_combo_box_right+list_settings_label_left+list_settings_label_right
    for element in list_profile_info_all_combo_box_label:
        element.grid_forget()
        
    list_profile_info_all_other = [settings_button_save,settings_button_reset,settings_canvas_left,settings_vbar_left,settings_canvas_right,settings_vbar_right,settings_button_right_selected,settings_button_left_selected,settings_button_left_not,settings_button_right_not,settings_back_button,settings_label_profile,settings_label_profile_selection,settings_button_profile_reload,settings_button_profile_new]
    
    for element in list_profile_info_all_other:
        element.place_forget()

def open_profile_info():
    clear_active_page()
    place_profile_info()

def back_from_profile_info():
    clear_profile_info()    
    main_page_place_all()

#endregion

#create start menu and read all possible cameras
#region login

def login_page_place_all():
    global login_page_rec_white,login_page_rec_blue,login_page_logo, active_page
    
    active_page = "Login"
    
    login_page_rec_white = all_canvas.create_rectangle(
        640.0,
        0.0,
        1280.0,
        720.0,
        fill=bg_white,
        outline="")

    login_page_rec_blue = all_canvas.create_rectangle(
        0.0,
        0.0,
        640.0,
        720.0,
        fill=bg_dark_blue,
        outline="")
    
    login_page_logo = all_canvas.create_image(
        320.0,
        360.0,
        image=login_page_logo_image
    )
    login_page_login_button.place(
        x=850.0,
        y=342.0,
        width=229.6397705078125,
        height=45.0
    )
    login_page_browser_button.place(
        x=1120.0,
        y=670.0,
        width=130.0,
        height=30.0
    )
    
    login_page_camera_selection.place(
        x=827,
        y=444,
        width=265,
        height=27
    )
    login_page_camera_selection.config(state="readonly")
    login_page_camera_selection.set("*Select Camera*")
    
    
def clear_login_page():
    login_page_login_button.place_forget()
    login_page_browser_button.place_forget()
    login_page_camera_selection.place_forget()
    
    for element in [login_page_rec_white,login_page_rec_blue,login_page_logo]:
        all_canvas.delete(element)
    
def login():
    global cap
    selected_cam = login_page_camera_selection.get()
    if selected_cam != "*Select Camera*":
    
        clear_active_page()  
        place_header()  
        main_page_place_all()
        
        
        cap = cv2.VideoCapture(camera_index_name_map[selected_cam])

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640 * 1)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480 * 1)
    else:
        place_message("Select a Cam")
 
def viste_website():
    webbrowser.open("http://swp.franjoli-productions.de")
    
def list_active_cameras(max_cameras=10):
    active_cameras = []
    
    for index in range(max_cameras):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            active_cameras.append(index)
            cap.release()  # Don't forget to release the camera
        else:
            cap.release()  # Make sure to release even if not opened
    
    return active_cameras

def get_camera_names():
    # Connect to WMI
    wmi = win32com.client.GetObject("winmgmts:")
    cameras = wmi.InstancesOf("Win32_PnPEntity")
    camera_names = []
    
    for camera in cameras:
        if camera.Name is not None:  # Check if Name attribute exists
            if "camera" in camera.Name.lower() or "video" in camera.Name.lower():
                camera_names.append(camera.Name)
    
    return camera_names

def match_cameras_with_names(active_indices, camera_names):
    
    index_name_map = {}
    
    for index in active_indices:
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            # Attempt to read a property to uniquely identify the camera
            ret, frame = cap.read()
            if ret:
                cap.release()
                
                for name in camera_names:
                    index_name_map[name]=index
                    camera_names.remove(name)
                    break
    
    return index_name_map

def get_all_cams():
    global camera_index_name_map
    active_cameras = list_active_cameras()
    camera_names = get_camera_names()
    camera_index_name_map = match_cameras_with_names(active_cameras, camera_names)
    
    
    return list(camera_index_name_map.keys())
    
#endregion

#make homepage 
#region main page


def main_page_place_all():
    global main_page_image_screen, active_page,main_page_feedback_button
    
    active_page = "Main"
    
    main_page_image_screen = all_canvas.create_image(644.0, 252.0, image=main_page_screen_image)
    main_page_info_label.place(x=270.0, y=417.0)
    main_page_desktop_button.place(
        x=33.0,
        y=275.0,
        width=320.0,
        height=52.0
    )
    main_page_games_button.place(
        x=935.0,
        y=275.0,
        width=320.0,
        height=52.0
    )
    main_page_feedback_button.place(
        x=1120.0,
        y=670.0,
        width=130.0,
        height=30.0
    )
    
def clear_main_page():
    for element in [main_page_info_label,main_page_desktop_button,main_page_games_button,main_page_feedback_button]:
        element.place_forget()
    
    all_canvas.delete(main_page_image_screen)

def play_games():
    clear_main_page()    
    game_menu_place_all()

def open_desktop_control_page():
    clear_active_page()
    place_desktop_control()

#endregion


#region game menu

def toggle_camera_game():
    global camera_feed_visible, running
    camera_feed_visible = not camera_feed_visible
    if camera_feed_visible:
        start_camera_game()
    else:
        stop_camera_game()
    
def start_camera_game():
    global running
    running = True
    
    
    desktop_control_camera_label.config(width=497, height=266)
    desktop_control_camera_label.place(x=392, y=202)
    show_camera()
    
def stop_camera_game():
    running = False
    desktop_control_camera_label.place_forget()  

def game_menu_place_all():
    global game_menu_game_1_picture,game_menu_game_3_picture, active_page
    
    active_page = "Game Menu"
    
    start_camera_game()
    
    game_menu_game_1_picture = all_canvas.create_image(
        216.0,
        335.0,
        image=game_menu_game_1_image
    )
   
    game_menu_game_3_picture = all_canvas.create_image(
        1064.0,
        335.0,
        image=game_menu_game_3_image
    )
    
    game_menu_game_1_button.place(
        x=56.0,
        y=559.0,
        width=320.0,
        height=52.0
    )
   
    game_menu_game_3_button.place(
        x=904.0,
        y=559.0,
        width=320.0,
        height=52.0
    )

    game_menu_switch_1_button.place(
        x=169.0,
        y=622.0,
        width=94.0,
        height=27.0
    )
   
    game_menu_switch_3_button.place(
        x=1024.0,
        y=622.0,
        width=94.0,
        height=27.0
    )

    game_menu_back_button.place(
        x=2.0,
        y=81.0,
        width=85.0,
        height=24.0
    )
    game_menu_label_profile.place(x=680, y= 660)
    game_menu_label_profile_selection.place(x=750, y=660)
    game_menu_label_profile_selection.bind("<Enter>", on_combobox_select)
    game_menu_button_profile_reload.place(x=990, y=660)
    

def show_camera():
    global gesture_name, previos_time, refresh_time, start_time, gesture_left, points_accurate_left,points_accurate_right,gesture_right, running, gesture_left_info, gesture_right_info, left_action, right_action, right, left, w_pressed, a_pressed, s_pressed, d_pressed, movement_point_right, movement_point_left
    
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    
    #import relations
    file_settings = open(main_path+"settings.json","r")    
    profile_name =json.loads(file_settings.read())["current_profile"]
    file_profile = open(profiles_path+profile_name,"r")    
    configuration =json.loads(file_profile.read())

    left = configuration["left"]
    left[""] = "None"
    right = configuration["right"]
    right[""] = "None"
    

    if running:
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)

            # Check if hands are detected
            if results.multi_hand_landmarks:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                    ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
                    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
                    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                    points = {
                       "thumb": thumb_tip,
                       "index": index_tip,
                        "middle": middle_tip,
                        "ring": ring_tip,
                        "pinky": pinky_tip,
                        "wrist": wrist
                    }
                    if handedness.classification[0].label == 'Left':
                        
                        points_accurate_left = copy.deepcopy(points)
                        for count, point in enumerate(points.items()):
                            point_x, points_y = int(point[1].x * frame.shape[1]), int(
                                point[1].y * frame.shape[0]
                            )
                            cv2.circle(frame, (point_x, points_y), 5, (0, 0, 255), -1)

                        for key in points.keys():
                            points[key].x = int(round(points[key].x * resolution_gesture, 0))
                            points[key].y = int(round(points[key].y * resolution_gesture, 0))
                        
                        for key in points_accurate_left.keys():
                            points_accurate_left[key].x = points_accurate_left[key].x * 100
                            points_accurate_left[key].y = points_accurate_left[key].y * 100
                        
                        gesture_left = gesture_check(points)
                        
                        left_action = left[gesture_left]
                            
                        gesture_left_info = {"gesture":gesture_left,"action":left_action}
                        point_info = {
                           "thumb": (thumb_tip.x, thumb_tip.y ),
                           "index": (index_tip.x, index_tip.y ),
                            "middle": (middle_tip.x, middle_tip.y),
                            "ring": (ring_tip.x, ring_tip.y),
                            "pinky": (pinky_tip.x, pinky_tip.y),
                            "wrist": (wrist.x, wrist.y)
                        }
                        gesture_left_info.update(point_info)
                        
                        movement_action = gesture_left_info["action"]
                        if movement_action == "turn_cam":
                            movement_point_left = (points_accurate_right["index"].x,points_accurate_right["index"].y,)

                    if handedness.classification[0].label == 'Right':
                        thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                        index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                        middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                        ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
                        pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
                        wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                        
                        points = {
                            "thumb": thumb_tip,
                            "index": index_tip,
                            "middle": middle_tip,
                            "ring": ring_tip,
                            "pinky": pinky_tip,
                            "wrist": wrist
                        }
                        
                        points_accurate_right = copy.deepcopy(points)                        

                        for count, point in enumerate(points.items()):
                            point_x, points_y = int(point[1].x * frame.shape[1]), int(
                               point[1].y * frame.shape[0]
                            )
                            cv2.circle(frame, (point_x, points_y), 5, (0, 0, 255), -1)

                        for key in points.keys():
                            points[key].x = int(round(points[key].x * resolution_gesture, 0))
                            points[key].y = int(round(points[key].y * resolution_gesture, 0))
                        
                        
                        for key in points_accurate_right.keys():
                            points_accurate_right[key].x = points_accurate_right[key].x * 100
                            points_accurate_right[key].y = points_accurate_right[key].y * 100
                            
                        gesture_right = gesture_check(points)     
                        right_action = right[gesture_right]
                        
                        gesture_right_info = {"gesture":gesture_right,"action":right_action}
                        
                        point_info = {
                           "thumb": (thumb_tip.x, thumb_tip.y ),
                           "index": (index_tip.x, index_tip.y ),
                            "middle": (middle_tip.x, middle_tip.y),
                            "ring": (ring_tip.x, ring_tip.y),
                            "pinky": (pinky_tip.x, pinky_tip.y),
                            "wrist": (wrist.x, wrist.y)
                        }
                        
                        gesture_right_info.update(point_info)
                        movement_action = gesture_right_info["action"]
                        if movement_action == "turn_cam":
                            movement_point_right = (points_accurate_right["index"].x,points_accurate_right["index"].y,)
                
                    if is_game_focused():
                        do_action_all()
                    else:
                        pag.mouseUp(button='right')
                        if w_pressed:
                            keyboard.release("W")
                            w_pressed = False
                        if a_pressed:                            
                            keyboard.release("A")
                            a_pressed = False
                        if d_pressed:
                            keyboard.release("d")
                            d_pressed = False
                        if s_pressed:
                            keyboard.release("S")
                            s_pressed = False
                                 
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            draw_left = ImageDraw.Draw(img)
            draw_left.text((20, 50), gesture_left, font=font, fill=(255, 255, 255))
            draw_left_action = ImageDraw.Draw(img)
            draw_left_action.text((20, 100), left_action, font=font, fill=(255, 255, 255))
            draw_right = ImageDraw.Draw(img)
            draw_right.text((400, 50), gesture_right, font=font, fill=(255, 255, 255))
            draw_right_action = ImageDraw.Draw(img)
            draw_right_action.text((400, 100), right_action, font=font, fill=(255, 255, 255))
            imgtk = ImageTk.PhotoImage(image=img)
            desktop_control_camera_label.imgtk = imgtk         #type: ignore
            desktop_control_camera_label.configure(image=imgtk)
            
        
        window.after(5, show_camera)


        
def turning(hand, coords_normal):
    if thread_running:
        time.sleep(0.2)
        if thread_running:
            x_normal = coords_normal.x
            y_normal = coords_normal.y

            if hand == "left":

                x_after = movement_point_left[0]
                y_after = movement_point_left[1]
            elif hand == "right":

                x_after = movement_point_right[0]
                y_after = movement_point_right[1]                
                
            multiplicator = 10 * -1
            move_x = (x_normal-x_after) * multiplicator 
            move_y = (y_normal-y_after) * multiplicator
            
            move(move_x, move_y, 10, 0.05)

def do_action_all():
    global gesture_right, gesture_left, w_pressed, a_pressed, s_pressed, d_pressed, thread_running
    try:        
        right_gesture = gesture_right_info["action"]
    except:
        right_gesture = ""
    try:
        left_gesture = gesture_left_info["action"]
    except:
        left_gesture = ""
    
    if (right_gesture == "walk_forward") or (left_gesture == "walk_forward"):
        keyboard.press("W")
        w_pressed = True
    elif w_pressed:
        keyboard.release("W")
        w_pressed = False
    if (right_gesture == "walk_left") or (left_gesture == "walk_left"):
        keyboard.press("A")
        a_pressed = True
    elif a_pressed:
        keyboard.release("A")
        a_pressed = False
    if (right_gesture == "walk_right") or (left_gesture == "walk_right"):
        keyboard.press("d")
        d_pressed = True
    elif d_pressed:
        keyboard.release("d")
        d_pressed = False
    if (right_gesture == "walk_back") or (left_gesture == "walk_back"):
        keyboard.press("S")
        s_pressed = True
    elif s_pressed:
        keyboard.release("S")
        s_pressed = False        
    if (right_gesture == "turn_cam") or (left_gesture == "turn_cam"):
        if (right_gesture == "turn_cam"):
            thread_running = True
            pag.mouseDown(button='right')            
            right_thread = threading.Thread(target=turning, args=("right",points_accurate_right["index"]))
            right_thread.start()
        elif (left_gesture == "turn_cam"):
            thread_running = True
            pag.mouseDown(button='right')
            left_thread = threading.Thread(target=turning, args=("left",points_accurate_left["index"]))
            left_thread.start()
    else:
        thread_running = False        
        pag.mouseUp(button='right')
    if (right_gesture == "attack_normal") or (left_gesture == "attack_normal"):
        pag.click(button="left")
    if (right_gesture == "interact") or (left_gesture == "interact"):
        keyboard.press_and_release("E")
    if (right_gesture == "stun") or (left_gesture == "stun"):
        keyboard.press_and_release("F")
    if (right_gesture == "finisher") or (left_gesture == "finisher"):
        keyboard.press_and_release("G")
    if (right_gesture == "attack_ulti") or (left_gesture == "attack_ulti"):
        keyboard.press_and_release("U")
        



def move(x, y, steps, duration):
    global main_thread, thread_running
    
    each_x = x / steps
    each_y = y / steps
    each_time = duration / steps
    
    for i in range(steps):
        if thread_running:
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(each_x), int(each_y), 0, 0)
            time.sleep(each_time)            
        else:
            break
    
   

def is_game_focused():
    active_window_title = win32gui.GetWindowText(win32gui.GetForegroundWindow())
    return active_window_title == "Break2Gesture"

      
def clear_game_menu():
    stop_camera_game()
    
    list_game_menu = [game_menu_button_profile_reload,game_menu_label_profile_selection,game_menu_label_profile,game_menu_game_1_button,game_menu_game_3_button,game_menu_switch_1_button,game_menu_switch_3_button,game_menu_back_button]#,game_menu_switch_2_button,game_menu_game_2_button
    for element in list_game_menu:
        element.place_forget()
    
    list_game_menu_canvas = [game_menu_game_1_picture,game_menu_game_3_picture]
    for element in list_game_menu_canvas:
        all_canvas.delete(element)
        
def set_base_profile():
    profile = open(main_path+"settings.json","r")
    profile_name = json.loads(profile.read())["current_profile"]
    game_menu_label_profile_selection.set(profile_name)
    
def switch_profile():
    file = open(main_path+"settings.json","r")    
    configuration =json.loads(file.read())
    configuration["current_profile"] = game_menu_label_profile_selection.get()
    with open(main_path+"settings.json","w") as settings:
        json.dump(configuration, settings)
        settings.close()
    place_message("Profile Switched") 
    
    
    
def back_from_game_page():
    clear_active_page()    
    main_page_place_all()

#endregion


#region feedback


def place_feedback_menu():
    global feedback_image_header,feedback_image_text, active_page, feedback_image_email, feedback_image_password
    
    active_page = "Feedback Menu"
    
    feedback_button_send.place(
        x=522.0,
        y=639.0,
        width=229.6397705078125,
        height=45.0)
    
    
    feedback_button_back_button.place(
        x=2.0,
        y=81.0,
        width=85.0,
        height=24.0
    )

    
    feedback_image_header = all_canvas.create_image(
        639.0,
        136.0,
        image=feedback_image_image_header
        )
    feedback_image_text = all_canvas.create_image(
        639.0,
        356.0,
        image=feedback_image_image_text
        )
    feedback_image_email = all_canvas.create_image(
        480.0,
        578.0,
        image=feedback_image_image_email
        )
    feedback_image_password = all_canvas.create_image(
        797.0,
        578.0,
        image=feedback_image_image_password
        )
    
    feedback_text.place(x=327, y=190, width=625, height=332)
    feedback_headline.place(x=327, y=124, width=625, height=25)
    feedback_email.place(x=327, y=566, width=306, height=25)
    feedback_password.place(x=644, y=566, width=306, height=25)
    
def clear_feedback_menu():
    
    list_feedback_menu = [feedback_email,feedback_password,feedback_button_send,feedback_button_back_button,feedback_text,feedback_headline]
    for element in list_feedback_menu:
        element.place_forget()
    
    
    list_feedback_menu_canvas = [feedback_image_header,feedback_image_text,feedback_image_email,feedback_image_password]
    for element in list_feedback_menu_canvas:
        all_canvas.delete(element)


def open_feedback():
    clear_active_page()
    place_feedback_menu()
 
def back_from_feedback_menu():
    clear_active_page()
    main_page_place_all()
 
def send_feedback():
    try:
        heading = feedback_headline.get()
        content = feedback_text.get("1.0", "end-1c")
        sender = "username"
        time = asctime(gmtime())
        status = "unseen"
    
        print("Feedback submitted")
    except:
        print("Something went wrong")
    
    back_from_feedback_menu()




        
def feedback_text_on_entry_click(event):
    if feedback_text.get("1.0", "end-1c") == 'Enter Text here':
        feedback_text.delete("1.0", "end") 
        feedback_text.insert("1.0", '') 

def feedback_text_on_focusout(event):
    if feedback_text.get("1.0", "end-1c") == '':
        feedback_text.insert("1.0", 'Enter Text here')
        
def feedback_headline_on_entry_click(event):
    if feedback_headline.get() == 'Enter Headline here':
        feedback_headline.delete(0, "end")  
        feedback_headline.insert(0, '') 

def feedback_headline_on_focusout(event):
    if feedback_headline.get() == '':
        feedback_headline.insert(0, 'Enter Headline here')        
        
def feedback_email_on_entry_click(event):
    if feedback_email.get() == 'Enter Email here':
        feedback_email.delete(0, "end")  
        feedback_email.insert(0, '') 

def feedback_email_on_focus_out(event):
    if feedback_email.get() == '':
        feedback_email.insert(0, 'Enter Email here')
        
def feedback_password_on_entry_click(event):
    if feedback_password.get() == 'Enter Password here':
        feedback_password.config(show="●")
        feedback_password.delete(0, "end")  
        feedback_password.insert(0, '') 

def feedback_password_on_focus_out(event):
    if feedback_password.get() == '':
        feedback_password.config(show="")
        feedback_password.insert(0, 'Enter Password here')

#endregion


#region desktop


def place_desktop_control():
    global active_page, running,camera_feed_visible
    running = False
    
    active_page = "Desktop Control"
    camera_feed_visible = False
        
    desktop_control_camera_label.place(x=325, y=159)
    
    desktop_control_button_toggle.place(
        x=525.0,
        y=608.0,
        width=229.6397705078125,
        height=43.0,
    )
    desktop_control_button_back.place(
        x=1190.0,
        y=81.0,
        width=85.0,
        height=24.0
    )
    
    
def clear_desktop_control():
    stop_camera_feed()
    
    list_desktop_control = [game_menu_button_profile_reload,game_menu_label_profile_selection,game_menu_label_profile,desktop_control_camera_label,desktop_control_button_toggle,desktop_control_button_back,desktop_control_button_toggle]
    
    for element in list_desktop_control:
        element.place_forget()
        

        
def back_from_desktop_control():
    clear_active_page()
    main_page_place_all()

def show_camera_desktop():
    global gesture_name, previos_time, previous_gesture, refresh_time, start_time, gesture_left, gesture_right, running, gesture_left_info, gesture_right_info, left_action, right_action
    
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)

    if running:
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)

            # Check if hands are detected
            if results.multi_hand_landmarks:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                    if handedness.classification[0].label == 'Left':
                        thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                        index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                        middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                        ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
                        pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
                        wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]

                        points = {
                           "thumb": thumb_tip,
                           "index": index_tip,
                            "middle": middle_tip,
                            "ring": ring_tip,
                            "pinky": pinky_tip,
                            "wrist": wrist
                        }

                        for count, point in enumerate(points.items()):
                            point_x, points_y = int(point[1].x * frame.shape[1]), int(
                                point[1].y * frame.shape[0]
                            )
                            cv2.circle(frame, (point_x, points_y), 5, (0, 0, 255), -1)

                        for key in points.keys():
                            points[key].x = int(round(points[key].x * resolution_gesture, 0))
                            points[key].y = int(round(points[key].y * resolution_gesture, 0))
                        
                        gesture_left = gesture_check(points)
                        
                        gesture_left_info = {"gesture":gesture_left}
                        point_info = {
                           "thumb": (thumb_tip.x, thumb_tip.y ),
                           "index": (index_tip.x, index_tip.y ),
                            "middle": (middle_tip.x, middle_tip.y),
                            "ring": (ring_tip.x, ring_tip.y),
                            "pinky": (pinky_tip.x, pinky_tip.y),
                            "wrist": (wrist.x, wrist.y)
                        }
                        gesture_left_info.update(point_info)
                        
                        
                        convert_left_to_action()

                    if handedness.classification[0].label == 'Right':
                        thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                        index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                        middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                        ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
                        pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
                        wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]

                        points = {
                            "thumb": thumb_tip,
                            "index": index_tip,
                            "middle": middle_tip,
                            "ring": ring_tip,
                            "pinky": pinky_tip,
                            "wrist": wrist
                        }

                        for count, point in enumerate(points.items()):
                            point_x, points_y = int(point[1].x * frame.shape[1]), int(
                               point[1].y * frame.shape[0]
                            )
                            cv2.circle(frame, (point_x, points_y), 5, (0, 0, 255), -1)

                        for key in points.keys():
                            points[key].x = int(round(points[key].x * resolution_gesture, 0))
                            points[key].y = int(round(points[key].y * resolution_gesture, 0))

                        gesture_right = gesture_check(points)
                                                    
                        gesture_right_info = {"gesture":gesture_right}
                        point_info = {
                            "thumb": (thumb_tip.x, thumb_tip.y ),
                            "index": (index_tip.x, index_tip.y ),
                            "middle": (middle_tip.x, middle_tip.y),
                            "ring": (ring_tip.x, ring_tip.y),
                            "pinky": (pinky_tip.x, pinky_tip.y),
                            "wrist": (wrist.x, wrist.y)
                        }
                        gesture_right_info.update(point_info)
                        
                        
                        convert_right_to_action()
                        #print(gesture_right_info["index"])

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            draw_left = ImageDraw.Draw(img)
            draw_left.text((20, 50), gesture_left, font=font, fill=(255, 255, 255))
            draw_right = ImageDraw.Draw(img)
            draw_right.text((400, 50), gesture_right, font=font, fill=(255, 255, 255))
            imgtk = ImageTk.PhotoImage(image=img)
            desktop_control_camera_label.imgtk = imgtk         #type: ignore
            desktop_control_camera_label.configure(image=imgtk)

        previous_gesture = gesture_name

        window.after(10, show_camera_desktop)

        
def set_base_action():
    global gesture_right_info, gesture_left_info
    file_settings = open(main_path+"controls.json","r")
    gesture_left_info =json.loads(file_settings.read())
    
    gesture_right_info = gesture_left_info
    


def convert_left_to_action():
    file_settings = open(main_path+"controls.json","r")
    settings =json.loads(file_settings.read())
    left_control = settings["left"]
    temp_left = gesture_left_info["gesture"]
    command_left = left_control[temp_left]
    action_left(command_left)
    
def convert_right_to_action():
    file_settings = open(main_path+"controls.json","r")
    settings =json.loads(file_settings.read())
    right_control = settings["right"]
    temp_right = gesture_right_info["gesture"]
    command_right = right_control[temp_right]
    # print(f"\x1b[38;5;9m converting the action\033[0m")
    action_right(command_right)
    # print(f"\x1b[38;5;40m converting successful\033[0m")    
    
def action_left(command_left):
    if command_left == "click":
        pag.click(button = "left")
    
    global x_tmp_l, y_tmp_l
    
    if command_left == "drag":
        x = gesture_right_info["index"][0]
        # print(f"\x1b[38;5;33m x = {x}\033[0m")
        y = gesture_right_info["index"][1]
        # print(f"\x1b[38;5;33m y = {y}\033[0m")
        if x > x_tmp_l and y > y_tmp_l:
            pag.drag(-10, -10)
            x_tmp_l = x
            y_tmp_l = y
        elif x > x_tmp_l:
            pag.drag(10,-10)
            x_tmp_l = x
        elif y > y_tmp_l:
            pag.drag(-10,10)
            y_tmp_l = y
        elif x < x_tmp_l and y < y_tmp_l:
            pag.drag(10,10)
            x_tmp_l = x
            y_tmp_l = y
            
    if command_left == "Alt_F4":
        pag.hotkey("alt", "f4")
        
    return x_tmp_l, y_tmp_l
        

def action_right(command_right):
    global x_tmp_r, y_tmp_r
    if command_right == "click":
        pag.click(button = "right")
    if command_right == "move":
        x = gesture_right_info["index"][0]
        # print(f"\x1b[38;5;33m x = {x}\033[0m")
        y = gesture_right_info["index"][1]
        # print(f"\x1b[38;5;33m y = {y}\033[0m")
        if x > x_tmp_r and y > y_tmp_r:
            pag.move(-10, -10)
            x_tmp_r = x
            y_tmp_r = y
        elif x > x_tmp_r:
            pag.move(10,-10)
            x_tmp_r = x
        elif y > y_tmp_r:
            pag.move(-10,10)
            y_tmp_r = y
        elif x < x_tmp_r and y < y_tmp_r:
            pag.move(10,10)
            x_tmp_r = x
            y_tmp_r = y
        
    if command_right == "drag":
        x = gesture_right_info["index"][0]
        # print(f"\x1b[38;5;33m x = {x}\033[0m")
        y = gesture_right_info["index"][1]
        # print(f"\x1b[38;5;33m y = {y}\033[0m")
        if x > x_tmp_r and y > y_tmp_r:
            pag.drag(-10, -10)
            x_tmp_r = x
            y_tmp_r = y
        elif x > x_tmp_r:
            pag.drag(10,-10)
            x_tmp_r = x
        elif y > y_tmp_r:
            pag.drag(-10,10)
            y_tmp_r = y
        elif x < x_tmp_r and y < y_tmp_r:
            pag.drag(10,10)
            x_tmp_r = x
            y_tmp_r = y
        
    return x_tmp_r, y_tmp_r
    


def toggle_camera_feed():
    global camera_feed_visible, running
    camera_feed_visible = not camera_feed_visible
    if camera_feed_visible:
        start_camera_feed()
    else:
        stop_camera_feed()
    
def start_camera_feed():
    global running
    running = True
    show_camera_desktop()
    desktop_control_camera_label.place(x=325, y=159)
    
    
def stop_camera_feed():
    global running
    running = False
    desktop_control_camera_label.place_forget()    
    
#endregion


#region message
def place_message(text):
    
    message_text.config(text=text)
    message_headline.place(x=5, y=660)
    message_text.place(x=20, y=683)
    message_close.place(x=160, y=700)
def hide_message(event):
    message_headline.place_forget()
    message_text.place_forget()
    message_close.place_forget()
    
#endregion


#region all


def clear_active_page():
    global active_page
    if active_page  == "Main":
        clear_main_page()
    elif active_page == "Game Menu":
        clear_game_menu()
    elif active_page == "Profile Info":
        clear_profile_info()
    elif active_page == "Login":
        clear_login_page()
    elif active_page == "Feedback Menu":
        clear_feedback_menu() 
    elif active_page == "Desktop Control":
        clear_desktop_control() 
    else:
        print(f"Active Page: {active_page}")
    try:
        clear_header_menu()
    except:
        pass

def logout():
    global active_page
    clear_active_page()
    active_page = "Login"
    
    feedback_headline.insert(0, 'Enter Headline here')
    feedback_text.insert("1.0", 'Enter Text here')
    
    clear_header()
    login_page_place_all()

def start():
    set_base_profile()
    load_base()
    login_page_place_all()
    #set_base_action()
    all_canvas.place(x=0, y=0)  





#endregion


########################################################################        


window = Tk()

window.geometry("1280x720")
window.configure(bg = bg_white)
window.title("Gesturize")
window.resizable(False, False)
window.bind("<Button-1>", hide_message)

all_canvas = Canvas(
    window,
    bg = bg_white,
    height = 720,
    width = 1280,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)



#region header

#header

header_logo_hand_image = PhotoImage(file=picture_path + "header_logo_hand_image.png")
header_logo_text_image = PhotoImage(file=picture_path + "header_logo_text_image.png")
header_profile_button = Button(
        command=header_menu_hide_show,
        text="Username",
        fg="#60ABED",
        font=("Inter", 20 * -1)
    )



#header menu

header_menu_info_button = Button(
    text="Profile Info",
    command=open_profile_info,
    anchor="w", 
    justify="left",
    fg="#5DADEC",
    font=("Helvetica", 16)
)
header_menu_logout_button = Button(
    text="Logout",
    command=logout,
    anchor="w", 
    justify="left",
    fg="red",
    font=("Helvetica", 16)
)
#endregion


#region game menu

game_menu_game_1_button_image = PhotoImage(file=picture_path + "game_menu_game_1_button.png")
game_menu_game_1_button = Button(
    image=game_menu_game_1_button_image,
    command=lambda: print("Game 1 button clicked")
)

game_menu_game_3_button_image = PhotoImage(file=picture_path + "game_menu_game_3_button.png")
game_menu_game_3_button = Button(
    image=game_menu_game_3_button_image,
    command=lambda: print("Game 3 button clicked")
)




game_menu_game_1_image = PhotoImage(file=picture_path + "game_menu_placeholder_image.png")

game_menu_game_3_image = PhotoImage(file=picture_path + "game_menu_placeholder_image.png")


game_menu_switch_button_image = PhotoImage(file=picture_path + "game_menu_switch_button.png")
    
game_menu_switch_1_button = Button(
    image=game_menu_switch_button_image,
    command=lambda: print("Switch 1 button clicked")
)

game_menu_switch_3_button = Button(
    image=game_menu_switch_button_image,
    command=lambda: print("Switch 3 button clicked")
)

game_menu_back_button_image = PhotoImage(file=picture_path + "game_menu_back_button.png")

game_menu_back_button = Button(
    image=game_menu_back_button_image,
    command=back_from_game_page
)

profile_list = None
game_menu_label_profile = Label(window, text="Profile:")
game_menu_label_profile_selection = Combobox(window, values=profile_list, state="readonly", width=35)
game_menu_label_profile_selection.bind("<Enter>", on_combobox_select)
game_menu_button_profile_reload = Button(window, text="Load", command=switch_profile)

#endregion


#region login page

login_page_logo_image = PhotoImage(file=picture_path + "login_page_logo_image.png")

login_page_register_button_image = PhotoImage(file=picture_path + "login_page_register_button.png")

login_page_login_button_image = PhotoImage(file=picture_path + "desktop_control_start_button.png")
login_page_login_button = Button(
    image=login_page_login_button_image,
    command=login
)
login_page_browser_button = Button(
    command=viste_website,
    fg=bg_dark_blue,
    text="Visit Website",
    font=("Helvetica", 13),
)
login_page_camera_selection = Combobox(values=get_all_cams())

#endregion


#region main page

main_page_desktop_button_image = PhotoImage(file=picture_path + "main_page_desktop_button.png")
main_page_desktop_button = Button(
    image=main_page_desktop_button_image,
    command=open_desktop_control_page
)
main_page_button_games_image = PhotoImage(file=picture_path + "main_page_games_button.png")
main_page_games_button = Button(
    image=main_page_button_games_image,
    command=play_games
)

main_page_screen_image = PhotoImage(file=picture_path + "main_page_screen_image.png")

bg_color = window.cget("bg")
main_page_info_label = Label(window, text="Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor...", font=("Inter", 20 * -1), wraplength=741, bg=bg_color)

main_page_feedback_button = Button(
    command=open_feedback,
    fg=bg_dark_blue,
    text="Give Feedback",
    font=("Helvetica", 13),
)
    
#endregion


#region settings




#region left_right

combo_values = [
    "walk_forward",
    "walk_left",
    "walk_right",
    "walk_back",
    "turn_cam",
    "attack_normal",
    "interact",
    "stun",
    "finisher",
    "attact_ulti"
]


#left
settings_canvas_left = Canvas(window, bg=bg_white, scrollregion=(0, 285, 1280, 830),borderwidth=0, highlightthickness=0)
settings_vbar_left = Scrollbar(window, orient=VERTICAL, command=settings_canvas_left.yview)
settings_canvas_left.config(yscrollcommand=settings_vbar_left.set)
settings_frame_left = Frame(settings_canvas_left, bg=bg_white, width=1280, height=500,borderwidth=0, highlightthickness=0)
settings_frame_left.columnconfigure(0, minsize=300)
settings_frame_left.columnconfigure(1, minsize=400)


# Label creation
settings_label_left_1 = Label(settings_frame_left, text=gesture_functions[0])
settings_label_left_2 = Label(settings_frame_left, text=gesture_functions[1])
settings_label_left_3 = Label(settings_frame_left, text=gesture_functions[2])
settings_label_left_4 = Label(settings_frame_left, text=gesture_functions[3])
settings_label_left_5 = Label(settings_frame_left, text=gesture_functions[4])
settings_label_left_6 = Label(settings_frame_left, text=gesture_functions[5])
settings_label_left_7 = Label(settings_frame_left, text=gesture_functions[6])
settings_label_left_8 = Label(settings_frame_left, text=gesture_functions[7])
settings_label_left_9 = Label(settings_frame_left, text=gesture_functions[8])
settings_label_left_10 = Label(settings_frame_left, text=gesture_functions[9])
settings_label_left_11 = Label(settings_frame_left, text=gesture_functions[10])
settings_label_left_12 = Label(settings_frame_left, text=gesture_functions[11])
settings_label_left_13 = Label(settings_frame_left, text=gesture_functions[12])
settings_label_left_14 = Label(settings_frame_left, text=gesture_functions[13])
settings_label_left_15 = Label(settings_frame_left, text=gesture_functions[14])
list_settings_label_left = [settings_label_left_1,settings_label_left_2,settings_label_left_3,settings_label_left_4,settings_label_left_5,settings_label_left_6,settings_label_left_7,settings_label_left_8,settings_label_left_9,settings_label_left_10,settings_label_left_11,settings_label_left_12,settings_label_left_13,settings_label_left_14,settings_label_left_15]

for element in list_settings_label_left:
    element.bind("<MouseWheel>", on_mousewheel_left)


# Combo box creation

settings_combo_box_left_1 = Combobox(settings_frame_left)
settings_combo_box_left_2 = Combobox(settings_frame_left)
settings_combo_box_left_3 = Combobox(settings_frame_left)
settings_combo_box_left_4 = Combobox(settings_frame_left)
settings_combo_box_left_5 = Combobox(settings_frame_left)
settings_combo_box_left_6 = Combobox(settings_frame_left)
settings_combo_box_left_7 = Combobox(settings_frame_left)
settings_combo_box_left_8 = Combobox(settings_frame_left)
settings_combo_box_left_9 = Combobox(settings_frame_left)
settings_combo_box_left_10 = Combobox(settings_frame_left)
settings_combo_box_left_11 = Combobox(settings_frame_left)
settings_combo_box_left_12 = Combobox(settings_frame_left)
settings_combo_box_left_13 = Combobox(settings_frame_left)
settings_combo_box_left_14 = Combobox(settings_frame_left)
settings_combo_box_left_15 = Combobox(settings_frame_left)
list_settings_combo_box_left = [settings_combo_box_left_1, settings_combo_box_left_2, settings_combo_box_left_3, settings_combo_box_left_4, settings_combo_box_left_5, settings_combo_box_left_6, settings_combo_box_left_7, settings_combo_box_left_8, settings_combo_box_left_9, settings_combo_box_left_10, settings_combo_box_left_11, settings_combo_box_left_12, settings_combo_box_left_13, settings_combo_box_left_14, settings_combo_box_left_15]
for element in list_settings_combo_box_left:
    element.bind("<MouseWheel>", disable_mouse_scroll)


settings_canvas_left.bind("<MouseWheel>", on_mousewheel_left)
settings_frame_left.bind("<MouseWheel>", on_mousewheel_left)


#right
settings_canvas_right = Canvas(window, bg=bg_white, scrollregion=(0, 285, 1280, 830),borderwidth=0, highlightthickness=0)
settings_vbar_right = Scrollbar(window, orient=VERTICAL, command=settings_canvas_right.yview)
settings_canvas_right.config(yscrollcommand=settings_vbar_right.set)
settings_frame_right = Frame(settings_canvas_right, bg=bg_white, width=1280, height=500,borderwidth=0, highlightthickness=0)
settings_frame_right.columnconfigure(0, minsize=300)
settings_frame_right.columnconfigure(1, minsize=400)
# Label creation
settings_label_right_1 = Label(settings_frame_right, text=gesture_functions[0])
settings_label_right_2 = Label(settings_frame_right, text=gesture_functions[1])
settings_label_right_3 = Label(settings_frame_right, text=gesture_functions[2])
settings_label_right_4 = Label(settings_frame_right, text=gesture_functions[3])
settings_label_right_5 = Label(settings_frame_right, text=gesture_functions[4])
settings_label_right_6 = Label(settings_frame_right, text=gesture_functions[5])
settings_label_right_7 = Label(settings_frame_right, text=gesture_functions[6])
settings_label_right_8 = Label(settings_frame_right, text=gesture_functions[7])
settings_label_right_9 = Label(settings_frame_right, text=gesture_functions[8])
settings_label_right_10 = Label(settings_frame_right, text=gesture_functions[9])
settings_label_right_11 = Label(settings_frame_right, text=gesture_functions[10])
settings_label_right_12 = Label(settings_frame_right, text=gesture_functions[11])
settings_label_right_13 = Label(settings_frame_right, text=gesture_functions[12])
settings_label_right_14 = Label(settings_frame_right, text=gesture_functions[13])
settings_label_right_15 = Label(settings_frame_right, text=gesture_functions[14])
list_settings_label_right = [settings_label_right_1, settings_label_right_2, settings_label_right_3, settings_label_right_4, settings_label_right_5, settings_label_right_6, settings_label_right_7, settings_label_right_8, settings_label_right_9, settings_label_right_10, settings_label_right_11, settings_label_right_12, settings_label_right_13, settings_label_right_14, settings_label_right_15]
for element in list_settings_label_right:
    element.bind("<MouseWheel>", on_mousewheel_right)

# Combo box creation
settings_combo_box_right_1 = Combobox(settings_frame_right)
settings_combo_box_right_2 = Combobox(settings_frame_right)
settings_combo_box_right_3 = Combobox(settings_frame_right)
settings_combo_box_right_4 = Combobox(settings_frame_right)
settings_combo_box_right_5 = Combobox(settings_frame_right)
settings_combo_box_right_6 = Combobox(settings_frame_right)
settings_combo_box_right_7 = Combobox(settings_frame_right)
settings_combo_box_right_8 = Combobox(settings_frame_right)
settings_combo_box_right_9 = Combobox(settings_frame_right)
settings_combo_box_right_10 = Combobox(settings_frame_right)
settings_combo_box_right_11 = Combobox(settings_frame_right)
settings_combo_box_right_12 = Combobox(settings_frame_right)
settings_combo_box_right_13 = Combobox(settings_frame_right)
settings_combo_box_right_14 = Combobox(settings_frame_right)
settings_combo_box_right_15 = Combobox(settings_frame_right)
list_settings_combo_box_right = [settings_combo_box_right_1, settings_combo_box_right_2, settings_combo_box_right_3, settings_combo_box_right_4, settings_combo_box_right_5, settings_combo_box_right_6, settings_combo_box_right_7, settings_combo_box_right_8, settings_combo_box_right_9, settings_combo_box_right_10, settings_combo_box_right_11, settings_combo_box_right_12, settings_combo_box_right_13, settings_combo_box_right_14, settings_combo_box_right_15]
for element in list_settings_combo_box_right:
    element.bind("<MouseWheel>", disable_mouse_scroll)

settings_canvas_right.bind("<MouseWheel>", on_mousewheel_right)
settings_frame_right.bind("<MouseWheel>", on_mousewheel_right)

for element in list_settings_label_left + list_settings_label_right:
    element.config(bg=bg_white, anchor='w')    
for element in list_settings_combo_box_left + list_settings_combo_box_right:
    element.config(values=combo_values, state="readonly", width=50)

#endregion

settings_button_image_reset = PhotoImage(
    file=picture_path + "profile_info_button_reset.png")
settings_button_reset = Button(
    window,
    image=settings_button_image_reset,
    command=reset_settings
)
settings_button_image_save = PhotoImage(
    file=picture_path + "profile_info_button_save.png")
settings_button_save = Button(
    window,
    image=settings_button_image_save,
    command=save_profile
)
settings_button_image_right_not = PhotoImage(
    file=picture_path+"profile_info_button_right_not.png")
settings_button_right_not = Button(
    image=settings_button_image_right_not,
    command=swich_hand_to_right
)
settings_button_image_left_selected = PhotoImage(
    file=picture_path+"profile_info_button_left_selected.png")
settings_button_left_selected = Button(
    image=settings_button_image_left_selected
)
settings_button_image_right_selected = PhotoImage(
    file=picture_path+"profile_info_button_right_selected.png")
settings_button_right_selected = Button(
    image=settings_button_image_right_selected
)
settings_button_image_left_not = PhotoImage(
    file=picture_path+"profile_info_button_left_not.png")
settings_button_left_not = Button(
    image=settings_button_image_left_not,
    command=swich_hand_to_left
)
profile_list = None
settings_label_profile = Label(window, text="Profile:")
settings_label_profile_selection = Combobox(window, values=profile_list, state="readonly", width=35)
settings_label_profile_selection.bind("<Enter>", on_combobox_select)
settings_button_profile_reload = Button(window, text="Load", command=load_insert)
settings_button_profile_new = Button(window, text="Create New", command=create_new_window_profile)

settings_back_button_image = PhotoImage(file=picture_path + "game_menu_back_button.png")

settings_back_button = Button(
    image=settings_back_button_image,
    command=back_from_profile_info
)
#endregion


#region Feedback Menu

feedback_button_image_send = PhotoImage(
    file=picture_path + "feedback_button_send.png")
feedback_button_send = Button(
    image=feedback_button_image_send,
    command=send_feedback
)
feedback_button_back_button_image = PhotoImage(file=picture_path + "game_menu_back_button.png")
feedback_button_back_button = Button(
    image=game_menu_back_button_image,
    command=back_from_feedback_menu
)
feedback_image_image_header = PhotoImage(
    file=picture_path + "feedback_image_header.png")

feedback_image_image_text = PhotoImage(
    file=picture_path + "feedback_image_text.png")

feedback_image_image_email = PhotoImage(
    file=picture_path + "feedback_menu_image_email.png")

feedback_image_image_password = PhotoImage(
    file=picture_path + "feedback_menu_image_email.png")

feedback_headline = Entry(window, borderwidth=0)
feedback_headline.insert(0, "Enter Headline here")

feedback_text = Text(window, borderwidth=0)
feedback_text.insert("1.0", "Enter Text here")

feedback_email = Entry(window, borderwidth=0)
feedback_email.insert(0, "Enter Email here")

feedback_password = Entry(window, borderwidth=0)
feedback_password.insert(0, "Enter Password here")

# Binding events to functions
feedback_headline.bind('<FocusIn>', feedback_headline_on_entry_click)
feedback_headline.bind('<FocusOut>', feedback_headline_on_focusout)
feedback_text.bind('<FocusIn>', feedback_text_on_entry_click)
feedback_text.bind('<FocusOut>', feedback_text_on_focusout)

feedback_email.bind('<FocusIn>', feedback_email_on_entry_click)
feedback_email.bind('<FocusOut>', feedback_email_on_focus_out)
feedback_password.bind('<FocusIn>', feedback_password_on_entry_click)
feedback_password.bind('<FocusOut>', feedback_password_on_focus_out)

#endregion


#region Desktop Control

desktop_control_camera_label = Label(window, width=630, height=369, bg=bg_white)

desktop_control_button_image_toggle = PhotoImage(
    file=picture_path+"desktop_control_button_toggle.png")
desktop_control_button_toggle = Button(
    image=desktop_control_button_image_toggle,
    command=toggle_camera_feed
)
desktop_control_button_image_back = PhotoImage(
    file=picture_path+"desktop_control_button_back.png")
desktop_control_button_back = Button(
    image=desktop_control_button_image_back,
    command=back_from_desktop_control
)



#endregion


#region message
message_headline = Label(window, text="*Message*", fg="red")
message_text = Label(window)
message_close = Label(window, text="click anywhere to hide", bg=bg_white, font=("Inter", 10 * -1))
#endregion

#config all
all_buttons = [header_profile_button,header_menu_info_button,header_menu_logout_button,game_menu_game_1_button,game_menu_game_3_button,game_menu_switch_1_button,game_menu_switch_3_button,game_menu_back_button,login_page_login_button,login_page_browser_button,main_page_desktop_button,main_page_games_button,main_page_feedback_button,settings_button_reset,settings_button_save,settings_button_right_not,settings_button_left_selected,settings_button_right_selected,settings_button_left_not,settings_back_button,feedback_button_send,feedback_button_back_button,desktop_control_button_toggle,desktop_control_button_back]#,game_menu_switch_2_button,game_menu_game_2_button
for element in all_buttons:
    element.config(borderwidth=0,highlightthickness=0,relief="flat",bg=bg_white)    
    
for element in [header_profile_button,header_menu_info_button,header_menu_logout_button]:
    element.config(bg=bg_dark_blue)    

all_for_font = [settings_label_profile,settings_button_profile_reload,settings_button_profile_new,game_menu_label_profile,game_menu_button_profile_reload,message_headline,message_text]
for element in all_for_font:
    element.config(font=text_font,bg=bg_white) 

start()
window.mainloop()