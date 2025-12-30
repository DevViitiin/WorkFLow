import json
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty, BooleanProperty, get_color_from_hex
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbarText, MDSnackbar
from kivy.clock import Clock
from configurations import (DialogNoNet, DialogInfinityUpload, DialogErrorUnknow, 
                           firebase_url, SignController)


class WithoutContractor(MDScreen):

    """
    Tela exibida quando um funcionário ainda não possui um contratante.

    Esta tela permite que o funcionário envie uma solicitação de contratação e
    navegue entre diferentes telas do aplicativo. Ela gerencia os dados do
    perfil do funcionário e lida com a comunicação com o banco de dados Firebase.

    Atributos:
        current_nav_state (StringProperty): Estado atual da navegação.
        request (BooleanProperty): Indica se uma solicitação de contratação está ativa.
        city (StringProperty): Cidade do funcionário.
        state (StringProperty): Estado do funcionário.
        avatar (StringProperty): Caminho da imagem de avatar do funcionário.
        contractor (StringProperty): Identificador do contratante (se houver).
        employee_name (StringProperty): Nome completo do funcionário.
        employee_function (StringProperty): Função do funcionário.
        employee_mail (StringProperty): Email do funcionário.
        employee_telephone (StringProperty): Telefone do funcionário.
        key (StringProperty): Identificador único do funcionário no banco de dados.
        employee_summary (StringProperty): Resumo profissional do funcionário.
        skills (StringProperty): Habilidades do funcionário, separadas por vírgula.
    """
    current_nav_state = StringProperty()
    request = BooleanProperty(False)
    city = StringProperty()
    state = StringProperty()
    avatar = StringProperty()
    contractor = StringProperty()
    employee_name = StringProperty()
    token_id = StringProperty()
    local_id = StringProperty()
    api_key = StringProperty()
    refresh_token = StringProperty()
    employee_function = StringProperty()
    employee_mail = StringProperty()
    employee_telephone = StringProperty()
    key = StringProperty()
    employee_summary = StringProperty()
    skills = StringProperty()
    FIREBASE_URL = firebase_url()
    req = None
    result = None
    def on_enter(self):
        """
        Executado ao entrar na tela.

        Reinicia o estado da solicitação para garantir uma inicialização adequada.
        """
        self.request = False
        self._setup_dialogs()
        self.verific_token()
        self.event_token = Clock.schedule_interval(self.verific_token, 300)

    def _setup_dialogs(self):
        """Configura os dialogs de erro"""
        self.inf_dialog = DialogInfinityUpload()
        self.signcontroller = SignController(screen=self, name=self.name)
        
        self.dialog_not_net = DialogNoNet(
            subtitle='Não foi possível se conectar. Verifique sua internet e tente novamente',
            callback=lambda: self.signcontroller.retry_signup(self.add_request)
        )
        
        self.dialog_not_net_database = DialogNoNet(
            subtitle='Não foi carregar funções. Verifique sua internet e tente novamente',
            callback=lambda *_: self.signcontroller.retry_handle(
                lambda *_: self.save(self.req, self.result)
            )
        )

        self.dialog_error_unknown = DialogErrorUnknow(screen=f'{self.name}')

    def on_leave(self, *args):
        if hasattr(self, 'event_token'):
            self.event_token.cancel()
            
    def verific_token(self, *args):
        if not self.get_parent_window():
            return
        UrlRequest(
            f"{self.FIREBASE_URL}/Funcionarios/{self.local_id}.json?auth={self.token_id}",
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
        refresh_url = f"https://securetoken.googleapis.com/v1/token?key={self.api_key}?auth={self.token_id}"
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

    def add_request(self):
        """
        Envia uma solicitação de contratação para o banco de dados Firebase.

        Valida se todos os campos obrigatórios estão preenchidos antes de enviar
        a solicitação. Exibe mensagens de feedback apropriadas ao usuário.
        """
        missing_fields = []

        if 'Não definido' in self.employee_mail or not self.employee_mail:
            missing_fields.append("Email")

        if 'Não definido' in self.employee_telephone or not self.employee_telephone:
            missing_fields.append("Telefone")

        if 'Não definido' in self.employee_summary or not self.employee_summary:
            missing_fields.append("Resumo profissional")

        if not self.skills:
            missing_fields.append("Habilidades")

        if not self.city:
            missing_fields.append("Cidade")

        if not self.state:
            missing_fields.append("Estado")

        if missing_fields:
            missing_fields_str = ", ".join(missing_fields)
            self._show_snackbar(
                f'Por favor, preencha os seguintes campos: {missing_fields_str}',
                'red'
            )
            return

        url = f'{firebase_url()}/requets.json?auth={self.token_id}'
        data = {
            'avatar': self.avatar,
            'employee_name': self.employee_name,
            'employee_function': self.employee_function,
            'email': self.employee_mail,
            'telephone': self.employee_telephone,
            'key': self.local_id,
            'receiveds': "[]",
            'city': self.city,
            'state': self.state,
            'employee_summary': self.employee_summary,
            'skills': self.skills,
            'requests': "[]",
            'declines': "[]"
        }

        try:
            UrlRequest(
                url,
                method='POST',
                req_body=json.dumps(data),
                on_success=self.save,
                on_error=self.signcontroller.handle_signup_error,
                on_failure=self.signcontroller.handle_signup_failure,
                timeout=10
            )
        except Exception as e:
            self._show_snackbar(
                f'Erro ao enviar solicitação: {str(e)}',
                'red'
            )

    def _show_snackbar(self, text, bg_color='red'):
        """
        Método auxiliar para exibir um snackbar com o texto e a cor de fundo fornecidos.

        Args:
            text (str): Mensagem a ser exibida no snackbar.
            bg_color (str, opcional): Cor de fundo do snackbar. Padrão: 'red'.
        """
        MDSnackbar(
            MDSnackbarText(
                text=text,
                theme_text_color='Custom',
                text_color='white',
                bold=True
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            halign='center',
            size_hint_x=0.9,
            theme_bg_color='Custom',
            background_color=bg_color
        ).open()

    def error(self, request, error):
        """
        Callback para lidar com erros na solicitação.

        Args:
            request: Objeto da solicitação que gerou o erro.
            error: Informações do erro.
        """
        error_message = f"Erro na solicitação: {error}"
        self._show_snackbar(error_message, 'red')

    def on_failure(self, request, result):
        """
        Callback para lidar com falhas na solicitação (ex: problemas de rede).

        Args:
            request: Objeto da solicitação que falhou.
            result: Informações da falha.
        """
        self._show_snackbar("Falha na conexão. Verifique sua internet e tente novamente.", 'red')

    def save(self, req, result):
        """
        Atualiza o status do funcionário para indicar que há uma solicitação ativa.

        Chamado quando a solicitação de contratação é enviada com sucesso ao banco de dados.
        Atualiza o registro do funcionário para marcar que ele tem uma solicitação ativa.

        Args:
            req: Objeto da solicitação.
            result: Dados de retorno da solicitação.
        """
        url = f'{firebase_url()}/Funcionarios/{self.local_id}/.json?auth={self.token_id}'
        data = {'request': 'True'}
        self.request = True

        try:
            UrlRequest(
                url,
                method='PATCH',
                req_body=json.dumps(data),
                on_success=self.finally_screen,
                on_error=self.signcontroller.on_error,
                on_failure=self.signcontroller.on_failure,
                timeout=10
            )
        except Exception as e:
            self._show_snackbar(
                f'Erro ao atualizar status: {str(e)}',
                'red'
            )

    def finally_screen(self, instance, result):
        """
        Navega para a tela de confirmação após uma solicitação bem-sucedida.

        Transfere todos os dados relevantes do funcionário para a próxima tela e
        atualiza o estado da navegação.

        Args:
            instance: Instância da solicitação.
            result: Dados retornados da solicitação.
        """
        self.signcontroller.close_all_dialogs()
        try:
            app = MDApp.get_running_app()
            screenmanager = app.root
            perfil = screenmanager.get_screen('RequestSent')

            self._transfer_data_to_screen(perfil)

            perfil.tab_nav_state = 'received'
            perfil.current_nav_state = 'perfil'

            perfil.ids.vacancy.active = True
            perfil.ids.perfil.active = False
            perfil.refresh_token = self.refresh_token
            perfil.local_id = self.local_id
            perfil.token_id = self.token_id
            perfil.api_key = self.api_key
            perfil.ids.notification.active = False

            self._show_snackbar("Solicitação enviada com sucesso!", 'green')

            screenmanager.transition = SlideTransition(direction='right')
            screenmanager.current = 'RequestSent'
            
        except Exception as e:
            self.dialog_error_unknown.open()

    def _transfer_data_to_screen(self, target_screen):
        """
        Método auxiliar para transferir todos os dados do funcionário para outra tela.

        Args:
            target_screen: Tela de destino para onde os dados serão enviados.
        """
        try:
            target_screen.key = self.key
            target_screen.employee_name = self.employee_name
            target_screen.employee_function = self.employee_function
            target_screen.employee_mail = self.employee_mail
            target_screen.employee_telephone = self.employee_telephone
            target_screen.avatar = self.avatar
            target_screen.token_id = self.token_id
            target_screen.local_id = self.local_id
            target_screen.refresh_token = self.refresh_token
            target_screen.api_key = self.api_key
            target_screen.employee_summary = self.employee_summary
            target_screen.skills = self.skills
            target_screen.request = self.request
            target_screen.state = self.state
            target_screen.city = self.city

            if hasattr(self, 'contractor'):
                target_screen.contractor = self.contractor
        except:
            self.dialog_error_unknown.open()

    def _next_screen(self):
        """
        Navega para a tela de solicitações de vagas de emprego.

        Transfere os dados do funcionário e atualiza o estado da navegação.
        """
        try:
            app = MDApp.get_running_app()
            screenmanager = app.root
            perfil = screenmanager.get_screen('RequestsVacancy')

            self._transfer_data_to_screen(perfil)

            perfil.tab_nav_state = 'received'
            perfil.current_nav_state = 'perfil'
            perfil.refresh_token = self.refresh_token
            perfil.local_id = self.local_id
            perfil.token_id = self.token_id
            perfil.api_key = self.api_key

            perfil.ids.vacancy.active = False
            perfil.ids.perfil.active = False
            perfil.ids.notification.active = True

            screenmanager.transition = SlideTransition(direction='right')
            screenmanager.current = 'RequestsVacancy'
        except Exception as e:
            self.dialog_error_unknown.open()

    def perfil(self):
        """
        Navega para a tela de perfil do funcionário.

        Transfere os dados do funcionário e atualiza o estado da navegação.
        """
        try:
            app = MDApp.get_running_app()
            screenmanager = app.root
            perfil = screenmanager.get_screen('PrincipalScreenEmployee')

            self._transfer_data_to_screen(perfil)

            perfil.ids.vacancy.active = False
            perfil.ids.notification.active = False
            perfil.ids.perfil.active = True
            perfil.refresh_token = self.refresh_token
            perfil.local_id = self.local_id
            perfil.token_id = self.token_id
            perfil.api_key = self.api_key
            perfil.current_nav_state = 'perfil'

            if hasattr(self, 'tot_salary'):
                self.tot_salary = 0

            screenmanager.transition = SlideTransition(direction='right')
            screenmanager.current = 'PrincipalScreenEmployee'
        except Exception as e:
            self.dialog_error_unknown.open()

    def vacancy(self):
        """
        Navega para a tela de banco de vagas.

        Transfere os dados do funcionário e atualiza o estado da navegação.
        """
        try:
            app = MDApp.get_running_app()
            screenmanager = app.root
            vac = screenmanager.get_screen('VacancyBank')

            self._transfer_data_to_screen(vac)

            self.current_nav_state = 'vacancy'
            vac.refresh_token = self.refresh_token
            vac.local_id = self.local_id
            vac.token_id = self.token_id
            vac.api_key = self.api_key

            vac.ids.vacancy.active = True
            vac.ids.perfil.active = False
            vac.ids.notification.active = False

            screenmanager.transition = SlideTransition(direction='right')
            screenmanager.current = 'VacancyBank'
        except Exception as e:
            self.dialog_error_unknown.open()

    def req(self):
        """
        Navega para a tela de solicitações recebidas.

        Transfere os dados do funcionário e atualiza o estado da navegação.
        """
        try:
            app = MDApp.get_running_app()
            screenmanager = app.root
            vac = screenmanager.get_screen('RequestsVacancy')

            self._transfer_data_to_screen(vac)

            vac.tab_nav_state = 'request'

            vac.ids.vacancy.active = False
            vac.ids.perfil.active = False
            vac.ids.request.active = False
            vac.ids.notification.active = True
            vac.refresh_token = self.refresh_token
            vac.local_id = self.local_id
            vac.token_id = self.token_id
            vac.api_key = self.api_key

            screenmanager.transition = SlideTransition(direction='right')
            screenmanager.current = 'RequestsVacancy'
        except Exception as e:
            self.dialog_error_unknown.open()
