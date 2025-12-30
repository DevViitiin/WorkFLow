from kivy.properties import StringProperty, get_color_from_hex, BooleanProperty, NumericProperty
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
import logging
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.menu import MDDropdownMenu
from kivy.network.urlrequest import UrlRequest
from configurations import DialogNoNet, DialogInfinityUpload, DialogErrorUnknow, firebase_url, check_error, SignController
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
    FIREBASE_URL = firebase_url()

    def on_enter(self):
        """
        Método chamado quando a tela é exibida.

        Inicializa o estado da navegação e carrega as habilidades do funcionário.
        """

        try:
            logging.info(f'Acessando tela de funcionário com key: {self.key}')
            # Garantir que apenas o ícone de perfila esteja ativo
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
            self.dialog_error_unknown.open()
        
        self.dialog_error_unknown = DialogErrorUnknow(screen=f'{self.name}')
        self.verific_token()
        self.event_token = Clock.schedule_interval(self.verific_token, 300)
        self.upload_menu()

    def upload_menu(self):
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
            caller=self.ids.btn_menu,
            items=menu_itens,
            position='bottom',
            width_mult=2,
            max_height='300dp',
            size_hint_x=None,
            #pos_hint={'center_x': 0.5, 'center_y': 0.5},
            elevation=8,
            radius=[10, 10, 10, 10],
            border_margin=12,
            ver_growth="down",
            hor_growth="right",
        )

    def menu_callback(self, text_item):
        if text_item == 'sair':
            self.manager.current = 'Init'
            self.menu.dismiss()
        elif text_item == 'Denunciar':
            app = MDApp.get_running_app()
            screenmanager = app.root
            report_screen = screenmanager.get_screen('ReportScreen')
            report_screen.token_id = self.token_id
            report_screen.api_key = self.api_key
            report_screen.local_id = self.local_id
            report_screen.refresh_token = self.refresh_token
            report_screen.perso = 'Employee'
            report_screen.email_sender = self.employee_mail
            report_screen.name_sender = self.employee_name
            screenmanager.transition = SlideTransition(direction='right')
            self.menu.dismiss()
            screenmanager.current = 'ReportScreen'
            
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
        pass

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
            self.dialog_error_unknown.open()

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
            self.dialog_error_unknown.open()

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
            self.dialog_error_unknown.open()

    def chat(self, *args):
        """Navega para a tela de chat"""
        try:
            app = MDApp.get_running_app()
            screenmanager = app.root
            perfil = screenmanager.get_screen('ListChat')
            
            # Transfere dados do usuário
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
            perfil.perso = 'Employee'
            perfil.contractor = self.contractor
            perfil.request = self.request
            
            # ✅ CORRIGIDO: Atualiza o estado de navegação
            perfil.current_nav_state = 'chat'
            
            # ✅ CORRIGIDO: Atualiza os ícones de navegação
            if hasattr(perfil.ids, 'chat'):
                perfil.ids.chat.active = True
            if hasattr(perfil.ids, 'vacancy'):
                perfil.ids.vacancy.active = False
            if hasattr(perfil.ids, 'perfil'):
                perfil.ids.perfil.active = False
            if hasattr(perfil.ids, 'notification'):
                perfil.ids.notification.active = False
            
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = 'ListChat'
        except:
            self.dialog_error_unknown.open()

    def vacancy(self, *args):
        """Navega para a tela de vagas"""
        try:
            app = MDApp.get_running_app()
            screenmanager = app.root

            if self.request:
                # ✅ TEM CONTRATANTE - Vai para VacancyBank
                vac = screenmanager.get_screen('VacancyBank')
                
                # Transfere dados
                vac.key = self.key
                vac.api_key = self.api_key
                vac.refresh_token = self.refresh_token
                vac.local_id = self.local_id
                vac.token_id = self.token_id
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
                
                # ✅ CORRIGIDO: Atualiza estado de navegação
                vac.current_nav_state = 'vacancy'
                
                # ✅ CORRIGIDO: Atualiza ícones
                if hasattr(vac.ids, 'vacancy'):
                    vac.ids.vacancy.active = True
                if hasattr(vac.ids, 'perfil'):
                    vac.ids.perfil.active = False
                if hasattr(vac.ids, 'notification'):
                    vac.ids.notification.active = False
                if hasattr(vac.ids, 'chat'):
                    vac.ids.chat.active = False
                
                screenmanager.transition = SlideTransition(direction='right')
                self.manager.current = 'VacancyBank'
                
            else:
                # ✅ SEM CONTRATANTE - Vai para WithoutContractor
                vac = screenmanager.get_screen('WithoutContractor')
                
                # Transfere dados
                vac.key = self.key
                vac.api_key = self.api_key
                vac.refresh_token = self.refresh_token
                vac.local_id = self.local_id
                vac.token_id = self.token_id
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
                
                # ✅ CORRIGIDO: Atualiza ícones
                if hasattr(vac.ids, 'vacancy'):
                    vac.ids.vacancy.active = True
                if hasattr(vac.ids, 'perfil'):
                    vac.ids.perfil.active = False
                if hasattr(vac.ids, 'notification'):
                    vac.ids.notification.active = False
                if hasattr(vac.ids, 'chat'):
                    vac.ids.chat.active = False
                
                self.manager.current = 'WithoutContractor'
                    
        except Exception as e:
            logging.error(f"Erro ao navegar para tela de vagas: {str(e)}")
            self.dialog_error_unknown.open()

    def req(self, *args):
        """Navega para a tela de solicitações"""
        try:
            app = MDApp.get_running_app()
            screenmanager = app.root
            vac = screenmanager.get_screen('RequestsVacancy')
            
            # Transfere dados
            vac.key = self.key
            vac.token_id = self.token_id
            vac.refresh_token = self.refresh_token
            vac.local_id = self.local_id
            vac.api_key = self.api_key
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
            vac.state = self.state
            vac.contractor = self.contractor

            # ✅ CORRIGIDO: Atualiza ícones de navegação
            if hasattr(vac.ids, 'vacancy'):
                vac.ids.vacancy.active = False
            if hasattr(vac.ids, 'perfil'):
                vac.ids.perfil.active = False
            if hasattr(vac.ids, 'notification'):
                vac.ids.notification.active = True
            if hasattr(vac.ids, 'chat'):
                vac.ids.chat.active = False

            screenmanager.transition = SlideTransition(direction='right')
            screenmanager.current = 'RequestsVacancy'
            
        except Exception as e:
            logging.error(f"Erro ao navegar para tela de solicitações: {str(e)}")
            self.dialog_error_unknown.open()

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
                    destination_screen.ids.notification.active = False
                else:
                    logging.warning(f"Alguns elementos de navegação não encontrados na tela {screen_name}")
            
            elif screen_name in 'VacancyBank':
                if self.request:
                    screen_manager.current = screen_name
                    logging.info(f"Navegou para tela: {screen_name}")
                    return
                else:
                    screen_manager.current = 'WithoutContractor'

        except Exception as e:
            logging.error(f"Erro ao navegar para {screen_name}: {str(e)}")
            self.dialog_error_unknown.open()

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
            self.dialog_error_unknown.open()
    