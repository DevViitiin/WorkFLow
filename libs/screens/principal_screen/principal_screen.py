from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest

class PerfilScreen(MDScreen):
    api_key = StringProperty('AIzaSyA3vFR2WgCdBsyIIL1k9teQNZTi4ZAzhtg')
    username = StringProperty()
    avatar = StringProperty()
    can_add = False
    key = StringProperty()
    city = StringProperty()
    state = StringProperty()
    company = StringProperty()
    telefone = StringProperty()
    local_id = StringProperty()
    token_id = StringProperty()
    email = StringProperty()
    refresh_token = StringProperty()
    contratando = 'Sim'
    function = StringProperty()
    adicionado = 0
    cont = 0
    table = BooleanProperty(False)
    current_nav_state = StringProperty('perfil')
    FIREBASE_URL = 'https://obra-7ebd9-default-rtdb.firebaseio.com'

    def on_enter(self, *args):
        self.verific_perfil()
        self.verific_token()
        self.event_token = Clock.schedule_interval(self.verific_token, 300)
        self.ids.perfil.source = self.avatar
        self.ids.username.text = self.username
        self.ids.company.text = self.company
        print(self.email)
        if 'Não definido' in (self.city, self.state):
            self.ids.locate.text = f'Não definido'
        else:
            self.ids.locate.text = f'{self.city}, {self.state}'
        self.ids.function.text = f'{self.function}'
        self.ids.telefone.text = f'{self.telefone}'
        self.ids.email.text = f'{self.email}'

    def verific_perfil(self):
        if "Não definido" in (self.function, self.email, self.company, self.telefone, self.username, self.city, self.state) or not (self.function, self.email, self.company, self.telefone, self.username, self.city, self.state):
            self.can_add = False
        else:
            self.can_add = True
            
        print('Posso adicionar?: ', self.can_add)

    def verific_token(self):
        print('🔎 verificando token...')
        UrlRequest(
            f"{self.FIREBASE_URL}/Funcionarios/{self.local_id}.json?auth=s{self.token_id}sjwjjdfadsfaesasw",
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
        Clock.schedule_once(lambda dt: self.show_error('Refaça login no aplicativo'), 1)

    def page(self):
        self.manager.current = 'Function'

    def functions(self):
        if self.contratando == 'Sim':
            self.manager.transition = SlideTransition(direction='left')
            app = MDApp.get_running_app()
            screen_manager = app.root
            edit = screen_manager.get_screen('FunctionsScreen')
            edit.contractor = self.username
            edit.occupation = self.function
            edit.token_id = self.token_id
            edit.local_id = self.local_id
            edit.api_key = self.api_key
            edit.can_add = self.can_add
            edit.refresh_token = self.refresh_token
            edit.email = self.email
            edit.key_contractor = self.key
            edit.telephone = self.telefone
            edit.company = self.company
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = 'FunctionsScreen'

    def edit_profile(self):
        print('Chamando tela de editar perfil')
        self.manager.transition = SlideTransition(direction='left')
        app = MDApp.get_running_app()
        screen_manager = app.root
        edit = screen_manager.get_screen('EditProfile')
        edit.name_user = self.username
        edit.email = self.email
        edit.telefone = self.telefone
        edit.state = self.state
        edit.city = self.city
        edit.company = self.company
        edit.avatar = self.avatar
        edit.function = self.function
        edit.token_id = self.token_id
        edit.local_id = self.local_id
        edit.refresh_token = self.refresh_token
        edit.api_key = self.api_key
        self.manager.current = 'EditProfile'

    def search(self):
        app = MDApp.get_running_app()
        print('Passando essa key pra tela de search:', self.key)
        screen_manager = app.root
        screen_manager.transition = SlideTransition(direction='right')
        bricklayer = screen_manager.get_screen('VacancyContractor')
        bricklayer.key_contractor = self.key
        bricklayer.username = self.username
        bricklayer.api_key = self.api_key
        bricklayer.token_id = self.token_id
        bricklayer.refresh_token = self.refresh_token
        bricklayer.local_id = self.local_id
        bricklayer.ids.table.active = False
        bricklayer.can_add = self.can_add
        bricklayer.ids.perfil.active = False
        bricklayer.ids.search.active = True
        bricklayer.ids.request.active = False
        bricklayer.current_nav_state = 'search'
        screen_manager.current = 'VacancyContractor'

    def request(self):
        app = MDApp.get_running_app()
        screen_manager = app.root
        screen_manager.transition = SlideTransition(direction='right')
        bricklayer = screen_manager.get_screen('RequestContractor')
        bricklayer.key = self.key
        bricklayer.ids.table.active = False
        bricklayer.ids.perfil.active = False
        bricklayer.ids.search.active = False
        bricklayer.ids.request.active = True
        bricklayer.current_nav_state = 'request'
        bricklayer.token_id = self.token_id
        bricklayer.api_key = self.api_key
        bricklayer.local_id = self.local_id
        bricklayer.refresh_token = self.refresh_token
        bricklayer.name_contractor = self.username
        screen_manager.current = 'RequestContractor'

    def bricklayer(self):
        app = MDApp.get_running_app()
        screen_manager = app.root
        screen_manager.transition = SlideTransition(direction='right')
        bricklayer = screen_manager.get_screen('Table')
        bricklayer.key = self.key
        bricklayer.username = self.username
        bricklayer.api_key = self.api_key
        bricklayer.token_id = self.token_id
        bricklayer.refresh_token = self.refresh_token
        bricklayer.local_id = self.local_id
        bricklayer.ids.table.active = True
        bricklayer.ids.perfil.active = False
        bricklayer.ids.search.active = False
        bricklayer.ids.request.active = False
        bricklayer.current_nav_state = 'table'
        screen_manager.current = 'Table'
