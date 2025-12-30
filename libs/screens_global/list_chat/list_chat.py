from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.clock import Clock
import logging
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivy.utils import get_color_from_hex
from kivymd.uix.label import MDIcon
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivymd.uix.list import MDListItemLeadingAvatar, MDListItemHeadlineText, MDListItemSupportingText, MDListItem
from kivy.network.urlrequest import UrlRequest
from configurations import DialogNoNet, DialogInfinityUpload, DialogErrorUnknow, firebase_url, check_error, SignController


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
    firebase_url = firebase_url()
    chats = {}
    chat_widgets = {}  # ✅ Dicionário para mapear chat_id -> MDListItem
    
    # Autenticação
    api_key = StringProperty()
    refresh_token = StringProperty()
    local_id = StringProperty('6cE4OnZQK8dbpQmyHmeW1jhK5nr2')
    token_id = StringProperty('7Dc5jIxoKXWRbDJZaJ7IFahIfMTB5JcKnSjxTMsm')
    perso = StringProperty('Employee')  # ✅ SEMPRE Employee nesta tela
    text = StringProperty()

    # Dados do funcionário
    avatar = StringProperty()
    employee_name = StringProperty()
    employee_function = StringProperty()
    employee_mail = StringProperty()
    employee_telephone = StringProperty()
    employee_summary = StringProperty()
    skills = StringProperty()
    can = True
    
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
        self.search_event = None
        self.is_searching = False
        self.polling_event = None  # ✅ Evento de polling
    
    # ==================== CICLO DE VIDA ====================
    
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
            callback=lambda: self.signcontroller.retry_handle_list(lambda: self.search(self.text))
        )

        self.dialog_error_unknown = DialogErrorUnknow(screen=f'{self.name}')
        self.upload_chats()
        
        # ✅ Inicia polling a cada 5 segundos
        self.start_polling()

    def on_leave(self, *args):
        """Limpa a tela ao sair"""
        self.stop_polling()
        self.ids.main_scroll.clear_widgets()
        self.chat_widgets.clear()
    
    # ==================== POLLING ====================
    
    def start_polling(self):
        """Inicia atualização automática"""
        if self.polling_event:
            self.polling_event.cancel()
        self.polling_event = Clock.schedule_interval(self.poll_updates, 5)
        print('🔄 Polling iniciado')
    
    def stop_polling(self):
        """Para atualização automática"""
        if self.polling_event:
            self.polling_event.cancel()
            self.polling_event = None
        print('⏸️ Polling parado')
    
    def poll_updates(self, dt):
        """Busca atualizações sem limpar a tela"""
        url = f'{self.firebase_url}/Chats.json?orderBy="employee"&equalTo="{self.local_id}"&auth={self.token_id}'
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
        
        print('🔄 Processando atualizações...')
        
        for chat_id, chat_data in result.items():
            # Se o chat já existe, atualiza
            if chat_id in self.chat_widgets:
                self.update_chat_item(chat_id, chat_data)
            else:
                # Chat novo, cria
                self.fetch_user_and_create_chat(chat_id, chat_data)
    
    def update_chat_item(self, chat_id, new_chat_data):
        """Atualiza item existente SEM recriar"""
        if chat_id not in self.chat_widgets:
            print(f'⚠️ Chat {chat_id} não encontrado para atualização')
            return
        
        # Busca as mensagens atualizadas primeiro
        url = f'{self.firebase_url}/Chats/{chat_id}/messages.json?auth={self.token_id}'
        UrlRequest(
            url,
            on_success=lambda req, messages: self.update_chat_item_with_messages(
                chat_id, new_chat_data, messages
            )
        )
    
    def update_chat_item_with_messages(self, chat_id, new_chat_data, messages):
        """Atualiza o chat COM contagem correta de mensagens"""
        if chat_id not in self.chat_widgets:
            return
        
        item = self.chat_widgets[chat_id]
        old_last_message = item.last_message
        new_last_message = new_chat_data['metadata']['last_message']
        
        # Se mensagem mudou, move para o topo
        if old_last_message != new_last_message:
            print(f'📬 Nova mensagem em {chat_id}')
            self.move_chat_to_top(chat_id)
        
        # Atualiza dados armazenados
        item.chat_data = new_chat_data
        item.last_message = new_last_message
        
        # ✅ Calcula mensagens não lidas - EMPLOYEE verifica read_by_employee
        cont_msg_off = sum(
            1 for msg in messages.values()
            if msg.get('sender') == 'contractor' and not msg.get('read_by_employee', False)
        ) if messages else 0
        
        # Atualiza badge
        badge = item.children[0]
        badge_label = badge.children[0]
        badge_label.text = f"{cont_msg_off}"
        badge.opacity = 1 if cont_msg_off > 0 else 0
    
    def move_chat_to_top(self, chat_id):
        """Move chat para o topo da lista"""
        if chat_id not in self.chat_widgets:
            return
        
        item = self.chat_widgets[chat_id]
        scroll = self.ids.main_scroll
        
        # Remove da posição atual
        scroll.remove_widget(item)
        
        # Adiciona no início
        scroll.add_widget(item, index=len(scroll.children))
        
        print(f'⬆️ Chat {chat_id} movido para o topo')
    
    # ==================== CARREGAMENTO DE CHATS ====================
    
    def upload_chats(self, *args):
        """Carrega as conversas do Firebase"""
        url = f'{self.firebase_url}/Chats.json?orderBy="employee"&equalTo="{self.local_id}"&auth={self.token_id}'
        UrlRequest(
            url,
            on_success=self.upload_chats_part_two,
            on_error=self.signcontroller.handle_signup_error,
            on_failure=self.signcontroller.handle_signup_failure
        )
    
    def upload_chats_part_two(self, req, result):
        """Busca informações dos contratantes para cada chat"""
        print('📥 Resultado inicial:', result)
        self.chats = result
        
        if not result:
            print('❌ Nenhum chat encontrado')
            self.show_no_chat_box()
            return
        
        for chat_id, chat_data in result.items():
            self.fetch_user_and_create_chat(chat_id, chat_data)
    
    def fetch_user_and_create_chat(self, chat_id, chat_data):
        """Busca dados do usuário e mensagens, depois cria o chat"""
        print(f'🔍 Buscando dados para chat: {chat_id}')
        
        # Primeiro busca as mensagens
        url_messages = f'{self.firebase_url}/Chats/{chat_id}/messages.json?auth={self.token_id}'
        UrlRequest(
            url_messages,
            on_success=lambda req, messages: self.fetch_contractor_info(
                chat_id, chat_data, messages
            ),
            on_error=self.signcontroller.handle_signup_error,
            on_failure=self.signcontroller.handle_signup_failure
        )
    
    def fetch_contractor_info(self, chat_id, chat_data, messages):
        """Busca informações do contractor"""
        url = f"{self.firebase_url}/Users/{chat_data['contractor']}.json?auth={self.token_id}"
        UrlRequest(
            url,
            on_success=lambda req, user_info: self.create_chat_item_from_data(
                chat_id, chat_data, user_info, messages
            ),
            on_error=self.signcontroller.handle_signup_error,
            on_failure=self.signcontroller.handle_signup_failure
        )
    
    def create_chat_item_from_data(self, chat_id, chat_data, user_info, messages):
        """Cria item visual do chat COM dados do usuário E mensagens"""
        if not user_info:
            return
        
        print(f'✅ Criando chat: {user_info.get("name", "Desconhecido")}')
        
        # Se já existe, atualiza ao invés de criar
        if chat_id in self.chat_widgets:
            print(f'⚠️ Chat {chat_id} já existe, atualizando...')
            self.update_chat_item_with_messages(chat_id, chat_data, messages)
            return
        
        user_name = user_info.get('name', 'Desconhecido')
        perfil = user_info.get('perfil', 'https://res.cloudinary.com/dsmgwupky/image/upload/v1760448287/N%C3%A3o%20definido.jpg')
        
        cont_msg_off = sum(
            1 for msg in messages.values()
            if msg.get('sender') == 'contractor' and not msg.get('read_by_employee', False)
        ) if messages else 0
        
        print(f'📬 Mensagens não lidas: {cont_msg_off}')
        
        # Define cor e texto do último remetente
        last_sender = chat_data['metadata']['last_sender']
        if last_sender == 'employee':
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
            opacity=1 if cont_msg_off > 0 else 0  # ✅ Esconde se não houver mensagens
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

        supporting = MDListItemSupportingText(
            text="Disponível para conversa",
            max_lines=1,
            shorten=True
        )

        supporting.color = get_color_from_hex('#9CA3AF')

        # Item da lista
        item = MDListItem(
            MDListItemLeadingAvatar(source=perfil),
            MDListItemHeadlineText(text=user_name),
            supporting,
            badge,
            theme_bg_color='Custom',
            theme_line_color='Custom',
            line_color=get_color_from_hex('#E5E7EB'),
            md_bg_color=get_color_from_hex("#EDEFF2")
        )
        
        # ✅ Armazena dados no item
        item.chat_id = chat_id
        item.user_info = user_info
        item.chat_data = chat_data
        item.last_message = chat_data['metadata']['last_message']
        
        # ✅ Callback corrigido
        item.on_release = lambda: self.pre_next_screen(
            name=user_name,
            perfil=perfil,
            user_info=user_info,
            chat_id=chat_id
        )
        
        # ✅ Registra no dicionário
        self.chat_widgets[chat_id] = item
        
        # Adiciona na tela
        self.ids.main_scroll.add_widget(item)

        # ==================== BUSCA DE CHATS ====================
    
    def search(self, text, *args):
        """Busca chats pelo nome do usuário com debounce"""
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
            print('⏳ Busca já em andamento, ignorando...')
            return
        
        print(f'🔍 Buscando por: "{text}"')
        
        # Limpa resultados anteriores APENAS NA BUSCA
        self.ids.main_scroll.clear_widgets()
        self.chat_widgets.clear()
        
        if not text or text.strip() == '':
            print('ℹ️ Texto vazio, recarregando todos os chats')
            self.reload_all_chats()
            return
        
        self.is_searching = True
        self.search_text = text.lower().strip()
        self.search_results = {}
        self.pending_searches = 0
        
        if not self.chats:
            print('❌ Nenhum chat disponível')
            self.is_searching = False
            return
        
        # ✅ Employee busca por Contractor
        for chat_id, chat_data in self.chats.items():
            contractor_id = chat_data['contractor']
            self.pending_searches += 1
            url = f'{self.firebase_url}/Users/{contractor_id}.json?auth={self.token_id}'
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
                user_name = result.get('name', '')
                print(f'📋 Verificando: {user_name}')
                
                if self.search_text in user_name.lower():
                    print(f'✅ Match: {user_name}')
                    self.search_results[chat_id] = {
                        'chat_data': chat_data,
                        'user_name': user_name,
                        'perfil': result.get('perfil', 
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
        print('🔄 Pendentes:', self.pending_searches)

        if self.pending_searches <= 0:
            self.pending_searches = 0
            self.is_searching = False
            self.inf_dialog.dismiss()
            self.display_search_results()
            print('✅ Busca finalizada')
    
    def display_search_results(self):
        """Exibe os resultados da busca"""
        print(f'📊 Resultados encontrados: {len(self.search_results)}')
        
        if not self.search_results:
            self.show_no_search_results()
        else:
            # ✅ Busca mensagens antes de criar cada item
            for chat_id, data in self.search_results.items():
                url = f'{self.firebase_url}/Chats/{chat_id}/messages.json?auth={self.token_id}'
                UrlRequest(
                    url,
                    on_success=lambda req, messages, cid=chat_id, d=data: 
                        self.create_chat_item_from_data(
                            cid, d['chat_data'], d['user_info'], messages
                        )
                )
    
    def reload_all_chats(self):
        """Recarrega todos os chats (quando limpa a busca)"""
        if not self.chats:
            return
        
        # APENAS na recarga completa limpamos
        self.ids.main_scroll.clear_widgets()
        self.chat_widgets.clear()
            
        for chat_id, chat_data in self.chats.items():
            self.fetch_user_and_create_chat(chat_id, chat_data)
    
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
    
    def pre_next_screen(self, name, perfil, user_info, chat_id):
        """Busca dados completos do chat antes de navegar"""
        print('🔍 Preparando navegação para chat...')
        print(f'Nome: {name}')
        print(f'Foto de perfil: {perfil}')
        print(f'Id do chat: {chat_id}')

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
        """Navega para o chat COM dados completos"""
        print('📥 Dados do chat recebidos:', chat_data)
        
        try:
            # Extrai dados do chat
            contractor_id = chat_data['contractor']
            employee_id = chat_data['employee']
            
            # ✅ NOVA ESTRUTURA: Converte mensagens em lista
            messages_list = []
            
            if 'messages' in chat_data and chat_data['messages']:
                for msg_id, msg_data in chat_data['messages'].items():
                    messages_list.append(msg_data)
                
                # Ordena por timestamp
                messages_list.sort(key=lambda m: m.get('timestamp', 0))
            
            print(f'📬 Total de mensagens: {len(messages_list)}')
            
            # Extrai status dos participantes
            on_contractor = chat_data['participants']['contractor']
            on_employee = chat_data['participants']['employee']

            print(f'👤 Contractor: {on_contractor}')
            print(f'👤 Employee: {on_employee}')
            
            # Pega a tela de Chat
            app = MDApp.get_running_app()
            chat_screen = app.root.get_screen('Chat')
            
            # ==================== PASSA DADOS PARA A TELA DE CHAT ====================
            
            # IDs
            chat_screen.chat_id = chat_id
            chat_screen.contractor_id = contractor_id
            chat_screen.employee_id = employee_id
            
            # Dados do remetente (Employee)
            chat_screen.name_sender = self.employee_name
            chat_screen.email_sender = self.employee_mail
            
            # Dados visuais do destinatário
            chat_screen.perfil = perfil
            chat_screen.name_user = name
            
            # Autenticação
            chat_screen.local_id = self.local_id
            chat_screen.refresh_token = self.refresh_token
            chat_screen.api_key = self.api_key
            chat_screen.token_id = self.token_id
            
            # Status online
            chat_screen.on_contractor = (on_contractor == 'online')
            chat_screen.on_employee = (on_employee == 'online')
            
            # Persona
            chat_screen.perso = 'Employee'  # ✅ SEMPRE Employee nesta tela
            
            chat_screen.messages = messages_list

            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = 'Chat'
            
            print('✅ Navegação concluída')
            
        except KeyError as e:
            print(f'❌ Erro: Campo ausente nos dados - {e}')
            self.dialog_error_unknown.open()
        except Exception as e:
            print(f'❌ Erro ao navegar para chat: {e}')
            self.dialog_error_unknown.open()
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
            self.dialog_error_unknown.open()
    
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
            self.dialog_error_unknown.open()
    
    def perfil(self, *args):
        """Navega para tela de perfil"""
        try:
            app = MDApp.get_running_app()
            perfil = app.root.get_screen('PrincipalScreenEmployee')
            
            self._transfer_data(perfil)
            perfil.current_nav_state = 'perfil'
            self._update_nav_icons(perfil, perfil=True)

            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = 'PrincipalScreenEmployee'
        except Exception as e:
            print('Função perfil: ', e)
            self.dialog_error_unknown.open()
    
    # ==================== MÉTODOS AUXILIARES ====================
    
    def _transfer_data(self, destination_screen):
        """Transfere dados para tela de destino"""
        try:
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

        except Exception as e:
            print('Função _transfer_data: ', e)
            self.dialog_error_unknown.open()
    
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