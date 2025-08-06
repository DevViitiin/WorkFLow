import ast
import json

from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty, BooleanProperty, get_color_from_hex
from kivy.uix.screenmanager import SlideTransition
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.screen import MDScreen


class PerfilEmployee(MDScreen):
    avatar = StringProperty()
    employee_name = StringProperty()
    employee_function = StringProperty()
    employee_mail = StringProperty()
    employee_telephone = StringProperty()
    key = StringProperty()
    key_contractor = StringProperty()
    key_requests = StringProperty()
    state = StringProperty()
    city = StringProperty()
    employee_summary = StringProperty()
    skills = StringProperty()

    def on_enter(self):
        try:
            skills = eval(self.skills)

        except:
            skills = []

        self.ids.main_scroll.clear_widgets()
        self.add_skills(skills)

    def add_skills(self, skills):
        """ Adicionando as habilidades do funcionario na tela """
        if skills:
            self.ids.main_scroll.clear_widgets()
            for skill in skills:
                button = MDButton(
                    MDButtonText(
                        text=f'{skill}',
                        theme_text_color='Custom',
                        text_color='white',
                        bold=True
                    ),
                    theme_bg_color='Custom',
                    md_bg_color=get_color_from_hex('#0047AB')
                )
                self.ids.main_scroll.add_widget(button)
        else:
            self.ids.main_scroll.clear_widgets()
            button = MDButton(
                MDButtonText(
                    text=f'Nenhuma habilidade adicionada',
                    theme_text_color='Custom',
                    text_color='white',
                    bold=True
                ),
                theme_bg_color='Custom',
                md_bg_color=get_color_from_hex('#0047AB')
            )
            self.ids.main_scroll.add_widget(button)

    def request(self):
        """
        Eu preciso adicionar a key do contratante em requests na solicitações
        E adicionar a key do contratante em receives do funcionario

        """

        # Primeior o requests
        UrlRequest(
            f'https://obra-7ebd9-default-rtdb.firebaseio.com/requets/{self.key_requests}/.json',
            on_success=self.upload_request
        )

    def upload_request(self, req, result):
        data = ast.literal_eval(result['requests'])
        if self.key_contractor not in data:
            data.append(self.key_contractor)
        date = {
            'requests': f"{data}"
        }
        UrlRequest(
            f'https://obra-7ebd9-default-rtdb.firebaseio.com/requets/{self.key_requests}/.json',
            method='PATCH',
            req_body=json.dumps(date),
            on_success=self.ultimate_request
        )

    def ultimate_request(self, req, result):
        """
        adicionar essa porra dessa key la no receiveds da mesma forma que eu fiz agora
        """
        UrlRequest(
            f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.key}/.json',
            on_success=self.upload_receiveds
        )

    def upload_receiveds(self, req, result):
        print('rs')
        data = ast.literal_eval(result['receiveds'])
        if self.key_contractor not in data:
            data.append(self.key_contractor)

        date = {
            'receiveds': f"{data}"
        }
        UrlRequest(
            f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.key}/.json',
            req_body=json.dumps(date),
            method='PATCH',
            on_success=self.ultimate_receiveds
        )

    def ultimate_receiveds(self, req, result):
        self.ids.card.md_bg_color = [0.0, 1.0, 0.0, 1.0]
        self.ids.text_label.text = 'Enviado'

    def back(self):
        self.ids.card.md_bg_color = 'blue'
        self.ids.text_label.text = 'Contratar agora'
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'VacancyContractor'
