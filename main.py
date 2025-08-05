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
from kivy.graphics import Rectangle
from kivy.clock import Clock # for repitition

import win32api, win32con, win32gui # gets the desktop
import os


class l_Rloe(Screen): # character
    def __init__(self):
        super().__init__()
        self.pos = 10,10
        self.size_hint = (None, None) # ratio
        self.size = Vector(2360, 1640)*0.22

        _default_line = "default" # file location for animated png
        self._default_file_list = [os.path.join(_default_line, i) for i in os.listdir(_default_line)]
        print(self._default_file_list)

        self.animating = True        # For frame animation
        self.moving_right = True     # For horizontal motion
        self.mode = 0                # 0: move+animate, 1: animate only, 2: freeze

        self.s_index = 0
        self.check_list = self._default_file_list

        with self.canvas:
            self.update_img = Rectangle(size=self.size)

    # animation
    def default(self, dt): # default jump
        if not self.animating:
            return

        # Update image
        self.update_img.source = self.check_list[self.s_index] # select file
        
        # move horizontally to the right
        if self.moving_right:
            self.x +=5 
            if self.x >= self.parent.width: # come back from the left if it goes right out of the screen
                self.x = -self.width
        
        # plays the next frame from the png files
        self.s_index += 1 
        if self.s_index >= len(self.check_list)-0: # if number greater than the total number of files, 
            self.s_index = 0 # go back to 0

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

        self.l_rloe = l_Rloe() # add character
        self.body.add_widget(self.l_rloe) 

        Window.borderless = True 

        # Bind all touch events
        Window.bind(on_touch_down=self.on_touch_down)
        Window.bind(on_touch_move=self.on_touch_move) # distinguish between clicking and dragging
        Window.bind(on_touch_up=self.on_touch_up)

        self._touch_start_pos = None
        self._touch_start_time = 0 # add timing threshold to consider it a drag only if touch is too long
        self._is_dragging = False

    def toggle_animation(self, window, touch):
        if self.l_rloe.collide_point(*touch.pos):
            self.l_rloe.toggle_mode()  # Cycle between move+animate → animate → freeze

    def on_touch_down(self, window, touch):
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
        if self.l_rloe.collide_point(*touch.pos):
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
