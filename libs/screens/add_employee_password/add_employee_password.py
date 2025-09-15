from kivy.properties import StringProperty, get_color_from_hex
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
import bcrypt
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest

class AddEmployeePassword(MDScreen):
    # Contratante
    token_id = StringProperty()
    api_key = StringProperty()
    local_id = StringProperty()
    refresh_token = StringProperty()
    employee_name = StringProperty()
    function = StringProperty()
    password = StringProperty()
    email = StringProperty()
    contractor = StringProperty()
    method_salary = StringProperty()
    salary = StringProperty()
    scale = StringProperty()
    FIREBASE_URL = 'https://obra-7ebd9-default-rtdb.firebaseio.com'

    def on_enter(self):
        self.verific_token()
        self.event_token = Clock.schedule_interval(self.verific_token, 300)

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
        Clock.schedule_once(self.show_error('Refaça login no aplicativo'), 1.5)

    def hashed_password(self):
        print('Error: ', self.ids.email.error)
        password = self.ids.password.text
        if len(password) >= 8 and self.ids.email.error == False:
            self.email = self.ids.email.text
            hashed_password = self.ids.password.text.encode('utf-8')
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password=hashed_password, salt=salt).decode('utf-8')

            # Exibir a senha criptografada
            print('A senha criptgrafada é: ', hashed_password)
            self.next_page(hashed_password)
        else:
            self.show_message('As informações não atendem os requisitos', color="#FF0404")
            Clock.schedule_once(lambda dt: self.show_message('Ajuste as informações e tente novamente', color="#FF0404"), 2)

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

    def show_error(self, error_message):
        """Display an error message"""
        self.show_message(error_message, color='#FF0000')
        print(f"Error: {error_message}")

    def back_table(self, *args):
        self.manager.transition = SlideTransition(direction='left')
        app = MDApp.get_running_app()
        screen_manager = app.root
        employee_avatar = screen_manager.get_screen('Add')
        employee_avatar.token_id = self.token_id
        employee_avatar.api_key = self.api_key
        employee_avatar.local_id = self.local_id
        employee_avatar.refresh_id = self.refresh_token
        employee_avatar.password = self.ids.password.text
        self.ids.password.text = ''
        screen_manager.current = 'Add'

    def next_page(self, passsword, *args):
        self.manager.transition = SlideTransition(direction='left')
        app = MDApp.get_running_app()
        screen_manager = app.root
        employee_avatar = screen_manager.get_screen('EmployeeAvatar')
        employee_avatar.employee_name = self.employee_name
        employee_avatar.function = self.function
        employee_avatar.salary = self.salary
        employee_avatar.contractor = self.contractor
        employee_avatar.method_salary = self.method_salary
        employee_avatar.scale = self.scale
        employee_avatar.token_id = self.token_id
        employee_avatar.api_key = self.api_key
        employee_avatar.email = self.email
        employee_avatar.local_id = self.local_id
        employee_avatar.refresh_id = self.refresh_token
        employee_avatar.password = self.ids.password.text
        self.ids.password.text = ''
        screen_manager.current = 'EmployeeAvatar'