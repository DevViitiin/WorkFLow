from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
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
from configurations import DialogNoNet, DialogInfinityUpload, DialogErrorUnknow, firebase_url, check_error, SignController


# ==================== COMPONENTE DE CHAT VAZIO ====================

class NoChatBox(MDBoxLayout):
    """Widget exibido quando não há conversas ativas"""
    
    local_id = StringProperty()
    type = StringProperty()
    token_id = StringProperty()
    
    def on_kv_post(self, base_widget):
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
    chat_widgets = {}  # ✅ NOVO: Dicionário para controlar os itens na tela
    
    # Autenticação
    api_key = StringProperty()
    refresh_token = StringProperty()
    local_id = StringProperty('3cF7rV71WwPeKqSoyJHl1tSj0MJ2')
    perso = StringProperty('Contractor')  # ✅ SEMPRE 'Contractor' nesta tela
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
    text = StringProperty()
    skills = StringProperty()
    
    def on_kv_post(self, base_widget):
        self.search_event = None
        self.is_searching = False
        self.polling_event = None  # ✅ NOVO: Evento de polling
    
    # ==================== CICLO DE VIDA ===========================
    
    def on_enter(self):
        """Executa ao entrar na tela"""
        self.inf_dialog = DialogInfinityUpload()
        self.signcontroller = SignController(screen=self, name=self.name)
        
        self.dialog_not_net = DialogNoNet(
            subtitle='Não foi possível se conectar. Verifique sua internet e tente novamente',
            callback=lambda: self.signcontroller.retry_signup(self.upload_chats)
        )
        
        self.dialog_error_delete = DialogNoNet(
            subtitle='Não foi possível deletar. Verifique sua internet e tente novamente',
            callback=lambda: self.signcontroller.retry_delete(self.reload_all_chats)
        )
        
        self.dialog_not_net_database = DialogNoNet(
            subtitle='Não foi carregar funções. Verifique sua internet e tente novamente',
            callback=lambda: self.signcontroller.retry_handle_list(lambda: self.search_chat(self.text))
        )

        self.dialog_error_unknown = DialogErrorUnknow(screen=f'{self.name}')
        self.upload_chats()
        
        # ✅ NOVO: Inicia polling
        self.start_polling()
    
    def on_leave(self, *args):
        """Limpa a tela ao sair"""
        # ✅ NOVO: Para polling
        self.stop_polling()
        
        self.ids.main_scroll.clear_widgets()
        self.chat_widgets.clear()
    
    # ==================== POLLING ===========================
    
    def start_polling(self):
        """Inicia atualização automática"""
        if self.polling_event:
            self.polling_event.cancel()
        self.polling_event = Clock.schedule_interval(self.poll_updates, 5)
    
    def stop_polling(self):
        """Para atualização automática"""
        if self.polling_event:
            self.polling_event.cancel()
            self.polling_event = None
    
    def poll_updates(self, dt):
        """Busca atualizações sem limpar a tela"""
        url = f'{self.firebase_url}/Chats.json?orderBy="contractor"&equalTo="{self.local_id}"&auth={self.token_id}'
        UrlRequest(
            url,
            on_success=self.process_poll_updates,
            on_error=lambda req, err: print(f'❌ Erro no polling: {err}'),
            on_failure=lambda req, err: print(f'❌ Falha no polling: {err}')
        )
    
    def process_poll_updates(self, req, result):
        """Processa atualizações recebidas do polling"""
        if not result:
            return
        
        for chat_id, chat_data in result.items():
            # Busca mensagens e atualiza/cria chat
            self.fetch_messages_and_update_or_create(chat_id, chat_data)
    
    def fetch_messages_and_update_or_create(self, chat_id, chat_data):
        """Busca mensagens e decide se atualiza ou cria chat"""
        url = f'{self.firebase_url}/Chats/{chat_id}/messages.json?auth={self.token_id}'
        UrlRequest(
            url,
            on_success=lambda req, messages: self.handle_chat_with_messages(
                chat_id, chat_data, messages
            )
        )
    
    def handle_chat_with_messages(self, chat_id, chat_data, messages):
        """Atualiza ou cria chat com contagem de mensagens"""
        # Se já existe na tela, apenas atualiza
        if chat_id in self.chat_widgets:
            self.update_existing_chat(chat_id, chat_data, messages)
        else:
            # Chat novo, busca info do employee e cria
            url = f"{self.firebase_url}/Funcionarios/{chat_data['employee']}.json?auth={self.token_id}"
            UrlRequest(
                url,
                on_success=lambda req, user_info: self.create_chat_item_with_messages(
                    user_info, chat_data, chat_id, messages
                )
            )
    
    def update_existing_chat(self, chat_id, chat_data, messages):
        """Atualiza badge e última mensagem de um chat existente"""
        if chat_id not in self.chat_widgets:
            return
        
        item = self.chat_widgets[chat_id]
        
        # ✅ Conta não lidas - CONTRACTOR verifica read_by_contractor
        unread_count = sum(
            1 for msg in messages.values()
            if msg['sender'] == 'employee' and not msg.get('read_by_contractor', False)
        ) if messages else 0
        
        # Atualiza badge
        badge = item.children[0]
        badge_label = badge.children[0]
        badge_label.text = f"{unread_count}"
        badge.opacity = 1 if unread_count > 0 else 0
        
        # Atualiza texto da última mensagem
        last_sender = chat_data['metadata']['last_sender']
        if last_sender == 'contractor':
            color = "#006eff"
            who = 'Eu'
        else:
            color = "#ff0000"
            who = 'Ele'
        
        supporting_text = item.children[1]
        supporting_text.text = f"[color={color}]{who}[/color]: {chat_data['metadata']['last_message']}"

        # ==================== CARREGAMENTO DE CHATS ====================
    
    def upload_chats(self, *args):
        """Carrega as conversas do Firebase"""
        url = f'{self.firebase_url}/Chats.json?orderBy="contractor"&equalTo="{self.local_id}"&auth={self.token_id}'
        UrlRequest(
            url,
            on_success=self.upload_chats_part_two,
            on_error=self.signcontroller.handle_signup_error,
            on_failure=self.signcontroller.handle_signup_failure
        )
    
    def upload_chats_part_two(self, req, result):
        """Busca informações dos funcionários para cada chat"""
        self.chats = result
        
        if not result:
            self.show_no_requests_found()
            return
        
        for chat_id, chat_data in result.items():
            # ✅ NOVO: Busca mensagens primeiro
            self.fetch_messages_and_create_chat(chat_id, chat_data)
    
    def fetch_messages_and_create_chat(self, chat_id, chat_data):
        """Busca mensagens e cria o chat"""
        url = f'{self.firebase_url}/Chats/{chat_id}/messages.json?auth={self.token_id}'
        UrlRequest(
            url,
            on_success=lambda req, messages: self.fetch_employee_and_create(
                chat_id, chat_data, messages
            ),
            on_error=self.signcontroller.handle_signup_error,
            on_failure=self.signcontroller.handle_signup_failure
        )
    
    def fetch_employee_and_create(self, chat_id, chat_data, messages):
        """Busca dados do employee e cria o item visual"""
        url = f"{self.firebase_url}/Funcionarios/{chat_data['employee']}.json?auth={self.token_id}"
        UrlRequest(
            url,
            on_success=lambda req, user_info: self.create_chat_item_with_messages(
                user_info, chat_data, chat_id, messages
            ),
            on_error=self.signcontroller.handle_signup_error,
            on_failure=self.signcontroller.handle_signup_failure
        )
    
    def create_chat_item_with_messages(self, user_info, chat_data, chat_id, messages):
        """Cria o item visual COM a contagem correta de mensagens não lidas"""
        if not user_info:
            return
        
        # Se já existe, não cria duplicado
        if chat_id in self.chat_widgets:
            return
        
        user_name = user_info.get('Name', 'Desconhecido')
        avatar = user_info.get('avatar', 'https://res.cloudinary.com/dsmgwupky/image/upload/v1760448287/N%C3%A3o%20definido.jpg')
        
        if not messages:
            cont_msg_off = 0
        else:
            cont_msg_off = sum(
                1 for msg in messages.values()
                if msg.get('sender') == 'employee' and not msg.get('read_by_contractor', False)
            )
        
        # Define cor do último remetente
        last_sender = chat_data['metadata']['last_sender']
        if last_sender == 'contractor':
            color = "#006eff"
            who = 'Eu'
        else:
            color = "#ff0000"
            who = 'Ele'
        
        # Badge de mensagens não lidas
        badge = MDCard(
            size_hint=(None, None),
            size=("24dp", "24dp"),
            radius=["12dp"],
            theme_bg_color='Custom',
            md_bg_color=get_color_from_hex("#007BFF"),
            pos_hint={'center_y': 0.5, 'right': 0.95},
            padding=0,
            opacity=1 if cont_msg_off > 0 else 0  # ✅ Esconde badge se não houver mensagens
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
        supporting = MDListItemSupportingText(
            text="Disponível para conversa",
            max_lines=1,
            shorten=True
        )

        supporting.color = get_color_from_hex('#9CA3AF')
        # Item da lista
        item = MDListItem(
            MDListItemLeadingAvatar(source=avatar),
            MDListItemHeadlineText(text=user_name),
            supporting,
            badge,
            theme_bg_color='Custom',
            theme_line_color='Custom',
            line_color=get_color_from_hex('#E5E7EB'),
            md_bg_color=get_color_from_hex("#EDEFF2")
        )
        
        # ✅ NOVO: Armazena dados no item
        item.chat_id = chat_id
        item.user_info = user_info
        item.chat_data = chat_data
        item.last_message = chat_data['metadata']['last_message']
        
        # ✅ Callback corrigido
        item.on_release = lambda: self.pre_next_screen(
            name=user_name,
            perfil=avatar,
            user_info=user_info,
            chat_id=chat_id
        )
        
        # ✅ NOVO: Registra no dicionário
        self.chat_widgets[chat_id] = item
        
        # Adiciona na tela
        self.ids.main_scroll.add_widget(item)
    
    # ==================== BUSCA DE CHATS ====================
    
    def search_chat(self, text, *args):
        """Busca chats pelo nome do funcionário com debounce"""
        self.text = text
        
        if self.search_event:
            self.search_event.cancel()
        
        self.search_event = Clock.schedule_once(
            lambda dt: self._execute_search(text), 
            0.5
        )
    
    def _execute_search(self, text):
        """Executa a busca de fato"""
        if self.is_searching:
            return
        
        # Limpa resultados anteriores
        self.ids.main_scroll.clear_widgets()
        self.chat_widgets.clear()
        
        if not text or text.strip() == '':
            self.reload_all_chats()
            return
        
        self.is_searching = True
        self.search_text = text.lower().strip()
        self.search_results = {}
        self.pending_searches = 0
        
        if not self.chats:
            self.is_searching = False
            return
        
        # ✅ Contractor sempre busca por Employee
        for chat_id, chat_data in self.chats.items():
            employee_id = chat_data['employee']
            self.pending_searches += 1
            url = f'{self.firebase_url}/Funcionarios/{employee_id}.json?auth={self.token_id}'
            UrlRequest(
                url,
                on_success=lambda req, result, cid=chat_id, cdata=chat_data: 
                    self.on_search_name_received(req, result, cid, cdata),
                on_error=self.signcontroller.on_error,
                on_failure=self.signcontroller.on_failure
            )
    
    def on_search_name_received(self, req, result, chat_id, chat_data):
        """Processa resultado da busca por nome"""
        try:
            if result:
                user_name = result.get('Name', '')
                
                if self.search_text in user_name.lower():
                    # ✅ NOVO: Adiciona aos resultados
                    self.search_results[chat_id] = {
                        'chat_data': chat_data,
                        'user_name': user_name,
                        'avatar': result.get('avatar', 
                            'https://res.cloudinary.com/dsmgwupky/image/upload/v1760448287/N%C3%A3o%20definido.jpg'),
                        'user_info': result
                    }
        except:
            self.dialog_error_unknown.open()
        
        finally:
            self._finish_search_request()

    def _finish_search_request(self):
        """Finaliza uma requisição de busca"""
        self.pending_searches -= 1

        if self.pending_searches <= 0:
            self.pending_searches = 0
            self.is_searching = False
            self.inf_dialog.dismiss()
            self.display_search_results()
        
    def display_search_results(self):
        """Exibe os resultados da busca"""
        
        if not self.search_results:
            self.show_no_search_results()
        else:
            # ✅ NOVO: Busca mensagens antes de criar cada item
            for chat_id, data in self.search_results.items():
                url = f'{self.firebase_url}/Chats/{chat_id}/messages.json?auth={self.token_id}'
                UrlRequest(
                    url,
                    on_success=lambda req, messages, cid=chat_id, d=data: 
                        self.create_chat_item_with_messages(
                            d['user_info'], d['chat_data'], cid, messages
                        )
                )
    
    def reload_all_chats(self):
        """Recarrega todos os chats (quando limpa a busca)"""
        if not self.chats:
            return
        
        # Limpa tela
        self.ids.main_scroll.clear_widgets()
        self.chat_widgets.clear()
        
        for chat_id, chat_data in self.chats.items():
            self.fetch_messages_and_create_chat(chat_id, chat_data)
    
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

    def pre_next_screen(self, name, perfil, user_info, chat_id):
        """Busca dados completos do chat antes de navegar"""

        url = f'{self.firebase_url}/Chats/{chat_id}.json?auth={self.token_id}'

        UrlRequest(
            url,
            on_success=lambda req, result: self.next_screen(
                name=name,
                perfil=perfil,
                chat_id=chat_id,
                chat_data=result
            ),
            on_error=lambda req, err: print(f'❌ Erro ao buscar chat: {err}'),
            on_failure=lambda req, err: print(f'❌ Falha ao buscar chat: {err}')
        )

    def next_screen(self, name, perfil, chat_id, chat_data):
        """Navega para a tela de chat individual COM nova estrutura"""     
        try:
            # Extrai IDs
            contractor_id = chat_data['contractor']
            employee_id = chat_data['employee']
            
            # ✅ NOVA ESTRUTURA: Converte mensagens em lista
            messages_list = []
            
            if 'messages' in chat_data and chat_data['messages']:
                for msg_id, msg_data in chat_data['messages'].items():
                    messages_list.append(msg_data)
                
                # Ordena por timestamp
                messages_list.sort(key=lambda m: m.get('timestamp', 0))
            
            
            # Extrai status dos participantes
            on_contractor = chat_data['participants']['contractor']
            on_employee = chat_data['participants']['employee']

            
            # Pega a tela de Chat
            app = MDApp.get_running_app()
            chat = app.root.get_screen('Chat')
            
            # ==================== PASSA DADOS PARA CHAT.PY ====================
            
            # IDs do chat
            chat.chat_id = chat_id
            chat.contractor_id = contractor_id
            chat.employee_id = employee_id
            
            # Dados do remetente (Contractor)
            chat.name_sender = self.employee_name
            chat.email_sender = self.employee_mail
            
            # Dados visuais do destinatário (Employee)
            chat.perfil = perfil
            chat.name_user = name
            
            # Tokens de autenticação
            chat.local_id = self.local_id
            chat.refresh_token = self.refresh_token
            chat.api_key = self.api_key
            chat.token_id = self.token_id
            
            # Status online
            chat.on_contractor = (on_contractor == 'online')
            chat.on_employee = (on_employee == 'online')
            
            # Persona
            chat.perso = 'Contractor'  # ✅ SEMPRE Contractor nesta tela
            
            # ✅ NOVA ESTRUTURA: Passa lista unificada de mensagens
            chat.messages = messages_list
            
            # ✅ REMOVIDO: Não passa mais estas propriedades antigas
            # - chat.messages_contractor_off
            # - chat.messages_employee_off
            # - chat.historical_contractor
            # - chat.historical_employee
            
            # Navega
            self.manager.transition = SlideTransition(direction='right')
            self.ids.main_scroll.clear_widgets()
            self.manager.current = 'Chat'
            
        except KeyError as e:
            self.dialog_error_unknown.open()
        except Exception as e:
            self.dialog_error_unknown.open()
    
    # ==================== NAVEGAÇÃO BOTTOM BAR ====================

    def passo(self, *args):
        """Navega para tela de perfil"""
        try:
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
        except Exception as e:
            self.dialog_error_unknown.open()
    
    def search(self):
        """Navega para tela de busca de vagas"""
        try:
            app = MDApp.get_running_app()            
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
        except Exception as e:
            self.dialog_error_unknown.open()

    def request(self):
        """Navega para tela de requisições"""
        try:
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
        except Exception as e:
            self.dialog_error_unknown.open()
    
    # ==================== TRATAMENTO DE ERROS ====================
    
    def error(self, req, result):
        """Trata erros de requisição"""
        self.show_no_requests_found()
        