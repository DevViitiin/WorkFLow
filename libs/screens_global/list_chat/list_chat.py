from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
import ast
from kivy.clock import Clock
import logging
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivy.utils import get_color_from_hex
from kivymd.uix.label import MDIcon
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivymd.uix.list import MDListItemLeadingAvatar, MDListItemHeadlineText, MDListItemSupportingText, MDListItem
from kivy.network.urlrequest import UrlRequest


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


# ==================== TELA DE LISTA DE CHATS ====================

class ListChat(MDScreen):
    """Tela que exibe a lista de conversas ativas do usuário"""
    
    # Configurações gerais
    current_nav_state = StringProperty('chat')
    firebase_url = 'https://obra-7ebd9-default-rtdb.firebaseio.com'
    chats = {}
    
    # Autenticação
    api_key = StringProperty()
    refresh_token = StringProperty()
    local_id = StringProperty('aOp9V6ZrmJcmENfUOoeiiuOCaOg2')
    token_id = StringProperty('7Dc5jIxoKXWRbDJZaJ7IFahIfMTB5JcKnSjxTMsm')
    perso = StringProperty('Employee')
    
    # Dados do funcionário
    avatar = StringProperty()
    employee_name = StringProperty()
    employee_function = StringProperty()
    employee_mail = StringProperty()
    employee_telephone = StringProperty()
    employee_summary = StringProperty()
    skills = StringProperty()
    
    # Dados adicionais
    request = BooleanProperty()
    city = StringProperty()
    state = StringProperty()
    contractor = StringProperty()
    data_contractor = StringProperty()
    key = StringProperty()
    salary = NumericProperty()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search_event = None  # Evento agendado para busca
        self.is_searching = False  # Flag para controlar busca em andamento
    
    # ==================== CICLO DE VIDA ====================
    
    def on_enter(self):
        """Executa ao entrar na tela"""
        self.upload_chats()
    
    def on_leave(self, *args):
        """Limpa a tela ao sair"""
        self.ids.main_scroll.clear_widgets()
    
    # ==================== CARREGAMENTO DE CHATS ====================
    
    def upload_chats(self, *args):
        """Carrega as conversas do Firebase"""
        url = f'{self.firebase_url}/Chats.json?orderBy="employee"&equalTo="{self.local_id}"&auth={self.token_id}'
        UrlRequest(
            url,
            on_success=self.upload_chats_part_two,
            on_error=self.error,
            on_failure=self.error
        )
    
    def upload_chats_part_two(self, req, result):
        """Busca informações dos contratantes para cada chat"""
        print('O resultado é: ', result)
        self.chats = result
        
        if not result:
            print('❌ Nenhum chat encontrado')
            self.show_no_chat_box()
            return
        
        for key, data in result.items():
            print(f'Chat ID: {key}')
            UrlRequest(
                f"{self.firebase_url}/Users/{data['contractor']}.json?auth={self.token_id}",
                on_success=lambda req, res, d=data, result_chat=result: self.chats_part_three(req, res, d, None, result_chat)
            )

    def chats_part_three(self, req, result, data, chat, chat_result):
        """Cria o item visual do chat na lista"""
        if not result:
            return
            
        print('Contratante:', result['name'])
        
        # Calcula mensagens não vistas
        if self.perso == 'Contractor':
            msg = ast.literal_eval(data['message_offline']['employee'])
            cont_msg_off = len(msg)
        else:
            msg = ast.literal_eval(data['message_offline']['contractor'])
            cont_msg_off = len(msg)
            
        # Define cor e texto do último remetente
        if data['metadata']['last_sender'] == 'Contractor' and self.perso == 'Contractor':
            color = "#006eff"
            who = 'Eu'
        elif data['metadata']['last_sender'] == 'Employee' and self.perso == 'Employee':
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
            MDListItemLeadingAvatar(source=result['perfil']),
            MDListItemHeadlineText(text=result['name']),
            MDListItemSupportingText(
                text=f"[color={color}]{who}[/color]: {data['metadata']['last_message']}",
                markup=True
            ),
            badge,
            theme_bg_color='Custom',
            md_bg_color=get_color_from_hex("#ffffff")
        )
        
        item.on_release = lambda: self.next_screen(
            result['name'], 
            result['perfil'], 
            result, 
            chat, 
            chat_result
        )
        
        self.ids.main_scroll.add_widget(item)
    
    # ==================== BUSCA DE CHATS ====================
    
    def search(self, text, *args):
        """Busca chats pelo nome do usuário com debounce"""
        
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
        
        # Busca nos chats
        for chat_id, chat_data in self.chats.items():
            if self.perso == 'Contractor':
                # Contractor busca por Employee
                employee_id = chat_data['employee']
                self.pending_searches += 1
                url = f'{self.firebase_url}/Funcionarios/{employee_id}.json?auth={self.token_id}'
                UrlRequest(
                    url,
                    on_success=lambda req, result, cid=chat_id, cdata=chat_data: 
                        self.on_search_name_received(req, result, cid, cdata, 'employee')
                )
            else:
                # Employee busca por Contractor
                contractor_id = chat_data['contractor']
                self.pending_searches += 1
                url = f'{self.firebase_url}/Users/{contractor_id}.json?auth={self.token_id}'
                UrlRequest(
                    url,
                    on_success=lambda req, result, cid=chat_id, cdata=chat_data: 
                        self.on_search_name_received(req, result, cid, cdata, 'contractor')
                )
    
    def on_search_name_received(self, req, result, chat_id, chat_data, user_type):
        """Processa resultado da busca por nome"""
        if result:
            # Pega o nome correto
            user_name = result.get('name', '') or result.get('Name', '')
            print(f'📋 Verificando: {user_name}')
            
            # Verifica se contém o texto buscado
            if self.search_text in user_name.lower():
                print(f'✅ Match: {user_name}')
                self.search_results[chat_id] = {
                    'chat_data': chat_data,
                    'user_name': user_name,
                    'perfil': result.get('perfil', result.get('avatar', 
                        'https://res.cloudinary.com/dsmgwupky/image/upload/v1760448287/N%C3%A3o%20definido.jpg')),
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
            url = f"{self.firebase_url}/Users/{data['contractor']}.json?auth={self.token_id}"
            UrlRequest(
                url,
                on_success=lambda req, res, d=data, result_chat=self.chats: 
                    self.chats_part_three(req, res, d, None, result_chat)
            )
    
    def create_chat_item(self, user_info, chat_data, chat_id):
        """Cria item visual do chat (usado na busca)"""
        user_name = user_info.get('name', '') or user_info.get('Name', '')
        perfil = user_info.get('perfil', user_info.get('avatar', 
            'https://res.cloudinary.com/dsmgwupky/image/upload/v1760448287/N%C3%A3o%20definido.jpg'))
        
        # Calcula mensagens não vistas
        if self.perso == 'Contractor':
            msg = ast.literal_eval(chat_data['message_offline']['employee'])
        else:
            msg = ast.literal_eval(chat_data['message_offline']['contractor'])
        cont_msg_off = len(msg)

        # Define cor e texto
        if chat_data['metadata']['last_sender'] == self.perso:
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
            MDListItemLeadingAvatar(source=perfil),
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
            user_name, perfil, user_info, chat_id, chat_result
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
    
    def show_no_chat_box(self):
        """Exibe widget de nenhuma conversa ativa"""
        nochat = NoChatBox()
        self.ids.main_scroll.add_widget(nochat)
    
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
        chat.name_sender = self.employee_name
        chat.email_sender = self.employee_mail
        chat.employee_id = employee_id
        
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
        chat.perso = 'Employee'
        
        # Mensagens
        chat.messages_contractor_off = msg_off_contractor
        chat.messages_employee_off = msg_off_employee
        chat.historical_contractor = historical_contractor
        chat.historical_employee = historical_employee
        
        self.manager.transition = SlideTransition(direction='right')
        self.ids.main_scroll.clear_widgets()
        self.manager.current = 'Chat'
    
    # ==================== NAVEGAÇÃO BOTTOM BAR ====================
    
    def vacancy(self, *args):
        """Navega para tela de vagas"""
        try:
            app = MDApp.get_running_app()
            
            if self.request:
                vac = app.root.get_screen('VacancyBank')
            else:
                vac = app.root.get_screen('WithoutContractor')
            
            self._transfer_data(vac)
            vac.current_nav_state = 'vacancy'
            self._update_nav_icons(vac, vacancy=True)

            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = 'VacancyBank' if self.request else 'WithoutContractor'
                    
        except Exception as e:
            logging.error(f"Erro ao navegar: {e}")
    
    def req(self, *args):
        """Navega para tela de requisições"""
        try:
            app = MDApp.get_running_app()
            vac = app.root.get_screen('RequestsVacancy')
            
            self._transfer_data(vac)
            vac.tab_nav_state = 'request'
            self._update_nav_icons(vac, notification=True)

            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = 'RequestsVacancy'
            
        except Exception as e:
            logging.error(f"Erro ao navegar: {e}")
    
    def perfil(self, *args):
        """Navega para tela de perfil"""
        app = MDApp.get_running_app()
        perfil = app.root.get_screen('PrincipalScreenEmployee')
        
        self._transfer_data(perfil)
        perfil.current_nav_state = 'perfil'
        self._update_nav_icons(perfil, perfil=True)

        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'PrincipalScreenEmployee'
    
    # ==================== MÉTODOS AUXILIARES ====================
    
    def _transfer_data(self, destination_screen):
        """Transfere dados para tela de destino"""
        destination_screen.key = self.key
        destination_screen.employee_name = self.employee_name
        destination_screen.employee_function = self.employee_function
        destination_screen.employee_mail = self.employee_mail
        destination_screen.employee_telephone = self.employee_telephone
        destination_screen.avatar = self.avatar
        destination_screen.employee_summary = self.employee_summary
        destination_screen.skills = self.skills
        destination_screen.state = self.state
        destination_screen.api_key = self.api_key
        destination_screen.token_id = self.token_id
        destination_screen.local_id = self.local_id
        destination_screen.refresh_token = self.refresh_token
        destination_screen.city = self.city
        destination_screen.contractor = self.contractor
        destination_screen.request = self.request
    
    def _update_nav_icons(self, screen, vacancy=False, perfil=False, notification=False, chat=False):
        """Atualiza ícones da navegação"""
        if hasattr(screen.ids, 'vacancy'):
            screen.ids.vacancy.active = vacancy
        if hasattr(screen.ids, 'perfil'):
            screen.ids.perfil.active = perfil
        if hasattr(screen.ids, 'notification'):
            screen.ids.notification.active = notification
        if hasattr(screen.ids, 'chat'):
            screen.ids.chat.active = chat
    
    # ==================== TRATAMENTO DE ERROS ====================
    
    def error(self, req, result):
        """Trata erros de requisição"""
        print(f'❌ Erro: {result}')
        self.show_no_chat_box()