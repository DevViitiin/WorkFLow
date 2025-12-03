from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
import ast
import logging
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivy.utils import get_color_from_hex
from kivymd.uix.label import MDIcon
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivymd.uix.list import MDListItemLeadingAvatar, MDListItemHeadlineText, MDListItemSupportingText, MDListItem
from kivy.network.urlrequest import UrlRequest
from kivy.uix.image import AsyncImage
from kivy.clock import Clock


# ==================== COMPONENTE DE CHAT VAZIO ====================

class NoChatBox(MDBoxLayout):
    """Widget exibido quando não há conversas ativas"""
    
    local_id = StringProperty()
    type = StringProperty()
    token_id = StringProperty()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_bg_color = "Custom"
        self.md_bg_color = get_color_from_hex("#ffffffff")
        self.size_hint_y = None
        self.height = "200dp"
        self.orientation = "vertical"

        relative = MDRelativeLayout()

        icon = MDIcon(
            icon="chat-remove-outline",
            theme_font_size="Custom",
            font_size="50dp",
            theme_icon_color="Custom",
            icon_color="grey",
            pos_hint={"center_x": 0.5, "center_y": 0.75},
        )

        label_title = MDLabel(
            text="Nenhuma conversa ativa",
            theme_text_color="Custom",
            text_color="black",
            bold=True,
            halign="center",
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )

        label_sub = MDLabel(
            text="Você ainda não aceitou nenhuma solicitação de conversa.",
            theme_text_color="Custom",
            font_style="Body",
            role="small",
            text_color="grey",
            halign="center",
            pos_hint={"center_x": 0.5, "center_y": 0.38},
        )

        card = MDCard(
            style="elevated",
            size_hint=(0.65, 0.2),
            pos_hint={"center_x": 0.5, "center_y": 0.15},
            theme_bg_color="Custom",
            md_bg_color=get_color_from_hex("#26547C"),
        )

        card_layout = MDRelativeLayout()
        card_label = MDLabel(
            text="Ver Requisições Pendentes",
            halign="center",
            font_style="Body",
            bold=True,
            role="medium",
            theme_text_color="Custom",
            text_color="white",
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        card_layout.add_widget(card_label)
        card.add_widget(card_layout)

        relative.add_widget(icon)
        relative.add_widget(label_title)
        relative.add_widget(label_sub)
        relative.add_widget(card)

        self.add_widget(relative)


# ==================== TELA DE LISTA DE CHATS (CONTRACTOR) ====================

class ListChatContractor(MDScreen):
    """Tela que exibe lista de conversas do Contractor"""
    
    # Configurações gerais
    current_nav_state = StringProperty('chat')
    firebase_url = 'https://obra-7ebd9-default-rtdb.firebaseio.com'
    chats = {}
    
    # Autenticação
    api_key = StringProperty()
    refresh_token = StringProperty()
    local_id = StringProperty('3cF7rV71WwPeKqSoyJHl1tSj0MJ2')
    perso = StringProperty('Contractor')
    token_id = StringProperty('7Dc5jIxoKXWRbDJZaJ7IFahIfMTB5JcKnSjxTMsm')

    # Contractor info
    username = StringProperty()
    key_contractor = StringProperty()

    # Employees info
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
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search_event = None  # Evento agendado para busca
        self.is_searching = False  # Flag para controlar busca em andamento
    
    # ==================== CICLO DE VIDA ===========================
    
    def on_enter(self):
        """Executa ao entrar na tela"""
        print('Local ID:', self.local_id)
        self.upload_chats()
    
    def on_leave(self, *args):
        """Limpa a tela ao sair"""
        self.ids.main_scroll.clear_widgets()
    
    # ==================== CARREGAMENTO DE CHATS ====================
    def upload_chats(self, *args):
        """Carrega as conversas do Firebase"""
        url = f'{self.firebase_url}/Chats.json?orderBy="contractor"&equalTo="{self.local_id}"&auth={self.token_id}'
        UrlRequest(
            url,
            on_success=self.upload_chats_part_two,
            on_error=self.error,
            on_failure=self.error
        )
    
    def upload_chats_part_two(self, req, result):
        """Busca informações dos funcionários para cada chat"""
        print('Resultado:', result)
        self.chats = result
        
        if not result:
            print('❌ Nenhum chat encontrado')
            self.show_no_requests_found()
            return
        
        for key, data in result.items():
            print(f'Chat ID: {key}')
            UrlRequest(
                f"{self.firebase_url}/Funcionarios/{data['employee']}.json?auth={self.token_id}",
                on_success=lambda req, res, d=data, result_chat=result: 
                    self.chats_part_three(req, res, d, None, result_chat)
            )

    def chats_part_three(self, req, result, data, chat, chat_result):
        """Cria o item visual do chat na lista"""
        if not result:
            return
            
        print('Funcionário:', result['Name'])
        
        # Calcula mensagens não vistas
        msg = ast.literal_eval(data['message_offline']['employee'])
        cont_msg_off = len(msg)

        # Define cor e texto do último remetente
        if data['metadata']['last_sender'] == 'Contractor':
            color = "#006eff"
            who = 'Eu'
        else:
            color = "#ff0000"
            who = 'Ele'

        print(f'Mensagens não vistas: {cont_msg_off}')
        
        # Badge de mensagens não lidas
        badge = MDCard(
            size_hint=(None, None),
            size=("24dp", "24dp"),
            radius=["12dp"],
            theme_bg_color='Custom',
            md_bg_color=get_color_from_hex("#007BFF"),
            pos_hint={'center_y': 0.5, 'right': 0.95},
            padding=0
        )

        badge_label = MDLabel(
            text=f"{cont_msg_off}",
            bold=True,
            font_style="Label",
            theme_text_color="Custom",
            text_color=get_color_from_hex("#FFFFFF"),
            halign="center",
            valign="middle"
        )
        badge.add_widget(badge_label)

        # Item da lista
        item = MDListItem(
            MDListItemLeadingAvatar(source=result['avatar']),
            MDListItemHeadlineText(text=result['Name']),
            MDListItemSupportingText(
                text=f"[color={color}]{who}[/color]: {data['metadata']['last_message']}",
                markup=True
            ),
            badge,
            theme_bg_color='Custom',
            md_bg_color=get_color_from_hex("#ffffff")
        )
        
        item.on_release = lambda: self.next_screen(
            result['Name'], 
            result['avatar'], 
            result, 
            chat, 
            chat_result
        )
        
        self.ids.main_scroll.add_widget(item)
    
    # ==================== BUSCA DE CHATS ====================
    
    def search_chat(self, text, *args):
        """Busca chats pelo nome do funcionário com debounce"""
        
        # Cancela busca anterior se existir
        if self.search_event:
            self.search_event.cancel()
        
        # Agenda nova busca após 0.5 segundos
        self.search_event = Clock.schedule_once(
            lambda dt: self._execute_search(text), 
            0.5
        )
    
    def _execute_search(self, text):
        """Executa a busca de fato"""
        
        # Se já está buscando, ignora
        if self.is_searching:
            print('⏳ Busca já em andamento, ignorando...')
            return
        
        print(f'🔍 Buscando por: "{text}"')
        
        # Limpa resultados anteriores
        self.ids.main_scroll.clear_widgets()
        
        if not text or text.strip() == '':
            print('ℹ️ Texto vazio, recarregando todos os chats')
            self.reload_all_chats()
            return
        
        # Marca que está buscando
        self.is_searching = True
        
        # Inicia busca
        self.search_text = text.lower().strip()
        self.search_results = {}
        self.pending_searches = 0
        
        if not self.chats:
            print('❌ Nenhum chat disponível')
            self.is_searching = False
            return
        
        # Contractor sempre busca por Employee
        for chat_id, chat_data in self.chats.items():
            employee_id = chat_data['employee']
            self.pending_searches += 1
            url = f'{self.firebase_url}/Funcionarios/{employee_id}.json?auth={self.token_id}'
            UrlRequest(
                url,
                on_success=lambda req, result, cid=chat_id, cdata=chat_data: 
                    self.on_search_name_received(req, result, cid, cdata)
            )
    
    def on_search_name_received(self, req, result, chat_id, chat_data):
        """Processa resultado da busca por nome"""
        if result:
            user_name = result.get('Name', '')
            print(f'📋 Verificando: {user_name}')
            
            # Verifica se contém o texto buscado
            if self.search_text in user_name.lower():
                print(f'✅ Match: {user_name}')
                self.search_results[chat_id] = {
                    'chat_data': chat_data,
                    'user_name': user_name,
                    'avatar': result.get('avatar', 
                        'https://res.cloudinary.com/dsmgwupky/image/upload/v1760448287/N%C3%A3o%20definido.jpg'),
                    'user_info': result
                }
        
        self.pending_searches -= 1
        
        # Quando terminar todas as buscas
        if self.pending_searches == 0:
            self.display_search_results()
            self.is_searching = False  # Libera para novas buscas
    
    def display_search_results(self):
        """Exibe os resultados da busca"""
        print(f'📊 Resultados encontrados: {len(self.search_results)}')
        
        # Limpa tela novamente (por segurança)
        self.ids.main_scroll.clear_widgets()
        
        if not self.search_results:
            self.show_no_search_results()
        else:
            # Adiciona os chats encontrados IMEDIATAMENTE
            for chat_id, data in self.search_results.items():
                self.create_chat_item(
                    user_info=data['user_info'],
                    chat_data=data['chat_data'],
                    chat_id=chat_id
                )
    
    def reload_all_chats(self):
        """Recarrega todos os chats (quando limpa a busca)"""
        if not self.chats:
            return
            
        for key, data in self.chats.items():
            url = f"{self.firebase_url}/Funcionarios/{data['employee']}.json?auth={self.token_id}"
            UrlRequest(
                url,
                on_success=lambda req, res, d=data, result_chat=self.chats: 
                    self.chats_part_three(req, res, d, None, result_chat)
            )
    
    def create_chat_item(self, user_info, chat_data, chat_id):
        """Cria item visual do chat (usado na busca)"""
        user_name = user_info.get('Name', '')
        avatar = user_info.get('avatar', 
            'https://res.cloudinary.com/dsmgwupky/image/upload/v1760448287/N%C3%A3o%20definido.jpg')
        
        # Calcula mensagens não vistas
        msg = ast.literal_eval(chat_data['message_offline']['employee'])
        cont_msg_off = len(msg)

        # Define cor e texto
        if chat_data['metadata']['last_sender'] == 'Contractor':
            color = "#006eff"
            who = 'Eu'
        else:
            color = "#ff0000"
            who = 'Ele'
        
        # Badge
        badge = MDCard(
            size_hint=(None, None),
            size=("24dp", "24dp"),
            radius=["12dp"],
            theme_bg_color='Custom',
            md_bg_color=get_color_from_hex("#007BFF"),
            pos_hint={'center_y': 0.5, 'right': 0.95},
            padding=0
        )

        badge_label = MDLabel(
            text=f"{cont_msg_off}",
            bold=True,
            font_style="Label",
            theme_text_color="Custom",
            text_color=get_color_from_hex("#FFFFFF"),
            halign="center",
            valign="middle"
        )
        badge.add_widget(badge_label)

        # Item
        item = MDListItem(
            MDListItemLeadingAvatar(source=avatar),
            MDListItemHeadlineText(text=user_name),
            MDListItemSupportingText(
                text=f"[color={color}]{who}[/color]: {chat_data['metadata']['last_message']}",
                markup=True
            ),
            badge,
            theme_bg_color='Custom',
            md_bg_color=get_color_from_hex("#ffffff")
        )
        
        chat_result = {chat_id: chat_data}
        item.on_release = lambda: self.next_screen(
            user_name, avatar, user_info, chat_id, chat_result
        )
        
        self.ids.main_scroll.add_widget(item)
    
    def show_no_search_results(self):
        """Exibe mensagem de nenhum resultado na busca"""
        container = MDBoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height="300dp",
            pos_hint={'center_x': 0.5},
            spacing="20dp",
            padding="20dp"
        )

        icon = MDIcon(
            icon="account-search-outline",
            theme_font_size="Custom",
            font_size="80dp",
            theme_icon_color="Custom",
            icon_color="grey",
            halign='center'
        )

        label = MDLabel(
            text="Nenhum chat encontrado",
            halign='center',
            font_style='Title',
            role='large',
            theme_text_color='Custom',
            text_color='grey',
            adaptive_height=True
        )
        
        sublabel = MDLabel(
            text="Tente buscar por outro nome",
            halign='center',
            font_style='Body',
            role='medium',
            theme_text_color='Custom',
            text_color='grey',
            adaptive_height=True
        )
        
        container.add_widget(icon)
        container.add_widget(label)
        container.add_widget(sublabel)
        self.ids.main_scroll.add_widget(container)
    
    def show_no_requests_found(self):
        """Exibe widget de nenhuma conversa ativa"""
        self.ids.main_scroll.clear_widgets()

        container = MDBoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height="300dp",
            pos_hint={'center_x': 0.5}
        )

        image = AsyncImage(
            source='https://res.cloudinary.com/dsmgwupky/image/upload/v1762258289/Nenhum_chat_encontrado_-_Mensagem_vazia_1_y0csqu.png',
            size_hint=(0.65, 0.65),
            pos_hint={'center_x': 0.5, 'center_y': 0.2}
        )
        container.add_widget(image)
        self.ids.main_scroll.add_widget(container)
    
    # ==================== NAVEGAÇÃO PARA CHAT ====================

    def next_screen(self, name, perfil, req, chat_id, chat_data):
        """Navega para a tela de chat individual"""
        historical_contractor = []
        historical_employee = []
        msg_off_contractor = []
        msg_off_employee = []
        on_contractor = ''
        on_employee = ''
        contractor_id = ''
        employee_id = ''
        chat_id = ''
        
        for key, info in chat_data.items():
            contractor_id = info['contractor']
            employee_id = info['employee']
            chat_id = key
            historical_contractor = ast.literal_eval(info['historical_messages']['messages_contractor'])
            historical_employee = ast.literal_eval(info['historical_messages']['messages_employee'])
            msg_off_contractor = ast.literal_eval(info['message_offline']['contractor'])
            msg_off_employee = ast.literal_eval(info['message_offline']['employee'])
            on_contractor = info['participants']['contractor']
            on_employee = info['participants']['employee']

        print('Contractor online:', on_contractor)
        
        app = MDApp.get_running_app()
        chat = app.root.get_screen('Chat')
        
        # IDs do chat
        chat.chat_id = chat_id
        chat.contractor_id = contractor_id
        chat.employee_id = employee_id
        chat.name_sender = self.employee_name
        chat.email_sender = self.employee_mail
        
        # Dados visuais
        chat.perfil = perfil
        chat.name_user = name
        
        # Tokens
        chat.local_id = self.local_id
        chat.refresh_token = self.refresh_token
        chat.api_key = self.api_key
        chat.token_id = self.token_id
        
        # Status
        chat.on_contractor = on_contractor == 'online'
        chat.on_employee = on_employee == 'online'
        chat.perso = 'Contractor'
        
        # Mensagens
        chat.messages_contractor_off = msg_off_contractor
        chat.messages_employee_off = msg_off_employee
        chat.historical_contractor = historical_contractor
        chat.historical_employee = historical_employee
        
        self.manager.transition = SlideTransition(direction='right')
        self.ids.main_scroll.clear_widgets()
        self.manager.current = 'Chat'
    
    # ==================== NAVEGAÇÃO BOTTOM BAR ====================

    def passo(self, *args):
        """Navega para tela de perfil"""
        app = MDApp.get_running_app()
        bricklayer = app.root.get_screen('Perfil')
        
        bricklayer.ids.perfil.active = True
        bricklayer.token_id = self.token_id
        bricklayer.refresh_token = self.refresh_token
        bricklayer.api_key = self.api_key
        bricklayer.local_id = self.local_id
        bricklayer.ids.search.active = False
        bricklayer.ids.request.active = False
        bricklayer.ids.perfil.active = True
        bricklayer.ids.chat.active = False
        bricklayer.current_nav_state = 'perfil'
        bricklayer.username = self.username
        bricklayer.key = self.key_contractor
        
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'Perfil'
    
    def search(self):
        """Navega para tela de busca de vagas"""
        app = MDApp.get_running_app()
        print('Key passada:', self.key)
        
        bricklayer = app.root.get_screen('VacancyContractor')
        bricklayer.key_contractor = self.key_contractor
        bricklayer.username = self.username
        bricklayer.api_key = self.api_key
        bricklayer.token_id = self.token_id
        bricklayer.refresh_token = self.refresh_token
        bricklayer.local_id = self.local_id
        bricklayer.ids.perfil.active = False
        bricklayer.ids.search.active = True
        bricklayer.ids.chat.active = False
        bricklayer.ids.request.active = False
        bricklayer.current_nav_state = 'search'
        
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'VacancyContractor'

    def request(self):
        """Navega para tela de requisições"""
        app = MDApp.get_running_app()
        bricklayer = app.root.get_screen('RequestContractor')
        
        bricklayer.key = self.key
        bricklayer.ids.perfil.active = False
        bricklayer.ids.search.active = False
        bricklayer.ids.request.active = True
        bricklayer.ids.chat.active = False
        bricklayer.current_nav_state = 'request'
        bricklayer.token_id = self.token_id
        bricklayer.api_key = self.api_key
        bricklayer.local_id = self.local_id
        bricklayer.refresh_token = self.refresh_token
        bricklayer.name_contractor = self.username
        
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'RequestContractor'
    
    # ==================== TRATAMENTO DE ERROS ====================
    
    def error(self, req, result):
        """Trata erros de requisição"""
        print(f'❌ Erro: {result}')
        self.show_no_requests_found()
        