from kivy.properties import StringProperty, get_color_from_hex, BooleanProperty, NumericProperty
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
import logging
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class PrincipalScreenEmployee(MDScreen):
    """
    Tela principal do perfil do funcionário.

    Esta classe gerencia a exibição e interação com o perfil do funcionário,
    incluindo informações pessoais, habilidades e navegação para outras telas.

    Attributes:
        current_nav_state (StringProperty): Estado atual da navegação.
        avatar (StringProperty): Caminho para a imagem do avatar do funcionário.
        request (BooleanProperty): Indica se há uma solicitação pendente.
        city (StringProperty): Cidade do funcionário.
        state (StringProperty): Estado do funcionário.
        employee_name (StringProperty): Nome do funcionário.
        contractor (StringProperty): Identificador do contratante.
        employee_function (StringProperty): Função do funcionário.
        employee_mail (StringProperty): Email do funcionário.
        employee_telephone (StringProperty): Telefone do funcionário.
        key (StringProperty): Chave única de identificação do funcionário.
        salary (NumericProperty): Salário do funcionário.
        employee_summary (StringProperty): Resumo profissional do funcionário.
        skills (StringProperty): Habilidades do funcionário em formato de string.
    """
    current_nav_state = StringProperty('perfil')
    api_key = StringProperty()
    token_id = StringProperty()
    local_id = StringProperty()
    refresh_token = StringProperty()
    avatar = StringProperty()
    request = BooleanProperty()
    city = StringProperty()
    state = StringProperty()
    employee_name = StringProperty()
    contractor = StringProperty()
    employee_function = StringProperty()
    employee_mail = StringProperty()
    employee_telephone = StringProperty()
    data_contractor = StringProperty()
    key = StringProperty()
    salary = NumericProperty() 
    employee_summary = StringProperty()
    skills = StringProperty()
    FIREBASE_URL = 'https://obra-7ebd9-default-rtdb.firebaseio.com'

    def on_enter(self):
        """
        Método chamado quando a tela é exibida.

        Inicializa o estado da navegação e carrega as habilidades do funcionário.
        """
        print('O safado do contratante é: ', self.contractor)
        try:
            logging.info(f'Acessando tela de funcionário com key: {self.key}')
            # Garantir que apenas o ícone de perfil esteja ativo
            self.current_nav_state = 'perfil'

            # Verificar se os IDs existem antes de acessá-los
            if hasattr(self.ids, 'perfil') and hasattr(self.ids, 'vacancy'):
                self.ids.perfil.active = True
                self.ids.vacancy.active = False
            else:
                logging.error("IDs de navegação não encontrados")

            # Carregar habilidades
            self._load_skills()
        except Exception as e:
            logging.error(f"Erro ao inicializar tela: {str(e)}")
            self._show_error_message("Erro ao carregar dados do perfil")
        self.verific_token()
        self.event_token = Clock.schedule_interval(self.verific_token, 300)


    def verific_token(self, *args):
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
        print('✅ Token válido, usuário encontrado:')


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

    def _load_skills(self):
        """
        Método interno para carregar as habilidades do funcionário.

        Tenta converter a string de habilidades em uma lista e chama o método
        para adicionar as habilidades à UI.
        """
        try:
            skills = eval(self.skills) if self.skills else []
        except (SyntaxError, NameError, TypeError) as e:
            logging.warning(f"Erro ao interpretar habilidades: {str(e)}")
            skills = []

        try:
            if hasattr(self.ids, 'main_scroll'):
                self.ids.main_scroll.clear_widgets()
                self.skill_add = 0
                self.add_skills(skills)
            else:
                logging.error("Container de habilidades não encontrado")
        except Exception as e:
            logging.error(f"Erro ao adicionar habilidades: {str(e)}")

    def add_skills(self, skills):
        """
        Adiciona as habilidades do funcionário na tela.

        Args:
            skills (list): Lista de habilidades do funcionário.
        """
        try:
            if not hasattr(self.ids, 'main_scroll'):
                logging.error("Container de habilidades não encontrado")
                return

            self.ids.main_scroll.clear_widgets()

            if skills:
                for skill in skills:
                    try:
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
                    except Exception as e:
                        logging.error(f"Erro ao criar botão para habilidade '{skill}': {str(e)}")
            else:
                button = MDButton(
                    MDButtonText(
                        text='Nenhuma habilidade adicionada',
                        theme_text_color='Custom',
                        text_color='white',
                        bold=True
                    ),
                    theme_bg_color='Custom',
                    md_bg_color=get_color_from_hex('#0047AB')
                )
                self.ids.main_scroll.add_widget(button)
        except Exception as e:
            logging.error(f"Erro ao adicionar habilidades: {str(e)}")
            self._show_error_message("Erro ao exibir habilidades")

    def _next_profile_edit(self, *args):
        """
        Navega para a tela de edição de perfil e passa os dados do funcionário.
        """
        try:
            app = MDApp.get_running_app()
            if not app:
                logging.error("Aplicativo não encontrado")
                return

            screenmanager = app.root
            if not screenmanager:
                logging.error("Gerenciador de telas não encontrado")
                return

            # Verifica se a tela existe
            perfil = screenmanager.get_screen('EditEmployee')
            if not perfil:
                logging.error("Tela de edição não encontrada")
                return

            # Transfere os dados para a tela de edição
            perfil.employee_name = self.employee_name
            perfil.employee_function = self.employee_function
            perfil.employee_mail = self.employee_mail
            perfil.employee_telephone = self.employee_telephone
            perfil.key = self.key
            perfil.api_key = self.api_key
            perfil.avatar = self.avatar
            perfil.employee_summary = self.employee_summary
            perfil.skills = self.skills
            perfil.token_id = self.token_id
            perfil.local_id = self.local_id
            perfil.refresh_token = self.refresh_token
            perfil.city = self.city
            perfil.state = self.state

            # Navega para a tela de edição
            screenmanager.transition = SlideTransition(direction='left')
            screenmanager.current = 'EditEmployee'
            logging.info(f"Navegando para edição de perfil do funcionário: {self.employee_name}")
        except Exception as e:
            logging.error(f"Erro ao navegar para edição de perfil: {str(e)}")
            self._show_error_message("Erro ao acessar edição de perfil")

    def vacancy(self, *args):
        """
        Navega para a tela de vagas e ajusta o estado global de navegação.
        """
        try:
            app = MDApp.get_running_app()
            if not app:
                logging.error("Aplicativo não encontrado")
                return

            screenmanager = app.root
            if not screenmanager:
                logging.error("Gerenciador de telas não encontrado")
                return

            # Verifica se a tela existe
            try:
                vac = screenmanager.get_screen('VacancyBank')
            except Exception as e:
                logging.error(f"Tela de vagas não encontrada: {str(e)}")
                self._show_error_message("Tela de vagas não disponível")
                return

            # Transfere os dados do usuário
            vac.key = self.key
            vac.api_key = self.api_key
            vac.refresh_token = self.refresh_token
            vac.local_id = self.local_id
            vac.token_id = self.token_id
            logging.info(f"Acessando banco de vagas com key: {self.key}")
            vac.employee_name = self.employee_name
            vac.employee_function = self.employee_function
            vac.employee_mail = self.employee_mail
            vac.employee_telephone = self.employee_telephone
            vac.avatar = self.avatar
            vac.employee_summary = self.employee_summary
            vac.skills = self.skills
            vac.contractor = self.contractor
            vac.request = self.request
            vac.city = self.city
            vac.state = self.state

            # Define o estado de navegação global
            self.current_nav_state = 'vacancy'

            # Atualiza a navegação visualmente
            if all(hasattr(vac.ids, attr) for attr in ['vacancy', 'perfil', 'notification', 'payment']):
                vac.ids.vacancy.active = True
                vac.ids.perfil.active = False
                vac.ids.notification.active = False
                vac.ids.payment.active = False
            else:
                logging.warning("Alguns elementos de navegação não encontrados")

            # Navega para a tela de vagas
            screenmanager.transition = SlideTransition(direction='right')
            screenmanager.current = 'VacancyBank'
        except Exception as e:
            logging.error(f"Erro ao navegar para tela de vagas: {str(e)}")
            self._show_error_message("Erro ao acessar banco de vagas")

    def req(self, *args):
        """
        Navega para a tela de solicitações de vagas.
        """
        try:
            app = MDApp.get_running_app()
            if not app:
                logging.error("Aplicativo não encontrado")
                return

            screenmanager = app.root
            if not screenmanager:
                logging.error("Gerenciador de telas não encontrado")
                return

            # Verifica se a tela existe
            try:
                vac = screenmanager.get_screen('RequestsVacancy')
            except Exception as e:
                logging.error(f"Tela de solicitações não encontrada: {str(e)}")
                self._show_error_message("Tela de solicitações não disponível")
                return

            # Transfere os dados do usuário
            vac.key = self.key
            vac.token_id = self.token_id
            vac.refresh_token = self.refresh_token
            vac.local_id = self.local_id
            vac.tab_nav_state = 'request'
            vac.employee_name = self.employee_name
            vac.employee_function = self.employee_function
            vac.employee_mail = self.employee_mail
            vac.employee_telephone = self.employee_telephone
            vac.avatar = self.avatar
            vac.employee_summary = self.employee_summary
            vac.skills = self.skills
            vac.request = self.request
            vac.city = self.city
            vac.api_key = self.api_key
            vac.state = self.state
            vac.contractor = self.contractor

            # Atualiza a navegação visualmente
            if all(hasattr(vac.ids, attr) for attr in ['vacancy', 'perfil', 'request', 'notification']):
                vac.ids.vacancy.active = False
                vac.ids.perfil.active = False
                vac.ids.request.active = True
                vac.ids.notification.active = True
            else:
                logging.warning("Alguns elementos de navegação não encontrados")

            # Navega para a tela de solicitações
            screenmanager.transition = SlideTransition(direction='right')
            screenmanager.current = 'RequestsVacancy'
            logging.info(f"Navegando para solicitações de vagas do funcionário: {self.employee_name}")
        except Exception as e:
            logging.error(f"Erro ao navegar para tela de solicitações: {str(e)}")
            self._show_error_message("Erro ao acessar solicitações")

    def requests(self):
        """
        Gerencia a navegação para as telas de solicitações com base no estado atual do funcionário.

        Redireciona para diferentes telas dependendo do estado do contratante e das solicitações.
        """
        try:
            logging.info(f"Processando solicitações - contractor: {self.contractor}, request: {self.request}")
            app = MDApp.get_running_app()
            if not app:
                logging.error("Aplicativo não encontrado")
                return

            screen = app.root
            if not screen:
                logging.error("Gerenciador de telas não encontrado")
                return

            # Verifica o estado do contratante
            if not self.contractor:
                # Sem contratante e sem solicitação
                if not self.request:
                    self._navigate_to_screen(screen, 'WithoutContractor')
                # Sem contratante, mas com solicitação enviada
                else:
                    self._navigate_to_screen(screen, 'RequestSent')
            # Com contratante
            else:
                self._navigate_to_screen(screen, 'ReviewScreen')
        except Exception as e:
            logging.error(f"Erro ao processar solicitações: {str(e)}")
            self._show_error_message("Erro ao processar solicitações")

    def _navigate_to_screen(self, screen_manager, screen_name, *args):
        """
        Método auxiliar para navegar para uma tela específica.

        Args:
            screen_manager: Gerenciador de telas do aplicativo.
            screen_name (str): Nome da tela para a qual navegar.
        """
        try:
            # Verifica se a tela existe
            destination_screen = screen_manager.get_screen(screen_name)
            if not destination_screen:
                logging.error(f"Tela {screen_name} não encontrada")
                return

            # Transfere os dados do usuário
            destination_screen.key = self.key
            destination_screen.employee_name = self.employee_name
            destination_screen.employee_function = self.employee_function
            destination_screen.employee_mail = self.employee_mail
            destination_screen.employee_telephone = self.employee_telephone
            destination_screen.avatar = self.avatar
            destination_screen.employee_summary = self.employee_summary
            destination_screen.skills = self.skills
            destination_screen.data_contractor = self.data_contractor
            destination_screen.city = self.city
            destination_screen.state = self.state
            destination_screen.request = self.request
            destination_screen.contractor = self.contractor
            destination_screen.token_id = self.token_id
            destination_screen.local_id = self.local_id
            destination_screen.api_key = self.api_key
            destination_screen.refresh_token = self.refresh_token

            # Configurações específicas para cada tela
            if screen_name in ['WithoutContractor', 'RequestSent']:
                destination_screen.tab_nav_state = 'request'

                # Atualiza a navegação visualmente se os IDs existirem
                if all(hasattr(destination_screen.ids, attr) for attr in
                       ['vacancy', 'perfil', 'payment', 'notification']):
                    destination_screen.ids.vacancy.active = False
                    destination_screen.ids.perfil.active = False
                    destination_screen.ids.payment.active = True
                    destination_screen.ids.notification.active = False
                else:
                    logging.warning(f"Alguns elementos de navegação não encontrados na tela {screen_name}")

            elif screen_name == 'ReviewScreen':
                destination_screen.current_nav_state = 'payment'
                destination_screen.salary = self.salary

                # Atualiza a navegação visualmente se os IDs existirem
                if all(hasattr(destination_screen.ids, attr) for attr in
                       ['vacancy', 'perfil', 'payment', 'notification']):
                    destination_screen.ids.vacancy.active = False
                    destination_screen.ids.perfil.active = False
                    destination_screen.ids.payment.active = True
                    destination_screen.ids.notification.active = False
                else:
                    logging.warning(f"Alguns elementos de navegação não encontrados na tela {screen_name}")

            # Navega para a tela
            screen_manager.current = screen_name
            logging.info(f"Navegou para tela: {screen_name}")
        except Exception as e:
            logging.error(f"Erro ao navegar para {screen_name}: {str(e)}")
            self._show_error_message(f"Erro ao acessar {screen_name}")

    def _show_error_message(self, message):
        """
        Exibe uma mensagem de erro na interface.

        Args:
            message (str): Mensagem de erro a ser exibida.
        """
        try:
            # Verifica se temos um container para exibir erros
            if hasattr(self.ids, 'error_container'):
                self.ids.error_container.clear_widgets()

                error_label = MDLabel(
                    text=message,
                    theme_text_color="Error",
                    halign="center"
                )
                self.ids.error_container.add_widget(error_label)
            else:
                # Caso não haja container específico, apenas loga o erro
                logging.error(f"Erro UI: {message}")
        except Exception as e:
            logging.error(f"Erro ao exibir mensagem de erro: {str(e)}")
            