from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
import json
import re
from kivy.uix.widget import Widget
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogIcon,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogButtonContainer,
    MDDialogContentContainer,
)
from kivymd.uix.divider import MDDivider
from kivymd.uix.list import (
    MDListItem,
    MDListItemLeadingIcon,
    MDListItemSupportingText,
)
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.animation import Animation
from kivy.metrics import dp
import ast
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.screenmanager import SlideTransition
from kivymd.uix.label import MDLabel
from kivy.uix.widget import Widget
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivy.network.urlrequest import UrlRequest
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from datetime import datetime
from kivy.clock import Clock
from kivy.animation import Animation
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogIcon,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogButtonContainer,
)
from kivy.uix.image import AsyncImage
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window

# ==================== COMPONENTES DE MENSAGEM ====================


from kivy.core.window import Window

from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.utils import get_color_from_hex

def adjust_balloon(container, label, balloon):
    max_width = container.width * 0.8
    padding_x = dp(24)

    label.texture_update()
    text_width = label.texture_size[0]

    if text_width + padding_x <= max_width:
        balloon.width = text_width + padding_x
        label.width = text_width
        label.text_size = (None, None)
    else:
        balloon.width = max_width
        label.width = max_width - padding_x
        label.text_size = (label.width, None)


class MessageRight(MDBoxLayout):
    def __init__(self, text="", **kwargs):
        super().__init__(**kwargs)

        self.orientation = "horizontal"
        self.size_hint_x = 1   # 🔥 OBRIGATÓRIO
        self.size_hint_y = None
        self.adaptive_height = True
        self.padding = [dp(40), dp(4), dp(8), dp(4)]

        self.add_widget(Widget(size_hint_x=1))

        self.balloon = MDBoxLayout(
            adaptive_height=True,
            size_hint_x=None,
            padding=[dp(12), dp(8), dp(12), dp(8)],
            md_bg_color=get_color_from_hex("#E3F2FD"),
            theme_bg_color="Custom",
            radius=[dp(18), dp(18), dp(4), dp(18)],
        )

        self.label = MDLabel(
            text=text,
            adaptive_height=True,
            size_hint_x=None,
            halign="left",
        )

        self.balloon.add_widget(self.label)
        self.add_widget(self.balloon)

        Clock.schedule_once(self.update_layout, 0)
        self.bind(width=lambda *_: Clock.schedule_once(self.update_layout, 0))

    def update_layout(self, *_):
        adjust_balloon(self, self.label, self.balloon)


class MessageLeft(MDBoxLayout):
    def __init__(self, text="", **kwargs):
        super().__init__(**kwargs)

        self.orientation = "horizontal"
        self.size_hint_x = 1   # 🔥 OBRIGATÓRIO
        self.size_hint_y = None
        self.adaptive_height = True
        self.padding = [dp(8), dp(4), dp(40), dp(4)]

        self.balloon = MDBoxLayout(
            adaptive_height=True,
            size_hint_x=None,
            padding=[dp(12), dp(8), dp(12), dp(8)],
            md_bg_color=get_color_from_hex("#F5F5F5"),
            theme_bg_color="Custom",
            radius=[dp(18), dp(18), dp(18), dp(4)],
        )

        self.label = MDLabel(
            text=text,
            adaptive_height=True,
            size_hint_x=None,
            halign="left",
        )

        self.balloon.add_widget(self.label)
        self.add_widget(self.balloon)
        self.add_widget(Widget(size_hint_x=1))

        Clock.schedule_once(self.update_layout, 0)
        self.bind(width=lambda *_: Clock.schedule_once(self.update_layout, 0))

    def update_layout(self, *_):
        adjust_balloon(self, self.label, self.balloon)


# ==================== TELA DE CHAT ====================

class Chat(MDScreen):
    # IDs dos participantes
    chat_id = StringProperty()
    contractor_id = StringProperty()
    employee_id = StringProperty()
    
    # Informações visuais
    perfil = StringProperty('https://res.cloudinary.com/dsmgwupky/image/upload/v1766573255/GarotinhaEletrica.jpg')
    name_user = StringProperty('GarotinhaEletrica')

    # Caso haja denunciar
    name_sender = StringProperty()
    email_sender = StringProperty()
    
    # Tokens de autenticação
    local_id = StringProperty()
    refresh_token = StringProperty()
    api_key = StringProperty()
    token_id = StringProperty()
    
    # Status online/offline
    on_contractor = BooleanProperty()
    on_employee = BooleanProperty()
    perso = StringProperty()

    messages = ObjectProperty()  
    unread_count = 0 

    MESSAGES_PER_LOAD = 10 
    BATCH_SIZE = 3  
    
    def __init__(self, **kwargs):
        """Inicializa a tela de chat e configura o menu de opções"""
        super().__init__(**kwargs)
        
        # Controle de paginação
        self.loaded_message_ids = set()
        self.first_loaded_message = None  
        self.is_loading_more = False 
        self.last_scroll_y = 0
        self.loading_messages = False
        self.can_remove = False
        self.is_marking_offline = False
        self.loading_indicator_visible = False
        
        # Controle de inatividade 
        self.heartbeat_event = None
        self.heartbeat_interval = 10
        self.last_heartbeat = None

        Clock.schedule_once(self.setup_scroll_binding, 0.1)
        
        self.image = AsyncImage(
            source='https://res.cloudinary.com/dsmgwupky/image/upload/v1762258289/Nenhum_chat_encontrado_-_Mensagem_vazia_1_y0csqu.png',
            size_hint=(0.65, 0.65),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        Clock.schedule_once(self.setup_menu, 0.2)
        
        # Registrar evento de destruição da tela
        self.bind(on_pre_leave=self.mark_offline_on_leave)
    
    def setup_menu(self, dt):
        """Configura o menu após os ids estarem disponíveis"""
        try:
            states = ['Ver perfil', 'Denunciar', 'Apagar conversa']
            menu_itens = [
                {'text': state, 'on_release': lambda x=state: self.replace_state(x)}
                for state in states
            ]
            
            self.menu = MDDropdownMenu(
                caller=self.ids.options,
                items=menu_itens,
                size_hint_x=None,
                position='bottom',
            )
            print('✓ Menu configurado com sucesso')
        except Exception as e:
            print(f'❌ Erro ao configurar menu: {e}')
    
    def setup_scroll_binding(self, dt):
        """Configura o binding do scroll após os ids estarem disponíveis"""
        try:
            self.ids.scroll_view.bind(scroll_y=self.on_scroll)
            print('✓ Scroll binding configurado com sucesso')
        except Exception as e:
            print(f'❌ Erro ao configurar scroll binding: {e}')
    
    # ==================== ENTRADA E SAÍDA DA TELA ====================
    
    def on_enter(self, *args):
        """Executa ao entrar na tela: marca online e inicia monitoramento"""
        print('='*50)
        print(f'🚪 ENTRANDO NO CHAT')
        print(f'Tipo: {self.perso}')
        print(f'Chat ID: {self.chat_id}')
        print('='*50)
        
        # Limpa flags
        self.is_marking_offline = False
        
        # Inicializa lista de mensagens se necessário
        if not self.messages:
            self.messages = []
        
        print(f'Total de mensagens no histórico: {len(self.messages)}')
        
        # Setup inicial
        self._setup_dialog()
        
        # MARCA COMO ONLINE PRIMEIRO (BLOQUEANTE)
        self.mark_user_online_blocking()
        
        # Carrega mensagens
        self.upload_historical_messages()
        
        # Marca mensagens como lidas
        self.mark_messages_as_read()
        
        # Inicia monitoramento
        self.start_heartbeat()
        self.event_state = Clock.schedule_interval(lambda dt: self.check_state(), 3)
        self.event_messages = Clock.schedule_interval(lambda dt: self.check_new_messages(), 2)
        
        print('✓ Chat iniciado com sucesso')
        print('='*50)
    
    def on_leave(self, *args):
        """Limpa tudo ao sair"""
        print('='*50)
        print('🚪 SAINDO DA TELA DE CHAT')
        print('='*50)
        
        # Para heartbeat
        self.stop_heartbeat()
        
        # Marca como offline COM PRIORIDADE
        self.mark_user_offline_priority()
        
        # Cancela verificações
        try:
            Clock.unschedule(self.event_state)
            Clock.unschedule(self.event_messages)
        except:
            pass
        
        # Remove binding do scroll
        try:
            self.ids.scroll_view.unbind(scroll_y=self.on_scroll)
        except:
            pass
        
        # Reseta flags
        self.is_loading_more = False
        self.loading_messages = False
        self.loading_indicator_visible = False
        
        # Limpa tela
        self.ids.main_scroll.clear_widgets()
        
        print('✓ Limpeza completa ao sair')
    
    # ==================== SETUP DE DIALOGS ====================
    
    def _setup_dialog(self):
        """Configura o dialog de confirmação para apagar mensagens"""
        cancell = MDButton(
            MDButtonText(
                text="cancelar",
                theme_text_color='Custom',
                text_color=get_color_from_hex('#3EC300')
            ),
            style="text",
        )
        cancell.on_release = lambda: self.dismiss_alert_dialog()

        delete = MDButton(
            MDButtonText(
                text="apagar",
                theme_text_color='Custom',
                text_color=get_color_from_hex('#F22B29')
            ),
            style="text",
        )
        delete.on_release = lambda: self.delete_messages()

        self.dialog = MDDialog(
            MDDialogIcon(
                icon="alert",
                theme_icon_color='Custom',
                icon_color=get_color_from_hex('#FFBD00')
            ),
            MDDialogHeadlineText(
                text="Apagar mensagens?",
            ),
            MDDialogSupportingText(
                text="Tem certeza de que quer excluir as mensagens enviadas? Após confirmar, elas serão apagadas de forma permanente.",
                halign='left',
                theme_text_color='Custom',
                text_color=get_color_from_hex('#212227')
            ),
            MDDialogButtonContainer(
                Widget(),
                cancell,
                delete,
                spacing="8dp",
            ),
        )
        # ==================== SISTEMA DE STATUS ONLINE/OFFLINE ====================
    
    def mark_user_online_blocking(self):
        """Marca o usuário como ONLINE de forma SÍNCRONA ao entrar"""
        try:
            url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Chats/{self.chat_id}/participants.json?auth={self.token_id}'
            
            current_timestamp = int(datetime.now().timestamp())
            
            if self.perso == 'Contractor':
                data = {
                    'contractor': 'online',
                    'contractor_last_seen': current_timestamp
                }
            else:
                data = {
                    'employee': 'online',
                    'employee_last_seen': current_timestamp
                }
            
            UrlRequest(
                url,
                method='PATCH',
                req_body=json.dumps(data),
                on_success=lambda req, result: self.on_online_success(current_timestamp),
                on_error=lambda req, error: print(f'❌ Erro ao marcar online: {error}')
            )
            
        except Exception as e:
            print(f'❌ Exceção ao marcar online: {e}')
    
    def on_online_success(self, timestamp):
        """Callback de sucesso ao marcar online"""
        print(f'✅ Marcado como ONLINE às {timestamp}')
        
        # Atualiza o status local
        if self.perso == 'Contractor':
            self.on_contractor = True
        else:
            self.on_employee = True
        
        # Atualiza UI imediatamente
        self.update_status_ui()
    
    def update_status_ui(self):
        """Atualiza a UI com o status do outro usuário"""
        try:
            if self.perso == 'Employee':
                # Sou Employee, mostro status do Contractor
                status = 'Online' if self.on_contractor else 'Offline'
                self.ids.state.text = status
                self.ids.state.text_color = 'green' if self.on_contractor else 'red'
            else:
                # Sou Contractor, mostro status do Employee
                status = 'Online' if self.on_employee else 'Offline'
                self.ids.state.text = status
                self.ids.state.text_color = 'green' if self.on_employee else 'red'
        except Exception as e:
            print(f'❌ Erro ao atualizar UI de status: {e}')
    
    def mark_user_offline_priority(self):
        """Marca como OFFLINE com PRIORIDADE MÁXIMA ao sair"""
        if self.is_marking_offline:
            return
        
        self.is_marking_offline = True
        
        try:
            url = f"https://obra-7ebd9-default-rtdb.firebaseio.com/Chats/{self.chat_id}/participants.json?auth={self.token_id}"
            
            current_timestamp = int(datetime.now().timestamp())
            
            if self.perso == 'Contractor':
                data = {
                    'contractor': 'offline',
                    'contractor_last_seen': current_timestamp
                }
            else:
                data = {
                    'employee': 'offline',
                    'employee_last_seen': current_timestamp
                }
            
            UrlRequest(
                url,
                method='PATCH',
                req_body=json.dumps(data),
                on_success=lambda req, result: self.on_offline_success(current_timestamp),
                on_error=lambda req, error: print(f'❌ Erro ao marcar offline: {error}'),
                timeout=2
            )
            
        except Exception as e:
            print(f'❌ Exceção ao marcar offline: {e}')
        finally:
            self.is_marking_offline = False
    
    def on_offline_success(self, timestamp):
        """Callback de sucesso ao marcar offline"""
        print(f'✅ Marcado como OFFLINE às {timestamp}')
    
    def mark_offline_on_leave(self, *args):
        """Compatibilidade com binding on_pre_leave"""
        self.mark_user_offline_priority()
    
    # ==================== HEARTBEAT SYSTEM ====================
    
    def start_heartbeat(self):
        """Inicia o sistema de heartbeat"""
        if self.heartbeat_event:
            Clock.unschedule(self.heartbeat_event)
        
        # Envia heartbeat imediatamente
        self.send_heartbeat()
        
        # Agenda heartbeat periódico
        self.heartbeat_event = Clock.schedule_interval(
            lambda dt: self.send_heartbeat(), 
            self.heartbeat_interval
        )
        print('✓ Sistema de heartbeat iniciado')
    
    def send_heartbeat(self):
        """Envia um 'batimento cardíaco' atualizando o timestamp"""
        try:
            url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Chats/{self.chat_id}/participants.json?auth={self.token_id}'
            
            current_timestamp = int(datetime.now().timestamp())
            
            if self.perso == 'Contractor':
                data = {
                    'contractor': 'online',
                    'contractor_last_seen': current_timestamp
                }
            else:
                data = {
                    'employee': 'online',
                    'employee_last_seen': current_timestamp
                }
            
            UrlRequest(
                url,
                method='PATCH',
                req_body=json.dumps(data),
                on_success=lambda req, result: self.on_heartbeat_success(current_timestamp),
                on_error=lambda req, error: print(f'❌ Erro no heartbeat: {error}')
            )
            
        except Exception as e:
            print(f'❌ Exceção ao enviar heartbeat: {e}')
    
    def on_heartbeat_success(self, timestamp):
        """Callback de sucesso do heartbeat"""
        self.last_heartbeat = timestamp
        print(f'💓 Heartbeat enviado: {timestamp}')
    
    def stop_heartbeat(self):
        """Para o sistema de heartbeat"""
        if self.heartbeat_event:
            Clock.unschedule(self.heartbeat_event)
            self.heartbeat_event = None
            print('✓ Heartbeat parado')
    
    # ==================== VERIFICAÇÃO DE STATUS ====================
    
    def check_state(self, *args):
        """Verifica o status do outro usuário"""
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Chats/{self.chat_id}/participants.json?auth={self.token_id}'
        UrlRequest(
            url, 
            method='GET',
            on_success=self.on_check_state_success,
            on_error=lambda req, error: print(f'❌ Erro ao verificar status: {error}')
        )
    
    def on_check_state_success(self, req, result):
        """Processa o resultado da verificação de status"""
        try:
            # Atualiza status local
            self.on_contractor = (result.get('contractor', 'offline') == 'online')
            self.on_employee = (result.get('employee', 'offline') == 'online')
            
            contractor_status = 'Online' if self.on_contractor else 'Offline'
            employee_status = 'Online' if self.on_employee else 'Offline'
            
            print(f'📊 Status - Contractor: {contractor_status} | Employee: {employee_status}')
            
            # Atualiza UI
            self.update_status_ui()
            
        except Exception as e:
            print(f'❌ Erro ao processar status: {e}')
    
    # ==================== ENVIO DE MENSAGENS ====================
    
    def add_message(self, *args):
        """Valida e prepara mensagem para envio"""
        msg = str(self.ids.message_text.text).strip().replace("'", '')
        
        if not msg:
            return
        
        print('='*50)
        print('📤 ENVIANDO MENSAGEM')
        print(f'Texto: "{msg}"')
        print(f'Remetente: {self.perso}')
        print('='*50)
        
        # Limpa o campo de texto IMEDIATAMENTE
        self.ids.message_text.text = ''
        
        # Envia a mensagem
        self.send_message_to_firebase(msg)
    
    def send_message_to_firebase(self, message_text):
        """Envia mensagem para o Firebase na estrutura unificada"""
        
        # Prepara objeto da mensagem COM timestamp
        timestamp = int(datetime.now().timestamp() * 1000)  # Milissegundos
        
        message_obj = {
            'sender': str(self.perso).lower(),
            'text': message_text,
            'timestamp': timestamp,
            'read_by_contractor': (self.perso == 'Contractor'),
            'read_by_employee': (self.perso == 'Employee')
        }
        
        print(f'📦 Objeto da mensagem: {message_obj}')
        
        # Adiciona à lista local IMEDIATAMENTE para exibição instantânea
        self.messages.append(message_obj)
        self.display_sent_message(message_text)
        
        # Envia para o Firebase usando PUSH para evitar race conditions
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Chats/{self.chat_id}/messages.json?auth={self.token_id}'
        
        UrlRequest(
            url,
            method='POST',  # POST cria uma nova entrada com ID único
            req_body=json.dumps(message_obj),
            on_success=lambda req, result: self.on_message_sent_success(message_text, timestamp),
            on_error=lambda req, error: self.on_message_error(message_text, error)
        )
    
    def on_message_sent_success(self, message_text, timestamp):
        """Callback de sucesso ao enviar mensagem"""
        print('✅ Mensagem enviada ao Firebase')
        
        # Atualiza metadata do chat
        self.update_chat_metadata(message_text, timestamp)
    
    def update_chat_metadata(self, message_text, timestamp):
        """Atualiza os metadados do chat (última mensagem, remetente, timestamp)"""
        
        url = f"https://obra-7ebd9-default-rtdb.firebaseio.com/Chats/{self.chat_id}/metadata.json?auth={self.token_id}"
        
        data = {
            'last_message': message_text,
            'last_sender': self.perso.lower(),
            'last_timestamp': timestamp
        }
        
        UrlRequest(
            url,
            method='PATCH',
            req_body=json.dumps(data),
            on_success=lambda req, result: print('✅ Metadata atualizado'),
            on_error=lambda req, error: print(f'❌ Erro ao atualizar metadata: {error}')
        )
    
    def display_sent_message(self, message_text):
        """Exibe a mensagem enviada na tela"""
        try:
            # Cria balão de mensagem
            msg_widget = MessageRight(text=message_text)
            
            # Adiciona com animação
            msg_widget.opacity = 0
            self.ids.main_scroll.add_widget(msg_widget)
            
            anim = Animation(opacity=1, duration=0.3)
            anim.start(msg_widget)
            
            # Scroll para baixo
            Clock.schedule_once(lambda dt: setattr(self.ids.scroll_view, 'scroll_y', 0), 0.1)
            
            print('✅ Mensagem exibida na tela')
            
        except Exception as e:
            print(f'❌ Erro ao exibir mensagem: {e}')
    
    def on_message_error(self, message_text, error):
        """Callback de erro ao enviar mensagem"""
        print(f'❌ Erro ao enviar mensagem: {error}')
        
        # Remove da lista local se falhou
        if self.messages and self.messages[-1]['text'] == message_text:
            self.messages.pop()
        
        # Mostra erro para o usuário
        self.show_error('Não foi possível enviar a mensagem')
        Clock.schedule_once(lambda dt: self.show_error('Verifique sua conexão'), 2)
        # ==================== CARREGAMENTO DO HISTÓRICO ====================
    
    def upload_historical_messages(self):
        """Carrega o histórico de mensagens progressivamente com animação"""
        print('='*50)
        print(f'📊 CARREGAMENTO INICIAL')
        print(f'Total de mensagens disponíveis: {len(self.messages)}')
        
        # Limpa widgets e IDs anteriores
        self.ids.main_scroll.clear_widgets()
        self.loaded_message_ids.clear()
        
        # Ordena mensagens por timestamp
        sorted_messages = sorted(self.messages, key=lambda m: m.get('timestamp', 0))
        
        # Pega as últimas N mensagens
        if len(sorted_messages) > self.MESSAGES_PER_LOAD:
            messages_to_load = sorted_messages[-self.MESSAGES_PER_LOAD:]
            print(f'⚠️  Limitando para as últimas {self.MESSAGES_PER_LOAD} mensagens')
        else:
            messages_to_load = sorted_messages
            print(f'✓ Carregando todas as {len(sorted_messages)} mensagens')
        
        print(f'Mensagens a carregar: {len(messages_to_load)}')
        
        # Marca as mensagens como carregadas
        for idx, msg in enumerate(messages_to_load):
            msg_id = f"{msg['sender']}_{msg['text']}_{msg['timestamp']}"
            self.loaded_message_ids.add(msg_id)
        
        # Guarda referência da primeira mensagem
        if messages_to_load:
            self.first_loaded_message = messages_to_load[0]
            print(f'✓ Primeira mensagem: "{self.first_loaded_message["text"][:30]}..."')
        
        # Carrega em lotes para não travar a UI
        def load_batch(batch_start):
            batch_end = min(batch_start + self.BATCH_SIZE, len(messages_to_load))
            
            print(f'  → Carregando lote {batch_start} a {batch_end}')
            
            for i in range(batch_start, batch_end):
                message = messages_to_load[i]
                
                if message['sender'] == str(self.perso).lower():
                    msg = MessageRight(message['text'])
                else:
                    msg = MessageLeft(message['text'])
                
                # Adiciona com animação de fade
                msg.opacity = 0
                self.ids.main_scroll.add_widget(msg)
                
                # Anima a entrada da mensagem
                anim = Animation(opacity=1, duration=0.3)
                anim.start(msg)
            
            if batch_end < len(messages_to_load):
                Clock.schedule_once(lambda dt: load_batch(batch_end), 0.10)
            else:
                Clock.schedule_once(self.scroll_to_bottom, 0.3)
                print(f'✓ Todas as {len(messages_to_load)} mensagens foram carregadas!')
        
        if messages_to_load:
            load_batch(0)
        else:
            print('⚠️  Nenhuma mensagem para carregar')
        
        print('='*50)
    
    def on_scroll(self, instance, value):
        """Detecta scroll para cima e carrega mensagens antigas com debounce"""
        if value >= 0.95 and not self.is_loading_more:
            if hasattr(self, 'last_scroll_y') and value > self.last_scroll_y:
                print('🔝 Usuário chegou no topo! Aguardando para carregar...')
                Clock.unschedule(self.delayed_load_more)
                Clock.schedule_once(self.delayed_load_more, 0.3)
        
        self.last_scroll_y = value
    
    def delayed_load_more(self, dt):
        """Carrega mais mensagens com delay para evitar spam"""
        if not self.is_loading_more:
            self.upload_more_messages()
    
    def upload_more_messages(self, *args):
        """Carrega mais mensagens ao chegar no topo com animação suave"""
        
        if self.is_loading_more:
            print('⏳ Já está carregando mensagens...')
            return
        
        if not self.first_loaded_message:
            print('⚠️  Nenhuma mensagem de referência encontrada')
            return
        
        print('='*50)
        print('📥 CARREGANDO MAIS MENSAGENS ANTIGAS')
        
        self.is_loading_more = True
        self.show_loading_indicator()
        
        # Ordena mensagens
        sorted_messages = sorted(self.messages, key=lambda m: m.get('timestamp', 0))
        
        # Encontra o índice da primeira mensagem carregada
        first_msg_index = None
        for idx, msg in enumerate(sorted_messages):
            if (msg['sender'] == self.first_loaded_message['sender'] and 
                msg['text'] == self.first_loaded_message['text'] and
                msg['timestamp'] == self.first_loaded_message['timestamp']):
                first_msg_index = idx
                break
        
        if first_msg_index is None:
            print('✗ Primeira mensagem não encontrada no histórico')
            self.is_loading_more = False
            self.hide_loading_indicator()
            return
        
        if first_msg_index == 0:
            print('✓ Não há mais mensagens antigas para carregar')
            self.is_loading_more = False
            self.hide_loading_indicator()
            return
        
        # Calcula o índice de início
        start_index = max(0, first_msg_index - self.MESSAGES_PER_LOAD)
        messages_to_load = sorted_messages[start_index:first_msg_index]
        
        print(f'Índice da primeira mensagem carregada: {first_msg_index}')
        print(f'Buscando mensagens do índice {start_index} até {first_msg_index}')
        print(f'Mensagens encontradas: {len(messages_to_load)}')
        
        # Filtra apenas mensagens não carregadas
        new_messages = []
        for idx, msg in enumerate(messages_to_load):
            msg_id = f"{msg['sender']}_{msg['text']}_{msg['timestamp']}"
            if msg_id not in self.loaded_message_ids:
                new_messages.append(msg)
                self.loaded_message_ids.add(msg_id)
        
        if not new_messages:
            print('✓ Todas as mensagens anteriores já foram carregadas')
            self.is_loading_more = False
            self.hide_loading_indicator()
            return
        
        print(f'✓ {len(new_messages)} novas mensagens para adicionar')
        
        # Atualiza a primeira mensagem
        self.first_loaded_message = new_messages[0]
        
        # Pega referências
        scroll_view = self.ids.scroll_view
        container = self.ids.main_scroll
        
        # Salva a altura atual do container
        initial_height = container.height
        
        print(f'Altura inicial do container: {initial_height}')
        
        # Carrega as novas mensagens NO TOPO com animação
        def load_batch(batch_start):
            batch_end = min(batch_start + self.BATCH_SIZE, len(new_messages))
            
            print(f'  → Adicionando lote {batch_start} a {batch_end} no topo')
            
            for i in range(batch_start, batch_end):
                message = new_messages[i]
                
                if message['sender'] == str(self.perso).lower():
                    msg = MessageRight(message['text'])
                else:
                    msg = MessageLeft(message['text'])
                
                msg.opacity = 0
                container.add_widget(msg, index=len(container.children))
                
                anim = Animation(opacity=1, duration=0.3)
                anim.start(msg)
            
            if batch_end < len(new_messages):
                Clock.schedule_once(lambda dt: load_batch(batch_end), 0.10)
            else:
                def finalize_loading(dt):
                    new_height = container.height
                    height_diff = new_height - initial_height
                    
                    print(f'Nova altura do container: {new_height}')
                    print(f'Diferença de altura: {height_diff}')
                    
                    if scroll_view.height > 0 and new_height > scroll_view.height:
                        scroll_view.scroll_y = min(1.0, scroll_view.scroll_y + (height_diff / (new_height - scroll_view.height)))
                    
                    self.is_loading_more = False
                    self.hide_loading_indicator()
                    print(f'✓ {len(new_messages)} mensagens antigas carregadas!')
                    print('='*50)
                
                Clock.schedule_once(finalize_loading, 0.3)
        
        load_batch(0)

    # ==================== VERIFICAÇÃO DE NOVAS MENSAGENS ====================

    def check_new_messages(self):
        """Verifica periodicamente se há novas mensagens"""
        
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Chats/{self.chat_id}/messages.json?auth={self.token_id}'
        
        UrlRequest(
            url,
            method='GET',
            on_success=self.process_new_messages,
            on_error=lambda req, error: print(f'❌ Erro ao verificar mensagens: {error}')
        )

    def process_new_messages(self, request, result):
        """Processa novas mensagens do Firebase"""
        
        try:
            if not result:
                return
            
            # Converte o objeto do Firebase em lista
            remote_messages = []
            for key, msg_data in result.items():
                remote_messages.append(msg_data)
            
            # Ordena por timestamp
            remote_messages.sort(key=lambda m: m.get('timestamp', 0))
            
            # Compara tamanhos primeiro (otimização)
            if len(remote_messages) <= len(self.messages):
                return  # Não há novas mensagens
            
            # Cria hash set das mensagens locais
            local_hashes = {f"{m['sender']}_{m['text']}_{m['timestamp']}" for m in self.messages}
            
            # Encontra mensagens novas
            new_messages = []
            for msg in remote_messages:
                msg_hash = f"{msg['sender']}_{msg['text']}_{msg['timestamp']}"
                if msg_hash not in local_hashes and msg['sender'] != self.perso.lower():
                    new_messages.append(msg)
            
            if new_messages:
                print('='*50)
                print(f'📨 {len(new_messages)} NOVA(S) MENSAGEM(NS)')
                print('='*50)
                
                # Adiciona ao histórico local
                self.messages.extend(new_messages)
                
                # Exibe mensagens novas
                for msg in new_messages:
                    self.display_received_message(msg)
                
                # Marca como lida
                self.mark_messages_as_read()
                
                print('✅ Histórico local atualizado')
            
        except Exception as e:
            print(f'❌ Erro ao processar novas mensagens: {e}')
            import traceback
            traceback.print_exc()

    def display_received_message(self, message_obj):
        """Exibe mensagem recebida na tela"""
        
        try:
            message_text = message_obj.get('text', '')
            sender = message_obj.get('sender', '').lower()
            
            # Cria balão correto
            if sender == self.perso.lower():
                msg_widget = MessageRight(text=message_text)
            else:
                msg_widget = MessageLeft(text=message_text)
            
            # Adiciona com animação
            msg_widget.opacity = 0
            self.ids.main_scroll.add_widget(msg_widget)
            
            anim = Animation(opacity=1, duration=0.3)
            anim.start(msg_widget)
            
            # Scroll para baixo
            Clock.schedule_once(lambda dt: setattr(self.ids.scroll_view, 'scroll_y', 0), 0.1)
            
            print(f'✅ Mensagem de {sender} exibida')
            
        except Exception as e:
            print(f'❌ Erro ao exibir mensagem recebida: {e}')

    def mark_messages_as_read(self):
        """Marca todas as mensagens não lidas como lidas"""
        
        try:
            url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Chats/{self.chat_id}/messages.json?auth={self.token_id}'
            
            # Busca todas as mensagens
            UrlRequest(
                url,
                method='GET',
                on_success=self.update_read_status,
                on_error=lambda req, error: print(f'❌ Erro ao buscar mensagens para marcar: {error}')
            )
            
        except Exception as e:
            print(f'❌ Erro ao marcar mensagens como lidas: {e}')

    def update_read_status(self, req, result):
        """Atualiza o status de leitura das mensagens"""
        
        try:
            if not result:
                return
            
            updates = {}
            
            for msg_id, msg_data in result.items():
                # Verifica se a mensagem não foi enviada por mim e se ainda não foi lida
                if msg_data['sender'] != self.perso.lower():
                    if self.perso == 'Contractor' and not msg_data.get('read_by_contractor', False):
                        updates[f'{msg_id}/read_by_contractor'] = True
                    elif self.perso == 'Employee' and not msg_data.get('read_by_employee', False):
                        updates[f'{msg_id}/read_by_employee'] = True
            
            if updates:
                url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Chats/{self.chat_id}/messages.json?auth={self.token_id}'
                
                UrlRequest(
                    url,
                    method='PATCH',
                    req_body=json.dumps(updates),
                    on_success=lambda req, result: print(f'✅ {len(updates)} mensagens marcadas como lidas'),
                    on_error=lambda req, error: print(f'❌ Erro ao atualizar status de leitura: {error}')
                )
            
        except Exception as e:
            print(f'❌ Erro ao processar status de leitura: {e}')

    # ==================== APAGAR MENSAGENS ====================

    def show_alert_dialog(self):
        """Exibe o dialog de confirmação"""
        self.dialog.open()

    def dismiss_alert_dialog(self, *args):
        """Fecha o dialog de confirmação"""
        self.dialog.dismiss()

    def delete_messages(self, *args):
        """Apaga TODAS as mensagens do chat (para ambos usuários)"""
        
        url = f"https://obra-7ebd9-default-rtdb.firebaseio.com/Chats/{self.chat_id}/messages.json?auth={self.token_id}"
        
        UrlRequest(
            url,
            method='DELETE',
            on_success=self.on_delete_success,
            on_error=lambda req, error: print(f'❌ Erro ao deletar: {error}')
        )

    def on_delete_success(self, req, result):
        """Callback de sucesso ao deletar mensagens"""
        print('✅ Mensagens deletadas com sucesso')
        
        self.dialog.dismiss()
        self.ids.main_scroll.clear_widgets()
        self.messages = []
        
        self.show_message('Mensagens apagadas com sucesso')

    # ==================== MENU DE OPÇÕES ====================

    def replace_state(self, state: str):
        """Gerencia as ações do menu de opções"""
        if not state:
            return
            
        if state == 'Ver perfil':
            if self.perso == 'Contractor':
                url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.employee_id}.json?auth={self.token_id}'
                UrlRequest(url, on_success=self.next_perfil_employee)
            else:
                url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Users/{self.contractor_id}.json?auth={self.token_id}'
                UrlRequest(url, on_success=self.next_perfil_contractor)
                
        elif state == 'Apagar conversa':
            self.show_alert_dialog()
        else:
            self.next_reported()

        self.menu.dismiss()

    def next_reported(self):
        """Chama a tela de denunciar o chat"""
        app = MDApp.get_running_app()
        scrennmanager = app.root
        report = scrennmanager.get_screen('ReportChat')
        report.token_id = self.token_id
        report.local_id = self.local_id
        report.api_key = self.api_key
        report.chat_id = self.chat_id
        report.name_sender = self.name_sender
        report.email_sender = self.email_sender
        report.username = self.name_user
        report.avatar = self.perfil
        report.refresh_token = self.refresh_token
        report.perso = self.perso
        if self.perso == 'Employee':
            report.key_accused = self.contractor_id
        else:
            report.key_accused = self.employee_id
        scrennmanager.transition = SlideTransition(direction='right')
        scrennmanager.current = 'ReportChat'

    def next_perfil_contractor(self, req, result):
        """Navega para o perfil do contratante"""
        self.menu.dismiss()
        app = MDApp.get_running_app()
        perfil = app.root.get_screen('PerfilContractorGlobal')
        
        perfil.api_key = self.api_key
        perfil.token_id = self.token_id
        perfil.local_id = self.local_id
        perfil.perso = self.perso
        perfil.refresh_token = self.refresh_token
        perfil.username = result['name']
        perfil.avatar = result['perfil']
        perfil.company = result['company']
        perfil.city = result['city']
        perfil.state = result['state']
        perfil.telefone = result['telefone']
        perfil.chat_id = self.chat_id
        perfil.email = result['email']
        perfil.function = result['function']
        
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'PerfilContractorGlobal'

    def next_perfil_employee(self, req, result):
        """Navega para o perfil do funcionário"""
        self.menu.dismiss()
        app = MDApp.get_running_app()
        perfil = app.root.get_screen('PerfilEmployeeGlobal')
        
        perfil.api_key = self.api_key
        perfil.token_id = self.token_id
        perfil.local_id = self.employee_id
        perfil.refresh_token = self.refresh_token
        perfil.chat_id = self.chat_id
        perfil.avatar = result['avatar']
        perfil.city = result['city']
        perfil.state = result['state']
        perfil.employee_name = result['Name']
        perfil.employee_function = result['function']
        perfil.employee_mail = result['email']
        perfil.employee_telephone = result['telefone']
        perfil.employee_summary = result['sumary']
        perfil.skills = result['skills']
        
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'PerfilEmployeeGlobal'

    # ==================== NAVEGAÇÃO ====================

    def show_loading_indicator(self):
        """Exibe um indicador visual de carregamento"""
        if not self.loading_indicator_visible:
            self.loading_indicator_visible = True
            print('⏳ Mostrando indicador de carregamento...')

    def hide_loading_indicator(self):
        """Esconde o indicador de carregamento"""
        if self.loading_indicator_visible:
            self.loading_indicator_visible = False
            print('✓ Escondendo indicador de carregamento...')

    def scroll_to_bottom(self, *args):
        """Move o scroll para o final (mensagens mais recentes)"""
        self.ids.scroll_view.scroll_y = 0

    def back(self, *args):
        """Volta para a lista de chats e marca como offline"""
        print('🔙 Voltando para lista de chats...')
        self.mark_user_offline_priority()
        Clock.schedule_once(self.finally_back, 0.3)

    def finally_back(self, dt=None):
        """Finaliza navegação de volta"""
        app = MDApp.get_running_app()
        screenmanager = app.root
        
        if self.perso == 'Employee':
            screen = screenmanager.get_screen('ListChat')
        else:
            screen = screenmanager.get_screen('ListChatContractor')
        
        screen.token_id = self.token_id
        screen.local_id = self.local_id
        screen.perso = self.perso
        screen.refresh_token = self.refresh_token
        screen.api_key = self.api_key
        
        self.manager.transition = SlideTransition(direction='left')
        
        if self.perso == 'Employee':
            self.manager.current = 'ListChat'
        else:
            self.manager.current = 'ListChatContractor'

    # ==================== FEEDBACK VISUAL ====================

    def show_message(self, message, color='#2196F3'):
        """Exibe snackbar com mensagem"""
        MDSnackbar(
            MDSnackbarText(
                text=message,
                theme_text_color='Custom',
                text_color='white',
                bold=True,
                halign='center',
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.94,
            theme_bg_color='Custom',
            background_color=get_color_from_hex(color),
            duration=3
        ).open()

    def show_error(self, error_message):
        """Exibe snackbar de erro"""
        self.show_message(error_message, color='#FF0000')
        
