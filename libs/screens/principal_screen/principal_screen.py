from kivy.properties import BooleanProperty, StringProperty, get_color_from_hex
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivy.metrics import dp
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest

class PerfilScreen(MDScreen):
    api_key = StringProperty()
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        menu_items = [
            {
                "text": f"Item {i}",
                "on_release": lambda x=f"Item {i}": self.menu_callback(x),
            } for i in range(5)
        ]
        menu_itens = []
        row = {
            'text': 'sair',
            'on_release': lambda x="sair": self.menu_callback(x),
            'font_style': "Subtitle1",
            'theme_text_color': 'Custom',
            'text_color': 'red',
            'height': dp(56),
            'icon': "checkbox-marked-circle-outline",
            'divider': "Full"
        }
        row2 = {
            'text': 'Denunciar',
            'on_release': lambda x="Denunciar": self.menu_callback(x),
            'font_style': "Subtitle1",
            'theme_text_color': 'Custom',
            'text_color': get_color_from_hex('#F0C808'),
            'height': dp(56),
            'icon': "checkbox-marked-circle-outline",
            'divider': "Full"
        }
        menu_itens.append(row)
        menu_itens.append(row2)

        self.menu = MDDropdownMenu(
            caller=self.ids.menu,
            items=menu_itens,
            size_hint_x=None,
            position='bottom',
            width_mult=2,
            max_height='300dp',
            #pos_hint={'center_x': 0.5, 'center_y': 0.5},
            elevation=8,
            radius=[10, 10, 10, 10],
            border_margin=12,
            ver_growth="down",
            hor_growth="right",
        )
    
    def menu_callback(self, text_item):
        print(text_item)
        if text_item == 'sair':
            self.manager.current = 'Init'
            self.menu.dismiss()
            
        elif text_item == 'Denunciar':
            print('Entrar na tela de denuncias')
            app = MDApp.get_running_app()
            screenmanager = app.root
            report_screen = screenmanager.get_screen('ReportScreen')
            report_screen.token_id = self.token_id
            report_screen.api_key = self.api_key
            report_screen.name_sender = self.username
            report_screen.email_sender = self.email
            report_screen.local_id = self.local_id
            report_screen.refresh_token = self.refresh_token
            report_screen.perso = 'Contractor'
            screenmanager.transition = SlideTransition(direction='right')
            self.menu.dismiss()
            screenmanager.current = 'ReportScreen'
                  
    def verific_perfil(self):
        if "Não definido" in (self.function, self.email, self.company, self.telefone, self.username, self.city, self.state) or not (self.function, self.email, self.company, self.telefone, self.username, self.city, self.state):
            self.can_add = False
        else:
            self.can_add = True
            
        print('Posso adicionar?: ', self.can_add)

    def on_leave(self, *args):
        if hasattr(self, 'event_token'):
            self.event_token.cancel()
            print("⏱️ Clock do token cancelado ao sair da tela")
            
    def verific_token(self, *args):
        if not self.get_parent_window():
            return
        print('🔎 verificando token...')
        UrlRequest(
            f"{self.FIREBASE_URL}/Users/{self.local_id}.json?auth=s{self.token_id}sjwjjdfadsfaesasw",
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

    def page(self):
        self.manager.current = 'Function'

    def functions(self):
        print('O token id está aqui: ', self.token_id)
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
        bricklayer.can_add = self.can_add
        bricklayer.ids.perfil.active = False
        bricklayer.ids.search.active = True
        bricklayer.ids.chat.active = False
        bricklayer.ids.request.active = False
        bricklayer.current_nav_state = 'search'
        screen_manager.current = 'VacancyContractor'

    def request(self):
        app = MDApp.get_running_app()
        screen_manager = app.root
        screen_manager.transition = SlideTransition(direction='right')
        bricklayer = screen_manager.get_screen('RequestContractor')
        bricklayer.key = self.key
        bricklayer.ids.perfil.active = False
        bricklayer.ids.search.active = False
        bricklayer.ids.request.active = True
        bricklayer.ids.chat.active = False
        bricklayer.current_nav_state = 'request'
        bricklayer.token_id = self.token_id
        bricklayer.api_key = self.api_key
        bricklayer.local_id = self.local_id
        bricklayer.refresh_token = self.refresh_token
        bricklayer.name_contractor = self.username
        screen_manager.current = 'RequestContractor'

    def chat(self, *args):
        app = MDApp.get_running_app()
        screen_manager = app.root
        screen_manager.transition = SlideTransition(direction='right')
        bricklayer = screen_manager.get_screen('ListChatContractor')
        bricklayer.ids.perfil.active = False
        bricklayer.ids.search.active = False
        bricklayer.ids.request.active = False
        bricklayer.ids.perso = 'Contractor'
        bricklayer.ids.chat.active = True
        bricklayer.current_nav_state = 'chat'
        bricklayer.token_id = self.token_id
        bricklayer.api_key = self.api_key
        bricklayer.local_id = self.local_id
        bricklayer.username = self.username
        bricklayer.key_contractor = self.local_id
        bricklayer.refresh_token = self.refresh_token
        screen_manager.current = 'ListChatContractor'
