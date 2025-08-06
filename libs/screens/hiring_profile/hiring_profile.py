import ast
import json
from datetime import datetime

from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty, get_color_from_hex
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.screen import MDScreen


class HiringProfile(MDScreen):
    # informações que eu vou adicionar ao funcionario ------------------------------------------------------------------
    username = StringProperty()
    salary = StringProperty()
    function = StringProperty()
    method_salary = StringProperty()
    scale = StringProperty('5x2')

    # Informações do meu funcionario -----------------------------------------------------------------------------------
    avatar = StringProperty()
    employee_name = StringProperty()
    employee_function = StringProperty()
    employee_mail = StringProperty()
    employee_telephone = StringProperty()
    key = StringProperty()
    key_contractor = StringProperty()
    name_contractor = StringProperty()
    key_requests = StringProperty()
    state = StringProperty()
    city = StringProperty()
    employee_summary = StringProperty()
    skills = StringProperty()

    def on_enter(self):
        print('Nome do contratante  ', self.username)
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

    def recruit(self):
        """ Adicionar o nosso funcionario na equipe I can do it"""
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.key}/.json'
        month = datetime.today().month
        # Obtém a data atual
        data_atual = datetime.now()

        # Formata no padrão brasileiro
        data_formatada = data_atual.strftime('%d/%m/%Y')

        data = {
            'contractor': self.username,
            'function': self.function,
            'method_salary': self.method_salary,
            'salary': self.salary,
            'scale': self.scale,
            'contractor_month': month,
            'data_contractor': f"{data_formatada}"
        }
        UrlRequest(
            url,
            req_body=json.dumps(data),
            method='PATCH',
            on_success=self.save_contractor_name
        )

    def save_contractor_name(self, req, result):
        self.back()
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Functions/{self.key_requests}/.json'
        UrlRequest(
            url,
            req_body=None,
            method='DELETE',
            on_success=self.final_delete
        )

    def final_delete(self, req, result):
        url = 'https://obra-7ebd9-default-rtdb.firebaseio.com/requets/.json'

        UrlRequest(
            url,
            on_success=self.upload_requests
        )

    def upload_requests(self, req, result):
        for key, request in result.items():
            if key in self.key:
                UrlRequest(
                    f'https://obra-7ebd9-default-rtdb.firebaseio.com/requets/{self.key}/.json',
                    method='DELETE',
                    on_success=self.final_delete_request
                )

    def final_delete_request(self, req, result):
        self.back()

    def dispense(self):
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Functions/{self.key_requests}/.json'
        UrlRequest(
            url,
            on_success=self.upload_decline
        )
    
    def upload_decline(self, req, result):
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Functions/{self.key_requests}/.json'
        decline = ast.literal_eval(result['decline'])
        request = ast.literal_eval(result['requests'])
        request.remove(self.key)
        print(request)
        decline.append(self.key)
        data = {
            'decline': f'{decline}',
            'requests': f'{request}'
        }
        UrlRequest(
            url,
            method='PATCH',
            req_body=json.dumps(data),
            on_success=self.final_decline
        )

    def final_decline(self, req, result):
        self.back()

    def back(self):
        app = MDApp.get_running_app()
        screenmanager = app.root
        request = screenmanager.get_screen('RequestContractor')
        request.username = self.username
        request.key = self.key_contractor
        screenmanager.transition = SlideTransition(direction='left')
        screenmanager.current = 'RequestContractor'
