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
        self.pos = 50,30
        self.size_hint = (None, None) # ratio
        self.size = Vector(2360, 1640)*0.25
        
        _default_line = "default" # file location for animated png
        self._default_file_list = [os.path.join(_default_line, i) for i in os.listdir(_default_line)]
        print(self._default_file_list)

        self.s_index = 0
        self.check_list = self._default_file_list

        with self.canvas:
            self.update_img = Rectangle(size=self.size)

    # movement
    def default(self, ints): # move horizontally
        self.update_img.source = self.check_list[self.s_index] # select file
        self.s_index += 1

        if self.s_index >= len(self.check_list)-0: # if number greater than the total number of files, 
            self.s_index = 0 # go back to 0

class MainApp(App): # background screen
    def __init__(self): # initialise
        super().__init__() 
        self.body = Screen(name="master_box") 

        self.l_rloe = l_Rloe() # add character
        self.body.add_widget(self.l_rloe) 

        Window.borderless = True 

    def build(self):
        return self.body
    
    def on_start(self):
        hwnd = win32gui.GetForegroundWindow() # gets Handle
        window_hwnd = win32gui.GetDesktopWindow() # size of desktop
        left, top, right, botton = win32gui.GetWindowRect(window_hwnd) # position on desktop
        win32gui.MoveWindow(hwnd, left, top, right, botton, False) # change the size of the screen
        
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) 
        win32api.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style | win32con.WS_EX_LAYERED) 
        
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 0, win32con.LWA_COLORKEY) # make the screen transparent

        Clock.schedule_interval(self.l_rloe.default, 1/8)

        #self.l_rloe.default(1)
    
# run
if __name__ == '__main__': 
    MainApp().run()
