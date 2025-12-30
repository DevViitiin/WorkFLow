from kivy.properties import StringProperty, BooleanProperty, get_color_from_hex
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivy.network.urlrequest import UrlRequest
from configurations import DialogNoNet, DialogInfinityUpload, DialogErrorUnknow, firebase_url, check_error, SignController


class RequestSent(MDScreen):
    # Propriedades que serão transferidas entre telas
    current_nav_state = StringProperty('payment')
    request = BooleanProperty()
    avatar = StringProperty()
    token_id = StringProperty()
    local_id = StringProperty()
    refresh_token = StringProperty()
    employee_name = StringProperty()
    employee_function = StringProperty()
    employee_mail = StringProperty()
    employee_telephone = StringProperty()
    key = StringProperty()
    employee_summary = StringProperty()
    skills = StringProperty()
    contractor = StringProperty()
    api_key = StringProperty()
    FIREBASE_URL = firebase_url()

    def on_enter(self, *args):
        """
        Evento acionado quando a tela é exibida. 
        Garante que o valor de 'request' seja um booleano real.
        Executa função de verificar o token id de 5 em 5 minutos
        """
        self.request = bool(self.request)
        self.verific_token()
        self.event_token = Clock.schedule_interval(self.verific_token, 300)


    def on_leave(self, *args):
        if hasattr(self, 'event_token'):
            self.event_token.cancel()
            
    def verific_token(self, *args):
        if not self.get_parent_window():
            return

        UrlRequest(
            f"{self.FIREBASE_URL}/Funcionarios/{self.local_id}.json?auth=s{self.token_id}sjwjjdfadsfaesasw",
            on_success=self.on_success,
            on_failure=self.on_failure,
            on_error=self.on_failure,
            method="GET"
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
            size_hint_x=0.8,
            theme_bg_color='Custom',
            background_color=get_color_from_hex(color)
        ).open()

    def show_error(self, error_message):
        """Display an error message"""
        self.show_message(error_message, color='#FF0000')

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

    def on_refresh_failure(self, req, result):
        self.show_error('O token não foi renovado')
        Clock.schedule_once(lambda dt: self.show_error('Refaça login no aplicativo'), 1)

    def _next_screen(self, *args):
        """
        Navega para a tela 'RequestsVacancy' com os dados do funcionário.
        Ativa o ícone de notificações como estado de navegação.
        """
        try:
            app = MDApp.get_running_app()
            screenmanager = app.root

            perfil = screenmanager.get_screen('RequestsVacancy')

            # Transfere dados do funcionário
            perfil.key = self.key
            perfil.token_id = self.token_id 
            perfil.local_id = self.local_id
            perfil.api_key = self.api_key
            perfil.refresh_token = self.refresh_token
            perfil.employee_name = self.employee_name
            perfil.employee_function = self.employee_function
            perfil.employee_mail = self.employee_mail
            perfil.employee_telephone = self.employee_telephone
            perfil.avatar = self.avatar
            perfil.employee_summary = self.employee_summary
            perfil.skills = self.skills
            perfil.tab_nav_state = 'received'
            perfil.request = self.request

            # Estado de navegação
            perfil.current_nav_state = 'perfil'
            perfil.ids.vacancy.active = False
            perfil.ids.perfil.active = False
            perfil.ids.notification.active = True

            # Transição de tela
            self.event_token.cancel()
            screenmanager.transition = SlideTransition(direction='right')
            screenmanager.current = 'RequestsVacancy'
        except:
            self.dialog_error_unknown.open()

    def perfil(self, *args):
        """
        Navega para a tela de perfil do funcionário ('PrincipalScreenEmployee'),
        transfere todos os dados necessários e atualiza a navegação.
        """
        try:
            app = MDApp.get_running_app()
            screenmanager = app.root

            perfil = screenmanager.get_screen('PrincipalScreenEmployee')

            # Transfere dados
            perfil.key = self.key
            perfil.employee_name = self.employee_name
            perfil.employee_function = self.employee_function
            perfil.employee_mail = self.employee_mail
            perfil.employee_telephone = self.employee_telephone
            perfil.avatar = self.avatar
            perfil.employee_summary = self.employee_summary
            perfil.skills = self.skills
            perfil.request = self.request
            perfil.token_id = self.token_id
            perfil.local_id = self.local_id
            perfil.api_Key = self.api_key
            perfil.refresh_token = self.refresh_token

            # Estado de navegação
            perfil.ids.vacancy.active = False
            perfil.ids.notification.active = False
            perfil.ids.perfil.active = True
            perfil.current_nav_state = 'perfil'

            self.tot_salary = 0  # Inicializa salário total

            # Transição de tela
            self.event_token.cancel()
            screenmanager.transition = SlideTransition(direction='right')
            screenmanager.current = 'PrincipalScreenEmployee'
        except:
            self.dialog_error_unknown.open()

    def vacancy(self, *args):
        """
        Navega para a tela de banco de vagas ('VacancyBank'),
        passa todos os dados do funcionário e marca a aba de vagas como ativa.
        """
        try:
            app = MDApp.get_running_app()
            screenmanager = app.root

            vac = screenmanager.get_screen('VacancyBank')

            # Transfere dados
            vac.key = self.key
            vac.employee_name = self.employee_name
            vac.employee_function = self.employee_function
            vac.employee_mail = self.employee_mail
            vac.employee_telephone = self.employee_telephone
            vac.avatar = self.avatar
            vac.employee_summary = self.employee_summary
            vac.skills = self.skills
            vac.contractor = self.contractor
            vac.request = True
            vac.local_id = self.local_id
            vac.token_id = self.token_id
            vac.api_key = self.api_key
            vac.refresh_token = self.refresh_token

            # Estado de navegação
            self.current_nav_state = 'vacancy'
            vac.ids.vacancy.active = True
            vac.ids.perfil.active = False
            vac.ids.notification.active = False

            # Transição de tela
            self.event_token.cancel()
            screenmanager.transition = SlideTransition(direction='right')
            screenmanager.current = 'VacancyBank'
        except:
            self.dialog_error_unknown.open()

    def req(self, *args):
        """
        Navega para a tela 'RequestsVacancy', focando na aba de requisições.
        Transfere os dados do funcionário e configura o estado de navegação.
        """
        try:
            app = MDApp.get_running_app()
            screenmanager = app.root

            vac = screenmanager.get_screen('RequestsVacancy')

            # Transfere dados
            vac.key = self.key
            vac.tab_nav_state = 'request'
            vac.current_nav_state = 'notification'
            vac.employee_name = self.employee_name
            vac.employee_function = self.employee_function
            vac.employee_mail = self.employee_mail
            vac.employee_telephone = self.employee_telephone
            vac.avatar = self.avatar
            vac.employee_summary = self.employee_summary
            vac.skills = self.skills
            vac.token_id = self.token_id
            vac.refresh_token = self.refresh_token
            vac.local_id = self.local_id
            vac.api_key = self.api_key
            vac.request = self.request
            vac.contractor = self.contractor

            # Estado de navegação
            vac.ids.vacancy.active = False
            vac.ids.perfil.active = False
            vac.ids.notification.active = True

            # Transição de tela
            self.event_token.cancel()
            screenmanager.transition = SlideTransition(direction='right')
            screenmanager.current = 'RequestsVacancy'
        except:
            self.dialog_error_unknown.open()
