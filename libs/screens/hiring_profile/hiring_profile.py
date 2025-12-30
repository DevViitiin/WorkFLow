import ast
import json
from datetime import datetime
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty, get_color_from_hex
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from configurations import DialogNoNet, DialogInfinityUpload, DialogErrorUnknow, firebase_url, check_error, SignController
from kivymd.uix.snackbar import MDSnackbarText, MDSnackbar
from kivy.metrics import dp
import uuid


class HiringProfile(MDScreen):
    FIREBASE_URL = firebase_url()
    # Informações do banco de dados para efetuar alterações ------------------------------------------------------------
    token_id = StringProperty()
    api_key = StringProperty()
    local_id = StringProperty()
    refresh_token = StringProperty()

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
        self.verific_token()
        self.event_token = Clock.schedule_interval(self.verific_token, 300)
        # ====================== popups =============================
        self.inf_dialog = DialogInfinityUpload()
        self.signcontroller = SignController(screen=self, name=self.name)        
        self.dialog_not_net = DialogNoNet(
            subtitle='Não foi possível se conectar. Verifique sua internet e tente novamente',
            callback=lambda: self.signcontroller.retry_signup(self.recruit)
        )
        self.dialog_not_net = DialogNoNet(
            subtitle='Não foi possível se conectar. Verifique sua internet e tente novamente',
            callback=lambda: self.signcontroller.retry_delete(self.verific_data)
        )
        self.dialog_not_net_database = DialogNoNet(
            subtitle='Não foi carregar funções. Verifique sua internet e tente novamente',
            callback=lambda: self.signcontroller.retry_handle(self.final_delete)
        )

        self.dialog_error_unknown = DialogErrorUnknow(
            screen=f'{self.name}'
        )
        try:
            skills = ast.literal_eval(self.skills)

        except:
            skills = []

        self.ids.main_scroll.clear_widgets()
        self.add_skills(skills)

    def on_leave(self, *args):
        if hasattr(self, 'event_token'):
            self.event_token.cancel()
            
    def verific_token(self, *args):
        if not self.get_parent_window():
            return
        UrlRequest(
            f"{self.FIREBASE_URL}/Users/{self.local_id}.json?auth={self.token_id}",
            on_success=self.on_success,
            on_failure=self.on_failure,
            on_error=self.on_failure,
            method="GET"
        )

    def on_failure(self, req, result):
        self.refresh_id_token()  # chama atualização

    def on_success(self, req, result):
        pass

    def show_error(self, error_message):
        """Display an error message"""
        self.show_message(error_message, color='#FF0000')
    
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
            size_hint_x=0.8,
            theme_bg_color='Custom',
            background_color=get_color_from_hex(color)
        ).open()

    # --- ATUALIZAÇÃO DO TOKEN ---
    def refresh_id_token(self):
        refresh_url = f"https://securetoken.googleapis.com/v1/token?key={self.api_key}"
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }
        data = "&".join([f"{k}={v}" for k, v in payload.items()])

        UrlRequest(
            refresh_url,
            on_success=self.on_refresh_success,
            on_failure=self.on_refresh_failure,
            on_error=self.on_refresh_failure,
            req_body=data,
            req_headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST"
        )

    def on_refresh_success(self, req, result):
        self.token_id = result["id_token"]
        self.refresh_token = result["refresh_token"]  # Firebase pode mandar de novo

    def on_refresh_failure(self, req, result):
        self.show_error('O token não foi renovado')
        Clock.schedule_once(lambda dt: self.show_error('Refaça login no aplicativo'), 1)

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
        """ Cria um chat com o funcionario"""
        month = datetime.today().month
        # Obtém a data atual
        data_atual = datetime.now()

        chat_id = str(uuid.uuid4())
        timestamp = data_atual.strftime('%d/%m/%Y')

        data = {
            'contractor': f'{self.local_id}',
            'employee': f'{self.key}',
            
            "participants": {
                'contractor': 'offline',
                'employee': 'offline'
            },
            "metadata": {
                "created_at": timestamp,
                "last_message": "",
                "last_sender": "",
                "last_timestamp": timestamp
            },
            "historical_messages": {
                'messages_contractor': '[]',
                'messages_employee': '[]'
            },
            'message_offline': {
                'contractor': '[]',
                'employee': '[]'
            }
        }

        UrlRequest(
            f"{self.FIREBASE_URL}/Chats/{chat_id}.json?auth={self.token_id}",
            req_body=json.dumps(data),
            method='PUT',
            on_success=self.final_delete_request,
            on_error=self.signcontroller.handle_signup_error,
            on_failure=self.signcontroller.handle_signup_failure,
            timeout=10
        )

    def on_error(self, req, error):
        pass
    
    def on_failure(self, req, failure):
        pass
    
    def save_contractor_name(self, req, result):
        self.back()
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Functions/{self.key_requests}/.json?auth={self.token_id}'
        UrlRequest(
            url,
            req_body=None,
            method='DELETE',
            on_success=self.final_delete
        )

    def final_delete(self, req, result):
        url = (
            f'https://obra-7ebd9-default-rtdb.firebaseio.com/'
            f'requets/{self.key}.json?auth={self.token_id}'
        )

        UrlRequest(
            url,
            method='DELETE',
            on_success=self.final_delete_request,
            on_error=self.signcontroller.on_error,
            on_failure=self.signcontroller.on_failure
        )

    def final_delete_request(self, req=None, result=None):
        base_url = f"https://obra-7ebd9-default-rtdb.firebaseio.com/Functions/{self.key_requests}.json?auth={self.token_id}"
        url = base_url

        UrlRequest(
            url,
            on_success=self.verific_data_wrapper,  # Use wrapper
            on_error=self.signcontroller.handle_delete_error,
            on_failure=self.signcontroller.handle_delete_failure
        )

    def verific_data_wrapper(self, req, result):
        """Wrapper que armazena req e result antes de chamar verific_data"""
        self.stored_req = req
        self.stored_result = result
        self.verific_data(req, result)

    def final_delete_request(self, req=None, result=None):
        base_url = f"{firebase_url()}/Functions/{self.key_requests}.json?auth={self.token_id}"
        url = base_url

        UrlRequest(
            url,
            on_success=self.verific_data_wrapper,  # Use wrapper
            on_error=self.signcontroller.handle_delete_error,
            on_failure=self.signcontroller.handle_delete_failure
        )

    def verific_data_wrapper(self, req, result):
        """Wrapper que armazena req e result antes de chamar verific_data"""
        self.stored_req = req
        self.stored_result = result
        self.verific_data(req, result)

    def remove_succefuly(self, req, result):
        self.back()
    
    def dispense(self):
        url = f'{firebase_url()}/Functions/{self.key_requests}/.json?auth={self.token_id}'
        UrlRequest(
            url,
            on_success=self.upload_decline
        )
    
    def upload_decline(self, req, result):
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Functions/{self.key_requests}/.json?auth={self.token_id}'
        decline = ast.literal_eval(result['decline'])
        request = ast.literal_eval(result['requests'])
        request.remove(self.key)
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
    def verific_data(self, req, result):
        url = f"https://obra-7ebd9-default-rtdb.firebaseio.com/Functions/{self.key_requests}.json?auth={self.token_id}"
        requisition = ast.literal_eval(result['requests'])
        try:
            requisition.remove(self.key)
        except:
            pass
        data = {
            'requests': f'{requisition}'
        }
        UrlRequest(
            url,
            method='PATCH',
            req_body=json.dumps(data),
            on_success=self.skyfall
        )
        
    def final_decline(self, req, result):
        self.back()

    def skyfall(self, req, result):
        """Método chamado após verific_data"""
        self.back()

    def back(self, *args):
        try:
            app = MDApp.get_running_app()
            screenmanager = app.root
            request = screenmanager.get_screen('RequestContractor')
            request.username = self.username
            request.key = self.key_contractor
            screenmanager.transition = SlideTransition(direction='left')
            screenmanager.current = 'RequestContractor'
        except:
            pass