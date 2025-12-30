from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
from kivy.utils import get_color_from_hex
import re
from kivymd.uix.snackbar import (
    MDSnackbar,
    MDSnackbarText,
)
from kivy.metrics import dp
from kivy.uix.screenmanager import SlideTransition
from urllib.parse import quote
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
from kivymd.app import MDApp
from configurations import (DialogNoNet, DialogInfinityUpload, DialogErrorUnknow, 
                           firebase_url, SignController)


class IdentifyContractor(MDScreen):
    # ==================== PROPERTIES ====================
    FIREBASE_URL = firebase_url()
    
    # Auth & User
    token_id = StringProperty()
    local_id = StringProperty()
    api_key = StringProperty()
    refresh_token = StringProperty()
    perso = StringProperty()
    type = StringProperty()
    name_sender = StringProperty()
    email_sender = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Adicionar flag para evitar múltiplas navegações
        self.is_navigating = False

    # ==================== LIFECYCLE METHODS ====================
    def on_enter(self):
        """Quando entra na tela"""
        print("🟢 ENTROU na tela IdentifyContractor")
        print(f"   Manager tem {len(self.manager.screens)} telas")
        print(f"   Telas disponíveis: {[s.name for s in self.manager.screens]}")
        
        # Reset do estado de navegação
        self.is_navigating = False
        
        # Inicializa os dialogs
        self._setup_dialogs()
        
        # Verifica token
        self.verific_token()
        self.event_token = Clock.schedule_interval(self.verific_token, 300)
    
    def on_leave(self):
        """Quando sai da tela"""
        print("🔴 SAIU da tela IdentifyContractor")
        print(f"   Manager tem {len(self.manager.screens)} telas")
        print(f"   Telas disponíveis: {[s.name for s in self.manager.screens]}")
        
        # Cancela o clock do token
        if hasattr(self, 'event_token'):
            self.event_token.cancel()
            print("⏱️ Clock do token cancelado ao sair da tela")
        
        # Limpa o campo de email
        self.ids.email.text = ''
        
        # Verifica se a tela ainda existe
        if self in self.manager.screens:
            print("   ✅ IdentifyContractor ainda está no manager")
        else:
            print("   ❌ IdentifyContractor FOI REMOVIDA DO MANAGER!")

    def _setup_dialogs(self):
        """Configura os dialogs de erro"""
        self.inf_dialog = DialogInfinityUpload()
        self.signcontroller = SignController(screen=self, name='IdentifyContractor')
        
        self.dialog_not_net = DialogNoNet(
            subtitle='Não foi possível se conectar. Verifique sua internet e tente novamente',
            callback=lambda: self.signcontroller.retry_signup(
                lambda: self.step_three(self.ids.email.text)
            )
        )
        
        self.dialog_error_unknown = DialogErrorUnknow(screen=f'{self.name}')

    # ==================== TOKEN MANAGEMENT ====================
    def verific_token(self, *args):
        """Verifica se o token ainda é válido"""
        if not self.get_parent_window():
            return
            
        print('🔎 Verificando token...')
        UrlRequest(
            f"{self.FIREBASE_URL}/Users/{self.local_id}.json?auth={self.token_id}",
            on_success=self.on_token_success,
            on_failure=self.on_token_failure,
            on_error=self.on_token_failure,
            method="GET"
        )

    def on_token_success(self, req, result):
        """Token válido"""
        print('✅ Token válido, usuário encontrado')

    def on_token_failure(self, req, result):
        """Token inválido, tenta renovar"""
        print('❌ Token inválido, tentando atualizar...', result)
        self.refresh_id_token()

    def refresh_id_token(self):
        """Renova o token de autenticação"""
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
        """Token renovado com sucesso"""
        self.token_id = result["id_token"]
        self.refresh_token = result.get("refresh_token", self.refresh_token)
        print("🔄 Token renovado com sucesso")

    def on_refresh_failure(self, req, result):
        """Falha ao renovar token"""
        print("❌ Erro ao renovar token:", result)
        self.show_snackbar_icon('O token não foi renovado', 'error')
        Clock.schedule_once(
            lambda dt: self.show_snackbar_icon('Refaça login no aplicativo', 'error'), 
            1
        )

    # ==================== EMAIL VALIDATION ====================
    def validar_email(self, email):
        """Valida se o email está no formato correto"""
        padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(padrao, email))

    def step_one(self, *args):
        """Chama a função que verifica se o formato do email é válido"""
        # Evita múltiplas buscas simultâneas
        if self.is_navigating:
            return
        
        self.ids.search.text = 'Buscando...'
        email = self.ids.email.text.strip()
        
        if not email:
            self.show_snackbar_icon('Por favor, digite um email', 'warning')
            self.ids.search.text = 'Buscar Usuário'
            return
        
        Clock.schedule_once(lambda dt: self.step_two(email), 0)

    def step_two(self, email):
        """Faz a separação e termina a verificação do email"""
        correct_format = self.validar_email(email)

        if correct_format:
            self.ids.email.error = False
            self.ids.email.helper_text = ''
            print('✅ O email está em um formato correto')
            self.step_three(email)
        else:
            print('❌ O email não está em um formato correto')
            self.show_snackbar_icon('Formato do email inválido', 'error')
            self.ids.search.text = 'Buscar Usuário'
            self.ids.email.error = True
            self.ids.email.helper_text = 'Email inválido'

    # ==================== USER SEARCH ====================
    def step_three(self, email):
        """Busca o usuário no Firebase"""
        # Mostra loading
        self.inf_dialog.open()
        
        email_escaped = quote(email).strip().replace(' ', '')
        print('='*50)
        print('🔑 Token de autenticação:', self.token_id[:20] + '...')
        print('📧 Email buscado:', email_escaped)
        print('👤 Tipo de usuário:', self.type)
        print('='*50)
        
        # Define a URL baseada no tipo
        if self.type == 'Contractor':
            url = (
                f'{self.FIREBASE_URL}/Users.json'
                f'?orderBy="email"&equalTo="{email_escaped}"&auth={self.token_id}'
            )
        else:
            url = (
                f'{self.FIREBASE_URL}/Funcionarios.json'
                f'?orderBy="email"&equalTo="{email_escaped}"&auth={self.token_id}'
            )
        
        UrlRequest(
            url,
            method='GET',
            on_success=self.on_search_success,
            on_error=self.signcontroller.handle_signup_error,
            on_failure=self.signcontroller.handle_signup_failure,
            timeout=10
        )

    def on_search_success(self, req, result):
        """Processa o resultado da busca"""
        self.signcontroller.close_all_dialogs()
        
        if result and isinstance(result, dict) and len(result) > 0:
            print("✅ Email encontrado:", result)
            
            # Pega o primeiro resultado
            for key, data in result.items():
                if self.type == 'Contractor':
                    self.step_four(
                        data.get('perfil', ''),
                        data.get('name', ''),
                        data.get('email', ''),
                        key
                    )
                else:
                    self.step_four(
                        data.get('avatar', ''),
                        data.get('Name', ''),
                        data.get('email', ''),
                        key
                    )
                break
        else:
            print("❌ Email não encontrado no banco de dados")
            self.show_snackbar_icon('Usuário não encontrado', 'warning')
            self.ids.search.text = 'Buscar Usuário'

    # ==================== NAVIGATION ====================
    def step_four(self, avatar, name, email, key):
        """Passa os dados para a tela de confirmação"""
        # Evita múltiplas navegações
        if self.is_navigating:
            return
        
        self.is_navigating = True
        
        print('=' * 50)
        print('📸 Avatar:', avatar)
        print('👤 Nome:', name)
        print('📧 Email:', email)
        print('🔑 Key:', key)
        print('=' * 50)
        
        Clock.schedule_once(
            lambda dt: self._navigate_to_perfil(avatar, name, email, key), 
            0.2
        )
        
        self.ids.search.text = 'Buscar Usuário'

    def _navigate_to_perfil(self, avatar, name, email, key):
        """Navega para a tela de perfil"""
        print("🚀 INICIANDO NAVEGAÇÃO PARA IdentifyPerfil")
        
        if not self.manager:
            print("❌ Manager não existe!")
            self.is_navigating = False
            return
        
        try:
            # Verifica se a tela existe
            if not self.manager.has_screen('IdentifyPerfil'):
                print("❌ Tela IdentifyPerfil não existe no manager!")
                self.show_snackbar_icon('Erro ao navegar para o perfil', 'error')
                self.is_navigating = False
                return
            
            # Pega a tela
            perfil_screen = self.manager.get_screen('IdentifyPerfil')
            
            # Define as propriedades
            perfil_screen.avatar = avatar
            perfil_screen.email = email
            perfil_screen.nami = name
            perfil_screen.token_id = self.token_id
            perfil_screen.refresh_token = self.refresh_token
            perfil_screen.local_id = self.local_id
            perfil_screen.api_key = self.api_key
            perfil_screen.name_sender = self.name_sender
            perfil_screen.email_sender = self.email_sender
            perfil_screen.key_accused = key
            perfil_screen.perso = self.perso
            perfil_screen.type = self.type
            
            # Limpa o campo de email
            self.ids.email.text = ''
            
            # Navega
            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = 'IdentifyPerfil'
            
            print("✅ NAVEGAÇÃO CONCLUÍDA!")
            
            # Reset após navegação bem-sucedida
            Clock.schedule_once(lambda dt: setattr(self, 'is_navigating', False), 1)
            
        except Exception as e:
            print(f"❌ ERRO AO NAVEGAR: {e}")
            import traceback
            traceback.print_exc()
            
            self.show_snackbar_icon('Erro ao carregar perfil', 'error')
            self.dialog_error_unknown.open()
            self.is_navigating = False

    def back_screen(self, *args):
        """Volta para a tela anterior"""
        try:
            app = MDApp.get_running_app()
            screenmanager = app.root
            home = screenmanager.get_screen('ReportScreen')
            
            home.token_id = self.token_id
            home.perso = self.perso
            home.local_id = self.local_id
            home.refresh_token = self.refresh_token
            home.api_key = self.api_key
            
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = 'ReportScreen'
            
        except Exception as e:
            print(f'❌ Erro ao voltar: {e}')
            self.dialog_error_unknown.open()

    # ==================== NOTIFICATIONS ====================
    def show_snackbar_icon(self, message, tipo='info'):
        """Snackbar com ícone e estilo baseado no tipo"""
        
        config = {
            'success': {
                'color': "#4CAF50",
                'icon': "check-circle",
            },
            'error': {
                'color': "#F44336",
                'icon': "alert-circle",
            },
            'warning': {
                'color': "#FF9800",
                'icon': "alert",
            },
            'info': {
                'color': "#2196F3",
                'icon': "information",
            },
        }
        
        settings = config.get(tipo, config['info'])
        
        snackbar = MDSnackbar(
            MDSnackbarText(
                text=message,
                theme_text_color="Custom",
                text_color='white',
                bold=True,
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            theme_bg_color='Custom',
            background_color=get_color_from_hex(settings['color']),
            size_hint_x=0.9,
            radius=[12, 12, 12, 12],
            elevation=6,
            duration=3,
        )
        
        snackbar.open()
        