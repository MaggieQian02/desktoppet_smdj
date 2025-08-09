import importlib
import subprocess
import sys
import time

# Map of pip package names to module import names
required_packages = {
    'kivy': 'kivy',                  # covers kivy.app, kivy.uix.*, etc.
    'pypiwin32': 'win32api',         # win32api, win32con, win32gui
    'pywin32': 'win32gui',           # depending on environment
    'setuptools': 'pkg_resources',   # required by some win32 installations
}

def install_and_import(pip_name, import_name):
    try:
        importlib.import_module(import_name)
    except ImportError:
        print(f"Installing missing package '{pip_name}'...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
    finally:
        globals()[import_name] = importlib.import_module(import_name)

for pip_name, import_name in required_packages.items():
    install_and_import(pip_name, import_name)

# Now you can safely import your modules
from kivy.app import App
from kivy.uix.screenmanager import Screen # uses the screen in terminal
from kivy.core.window import Window
from kivy.vector import Vector
from kivy.graphics import Rectangle, BoxShadow, Color
from kivy.clock import Clock # for repitition
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.utils import get_color_from_hex

from kivy.config import Config
Config.set('input', 'mouse', 'mouse,disable_multitouch')

import win32api, win32con, win32gui # gets the desktop
import os


class Select_Button(Button):
    def __init__(self, **kwargs):
        super(Select_Button, self).__init__()

        self.size = (70, 70)

        with self.canvas.before:
            # hex colour code: red = #781e18, blue = #121c3a, pink = #e99994, light blue = #39529c
            Color(*get_color_from_hex("#39529c"))
            self.rect = BoxShadow(size=self.size, border_radius=(45,45,45,45), inset=True, blur_radius=50)
        self.bind(pos=self.update_canvas)

        for key,values in kwargs.items():
            self.__setattr__(key, values) 

        self.background_color = (0.2, 0.2, 0.2, 0)
        self.size_hint = (None, None)

        self.start_an = Animation(blur_radius=0)
        self.end_an = Animation(blur_radius=100)
        
    def update_canvas(self, widget, pos):
        self.rect.pos = pos

    def on_press(self):
        self.start_an.start(self.rect)

    def on_release(self):
        self.end_an.start(self.rect)


class l_Rloe(Screen): # character
    def __init__(self):
        super().__init__()
        self.pos = 10,10
        self.size_hint = (None, None) # ratio
        self.size = Vector(2360, 1640)*0.2

        # file locations for animated png
        _default_line = "default" 
        self._default_file_list = [os.path.join(_default_line, i) for i in os.listdir(_default_line)]
        #print(self._default_file_list)

        _working_line = "working"
        self._working_file_list = [os.path.join(_working_line, i) for i in os.listdir(_working_line)]

        self.animating = True        # For frame animation
        self.moving_right = True     # For horizontal motion
        self.mode = 0                # 0: move+animate, 1: animate only, 2: freeze

        self.s_index = 0
        self.check_list = self._default_file_list
        #self.check_list = self._working_file_list

        with self.canvas:
            self.update_img = Rectangle(size=self.size)

    # move horizontally to the right
    def move_right(self):
            self.x += 2 
            if self.x >= self.parent.width: # come back from the left if it goes right out of the screen
                self.x = -self.width
    
    # animations
    # default jump
    def default(self, dt): 
        if not self.animating:
            return
        if self.moving_right:
            self.move_right()
        # Update image
        self.update_img.source = self.check_list[self.s_index] # select file
        # plays the next frame from the png files
        self.s_index += 1 
        if self.s_index >= len(self.check_list)-0: # if number greater than the total number of files, 
            self.s_index = 0 # go back to 0

    # working overtime 
    def working(self, dt):
        if not self.animating:
            return
        if self.moving_right:
            self.move_right()
        self.update_img.source = self.check_list[self.s_index] # select file
        self.s_index += 1 
        if self.s_index >= len(self.check_list)-0: 
            self.s_index = 0 


    def toggle_mode(self, *args):
        # Cycle through 0 → 1 → 2 → 0 ...
        self.mode = (self.mode + 1) % 3
        if self.mode == 0:
            self.animating = True
            self.moving_right = True
        elif self.mode == 1:
            self.animating = True
            self.moving_right = False
        elif self.mode == 2:
            self.animating = False
            self.moving_right = False


class MainApp(App): # background screen
    def __init__(self): # initialise
        super().__init__() 
        self.body = Screen(name="master_box") 

        # Add character
        self.l_rloe = l_Rloe() 
        self.body.add_widget(self.l_rloe) 

        # Add buttons to select animaitons
        self.check_box_list = list()
        c_b1 = Select_Button(pos=(-100, -100), text="Default", rotate=-25)
        c_b2 = Select_Button(pos=(-100, -100), text="Working", rotate=-50)
        c_b3 = Select_Button(pos=(-100, -100), text="Eating", rotate=-75)
        self.body.add_widget(c_b1)
        self.body.add_widget(c_b2)
        self.body.add_widget(c_b3)
        self.check_box_list.append(c_b1)
        self.check_box_list.append(c_b2)
        self.check_box_list.append(c_b3)

        Window.borderless = True 
        Window.always_on_top = True

        # Bind all touch events
        Window.bind(on_touch_down=self.on_touch_down)
        Window.bind(on_touch_move=self.on_touch_move) # distinguish between clicking and dragging
        Window.bind(on_touch_up=self.on_touch_up)
        Window.bind(on_keyboard = self.on_keyboard)

        self._touch_start_pos = None
        self._touch_start_time = 0 # add timing threshold to consider it a drag only if touch is too long
        self._is_dragging = False

    def toggle_animation(self, window, touch):
        if self.l_rloe.collide_point(*touch.pos):
            self.l_rloe.toggle_mode()  # Cycle between move+animate → animate → freeze

    def handle_right_click(self, touch):
        center = self.l_rloe.center
        height = self.l_rloe.height * 0.55
        for i in self.check_box_list:
            obst = Vector(0, height)
            i.pos = obst.rotate(i.rotate) + center

    def on_touch_down(self, window, touch):
        # Don't treat right click as normal click/drag
        if hasattr(touch, "button"):
            if touch.button == "right":
                self.handle_right_click(touch)
                return True  

        # Left click / drag handling here
        # If a button handled it, don't process further
        for widget in self.body.children:
            if isinstance(widget, Button) and widget.collide_point(*touch.pos):
                return False  # Stop here so animation doesn't get the click
        # Animation click logic    
        if self.l_rloe.collide_point(*touch.pos):
            self._touch_start_pos = touch.pos  # Store starting point
            self._touch_start_time = time.time()
            self._is_dragging = False  # Reset drag state

    def on_touch_move(self, window, touch):
        if self._touch_start_pos:
            dx = touch.pos[0] - self._touch_start_pos[0]
            dy = touch.pos[1] - self._touch_start_pos[1]
            distance_moved = (dx**2 + dy**2)**0.5

            if distance_moved > 10:  # Drag threshold (pixels)
                self._is_dragging = True
                self.l_rloe.x = touch.x - self.l_rloe.width / 2
                self.l_rloe.y = touch.y - self.l_rloe.height / 2

    def on_touch_up(self, window, touch):
        if self._touch_start_pos is not None and self.l_rloe.collide_point(*touch.pos):
            duration = time.time() - self._touch_start_time
            dx = touch.pos[0] - self._touch_start_pos[0]
            dy = touch.pos[1] - self._touch_start_pos[1]
            distance_moved = (dx**2 + dy**2)**0.5

            # If very little movement and short duration, treat as a click
            if not self._is_dragging and distance_moved <= 10 and duration <= 0.3:
                # Only toggle if no drag occurred
                self.l_rloe.toggle_mode()

        self._touch_start_pos = None
        self._is_dragging = False

    def on_keyboard(self, window, key, *args):
        #print(key)
        if key == 27:
            return True


    def build(self):
        return self.body
    
    def on_start(self):
        hwnd = win32gui.GetForegroundWindow() # gets Handle
        window_hwnd = win32gui.GetDesktopWindow() # size of desktop
        left, top, right, botton = win32gui.GetWindowRect(window_hwnd) # position on desktop
        win32gui.MoveWindow(hwnd, left, top, right, botton, False) # change the size of the screen to fit desktop size
        
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) 
        win32api.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style | win32con.WS_EX_LAYERED) 
        
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 0, win32con.LWA_COLORKEY) # make the screen transparent

        Clock.schedule_interval(self.l_rloe.default, 1/8) # animation play speed: seconds per frame

    
# run
if __name__ == '__main__': 
    MainApp().run()
