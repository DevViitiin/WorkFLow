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
from kivymd.uix.snackbar import MDSnackbarText, MDSnackbar
from kivy.metrics import dp
import uuid


class HiringProfile(MDScreen):
    FIREBASE_URL = 'https://obra-7ebd9-default-rtdb.firebaseio.com'
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
        print('A key da requisião é: ', self.key_requests)
        print('A key do funcionario é: ', self.key)
        self.event_token = Clock.schedule_interval(self.verific_token, 300)
        print('Local id: ', self.local_id)
        try:
            skills = eval(self.skills)

        except:
            skills = []

        self.ids.main_scroll.clear_widgets()
        self.add_skills(skills)

    def on_leave(self, *args):
        if hasattr(self, 'event_token'):
            self.event_token.cancel()
            print("⏱️ Clock do token cancelado ao sair da tela")
            
    def verific_token(self, *args):
        if not self.get_parent_window():
            return
        print('🔎 verificando token...')
        UrlRequest(
            f"{self.FIREBASE_URL}/Users/{self.local_id}.json?auth={self.token_id}",
            on_success=self.on_success,
            on_failure=self.on_failure,
            on_error=self.on_failure,
            method="GET"
        )

    def on_failure(self, req, result):
        print('❌ Token inválido, tentando atualizar...', result)
        self.refresh_id_token()  # chama atualização

    def on_success(self, req, result):
        print('✅ Token válido, usuário encontrado:', result)

    def show_error(self, error_message):
        """Display an error message"""
        self.show_message(error_message, color='#FF0000')
        print(f"Error: {error_message}")
    
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
        print("🔄 Token renovado com sucesso:", self.token_id)

    def on_refresh_failure(self, req, result):
        print("❌ Erro ao renovar token:", result)
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
        """ Adicionar o nosso funcionario na equipe I can do it"""
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
            on_error=self.on_error,
            on_failure=self.on_failure,
            timeout=10
        )

    def on_error(self, req, error):
        print('Deu erro no erro: ', error)
    
    def on_failure(self, req, failure):
        print('Deus failure: ', failure)
    
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
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/requets/.json?auth={self.token_id}'

        UrlRequest(
            url,
            on_success=self.upload_requests
        )

    def upload_requests(self, req, result):
        for key, request in result.items():
            if key in self.key:
                UrlRequest(
                    f'https://obra-7ebd9-default-rtdb.firebaseio.com/requets/{self.key}/.json?auth={self.token_id}',
                    method='DELETE',
                    on_success=self.final_delete_request
                )

    def final_delete_request(self, req=None, result=None):
        # tambem tenho que tirar a key do funcionario de Functions
        base_url = f"https://obra-7ebd9-default-rtdb.firebaseio.com/Functions/{self.key_requests}.json?auth={self.token_id}"
        url = base_url

        UrlRequest(
            url,
            on_success=self.verific_data,
        )
        #self.back()

    def verific_data(self, req, result):
        
        print('Verific data: ', result)
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
        print('A nova requisição após remoção é: ', requisition)

    def remove_succefuly(self, req, result):
        print('As requisições foram removidas com sucesso')
        self.back()
    
    def dispense(self):
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Functions/{self.key_requests}/.json?auth={self.token_id}'
        UrlRequest(
            url,
            on_success=self.upload_decline
        )
    
    def upload_decline(self, req, result):
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Functions/{self.key_requests}/.json?auth={self.token_id}'
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

    def skyfall(self, req, result):
        """Método chamado após verific_data"""
        print('Operação skyfall concluída')
        self.back()

    def back(self, *args):
        app = MDApp.get_running_app()
        screenmanager = app.root
        request = screenmanager.get_screen('RequestContractor')
        request.username = self.username
        request.key = self.key_contractor
        screenmanager.transition = SlideTransition(direction='left')
        screenmanager.current = 'RequestContractor'