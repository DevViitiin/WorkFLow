from kivy.uix.screenmanager import SlideTransition
from kivymd.uix.screen import MDScreen


class PermissionDenied(MDScreen):

    def denied_pass(self):
        self.manager.trasition = SlideTransition(direction='right')
        self.manager.current = 'EditProfile'

    def confirm_permissions(self):
        self.manager.trasition = SlideTransition(direction='right')
        self.manager.current = 'Confirm'