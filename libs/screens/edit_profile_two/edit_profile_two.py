import json
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty, get_color_from_hex
from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.progressindicator import MDCircularProgressIndicator
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from libs.screens.edit_profile_two.citys import *
from configurations import DialogNoNet, DialogInfinityUpload, DialogErrorUnknow, firebase_url, check_error, SignController
from kivy.clock import Clock


class EditProfileTwo(MDScreen):
    token_id = StringProperty()
    local_id = StringProperty()
    api_key = StringProperty()
    refresh_token = StringProperty()
    name_user = StringProperty('Solitude')
    city = StringProperty('brasilia')
    state = StringProperty('distrito federal')
    company = StringProperty()
    avatar = StringProperty()
    function = StringProperty('Mestre de obra')
    email = StringProperty()
    telefone = StringProperty()
    FIREBASE_URL = 'https://obra-7ebd9-default-rtdb.firebaseio.com'
    # Inicalizando o programa e carregando as variaveis

    def on_enter(self, *args):
        if self.local_id and self.token_id:
            pass

        if self.company not in "Não definido":
            self.ids.company.text = self.company

        # ====================== popups =============================
        self.inf_dialog = DialogInfinityUpload()
        self.signcontroller = SignController(screen=self, name=self.name)        
        self.dialog_not_net = DialogNoNet(
            subtitle='Não foi possível se conectar. Verifique sua internet e tente novamente',
            callback=lambda: self.signcontroller.retry_signup(self.step_two)
        )
        
        self.dialog_error_unknown = DialogErrorUnknow(
            screen=f'{self.name}'
        )

        self.ids.state.text = self.state
        self.ids.state.text_color = 'white'
        self.ids.function.text = f'{self.function}'
        self.ids.city.text = self.city
        self.ids.city.text_color = 'white'
        self.verific_token()
        self.event_token = Clock.schedule_interval(self.verific_token, 300)
        self.menu_states()
        self.menu_citys()
        self.menu_functions()
        
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
        
    def menu_functions(self):
        # Abrir um popup de menu para a pessoa escolher o seu estado
        states = [
            # Profissionais de nível superior
            "Engenheiro Civil",
            "Engenheiro de Produção Civil",
            "Engenheiro de Estruturas",
            "Engenheiro de Transportes",
            "Engenheiro de Geotecnia",
            "Engenheiro de Saneamento",
            "Engenheiro de Segurança do Trabalho",
            "Engenheiro Hidráulico",
            "Engenheiro de Materiais",
            "Engenheiro Ambiental",
            "Arquiteto e Urbanista",
            "Tecnólogo em Construção Civil",
            "Tecnólogo em Estruturas",
            "Tecnólogo em Edificações",

            # Profissionais técnicos
            "Técnico em Edificações",
            "Técnico em Construção Civil",
            "Técnico em Estradas",
            "Técnico em Geoprocessamento",
            "Técnico em Saneamento",
            "Técnico em Segurança do Trabalho",
            "Técnico em Topografia",
            "Técnico em Materiais de Construção",

            # Mão de obra especializada
            "Mestre de Obras",
            "Contramestre de Obras",
            "Pedreiro",
            "Azulejista",
            "Carpinteiro de Obras",
            "Carpinteiro de Esquadrias",
            "Armador de Ferragens",
            "Encanador",
            "Eletricista de Obras",
            "Pintor de Obras",
            "Gesseiro",
            "Vidraceiro",
            "Caldeireiro de Estruturas Metálicas",
            "Montador de Estruturas Metálicas",
            "Soldador de Estruturas",
            "Rejuntador",

            # Outros relacionados
            "Servente de Obras",
            "Operador de Betoneira",
            "Operador de Máquinas Pesadas",
            "Topógrafo",
            "Calceteiro",
            "Impermeabilizador",
            "Escorador",
            "Ladrilheiro",
            "Marceneiro de Obras",
            "Serralheiro",
            "Apontador de Obras",
            "Pavimentador"
        ]

        menu_itens = []
        position = 0
        for state in states:
            position += 1
            row = {'text': state, 'on_release': lambda x=state: self.replace_function(x)}
            menu_itens.append(row)

        self.menu2 = MDDropdownMenu(
            caller=self.ids.card_function,
            items=menu_itens,
            position='bottom',
            size_hint_x=None,
            width_mult=5,
            max_height='400dp',
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            # Adicionando personalizações estéticas
            elevation=8,
            radius=[10, 10, 10, 10],
            border_margin=12,
            ver_growth="down",
            hor_growth="right",
        )

        # Estilizando os itens do menu
        for item in menu_itens:
            item["font_style"] = "Subtitle1"
            item["height"] = dp(56)
            # Adicione ícones aos itens
            if "icon" not in item:
                item["icon"] = "checkbox-marked-circle-outline"
            item["divider"] = "Full"

    def replace_function(self, text):
        self.ids.function.text = text
        self.ids.function.text_color = get_color_from_hex('#FFFB46')
        self.menu2.dismiss()

    def menu_states(self):
        # Abrir um popup de menu para a pessoa escolher o seu estado
        states = ['Acre', 'Alagoas', 'Amapá', 'Amazonas', 'Bahia', 'Ceará',
                  'Distrito Federal', 'Espírito Santo', 'Goiás', 'Maranhão', 'Mato Grosso',
                  'Mato Grosso do Sul',
                  'Minas Gerais', 'Pará', 'Paraíba', 'Paraná',
                  'Pernambuco', 'Piauí', 'Rio de Janeiro', 'Rio Grande do Norte',
                  'Rio Grande do Sul', 'Rondônia', 'Roraima', 'Santa Catarina', 'São Paulo',
                  'Sergipe', 'Tocantins']

        menu_itens = []
        position = 0
        for state in states:
            position += 1
            row = {'text': state, 'on_release': lambda x=state: self.replace_state(x)}
            menu_itens.append(row)

        self.menu = MDDropdownMenu(
            caller=self.ids.card_state,
            items=menu_itens,
            position='bottom',
            size_hint_x=None,
            width_mult=1,
            max_height='300dp',
            pos_hint={'center_x': 0.5}
        )

    def menu_citys(self):
        menu_itens = []
        payments = ['Cidades indisponiveis']
        for payment in payments:
            row = {'text': payment, 'text_color': 'red'}
            menu_itens.append(row)

        self.menu_city = MDDropdownMenu(
            caller=self.ids.card_city,
            items=menu_itens,
            position='bottom',
            width_mult=3,
            max_height='400dp',
            pos_hint={'center_x': 0.5}
        )

    def create_menu(self, state):

        menu_items = []

        state_functions = {
            'Acre': acre,
            'Alagoas': alagoas,
            'Amapá': amapa,
            'Amazonas': amazonas,
            'Bahia': bahia,
            'Ceará': ceara,
            'Distrito Federal': distrito_federal,
            'Espírito Santo': espirito_santo,
            'Goiás': goias,
            'Maranhão': maranhao,
            'Mato Grosso': mato_grosso,
            'Mato Grosso do Sul': mato_grosso_do_sul,
            'Minas Gerais': minas_gerais,
            'Pará': para,
            'Paraíba': paraiba,
            'Paraná': parana,
            'Pernambuco': pernambuco,
            'Piauí': piaui,
            'Rio de Janeiro': rio_de_janeiro,
            'Rio Grande do Norte': rio_grande_do_norte,
            'Rio Grande do Sul': rio_grande_do_sul,
            'Rondônia': rondonia,
            'Roraima': roraima,
            'Santa Catarina': santa_catarina,
            'São Paulo': sao_paulo,
            'Sergipe': sergipe,
            'Tocantins': tocantins,
        }

        if state in state_functions:
            cities = state_functions[state]()
            for city in cities:
                row = {'text': city, 'on_release': lambda x=city: self.replace_city(x)}
                menu_items.append(row)
        else:
            pass

        self.menu_city.clear_widgets()
        self.menu_city = MDDropdownMenu(
            caller=self.ids.card_city,
            items=menu_items,
            position='bottom',
            size_hint_x=None,
            width_mult=2,
            max_height='400dp',
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

    # Ações dos widgets
    def replace_state(self, state):
        self.ids.city.text_color = get_color_from_hex('#FFFB46')
        self.ids.city.text = 'Selecione uma Cidade'
        self.ids.state.text_color = get_color_from_hex('#FFFB46')
        self.ids.state.text = f'{state}'
        self.menu.dismiss()
        self.create_menu(state)

    def replace_city(self, city):
        self.ids.city.text_color = get_color_from_hex('#FFFB46')
        self.ids.city.text = city
        self.menu_city.dismiss()

    # manipulando o banco de dados
    def step_one(self):
        # Get all the information
        state = self.ids.state.text
        city = self.ids.city.text
        function = self.ids.function.text
        company = self.ids.company.text
        if function in 'Selecione uma profissão':
            self.menu2.open()
            return

        if state in 'Selecione um Estado':
            self.menu.open()
            return

        if city in 'Selecione uma Cidade':
            self.menu_city.open()
            return

        if not company:
            self.ids.company.focus = True
            return

        def show_snackbar():
            MDSnackbar(
                MDSnackbarText(
                    text="Apresente novos dados para atualização",
                    theme_text_color='Custom',
                    text_color='white',
                    bold=True
                ),
                y=dp(24),
                pos_hint={"center_x": 0.5},
                halign='center',
                size_hint_x=0.85,
                theme_bg_color='Custom',
                background_color=get_color_from_hex('#00b894')
            ).open()

        # Verificação otimizada
        if self.state == state and self.city == city and self.company == self.ids.company.text and self.ids.function.text == self.function:
            show_snackbar()
            return

        self.step_two()

    def step_two(self):
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Users/{self.local_id}'

        if not self.ids.company.text:
            data = {
                'city': self.ids.city.text,
                'state': self.ids.state.text
            }
        else:
            data = {
                'city': self.ids.city.text,
                'state': self.ids.state.text,
                'company': self.ids.company.text,
                'function': self.ids.function.text
            }

        UrlRequest(
            url=f'{url}/.json?auth={self.token_id}',
            method='PATCH',
            req_body=json.dumps(data),
            on_success=self.database,
            on_error=self.signcontroller.handle_signup_error,
            on_failure=self.signcontroller.handle_signup_failure
        )

    def database(self, req, result):

        self.signcontroller.close_all_dialogs()
        self.login_variables()

    # Definindo a tela anterior
    def previous(self, *args):
        try:
            app = MDApp.get_running_app()
            screen_manager = app.root
            edit = screen_manager.get_screen('EditProfile')
            edit.token_id = self.token_id
            edit.local_id = self.local_id
            edit.refresh_token = self.refresh_token
            edit.api_key = self.api_key
            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = 'EditProfile'
        except:
            Clock.schedule_once(lambda dt: self.dialog_error_unknown.open(), 1)

    def login_variables(self, *args):
        try:
            app = MDApp.get_running_app()
            screen_manager = app.root
            perfil = screen_manager.get_screen('Perfil')
            perfil.username = self.name_user
            perfil.company = self.ids.company.text
            perfil.state = self.ids.state.text
            perfil.function = self.ids.function.text
            perfil.city = self.ids.city.text
            perfil.email = self.email
            perfil.token_id = self.token_id
            perfil.local_id = self.local_id
            perfil.refresh_token = self.refresh_token
            perfil.api_key = self.api_key
            perfil.telefone = self.telefone
            perfil.avatar = self.avatar
            self.manager.current = 'Perfil'
        except:
            Clock.schedule_once(lambda dt: self.dialog_error_unknown.open(), 1)

