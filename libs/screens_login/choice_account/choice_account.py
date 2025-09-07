from kivy.uix.screenmanager import SlideTransition
from kivymd.uix.screen import MDScreen


class ChoiceAccount(MDScreen):
    def funcionario(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'RegisterFuncionario'

    def contratante(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'RegisterContractor'

    def voltar(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'Init'
