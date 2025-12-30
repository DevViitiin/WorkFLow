import ast
import json
from functools import partial
import socket
from kivy.metrics import dp
from kivy.properties import get_color_from_hex, StringProperty, Clock
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivy.animation import Animation
from kivymd.uix.screen import MDScreen
from kivy.network.urlrequest import UrlRequest
from kivymd.uix.snackbar import MDSnackbarText, MDSnackbar
from configurations import firebase_url
from configurations import DialogNoNet, DialogInfinityUpload, DialogErrorUnknow, firebase_url, check_error, SignController
import os


class InitScreen(MDScreen):
    """
    Tela inicial do aplicativo que gerencia autenticação de usuários.
    
    Funcionalidades:
    - Login de funcionários e contratantes
    - Recuperação de senha via email
    - Validação de credenciais
    - Navegação para telas apropriadas baseado no tipo de usuário
    """
    
    # ==================== CONSTANTES E PROPRIEDADES ====================
    
    logo = "https://res.cloudinary.com/dsmgwupky/image/upload/v1757731316/logo-removebg-preview_sqstg8.png"
    carregado = False
    api1 = "AIzaSyA3vFR2WgCdB"
    api2 = "syIIL1k9teQNZTi4ZAzhtg"
    api_key = (api1 + api2 + 's')[:-1]
    key = StringProperty()
    name = False
    can_nonet = True
    can_net_login = True
    can_net_login2 = True
    senha = ''
    type = ''

    # ==================== INICIALIZAÇÃO ====================

    def on_enter(self, *args):
        """
        Callback executado quando a tela é exibida.
        
        Inicializa componentes visuais e diálogos de erro.
        """
        
        self.signcontroller = SignController(screen=self, name=self.name)   
        self.inf_dialog = DialogInfinityUpload()
        self.nonet = DialogNoNet(
            subtitle='Não foi possível enviar o email para realização da troca de senha, verifique sua internet e tente novamente',
            callback=lambda: self.signcontroller.retry_signup(self.send_password_recovery_email)
        )
        self.nonet_login = DialogNoNet(
            subtitle='Não foi possível verificar as informações de login, verifique sua internet e tente novamente',
            callback=lambda: self.signcontroller.retry_signup(self.authenticate_employee)
        )
        self.select_employee_profile()

        self.nonet_login2 = DialogNoNet(
            subtitle='Não foi possível verificar as informações de login, verifique sua internet e tente novamente',
            callback=lambda: self.signcontroller.retry_signup(self.authenticate_contractor)
        )
        self.stranger_error = DialogErrorUnknow(self.name)

    # ==================== RECUPERAÇÃO DE SENHA ====================
    
    def send_password_recovery_email(self, *args):
        """
        Envia email de recuperação de senha para o usuário.
        
        Valida o campo de email e faz requisição ao Firebase Auth
        para enviar o email de redefinição de senha em português.
        """
        if not self.can_nonet:
            self.can_nonet = True
            self.nonet.dismiss()
            self.inf_dialog.open()
        
        if not self.ids.email.text:
            self.show_error_message('Por favor preencha o email que será usado')
            Clock.schedule_once(lambda dt: self.show_error_message('Para enviar a troca de senha'), 1.5)
            return
        
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={self.api_key}"
        payload = {
            "requestType": "PASSWORD_RESET",
            "email": self.ids.email.text
        }
        headers = {
            "Content-Type": "application/json",
            "X-Firebase-Locale": "pt-BR"
        }
        
        try:
            UrlRequest(
                url,
                req_body=json.dumps(payload),
                req_headers=headers,
                on_success=self.on_email_sent_success,
                on_error=self.on_connection_error,
                on_failure=self.on_connection_error
            )
        except Exception as e:
            print(f"[ERRO REDE] Falha ao enviar email de recuperação: {e}")
            self.on_connection_error(None, None)

    def on_email_sent_success(self, req, result):
        """
        Callback executado quando o email de recuperação é enviado com sucesso.
        
        Args:
            req: Objeto de requisição
            result: Resposta da API
        """
        self.can_nonet = True
        self.show_success_message('Solicitação enviada com sucesso')
        Clock.schedule_once(lambda dt: self.show_success_message('Verifique seu email'), 1.5)
        print(f"Email de redefinição enviado: {result}")

    def on_connection_error(self, req, result):
        """
        Callback executado quando há erro de conexão.
        
        Args:
            req: Objeto de requisição
            result: Resposta de erro
        """
        if self.can_nonet:
            Clock.schedule_once(lambda dt: self.open_no_internet_dialog(), 1.5)
            self.can_nonet = False
        else:
            print('[ERRO REDE] Não foi possível conectar, tente novamente')

    def open_no_internet_dialog(self):
        """Fecha o diálogo de carregamento e abre o diálogo de erro de internet."""
        self.inf_dialog.dismiss()
        self.nonet.open()

    # ==================== SELEÇÃO DE TIPO DE USUÁRIO ====================
    
    def select_contractor_profile(self):
        """
        Seleciona o perfil de contratante e aplica feedback visual.
        
        Atualiza as cores dos cards e define o tipo de usuário como 'Contratante'.
        """
        self.ids.employee_card.line_color = 'white'
        anime = Animation(duration=0.2, line_color=[0, 0, 1, 1])
        anime.start(self.ids.contractor_card)
        
        self.ids.contractor_card.canvas.ask_update()
        self.ids.employee_card.canvas.ask_update()
        
        self.type = 'Contratante'

    def select_employee_profile(self):
        """
        Seleciona o perfil de funcionário e aplica feedback visual.
        
        Atualiza as cores dos cards e define o tipo de usuário como 'Funcionario'.
        """
        self.ids.contractor_card.line_color = 'white'
        anime = Animation(duration=0.2, line_color=[0, 0, 1, 1])
        anime.start(self.ids.employee_card)
        
        self.ids.employee_card.canvas.ask_update()
        self.ids.contractor_card.canvas.ask_update()
        
        self.type = 'Funcionario'

    # Mantém compatibilidade com código KV
    state_contractor = select_contractor_profile
    state_employee = select_employee_profile

    # ==================== VALIDAÇÃO DE LOGIN ====================
    
    def start_login_process(self):
        """
        Inicia o processo de login validando os campos de entrada.
        
        Verifica:
        - Se um tipo de usuário foi selecionado
        - Se o email foi preenchido
        - Se a senha foi preenchida
        
        Redireciona para o fluxo apropriado baseado no tipo de usuário.
        """
        try:
            if not self.type:
                self.show_error_message('Selecione o tipo de conta para efetuar o login')
                return
            
            if not self.ids.email.text:
                self.ids.email.focus = True
                self.show_error_message('Insira seu email de usuário')
                return
            
            if not self.ids.senha.text:
                self.ids.senha.focus = True
                self.show_error_message('Insira sua senha')
                return
            
            if self.type == 'Contratante':
                self.authenticate_contractor()
            else:
                self.authenticate_employee()
                
        except Exception as e:
            self.stranger_error.open()

    # Mantém compatibilidade
    etapa1 = start_login_process

    # ==================== AUTENTICAÇÃO DE FUNCIONÁRIO ====================
    
    def authenticate_employee(self):
        """
        Autentica um funcionário usando Firebase Authentication.
        
        Envia credenciais para o Firebase e processa a resposta.
        Em caso de sucesso, busca os dados completos do funcionário.
        """
        if not self.can_net_login:
            self.nonet_login.dismiss()
            self.inf_dialog.open()
            self.can_net_login = True
        
        print('[LOGIN] Autenticando funcionário...')
        
        api_key = "AIzaSyA3vFR2WgCdBsyIIL1k9teQNZTi4ZAzhtg"
        email = self.ids.email.text
        password = self.ids.senha.text
        
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        headers = {"Content-Type": "application/json"}
        
        try:
            UrlRequest(
                url,
                req_body=json.dumps(payload),
                req_headers=headers,
                method='POST',
                on_success=self.on_employee_auth_success,
                on_error=partial(self.on_auth_error, callback=self.authenticate_employee),
                on_failure=partial(self.on_auth_error, callback=self.authenticate_employee),
                on_cancel=partial(self.on_auth_error, callback=self.authenticate_employee)
            )
        except Exception as e:
            print(f"[ERRO REDE] Falha na autenticação do funcionário: {e}")
            self.on_auth_error(None, None, self.authenticate_employee)

    def on_employee_auth_success(self, req, result):
        """
        Callback executado após autenticação bem-sucedida do funcionário.
        
        Extrai tokens e busca dados completos do funcionário no Firebase Database.
        
        Args:
            req: Objeto de requisição
            result: Dados de autenticação (contém tokens)
        """
        print('[LOGIN] Autenticação bem-sucedida, buscando dados do funcionário...')
        
        id_token = result['idToken']
        id_local = result['localId']
        refresh = result['refreshToken']
        
        try:
            UrlRequest(
                f'{firebase_url()}/Funcionarios/{id_local}.json?auth={id_token}',
                method='GET',
                on_success=partial(self.load_employee_profile, token_id=id_token, local_id=id_local, refresh_token=refresh),
                on_error=self.on_employee_not_found,
                on_failure=self.on_employee_not_found,
                on_cancel=self.on_employee_not_found,
                req_headers={"Content-Type": "application/json"}
            )
        except Exception as e:
            print(f"[ERRO REDE] Falha ao buscar dados do funcionário: {e}")
            self.on_employee_not_found(None, None)

    def on_employee_not_found(self, req, result):
        """
        Callback executado quando os dados do funcionário não são encontrados.
        
        Args:
            req: Objeto de requisição
            result: Resposta de erro
        """
        print('[ERRO] Funcionário não encontrado no banco de dados')
        self.show_error_message("Usuário desconhecido, tente como contratante")

    def on_auth_error(self, req, result=None, callback=None):
        """
        Callback executado quando há erro na autenticação.
        
        Trata diferentes tipos de erros (credenciais inválidas, sem internet, etc).
        
        Args:
            req: Objeto de requisição
            result: Resposta de erro
            callback: Função de callback para retry
        """
        if result is None:
            print('[ERRO REDE] Erro de conexão durante autenticação')
            self.show_error_message("Erro de conexão, tente novamente")
            if callback:
                callback()
            return
        
        print('='*50)
        print('[ERRO AUTH]', result)
        print('='*50)
        
        try:
            if isinstance(result, dict) and 'error' in result:
                if 'INVALID_LOGIN_CREDENTIALS' in result['error'].get('message', ''):
                    self.show_error_message('As informações estão incorretas')
                else:
                    self.ids.email.error = True
                    self.ids.email.text = ''
                    self.show_error_message('Usuário inexistente')
            else:
                print("[ERRO REDE] Sem internet...")
                Clock.schedule_once(lambda dt: self.close_no_internet_login_dialog(), 1.5)
                self.can_net_login = False
                
        except socket.gaierror as e:
            print(f"[ERRO REDE] Sem internet ou não foi possível resolver o endereço: {e}")
            Clock.schedule_once(lambda dt: self.close_no_internet_login_dialog(), 1.5)
            self.can_net_login = False

        except Exception as e:
            self.stranger_error.open()

    def close_no_internet_login_dialog(self):
        """Fecha o diálogo de carregamento e abre o diálogo de erro de conexão no login."""
        self.inf_dialog.dismiss()
        self.nonet_login.open()

    # ==================== AUTENTICAÇÃO DE CONTRATANTE ====================
    
    def authenticate_contractor(self):
        """
        Autentica um contratante usando Firebase Authentication.
        
        Envia credenciais para o Firebase e processa a resposta.
        Em caso de sucesso, busca os dados completos do contratante.
        """
        print('[LOGIN] Autenticando contratante...')
        if not self.can_net_login2:
            self.nonet_login2.dismiss()
            self.inf_dialog.open()
            self.can_net_login2 = True

        api_key = "AIzaSyA3vFR2WgCdBsyIIL1k9teQNZTi4ZAzhtg"
        email = self.ids.email.text
        password = self.ids.senha.text
        
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        headers = {"Content-Type": "application/json"}
        
        try:
            UrlRequest(
                url,
                req_body=json.dumps(payload),
                req_headers=headers,
                method='POST',
                on_success=self.on_contractor_auth_success,
                on_error=self.on_contractor_auth_error,
                on_failure=self.on_contractor_auth_error,
                on_cancel=self.on_contractor_auth_error
            )
        except Exception as e:
            print(f"[ERRO REDE] Falha na autenticação do contratante: {e}")
            self.on_contractor_auth_error(None, None)

    def on_contractor_auth_success(self, req, result):
        """
        Callback executado após autenticação bem-sucedida do contratante.
        
        Extrai tokens e busca dados completos do contratante no Firebase Database.
        
        Args:
            req: Objeto de requisição
            result: Dados de autenticação (contém tokens)
        """
        print('[LOGIN] Autenticação bem-sucedida, buscando dados do contratante...')
        
        refresh = result['refreshToken']
        id_token = result['idToken']
        id_local = result['localId']
        
        try:
            UrlRequest(
                f'{firebase_url()}/Users/{id_local}.json?auth={id_token}',
                method='GET',
                on_success=lambda req, result: self.load_contractor_profile(req, result, id_token, id_local, refresh),
                on_error=self.on_contractor_not_found,
                on_failure=self.on_contractor_not_found,
                on_cancel=self.on_contractor_not_found,
                req_headers={"Content-Type": "application/json"}
            )
        except Exception as e:
            print(f"[ERRO REDE] Falha ao buscar dados do contratante: {e}")
            self.on_contractor_not_found(None, None)

    def on_contractor_auth_error(self, req, result):
        """
        Callback executado quando há erro na autenticação do contratante.
        
        Args:
            req: Objeto de requisição
            result: Resposta de erro
        """
        print('='*50)
        print(f"[ERRO REDE] Sem internet")
        Clock.schedule_once(lambda dt: self.close_no_internet_login_dialog2(), 1.5)
        self.can_net_login_2 = False
        print('='*50)
        

    def on_contractor_not_found(self, req, result):
        """
        Callback executado quando os dados do contratante não são encontrados.
        
        Args:
            req: Objeto de requisição
            result: Resposta de erro
        """
        print('[ERRO] Contratante não encontrado no banco de dados')
        self.show_error_message("Usuário desconhecido, tente como funcionário")

    def close_no_internet_login_dialog2(self):
        """Fecha o diálogo de carregamento e abre o diálogo de erro de conexão no login."""
        self.inf_dialog.dismiss()
        self.nonet_login2.open()
        self.can_net_login2 = False

    # ==================== MENSAGENS DE FEEDBACK ====================
    
    def show_success_message(self, message):
        """
        Exibe uma mensagem de sucesso para o usuário.
        
        Args:
            message: Texto da mensagem a ser exibida
        """
        self.show_message(message, color='#00ff15')

    def show_error_message(self, message):
        """
        Exibe uma mensagem de erro para o usuário.
        
        Args:
            message: Texto da mensagem de erro
        """
        self.show_message(message, color='#FF0000')
        print(f"[ERRO] {message}")

    def show_message(self, message, color='#2196F3'):
        """
        Exibe uma snackbar com uma mensagem personalizada.
        
        Args:
            message: Texto da mensagem
            color: Cor de fundo da snackbar (hex)
        """
        MDSnackbar(
            MDSnackbarText(
                text=message,
                theme_text_color='Custom',
                text_color='white',
                bold=True,
                halign='center'
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            halign='center',
            size_hint_x=0.9,
            theme_bg_color='Custom',
            background_color=get_color_from_hex(color)
        ).open()

    # ==================== UTILIDADES ====================
    
    def clear_form_fields(self):
        """Limpa todos os campos do formulário de login."""
        self.ids.email.text = ''
        self.ids.senha.text = ''

    def register(self):
        """
        Navega para a tela de registro de novo usuário.
        
        Reseta todos os campos e o estado visual dos cards antes de navegar.
        """
        self.clear_form_fields()
        self.type = ''
        
        self.ids.contractor_card.md_bg_color = 'white'
        self.ids.text_contractor.text_color = 'black'
        self.ids.employee_card.md_bg_color = 'white'
        self.ids.employee_text.text_color = 'black'
        
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'ChoiceAccount'


    # ==================== CARREGAMENTO DE PERFIL FUNCIONÁRIO ====================
    
    def load_employee_profile(self, req, result, token_id, local_id, refresh_token):
        """
        Carrega o perfil completo do funcionário e redireciona para a tela apropriada.
        
        Verifica se o usuário tem suspensão, advertência ou banimento ativo.
        Se não tiver, carrega os dados do perfil e navega para a tela principal.
        
        Args:
            req: Objeto de requisição
            result: Dados do perfil do funcionário
            token_id: Token de autenticação
            local_id: ID local do usuário
            refresh_token: Token de renovação
        """
        print(f'[LOGIN] Dados do funcionário carregados. Local ID: {local_id}')
        
        try:
            if not result:
                self.show_error_message("Usuário desconhecido, tente como contratante")
                return
            
            suspension = result.get('suspension', {})
            warnings = result.get('warnings', {})
            ban = result.get('ban', {})
            
            # Verifica suspensão
            if '' not in (suspension.get('description', ''), suspension.get('init', ''), suspension.get('end', '')):
                self.navigate_to_suspension_screen(suspension)
                return
            
            # Verifica advertência
            elif '' not in (warnings.get('description', ''), warnings.get('type', ''), 
                          warnings.get('data', ''), warnings.get('motive', '')):
                self.navigate_to_warning_screen(warnings, result, 'employee', token_id, local_id, refresh_token)
                return
            
            # Verifica banimento
            elif '' not in (ban.get('description', ''), ban.get('data', ''), ban.get('motive', '')):
                self.navigate_to_ban_screen(ban)
                return
            
            # Login normal - carrega perfil do funcionário
            app = MDApp.get_running_app()
            screenmanager = app.root
            perfil = screenmanager.get_screen('PrincipalScreenEmployee')
            
            perfil.employee_name = result.get('Name', '')
            perfil.contractor = result.get('contractor', '')
            perfil.employee_function = result.get('function', '')
            perfil.employee_mail = result.get('email', '')
            perfil.request = ast.literal_eval(result.get('request', '[]'))
            perfil.employee_telephone = result.get('telefone', '')
            perfil.avatar = result.get('avatar', '')
            perfil.city = result.get('city', '')
            perfil.api_key = self.api_key
            perfil.salary = result.get('salary', '')
            perfil.data_contractor = result.get('data_contractor', '')
            perfil.state = result.get('state', '')
            perfil.employee_summary = result.get('sumary', '')
            perfil.skills = result.get('skills', '[]')
            perfil.key = self.key
            perfil.refresh_token = refresh_token
            perfil.token_id = token_id
            perfil.local_id = local_id
            
            self.clear_form_fields()
            screenmanager.transition = SlideTransition(direction='right')
            screenmanager.current = 'PrincipalScreenEmployee'
            
        except Exception as e:
            self.stranger_error.open()

    # ==================== CARREGAMENTO DE PERFIL CONTRATANTE ====================
    
    def load_contractor_profile(self, req, result, token_id, local_id, refresh_token):
        """
        Carrega o perfil completo do contratante e redireciona para a tela apropriada.
        
        Verifica se o usuário tem suspensão, advertência ou banimento ativo.
        Se não tiver, carrega os dados do perfil e navega para a tela principal.
        
        Args:
            req: Objeto de requisição
            result: Dados do perfil do contratante
            token_id: Token de autenticação
            local_id: ID local do usuário
            refresh_token: Token de renovação
        """
        print(f'[LOGIN] Dados do contratante carregados. Local ID: {local_id}')
        
        try:
            if not result:
                self.show_error_message("Usuário desconhecido, tente como funcionário")
                return
            
            suspension = result.get('suspension', {})
            warnings = result.get('warnings', {})
            ban = result.get('ban', {})
            
            # Verifica suspensão
            if '' not in (suspension.get('description', ''), suspension.get('init', ''), suspension.get('end', '')):
                self.navigate_to_suspension_screen(suspension)
                return
            
            # Verifica advertência
            elif '' not in (warnings.get('description', ''), warnings.get('type', ''), 
                          warnings.get('data', ''), warnings.get('motive', '')):
                self.navigate_to_warning_screen(warnings, result, 'contractor', token_id, local_id, refresh_token)
                return
            
            # Verifica banimento
            elif '' not in (ban.get('description', ''), ban.get('data', ''), ban.get('motive', '')):
                self.navigate_to_ban_screen(ban)
                return
            
            # Login normal - configura ambas as telas (Chat e Perfil)
            app = MDApp.get_running_app()
            screen_manager = app.root
            
            # Configura tela Chat
            chat_screen = screen_manager.get_screen('Chat')
            chat_screen.function = result.get('function', '')
            chat_screen.username = result.get('name', '')
            chat_screen.avatar = result.get('perfil', '')
            chat_screen.telefone = result.get('telefone', '')
            chat_screen.state = result.get('state', '')
            chat_screen.city = result.get('city', '')
            chat_screen.company = result.get('company', '')
            chat_screen.email = result.get('email', '')
            chat_screen.local_id = local_id
            chat_screen.token_id = token_id
            chat_screen.refresh_token = refresh_token
            chat_screen.key = self.key
            chat_screen.api_key = self.api_key
            
            # Configura tela Perfil
            perfil_screen = screen_manager.get_screen('Perfil')
            perfil_screen.function = result.get('function', '')
            perfil_screen.username = result.get('name', '')
            perfil_screen.avatar = result.get('perfil', '')
            perfil_screen.telefone = result.get('telefone', '')
            perfil_screen.state = result.get('state', '')
            perfil_screen.city = result.get('city', '')
            perfil_screen.company = result.get('company', '')
            perfil_screen.email = result.get('email', '')
            perfil_screen.local_id = local_id
            perfil_screen.token_id = token_id
            perfil_screen.refresh_token = refresh_token
            perfil_screen.key = self.key
            perfil_screen.api_key = self.api_key
            
            self.clear_form_fields()
            self.type = result.get('type', '')
            self.navigate_to_main_screen()
            
        except Exception as e:
            self.stranger_error.open()

    # ==================== NAVEGAÇÃO PARA TELAS ESPECIAIS ====================
    
    def navigate_to_suspension_screen(self, suspension):
        """
        Navega para a tela de suspensão.
        
        Args:
            suspension: Dados da suspensão do usuário
        """
        app = MDApp.get_running_app()
        screenmanager = app.root
        screen = screenmanager.get_screen('SuspensionScreen')
        
        screen.motive = suspension['motive']
        screen.init = suspension['init']
        screen.end = suspension['end']
        
        self.clear_form_fields()
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'SuspensionScreen'

    def navigate_to_warning_screen(self, warnings, user_data, user_type, token_id, local_id, refresh_token):
        """
        Navega para a tela de advertência.
        
        Args:
            warnings: Dados da advertência
            user_data: Dados completos do usuário
            user_type: Tipo de usuário ('employee' ou 'contractor')
            token_id: Token de autenticação
            local_id: ID local do usuário
            refresh_token: Token de renovação
        """
        app = MDApp.get_running_app()
        screenmanager = app.root
        screen = screenmanager.get_screen('WarningScreen')
        
        screen.motive = warnings['motive']
        screen.data = warnings['data']
        screen.data_user = user_data
        screen.type_user = user_type
        screen.type = warnings['type']
        screen.api_key = self.api_key
        screen.local_id = local_id
        screen.refresh_token = refresh_token
        screen.token_id = token_id
        screen.description = warnings['description']
        
        self.clear_form_fields()
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'WarningScreen'

    def navigate_to_ban_screen(self, ban):
        """
        Navega para a tela de banimento.
        
        Args:
            ban: Dados do banimento do usuário
        """
        app = MDApp.get_running_app()
        screenmanager = app.root
        screen = screenmanager.get_screen('BanScreen')
        
        screen.motive = ban['motive']
        screen.description = ban['description']
        
        self.clear_form_fields()
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'BanScreen'

    def navigate_to_main_screen(self):
        """
        Redireciona para a tela principal apropriada após o login.
        
        Verifica o tipo de usuário e navega para a tela correspondente.
        """
        if self.type in 'contractor':
            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = 'Perfil'
        else:
            self.show_error_message("Tipo de usuário não reconhecido")

    # ==================== NAVEGAÇÃO AUXILIAR ====================
    
    def go_to_next(self, perfil, name):
        """
        Navega para a próxima tela após o login.
        
        Args:
            perfil: O tipo de perfil do usuário
            name: O nome do usuário
        """
        self.manager.transition = SlideTransition(direction='left')
        login = self.manager.get_screen('LoginScreen')
        login.perfil = perfil
        login.nome = name
        self.clear_form_fields()
        self.manager.current = 'LoginScreen'

    def page(self, instance):
        """
        Navega para a tela de perfil.
        
        Args:
            instance: O widget que iniciou a navegação
        """
        self.clear_form_fields()
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'Perfil'

    # ==================== MÉTODOS LEGADOS (COMPATIBILIDADE) ====================
    
    def usuarios_carregados(self, req, result):
        """
        Processa os dados dos usuários após carregamento bem-sucedido.
        Verifica se o nome de usuário existe na base de dados.
        
        Args:
            req: O objeto de requisição
            result: Os dados retornados pelo Firebase
        """
        try:
            if not result:
                self.show_error_message("Não foi possível carregar os dados de usuários")
                return

            self.name = False
            for cargo, nome in result.items():
                if nome['name'] == str(self.ids.nome.text):
                    self.name = True
                    self.senha = nome['senha']
                    self.key = cargo
                    self.etapa2(self.senha)
                    break

            if not self.name:
                self.ids.nome_errado.text = 'Usuário não cadastrado'
                self.ids.nome.error = True
        except Exception as e:
            print(f"[ERRO] Erro ao processar dados de usuários: {e}")
            self.show_error_message(f"Erro ao processar dados: {e}")

    # ==================== MÉTODOS LEGADOS (COMPATIBILIDADE) ====================

    def usuarios_carregados(self, req, result):
        """
        Processa os dados dos usuários após carregamento bem-sucedido.
        Verifica se o nome de usuário existe na base de dados.
        
        Args:
            req: O objeto de requisição
            result: Os dados retornados pelo Firebase
        """
        try:
            if not result:
                self.show_error_message("Não foi possível carregar os dados de usuários")
                return

            self.name = False
            for cargo, nome in result.items():
                if nome['name'] == str(self.ids.nome.text):
                    self.name = True
                    self.senha = nome['senha']
                    self.key = cargo
                    # Removido: self.etapa2(self.senha)
                    # A autenticação agora é feita apenas pelo Firebase Auth
                    self.show_message("Login realizado com sucesso!")
                    break

            if not self.name:
                self.ids.nome_errado.text = 'Usuário não cadastrado'
                self.ids.nome.error = True
        except Exception as e:
            print(f"[ERRO] Erro ao processar dados de usuários: {e}")
            self.show_error_message(f"Erro ao processar dados: {e}")
            
    senha_employee = authenticate_employee
    verificar_senha = authenticate_contractor
    send_password_verification = send_password_recovery_email
    