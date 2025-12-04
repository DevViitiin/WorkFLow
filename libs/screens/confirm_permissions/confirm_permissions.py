from kivy.uix.screenmanager import SlideTransition
from kivymd.uix.screen import MDScreen


class ConfirmPermissions(MDScreen):

    def next_page(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'EditProfile'
