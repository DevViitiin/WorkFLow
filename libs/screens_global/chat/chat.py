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


# ==================== COMPONENTES DE MENSAGEM ====================

class MessageRight(MDBoxLayout):
    """Balão de mensagem alinhado à direita (mensagens enviadas)"""
    
    def __init__(self, text="Meu irmão quer muito atuar nessa área", **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.adaptive_height = True
        self.spacing = 0
        
        spacer = Widget(size_hint_x=1)
        self.add_widget(spacer)
        
        balloon = MDBoxLayout(
            orientation='vertical',
            theme_bg_color='Custom',
            md_bg_color=get_color_from_hex('#DCF8C6'),
            padding=[15, 15, 15, 15],
            radius=[15, 15, 5, 15],
            size_hint_x=None,
            width=dp(280),
            adaptive_height=True
        )
        
        message_label = MDLabel(
            text=text,
            font_style="Label",
            role="medium",
            adaptive_height=True,
            size_hint_y=None
        )
        message_label.bind(
            width=lambda instance, value: setattr(
                instance, 'text_size', (value, None)
            )
        )
        
        balloon.add_widget(message_label)
        self.add_widget(balloon)


class MessageLeft(BoxLayout):
    """Balão de mensagem alinhado à esquerda (mensagens recebidas)"""
    
    def __init__(self, text="Eu já pensei em fazer gastronomia, mais não obrigada!", **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = self.minimum_height
        self.adaptive_height = True
        self.spacing = 0
        
        balloon = MDBoxLayout(
            orientation='vertical',
            theme_bg_color='Custom',
            md_bg_color=get_color_from_hex('#F1F0F0'),
            padding=[15, 15, 15, 15],
            radius=[15, 15, 5, 15],
            size_hint_x=None,
            width=dp(280),
            adaptive_height=True
        )
        
        message_label = MDLabel(
            text=text,
            font_style="Label",
            role="medium",
            adaptive_height=True,
            size_hint_y=None,
        )
        message_label.bind(
            width=lambda instance, value: setattr(
                instance, 'text_size', (value, None)
            )
        )
        
        def update_height(*args):
            self.height = balloon.height

        balloon.bind(height=update_height)
        balloon.add_widget(message_label)
        self.add_widget(balloon)


# ==================== TELA DE CHAT ====================

class Chat(MDScreen):
    # IDs dos participantes
    chat_id = StringProperty()
    contractor_id = StringProperty()
    employee_id = StringProperty()
    
    # Informações visuais
    perfil = StringProperty()
    name_user = StringProperty()

    # caso haja denunciar aqui está o nome e email 
    # do usuario ao qual vai enviar a denunca
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
    
    # Gerenciamento de mensagens
    messages_contractor_off = ObjectProperty()
    messages_employee_off = ObjectProperty()
    cont_message = 0
    historical_contractor = ObjectProperty()
    historical_employee = ObjectProperty()
    historical_messages = ObjectProperty()
    
    # ==================== CONFIGURAÇÕES DE CARREGAMENTO ====================
    # AJUSTE AQUI: Altere este número para testar diferentes quantidades
    MESSAGES_PER_LOAD = 10  # ← MUDE ESTE VALOR PARA TESTAR (5, 10, 20, 50, etc)
    BATCH_SIZE = 3  # ← Mensagens carregadas por vez (para não travar UI)
    
    # ==================== INICIALIZAÇÃO ====================
    
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
        
        # controle de inatividade 
        self.heartbeat_event = None
        self.heartbeat_interval = 10  # Atualiza a cada 10 segundos
        self.last_heartbeat = None

        # Bind do scroll será feito após o ids estar disponível
        Clock.schedule_once(self.setup_scroll_binding, 0.1)
        
        self.image = AsyncImage(
            source='https://res.cloudinary.com/dsmgwupky/image/upload/v1762258289/Nenhum_chat_encontrado_-_Mensagem_vazia_1_y0csqu.png',
            size_hint=(0.65, 0.65),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        states = ['Ver perfil', 'Denunciar', 'Apagar conversa']
        menu_itens = [
            {'text': state, 'on_release': lambda x=state: self.replace_state(x)}
            for state in states
        ]
        
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
                position='bottom',
            )
            print('Menu configurado com sucesso')
        except Exception as e:
            print(f'Erro ao configurar menu: {e}')
    
    def setup_scroll_binding(self, dt):
        """Configura o binding do scroll após os ids estarem disponíveis"""
        try:
            self.ids.scroll_view.bind(scroll_y=self.on_scroll)
            print('✓ Scroll binding configurado com sucesso')
        except Exception as e:
            print(f'✗ Erro ao configurar scroll binding: {e}')
    
    def on_enter(self, *args):
        """Executa ao entrar na tela: carrega histórico e configura dialogs"""
        if self.on_contractor:
            self.on_contractor = 'Online'
        else:
            self.on_contractor = 'Offline'
        
        if self.on_employee:
            self.on_employee = 'Online'
        else:
            self.on_employee = 'Offline'

        print('='*50)
        if self.on_employee == self.perso:
            self.ids.state.text = self.on_contractor
            if self.on_contractor == 'Online':
                self.ids.state.text_color = 'green'
            else:
                self.ids.state.text_color = 'red'
            
        else:
            self.ids.state.text = self.on_employee
            if self.on_employee == 'Online':
                self.ids.state.text_color = 'green'
            else:
                self.ids.state.text_color = 'red'
        
        self.start_heartbeat()
        print('✓ Sistema de heartbeat iniciado')

        print(f'ENTRANDO NO CHAT - Tipo: {self.perso}')
        print(f'Chat ID: {self.chat_id}')
        print(f'Total de mensagens no histórico: {len(self.historical_messages) if self.historical_messages else 0}')
        print('='*50)
        
        self.is_marking_offline = False
        
        if self.perso == 'Contractor':
            self.historical_messages = self.historical_contractor
        else:
            self.historical_messages = self.historical_employee
        
        self._setup_dialog()
        self.upload_on(self.perso)
        self.upload_historical_messages()
        self.upload_messages_offline()
        Clock.schedule_interval(lambda dt: self.check_state(), 3)
        Clock.schedule_interval(lambda dt: self.check_new_messages(), 2)
    
    
    # ============== verifica o estado online/offline ==========================
    def start_heartbeat(self):
        """Inicia o sistema de heartbeat (batimento cardíaco)"""
        # Cancela qualquer heartbeat anterior
        if self.heartbeat_event:
            Clock.unschedule(self.heartbeat_event)
        
        # Envia heartbeat imediatamente
        self.send_heartbeat()
        
        # Agenda heartbeat periódico
        self.heartbeat_event = Clock.schedule_interval(
            lambda dt: self.send_heartbeat(), 
            self.heartbeat_interval
        )

    def send_heartbeat(self):
        """Envia um 'batimento cardíaco' atualizando o timestamp"""
        try:
            url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Chats/{self.chat_id}/participants.json?auth={self.token_id}'
            
            # Timestamp atual em segundos
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

    def check_state(self, *args):
        """Puxa o estado dos usuarios do banco de dados """
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Chats/{self.chat_id}/participants.json?auth={self.token_id}'
        UrlRequest(
            url, 
            method='GET',
            on_success=self.check_state2,
        )
    
    def check_state2(self, req, result):
        """Atualiza o estado do outro participante do chat"""
        print('Verificando o estado do usuario rs')
        self.on_contractor = str(result['contractor']).capitalize()
        self.on_employee = str(result['employee']).capitalize()
        print('Estado do contratante: ', self.on_contractor)
        print('Estado do funciónario: ', self.on_employee)
        if self.on_employee == self.perso:
            self.ids.state.text = self.on_contractor
            if self.on_contractor == 'Online':
                self.ids.state.text_color = 'green'
            else:
                self.ids.state.text_color = 'red'
            
        else:
            self.ids.state.text = self.on_employee
            if self.on_employee == 'Online':
                self.ids.state.text_color = 'green'
            else:
                self.ids.state.text_color = 'red'
        print('='*50)

    # Carregamento inicial do historico de mensagens ----------------------------------------------------------
    def upload_historical_messages(self):
        """Carrega o histórico de mensagens progressivamente com animação"""
        print('='*50)
        print(f'📊 CARREGAMENTO INICIAL')
        print(f'Total de mensagens disponíveis: {len(self.historical_messages)}')
        
        # Limpa widgets e IDs anteriores
        self.ids.main_scroll.clear_widgets()
        self.loaded_message_ids.clear()
        
        # Pega as últimas N mensagens
        if len(self.historical_messages) > self.MESSAGES_PER_LOAD:
            messages_to_load = self.historical_messages[-self.MESSAGES_PER_LOAD:]
            print(f'⚠️  Limitando para as últimas {self.MESSAGES_PER_LOAD} mensagens')
        else:
            messages_to_load = self.historical_messages
            print(f'✓ Carregando todas as {len(self.historical_messages)} mensagens')
        
        print(f'Mensagens a carregar: {len(messages_to_load)}')
        
        # Marca as mensagens como carregadas
        for idx, msg in enumerate(messages_to_load):
            msg_id = f"{msg['who']}_{msg['message']}_{idx}"
            self.loaded_message_ids.add(msg_id)
        
        # Guarda referência da primeira mensagem
        if messages_to_load:
            self.first_loaded_message = messages_to_load[0]
            print(f'✓ Primeira mensagem: "{self.first_loaded_message["message"][:30]}..."')
        
        # Carrega em lotes para não travar a UI
        def load_batch(batch_start):
            batch_end = min(batch_start + self.BATCH_SIZE, len(messages_to_load))
            
            print(f'  → Carregando lote {batch_start} a {batch_end}')
            
            for i in range(batch_start, batch_end):
                message = messages_to_load[i]
                
                if message['who'] == str(self.perso).lower():
                    msg = MessageRight(message['message'])
                else:
                    msg = MessageLeft(message['message'])
                
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
        # Quando o scroll_y está perto de 1.0, está no topo
        if value >= 0.95 and not self.is_loading_more:
            # Verifica se está scrollando para cima
            if hasattr(self, 'last_scroll_y') and value > self.last_scroll_y:
                print('🔝 Usuário chegou no topo! Aguardando para carregar...')
                # Adiciona um pequeno delay para evitar múltiplas chamadas
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
        
        # Encontra o índice da primeira mensagem carregada
        first_msg_index = None
        for idx, msg in enumerate(self.historical_messages):
            if (msg['who'] == self.first_loaded_message['who'] and 
                msg['message'] == self.first_loaded_message['message']):
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
            self.show_message('Não há mais mensagens antigas', '#FF9800')
            return
        
        # Calcula o índice de início
        start_index = max(0, first_msg_index - self.MESSAGES_PER_LOAD)
        messages_to_load = self.historical_messages[start_index:first_msg_index]
        
        print(f'Índice da primeira mensagem carregada: {first_msg_index}')
        print(f'Buscando mensagens do índice {start_index} até {first_msg_index}')
        print(f'Mensagens encontradas: {len(messages_to_load)}')
        
        # Filtra apenas mensagens não carregadas
        new_messages = []
        for idx, msg in enumerate(messages_to_load):
            msg_id = f"{msg['who']}_{msg['message']}_{start_index + idx}"
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
        
        # Salva a altura atual do container para ajustar o scroll depois
        initial_height = container.height
        
        print(f'Altura inicial do container: {initial_height}')
        
        # Carrega as novas mensagens NO TOPO com animação
        def load_batch(batch_start):
            batch_end = min(batch_start + self.BATCH_SIZE, len(new_messages))
            
            print(f'  → Adicionando lote {batch_start} a {batch_end} no topo')
            
            for i in range(batch_start, batch_end):
                message = new_messages[i]
                
                if message['who'] == str(self.perso).lower():
                    msg = MessageRight(message['message'])
                else:
                    msg = MessageLeft(message['message'])
                
                # Adiciona invisível primeiro
                msg.opacity = 0
                container.add_widget(msg, index=len(container.children))
                
                # Anima a entrada da mensagem
                anim = Animation(opacity=1, duration=0.3)
                anim.start(msg)
            
            if batch_end < len(new_messages):
                # Continua carregando com delay
                Clock.schedule_once(lambda dt: load_batch(batch_end), 0.10)
            else:
                # Todas as mensagens foram carregadas
                def finalize_loading(dt):
                    # Calcula a diferença de altura
                    new_height = container.height
                    height_diff = new_height - initial_height
                    
                    print(f'Nova altura do container: {new_height}')
                    print(f'Diferença de altura: {height_diff}')
                    
                    # Ajusta o scroll para manter a posição visual
                    # (o scroll_y é uma porcentagem, então precisamos recalcular)
                    if scroll_view.height > 0 and new_height > scroll_view.height:
                        # Mantém a mesma posição visual aproximada
                        scroll_view.scroll_y = min(1.0, scroll_view.scroll_y + (height_diff / (new_height - scroll_view.height)))
                    
                    self.is_loading_more = False
                    self.hide_loading_indicator()
                    print(f'✓ {len(new_messages)} mensagens antigas carregadas!')
                    print('='*50)
                
                Clock.schedule_once(finalize_loading, 0.3)
        
        load_batch(0)
    
    # ================= Carregar mensagens offline ====================
    def upload_messages_offline(self, *args):
        """Carrega as mensagens que foram enviadas
           Enquanto o usuario estava offline"""
        update = []
        messages = []
        if self.perso == 'Contractor':
            messages = self.messages_contractor_off
        else:
            messages = self.messages_employee_off
        who = ''
        if self.perso == 'Contractor':
            who = 'employee'
        else:
            who = 'contractor'
        print('Essas são as mensagens offline enviadas pelo parceiro de chat: ', messages)
        for message in messages:
            msg = MessageLeft(message)
            print('Mensagem: ', message)
            line = {
                'who': who,
                'message': message
            }
            update.append(line)
            Clock.schedule_once(lambda dt, m=msg: self.ids.main_scroll.add_widget(m), 2)

        print('😴 Mensagens offlines carregadas chefe')
        self.clear_offline_messages()
        self.add_to_historical(update)
    
    def clear_offline_messages(self, *args):
        """Depois que carrega a lista de mensagens offline
           Essa função limpa a lista e salva no banco de dados"""
        base_url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Chats/{self.chat_id}' 
        data = {
            f'{str(self.perso).lower()}': '[]'
        }
        UrlRequest(
            f'{base_url}/message_offline.json?auth={self.token_id}',
            method='PATCH',
            req_body=json.dumps(data),
            on_success=self.finally_clear_off_msg,
            on_error=self.error1
        )
    
    def error1(self, req, result):
        self.open_popup(
        retry_callback=lambda: self.upload_messages_offline()
    )
    def finally_clear_off_msg(self, req, result):
        """Foi finalizada com sucesso a limpeza das mensagens offline"""
        print('Mensagens offlines apagadas papai👌')
    
    def add_to_historical(self, update):
        """Atualiza o historico de mensagens dos usuarios do chat"""
        url = f"https://obra-7ebd9-default-rtdb.firebaseio.com/Chats/{self.chat_id}"

        # históricos atuais
        historical = self.historical_contractor
        historical_fuc = self.historical_employee

        # ADICIONA cada item do update ao final dos históricos
        historical.extend(update)          # antes: append(line)
        historical_fuc.extend(update)

        # salva de volta
        self.historical_contractor = historical
        self.historical_employee = historical_fuc

        data = {
            'messages_contractor': f"{historical}",
            'messages_employee': f"{historical_fuc}"
        }

        UrlRequest(
            f"{url}/historical_messages.json?auth={self.token_id}",
            method='PATCH',
            req_body=json.dumps(data),
            on_success=self.finally_add_to_historical
        )
    
    def finally_add_to_historical(self, req, result):
        """Finalização da função que atualiza os historicals"""
        print('Historicos atualizados❤️‍🩹')
        print('Resultado: ', result)
        print('=' * 50)

    # ================= Enviar mensagens ==============================
    def add_message(self, *args):
        """Verifica se a mensagem está apta a ser enviada"""
        msg = str(self.ids.message_text.text).replace("'", '')
        if not msg:
            self.show_error('A mensagem não pode estar vazia')
            return

        print('A mensagem pode ser enviada👉👈')
        self.add_message2(msg)
    
    def add_message2(self, message):
        """Salva a mensagem no banco de dados Firebase"""
        
        base_url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Chats/{self.chat_id}'
        is_contractor = self.perso == 'Contractor'
        recipient_online = ''
        if is_contractor:
            recipient_online = self.on_employee
        else:
            recipient_online = self.on_contractor
            
        # Prepara a mensagem como dicionário (consistente para ambos os casos)
        message_dict = {
            'who': str(self.perso).lower(),
            'message': message
        }
        
        # Seleciona os historiais corretos baseado no tipo de usuário
        sender_historical = self.historical_contractor if is_contractor else self.historical_employee
        recipient_historical = self.historical_employee if is_contractor else self.historical_contractor
        
        if recipient_online:
            # Destinatário online: salva nos dois historiais
            sender_historical.append(message_dict)
            recipient_historical.append(message_dict)
            
            # Atualiza as referências
            if is_contractor:
                self.historical_contractor = sender_historical
                self.historical_employee = recipient_historical
            else:
                self.historical_employee = sender_historical
                self.historical_contractor = recipient_historical
            
            data = {
                'messages_contractor': f"{self.historical_contractor}",
                'messages_employee': f"{self.historical_employee}"
            }
            
            UrlRequest(
                f"{base_url}/historical_messages.json?auth={self.token_id}",
                method='PATCH',
                req_body=json.dumps(data),
                on_error=self.error2,
                on_success=self.add_message3
            )
        else:
            # Destinatário offline: salva no histórico do remetente e em mensagens offline
            sender_historical.append(message_dict)
            
            # Atualiza histórico do remetente
            historical_key = 'messages_contractor' if is_contractor else 'messages_employee'
            historical_data = {historical_key: f"{sender_historical}"}
            
            # Prepara mensagens offline
            offline_messages = self.messages_contractor_off
            offline_messages.append(message)
            offline_key = 'contractor' if is_contractor else 'employee'
            offline_data = {offline_key: f'{offline_messages}'}
            
            # Envia ambas as requisições
            UrlRequest(
                f"{base_url}/historical_messages.json?auth={self.token_id}",
                method='PATCH',
                req_body=json.dumps(historical_data),
                on_success=self.add_message3,
                on_error=self.error2,
                on_failure=self.error2
            )
            UrlRequest(
                f"{base_url}/message_offline.json?auth={self.token_id}",
                method='PATCH',
                req_body=json.dumps(offline_data),
                on_success=self.add_message3,
                on_error=self.error2,
                on_failure=self.error2
            )
    
    def error2(self, req, result):
        self.show_error('Não foi possivel enviar a mensagem')
        Clock.schedule_once(lambda dt: self.show_error('Verifique sua conexão'), 2)

    def add_message3(self, req, result):
        """Adiciona na ultima mensagem enviada"""
        url = f"https://obra-7ebd9-default-rtdb.firebaseio.com/Chats/{self.chat_id}/metadata.json?auth={self.token_id}"
        data = {
            'last_message': f"{self.ids.message_text.text}",
            'last_sender': f"{self.perso}",
            'last_timestamp': f"{datetime.today().day}/{datetime.today().month}/{datetime.today().year}"
        }
        UrlRequest(
            url,
            method='PATCH',
            req_body=json.dumps(data),
            on_success=self.add_message4,
        )

    def add_message4(self, req, result):
        """Depois de salvar no banco de dados adicionar a mensagem a tela"""
        print('Mensagem salva no banco de dados adicionar a tela')
        msg = str(self.ids.message_text.text).replace("'", '')
        self.ids.message_text.text = ''
        message = MessageRight(msg)
        self.ids.main_scroll.add_widget(message)

    # ================= Verificar se tem novas mensagens ========-=====
    def check_new_messages(self):
        """Versão otimizada que usa hash para comparação mais rápida"""
        print('Checando novas mensagens ')
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Chats/{self.chat_id}/historical_messages.json?auth={self.token_id}'
        
        UrlRequest(
            url,
            method='GET',
            on_success=self.on_check_messages_success_optimized,
            on_error=self.on_check_messages_error
        )

    def on_check_messages_error(self, req, error):
        """Mostra uma mensagem de erro ou abre um popup"""
        pass
    
    def on_check_messages_success_optimized(self, request, result):
        """Versão otimizada usando hash das mensagens"""
        try:
            if not result:
                return
            
            # Determina qual histórico verificar
            if self.perso == 'Contractor':
                remote_messages_str = result.get('messages_contractor', '[]')
                local_messages = self.historical_contractor
            else:
                remote_messages_str = result.get('messages_employee', '[]')
                local_messages = self.historical_employee
            
            # Converte string para lista
            try:
                remote_messages = ast.literal_eval(remote_messages_str)
            except (ValueError, SyntaxError):
                remote_messages = []
            
            # Cria set de hashes das mensagens locais para busca O(1)
            def message_hash(msg):
                """Cria um hash único para cada mensagem"""
                return f"{msg.get('who', '')}||{msg.get('message', '')}"
            
            local_hashes = {message_hash(msg) for msg in local_messages}
            
            # Encontra mensagens novas
            new_messages = []
            for msg in remote_messages:
                msg_hash = message_hash(msg)
                who = msg.get('who', '')
                
                # Se não está no local E não é minha mensagem
                if msg_hash not in local_hashes and who.lower() != self.perso.lower():
                    new_messages.append(msg)
            
            # Processa novas mensagens
            if new_messages:
                print(f'📨 {len(new_messages)} nova(s) mensagem(ns)!')
                
                for msg in new_messages:
                    self.display_message(msg['who'], msg['message'])
                
                # Atualiza histórico local
                if self.perso == 'Contractor':
                    self.historical_contractor = remote_messages
                else:
                    self.historical_employee = remote_messages
                
                print(f'✓ Histórico atualizado')
                print('NOvas mensagens: ', new_messages)
            
        except Exception as e:
            print(f"❌ Erro ao verificar: {e}")
            import traceback
            traceback.print_exc()

    def display_message(self, who, message):
        """Exibe a mensagem na interface"""
        try:
            perso = str(self.perso).lower()
            
            # Determina o tipo de balão baseado em quem enviou
            if perso == who.lower():
                # É minha mensagem
                msg_widget = MessageRight(text=message)
            else:
                # É mensagem do outro usuário
                msg_widget = MessageLeft(text=message)
            
            # Adiciona à tela com animação suave
            msg_widget.opacity = 0
            self.ids.main_scroll.add_widget(msg_widget)
            
            # Anima a entrada
            from kivy.animation import Animation
            anim = Animation(opacity=1, duration=0.3)
            anim.start(msg_widget)
            
            # Scroll para a nova mensagem
            Clock.schedule_once(lambda dt: setattr(self.ids.scroll_view, 'scroll_y', 0), 0.1)
            
            print(f'✓ Mensagem de {who} adicionada à tela')
            
        except Exception as e:
            print(f'❌ Erro ao exibir mensagem: {e}')
            import traceback
            traceback.print_exc()


    # ================= saida do usuario da tela ====================== 
    def on_leave(self, *args):
        """Limpa a tela ao sair"""
        print('🚪 Saindo da tela de chat...')
        
        # Para o heartbeat
        self.stop_heartbeat()
        
        # Marca como offline
        self.mark_user_offline()
        
        # Limpa verificações agendadas
        Clock.unschedule(self.check_new_messages)
        Clock.unschedule(self.check_state)
        
        # Limpa a tela
        self.cont_message = 0
        self.ids.main_scroll.clear_widgets()
        
        print('✓ Limpeza completa ao sair')
    
    def mark_user_offline(self):
        """Marca o usuário como offline de forma síncrona e garantida"""
        if self.is_marking_offline:
            return
        
        self.is_marking_offline = True
        
        try:
            url = f"https://obra-7ebd9-default-rtdb.firebaseio.com/Chats/{self.chat_id}/participants.json?auth={self.token_id}"
            
            # Timestamp atual
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
            
            # Usa timeout curto para não travar
            UrlRequest(
                url,
                method='PATCH',
                req_body=json.dumps(data),
                on_success=lambda req, result: print('✓ Marcado como offline com sucesso'),
                on_error=lambda req, error: print(f'❌ Erro ao marcar offline: {error}'),
                on_failure=lambda req, error: print(f'❌ Falha ao marcar offline: {error}'),
                timeout=3  # Timeout de 3 segundos
            )
            
        except Exception as e:
            print(f'❌ Exceção ao marcar offline: {e}')
        finally:
            self.is_marking_offline = False

    def mark_offline_on_leave(self, *args):
        """Marca como offline ao sair da tela (compatibilidade)"""
        self.mark_user_offline()
    
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
    
    # ==================== GERENCIAMENTO DE DIALOGS ====================
    
    def show_alert_dialog(self):
        """Exibe o dialog de confirmação"""
        self.dialog.open()

    def dismiss_alert_dialog(self, *args):
        """Fecha o dialog de confirmação"""
        self.dialog.dismiss()
    
    # ==================== APAGAR MENSAGENS ====================
    
    def delete_messages(self, *args):
        """Apaga as mensagens do histórico do usuário"""
        url = f"https://obra-7ebd9-default-rtdb.firebaseio.com/Chats/{self.chat_id}/historical_messages.json?auth={self.token_id}"
        
        if self.perso == 'Contractor':
            data = {'messages_contractor': '[]'}
        else:
            data = {'messages_employee': '[]'}
            
        UrlRequest(
            url,
            method='PATCH',
            req_body=json.dumps(data),
            on_success=self.delete_messages2
        )

    def delete_messages2(self, req, result):
        """Apaga as mensagens offline do usuário"""
        url = f"https://obra-7ebd9-default-rtdb.firebaseio.com/Chats/{self.chat_id}/message_offline.json?auth={self.token_id}"
        
        if self.perso == 'Contractor':
            data = {'employee': '[]'}
        else:
            data = {'contractor': '[]'}
            
        UrlRequest(
            url,
            method='PATCH',
            req_body=json.dumps(data),
            on_success=self.final_delete_message
        )
    
    def final_delete_message(self, req, result):
        """Finaliza a exclusão e atualiza a interface"""
        print('O chat foi apagado com sucesso')
        self.dialog.dismiss()
        self.ids.main_scroll.clear_widgets()
        
        if self.perso == 'Contractor':
            self.historical_contractor = []
            self.messages_employee_off = []
        else:
            self.historical_employee = []
            self.messages_contractor_off = []
        
        self.show_message('Mensagens apagadas com sucesso')
    
    # ==================== GERENCIAMENTO DE STATUS ====================
    
    def upload_on(self, user_type):
        """Marca o usuário como online no chat"""
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Chats/{self.chat_id}/participants.json?auth={self.token_id}'
        
        if user_type == 'Contractor':
            data = {'contractor': 'online'}
        else:
            data = {'employee': 'online'}
            
        UrlRequest(
            url,
            req_body=json.dumps(data),
            method='PATCH',
            on_success=self.finally_on_upload,
        )

    def finally_on_upload(self, req, result):
        """Callback após marcar como online"""
        print('✓ Usuário marcado como online')
    
    # ==================== NAVEGAÇÃO E SCROLL ====================
    
    def show_loading_indicator(self):
        """Exibe um indicador visual de carregamento"""
        if not self.loading_indicator_visible:
            self.loading_indicator_visible = True
            # Opcional: adicionar um label de "Carregando..." no topo
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
        print('Finalizando chat...')
        self.mark_user_offline()
        Clock.schedule_once(self.finnally_back, 0.5)
    
    def finnally_back(self, dt=None):
        """Finaliza a navegação de volta"""
        app = MDApp.get_running_app()
        screenmanager = app.root
        screenmanager.token_id = self.token_id
        screenmanager.local_id = self.local_id
        screenmanager.perso = self.perso
        screenmanager.refresh_token = self.refresh_token
        screenmanager.api_key = self.api_key
        self.cont_message = 0
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'ListChat'
    
    # ==================== FEEDBACK VISUAL ====================
    def open_popup(self, retry_callback=None, cancel_callback=None, **popup_config):
        """
        Abre um popup moderno e personalizável
        
        Args:
            retry_callback: Função a ser executada ao clicar em "Tentar novamente"
            cancel_callback: Função a ser executada ao clicar em "Cancelar" (opcional)
            **popup_config: Configurações opcionais do popup:
                - icon: ícone a ser exibido (padrão: "wifi-off")
                - icon_color: cor do ícone (padrão: "#ef4444")
                - title: título do popup (padrão: "Sem conexão")
                - message: mensagem do popup (padrão: mensagem de conexão)
                - retry_text: texto do botão retry (padrão: "Tentar novamente")
                - cancel_text: texto do botão cancelar (padrão: "Cancelar")
        """
        
        # Configurações padrão (podem ser sobrescritas)
        config = {
            'icon': 'wifi-off',
            'icon_color': '#ef4444',
            'title': 'Sem conexão',
            'message': 'Não foi possível carregar as mensagens. Verifique sua conexão com a internet e tente novamente.',
            'retry_text': 'Tentar novamente',
            'cancel_text': 'Cancelar',
        }
        config.update(popup_config)  # Atualiza com configs personalizadas
        
        def handle_retry(instance):
            """Executa callback e fecha o dialog"""
            if retry_callback:
                retry_callback()
            dialog.dismiss()
        
        def handle_cancel(instance):
            """Executa callback opcional e fecha o dialog"""
            if cancel_callback:
                cancel_callback()
            dialog.dismiss()
        
        # Cria o dialog
        dialog = MDDialog(
            # ----------------------------Icon-----------------------------
            MDDialogIcon(
                icon=config['icon'],
                theme_icon_color='Custom',
                theme_font_size='Custom',
                icon_color=config['icon_color'],
                font_size='40dp'
            ),
            
            # -----------------------Headline text-------------------------
            MDDialogHeadlineText(
                text=config['title'],
                halign='center',
                bold=True,
                font_style='Title',
                role='large',
                theme_text_color='Custom',
                text_color='#1f2937'
            ),
            
            # -----------------------Supporting text-----------------------
            MDDialogSupportingText(
                text=config['message'],
                halign='center',
                font_style='Body',
                role='medium',
                theme_text_color='Custom',
                text_color='#4b5563'
            ),

            # ---------------------Button container------------------------
            MDDialogButtonContainer(
                Widget(size_hint_y=None, height='8dp'),
                
                MDButton(
                    MDIconButton(icon="refresh"),
                    MDButtonText(text=config['retry_text']),
                    style="filled",
                    theme_bg_color='Custom',
                    md_bg_color=config['icon_color'],
                    size_hint_x=0.48,
                    on_release=handle_retry
                ),
                
                MDButton(
                    MDButtonText(
                        text=config['cancel_text'],
                        theme_text_color='Custom',
                        text_color='#374151',
                    ),
                    style="text",
                    theme_bg_color='Custom',
                    md_bg_color='#e5e7eb',
                    size_hint_x=0.48,
                    on_release=handle_cancel
                ),
                
                orientation='horizontal',
                spacing='8dp',
                padding=['16dp', '0dp', '16dp', '16dp']
            ),
            
            # -------------------------------------------------------------
            size_hint=(None, None),
            width='420dp',
            radius=[16, 16, 16, 16],
            auto_dismiss=False
        )
        
        dialog.open()
        return dialog

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