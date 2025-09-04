import ast
import json
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty, BooleanProperty, get_color_from_hex
from kivy.uix.screenmanager import SlideTransition
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivy.metrics import dp


class PerfilEmployee(MDScreen):
    avatar = StringProperty()
    employee_name = StringProperty()
    token_id = StringProperty()
    api_key = StringProperty()
    can_add = BooleanProperty()
    local_id = StringProperty()
    refresh_token = StringProperty()
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
        print('\n\n\n\n\n')
        print('Key da requisição: ', self.key_requests)
        print('Key do funcionario: ', self.key)
        print('Key do contratante: ', self.local_id)
        print('Token id: ', self.token_id)
        print('POde adicionar: ', self.can_add)
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

        if not self.can_add:
            self.show_message("O seu perfil não contem todas as informações=", color="#ff0707")
            Clock.schedule_once(lambda dt: self.show_message("Termine seu perfil antes de prosseguir", color="#ff0707"), 2)
            return
        
        # Primeior o requests
        UrlRequest(
            f'https://obra-7ebd9-default-rtdb.firebaseio.com/requets/{self.key_requests}/.json?auth={self.token_id}',
            on_success=self.upload_request
        )

    def show_message(self, message, color='#2196F3'):
        """Display a snackbar message"""
        MDSnackbar(
            MDSnackbarText(
                text=message,
                theme_text_color='Custom',
                text_color='white',
                bold=True
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            halign='center',
            size_hint_x=0.88,
            theme_bg_color='Custom',
            background_color=get_color_from_hex(color)
        ).open()

    def upload_request(self, req, result):
        data = ast.literal_eval(result['requests'])
        if self.local_id not in data:
            data.append(self.local_id)
        date = {
            'requests': f"{data}"
        }
        UrlRequest(
            f'https://obra-7ebd9-default-rtdb.firebaseio.com/requets/{self.key_requests}/.json?auth={self.token_id}',
            method='PATCH',
            req_body=json.dumps(date),
            on_success=self.ultimate_request
        )

    def ultimate_request(self, req, result):
        """
        adicionar essa porra dessa key la no receiveds da mesma forma que eu fiz agora
        """
        UrlRequest(
            f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.key}/.json?auth={self.token_id}',
            on_success=self.upload_receiveds
        )

    def upload_receiveds(self, req, result):
        print('rs')
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.key}/.json?auth={self.token_id}'
        data = ast.literal_eval(result['receiveds'])
        if self.local_id not in data:
            data.append(self.local_id)

        date = {
            'receiveds': f"{data}"
        }
        UrlRequest(
            url,
            req_body=json.dumps(date),
            method='PATCH',
            on_error=self.erro,
            on_failure=self.erro,
            on_success=self.ultimate_receiveds
        )


    def erro(self, req, result):
        """Analisa o erro da requisição e devolve um print"""
        print('Motivo do erro: ', result)

    def ultimate_receiveds(self, req, result):
        print('Enviado com sucesso')
        self.ids.text_label.text = 'Enviado'
        self.ids.card.md_bg_color = get_color_from_hex('#5EFC8D')
        self.ids.card.md_bg_color_disabled = get_color_from_hex('#5EFC8D')
        Clock.schedule_once(self.back, 1)

    def back(self):
        self.ids.card.md_bg_color = 'blue'
        self.ids.text_label.text = 'Contratar agora'
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'VacancyContractor'
