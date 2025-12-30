import ast
import json
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty, BooleanProperty, get_color_from_hex
from kivy.uix.screenmanager import SlideTransition
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from configurations import DialogNoNet, DialogInfinityUpload, DialogErrorUnknow, firebase_url, check_error, SignController
from kivy.metrics import dp
from kivymd.app import MDApp

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
        # ====================== popups =============================
        self.inf_dialog = DialogInfinityUpload()
        self.signcontroller = SignController(screen=self, name=self.name)        
        self.dialog_not_net = DialogNoNet(
            subtitle='Não foi possível se conectar. Verifique sua internet e tente novamente',
            callback=lambda: self.signcontroller.retry_signup(self.request)
        )
        self.dialog_not_net_database = DialogNoNet(
            subtitle='Não foi carregar funções. Verifique sua internet e tente novamente',
            callback=lambda: self.signcontroller.retry_handle(self.ultimate_request)
        )

        self.dialog_error_unknown = DialogErrorUnknow(
            screen=f'{self.name}'
        )
        try:
            skills = ast.literal_eval(self.skills)

        except:
            skills = []

        if 'main_scroll' in self.ids:
            self.ids.main_scroll.clear_widgets()
            self.add_skills(skills)
        else:
            Clock.schedule_once(lambda dt: self.dialog_error_unknown.open(), 1)

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
            self.show_message("O seu perfil não está completo", color="#ff0707")
            Clock.schedule_once(lambda dt: self.show_message("Complete seu perfil antes de prosseguir", color="#ff0707"), 2)
            return
        
        # Primeior o requests
        UrlRequest(
            f'{firebase_url()}/requets/{self.key_requests}/.json?auth={self.token_id}',
            on_success=self.upload_request,
            on_error=self.signcontroller.handle_signup_error,
            on_failure=self.signcontroller.handle_signup_failure
        )

    def show_message(self, message, color='#2196F3'):
        """
        Exibe uma mensagem na interface através de um snackbar.

        Args:
            message: A mensagem a ser exibida
            color: A cor de fundo do snackbar
        """
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
            size_hint_x=0.94,
            theme_bg_color='Custom',
            background_color=get_color_from_hex(color),
            duration=3  # Duração da exibição do snackbar em segundos
        ).open()

    def show_error(self, error_message):
        """
        Exibe uma mensagem de erro através de um snackbar vermelho.

        Args:
            error_message: A mensagem de erro a ser exibida
        """
        self.show_message(error_message, color='#FF0000')

    def upload_request(self, req, result):
        data = ast.literal_eval(result['requests'])
        if self.local_id not in data:
            data.append(self.local_id)
        date = {
            'requests': f"{data}"
        }
        UrlRequest(
            f'{firebase_url()}/requets/{self.key_requests}/.json?auth={self.token_id}',
            method='PATCH',
            req_body=json.dumps(date),
            on_success=self.ultimate_request,
            on_error=self.signcontroller.handle_signup_error,
            on_failure=self.signcontroller.handle_signup_failure
        )

    def ultimate_request(self, req, result):
        """
        adicionar essa porra dessa key la no receiveds da mesma forma que eu fiz agora
        """
        UrlRequest(
            f'{firebase_url()}/Funcionarios/{self.key}/.json?auth={self.token_id}',
            on_success=self.upload_receiveds,
            on_failure=self.signcontroller.on_failure,
            on_error=self.signcontroller.on_error

        )

    def upload_receiveds(self, req, result):
        url = f'{firebase_url()}/Funcionarios/{self.key}/.json?auth={self.token_id}'
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
        """Analisa o erro da requisição e devolve um escreva"""

    def ultimate_receiveds(self, req, result):
        self.ids.text_label.text = 'Enviado'
        self.ids.card.md_bg_color = get_color_from_hex('#5EFC8D')
        self.ids.card.md_bg_color_disabled = get_color_from_hex('#5EFC8D')
        Clock.schedule_once(self.back, 1)

    def back(self, *args):
        try:
            self.ids.card.md_bg_color = 'blue'
            self.ids.text_label.text = 'Solicitar chat'
            app = MDApp.get_running_app()
            screen = app.root
            contractor = screen.get_screen('VacancyContractor')
            contractor.local_id = self.local_id
            contractor.token_id = self.token_id
            contractor.refresh_token = self.refresh_token
            contractor.api_key = self.api_key
            self.manager.transition = SlideTransition(direction='left')
            self.signcontroller.close_all_dialogs()
            self.manager.current = 'VacancyContractor'
        except:
            self.dialog_error_unknown.open()
        