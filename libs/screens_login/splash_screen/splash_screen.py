from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.animation import Animation
from kivymd.app import MDApp
from kivy.uix.image import Image


class SplashScreen(MDScreen):
    logo = "https://res.cloudinary.com/dh7ixbnzc/image/upload/v1757677779/a-modern-logo-design-for-a-construction-_rTLcAT8eTSOBn0GCfdHWwQ_LW_ZvToNSpmvMtwMOX0iHw-removebg-preview_l3iyui.png"
    
    def on_enter(self, *args):
        self.ids.logo.source = self.logo
        # Pega a logo
        self.logo = self.ids.logo
        # Animação de fade in (aparecer)
        anim = Animation(opacity=1, duration=3)
        anim.bind(on_complete=lambda *x: self.fade_out())
        anim.start(self.logo)

    def fade_out(self):
        # Depois faz fade out (sumir)
        anim = Animation(opacity=0, duration=2)
        anim.bind(on_complete=lambda *x: self.go_home())
        anim.start(self.logo)

    def go_home(self):
        self.manager.current = "Init"