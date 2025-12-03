from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
from kivy.utils import get_color_from_hex
import re
from kivymd.uix.snackbar import (
    MDSnackbar,
    MDSnackbarText,
    MDSnackbarSupportingText,
    MDSnackbarButtonContainer,
    MDSnackbarCloseButton,
)
from kivy.metrics import dp

from kivy.uix.screenmanager import SlideTransition
from urllib.parse import quote
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
from kivymd.app import MDApp


class IdentifyContractor(MDScreen):
    token_id = StringProperty()
    local_id = StringProperty()
    api_key = StringProperty()
    refresh_token = StringProperty()
    perso = StringProperty()
    type = StringProperty()
    name_sender = StringProperty()
    email_sender = StringProperty()

    # ✅ ADICIONE ESSES MÉTODOS DE DEBUG
    def on_enter(self):
        """Quando entra na tela"""
        print("🟢 ENTROU na tela IdentifyContractor")
        print(f"   Manager tem {len(self.manager.screens)} telas")
        print(f"   Telas disponíveis: {[s.name for s in self.manager.screens]}")
    
    def on_leave(self):
        """Quando sai da tela"""
        print("🔴 SAIU da tela IdentifyContractor")
        print(f"   Manager tem {len(self.manager.screens)} telas")
        print(f"   Telas disponíveis: {[s.name for s in self.manager.screens]}")
        
        # ⚠️ VERIFICAR SE A TELA AINDA EXISTE
        if self in self.manager.screens:
            print("   ✅ IdentifyContractor ainda está no manager")
        else:
            print("   ❌ IdentifyContractor FOI REMOVIDA DO MANAGER!")

    # Funções de busca de usuario ------------------------------------
    def validar_email(self, email):
        """Valida se o email está no formato correto """
        padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if re.match(padrao, email):
            return True
        return False

    def step_one(self, *args):
        """ Chama a função que Verifica se o formato do email é valido"""
        self.ids.search.text = 'Buscando...'
        email = self.ids.email.text
        Clock.schedule_once(lambda dt: self.step_two(email), 0)

    def step_two(self, email):
        """Faz a separação e termina a verificação do email"""
        correct_format = self.validar_email(email)

        if correct_format:
            self.ids.search.error = False
            self.ids.help_text.text = ''
            print('O email está em um formato correto')
            self.step_three(email)
        else:
            print('O email não está em um formato correto')
            self.show_snackbar_icon('Formato do email invalido', 'error')
            self.ids.search.text = 'Buscar Usuário'
    
    def show_snackbar_icon(self, message, tipo='info'):
        """Snackbar com ícone e botão de fechar"""
        
        config = {
            'success': {
                'color': "#4CAF50",
                'icon': "check-circle",
                'text_color': (1, 1, 1, 1)
            },
            'error': {
                'color': "#F44336",
                'icon': "alert-circle",
                'text_color': (1, 1, 1, 1)
            },
            'warning': {
                'color': "#FF9800",
                'icon': "alert",
                'text_color': (1, 1, 1, 1)
            },
            'info': {
                'color': "#2196F3",
                'icon': "information",
                'text_color': (1, 1, 1, 1)
            },
        }
        
        settings = config.get(tipo, config['info'])
        
        snackbar = MDSnackbar(
            MDSnackbarText(
                text=message,
                theme_text_color="Custom",
                text_color='red',
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            theme_bg_color='Custom',
            background_color=get_color_from_hex('#F5F5F5'),
            size_hint_x=0.9,
            md_bg_color=settings['color'],
            radius=[12, 12, 12, 12],
            elevation=6,
        )
        
        snackbar.open()

    def step_three(self, email):
        """Versão alternativa usando UrlRequest com Bearer token"""
        
        email_escaped = quote(email).strip().replace(' ', '')
        print('='*50)
        print('Token de autenticação: ', self.token_id)
        print('='*50)
        url = ()
        if self.type == 'Contractor':
            url = (
                'https://obra-7ebd9-default-rtdb.firebaseio.com/Users.json'
                f'?orderBy="email"&equalTo="{email_escaped}"&auth={self.token_id}'
            )
        else:
            url = (
                'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios.json'
                f'?orderBy="email"&equalTo="{email_escaped}"&auth={self.token_id}'
            )
        
        headers = {
            'Authorization': f'Bearer {self.token_id.strip()}',
            'Content-Type': 'application/json'
        }
        
        def sucesso(req, result):
            if result:
                print("✅ Email encontrado:", result)
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
                print("❌ Email não encontrado")
        
        def erro(req, error):
            print(f"❌ Erro: {error}")
        
        def falha(req, result):
            print(f"❌ Falha: {result}")
        
        UrlRequest(
            url,
            method='GET',
            req_headers=headers,
            on_success=sucesso,
            on_error=erro,
            on_failure=falha,
            timeout=10
        )

    def step_four(self, avatar, name, email, key):
        """Passa os dados do contratante para a tela de confirmação"""
        print('=' * 50)
        print('Avatar:', avatar)
        print('Nome:', name)
        print('Email:', email)
        
        Clock.schedule_once(lambda dt: self._navigate_to_perfil(avatar, name, email, key), 0.1)
        
        self.ids.search.text = 'Buscar Usuário'
        print('=' * 50)

    def _navigate_to_perfil(self, avatar, name, email, key):
        """Navega para a tela de perfil"""
        print("🚀 INICIANDO NAVEGAÇÃO PARA IdentifyPerfil")
        print(f"📊 Manager atual: {self.manager}")
        print(f"📊 Tipo do manager: {type(self.manager)}")
        print(f"📊 Manager é None? {self.manager is None}")
        
        if self.manager:
            print(f"📊 Quantidade de telas no manager: {len(self.manager.screens)}")
            print(f"📊 Nomes das telas: {[s.name for s in self.manager.screens]}")
            
            # Verifica cada tela
            for screen in self.manager.screens:
                print(f"   - {screen.name} ({type(screen).__name__})")
                if screen.name == 'IdentifyPerfil':
                    print(f"   ✅ ENCONTREI! Tipo: {type(screen)}, ID: {id(screen)}")
        
        try:
            # Tenta pegar a tela de TODAS as formas possíveis
            print("\n🔍 TENTATIVA 1: has_screen")
            tem_tela = self.manager.has_screen('IdentifyPerfil')
            print(f"   Resultado: {tem_tela}")
            
            print("\n🔍 TENTATIVA 2: get_screen direto")
            try:
                tela = self.manager.get_screen('IdentifyPerfil')
                print(f"   ✅ CONSEGUIU! Tela: {tela}, Tipo: {type(tela)}")
            except Exception as e:
                print(f"   ❌ FALHOU: {e}")
            
            print("\n🔍 TENTATIVA 3: Buscar manualmente na lista")
            tela_encontrada = None
            for s in self.manager.screens:
                if s.name == 'IdentifyPerfil':
                    tela_encontrada = s
                    print(f"   ✅ ACHEI NA LISTA! {s}")
                    break
            
            if not tela_encontrada:
                print("   ❌ NÃO EXISTE NA LISTA!")
            
            print("\n🔍 TENTATIVA 4: Verificar screen_names")
            print(f"   screen_names: {self.manager.screen_names}")
            
            # Se chegou aqui, tenta navegar
            if tela_encontrada:
                print("\n🚀 Tentando navegar usando a tela encontrada manualmente...")
                
                # Define propriedades
                tela_encontrada.avatar = avatar
                tela_encontrada.email = email
                tela_encontrada.nami = name
                tela_encontrada.token_id = self.token_id
                tela_encontrada.refresh_token = self.refresh_token
                tela_encontrada.local_id = self.local_id
                tela_encontrada.api_key = self.api_key
                tela_encontrada.name_sender = self.name_sender
                tela_encontrada.email_sender = self.email_sender
                tela_encontrada.key_accused = key
                tela_encontrada.perso = self.perso
                tela_encontrada.type = self.type
                
                # Tenta mudar
                print(f"   Current antes: {self.manager.current}")
                self.manager.transition = SlideTransition(direction='right')
                
                # Tenta de 3 formas diferentes
                self.ids.email.text = ''
                print("\n   Tentando: self.manager.current = 'IdentifyPerfil'")
                self.manager.current = 'IdentifyPerfil'
                
                print(f"   Current depois: {self.manager.current}")
                print("✅ NAVEGAÇÃO CONCLUÍDA!")
            
        except Exception as e:
            print(f"\n❌❌❌ ERRO CRÍTICO: {e}")
            print(f"Tipo do erro: {type(e)}")
            import traceback
            traceback.print_exc()
            
            print("\n📸 SNAPSHOT DO ESTADO ATUAL:")
            print(f"   self: {self}")
            print(f"   self.manager: {self.manager}")
            if self.manager:
                print(f"   Telas: {[s.name for s in self.manager.screens]}")

    def back_screen(self, *args):
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