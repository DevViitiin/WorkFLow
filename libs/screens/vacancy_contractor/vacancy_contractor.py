import ast
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.properties import (get_color_from_hex, StringProperty, ListProperty, 
                            NumericProperty, BooleanProperty)
from kivy.clock import Clock
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButtonText, MDButton
from kivymd.uix.fitimage import FitImage
from kivymd.uix.label import MDIcon, MDLabel
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from configurations import (DialogNoNet, DialogInfinityUpload, DialogErrorUnknow, 
                           firebase_url, SignController)


class VacancyContractor(MDScreen):
    # ==================== PROPERTIES ====================
    FIREBASE_URL = firebase_url()
    
    # Auth & User
    token_id = StringProperty()
    local_id = StringProperty()
    api_key = StringProperty()
    refresh_token = StringProperty()
    key = StringProperty()
    key_contractor = StringProperty()
    username = StringProperty()
    
    # Navigation & State
    current_nav_state = StringProperty('search')
    can_add = BooleanProperty(False)
    on_search = BooleanProperty(False)
    type = StringProperty('loc')
    
    # Employee Management
    employee_key = StringProperty()
    request_key = StringProperty()
    all_employees = ListProperty([])
    loaded_employee_keys = ListProperty([])
    
    # Pagination
    current_page = NumericProperty(0)
    items_per_page = NumericProperty(3)
    
    # Internal
    cont = NumericProperty(0)
    add = BooleanProperty(True)

    def on_kv_post(self, base_widget):
        Clock.schedule_once(self.load, 0)

    def load(self, dt):
        self.text_search = None
        self.search_trigger = Clock.create_trigger(
            self.perform_debounced_search, 
            timeout=0.5
        )

    # ==================== LIFECYCLE METHODS ====================
    def on_enter(self, *args):
        """Inicializa a tela quando entra"""
        self.verific_token()
        self.event_token = Clock.schedule_interval(self.verific_token, 300)
        
        # Reset state
        self.type = 'loc'
        self.current_page = 0
        self.all_employees = []
        self.loaded_employee_keys = []
        self.ids.main_scroll.clear_widgets()
        
        # Initialize dialogs
        self._setup_dialogs()
        
        # Load employees
        self.upload_employees()

    def on_leave(self, *args):
        """Limpa recursos ao sair da tela"""
        if hasattr(self, 'event_token'):
            self.event_token.cancel()

    def _setup_dialogs(self):
        """Configura os dialogs de erro"""
        self.inf_dialog = DialogInfinityUpload()
        self.signcontroller = SignController(screen=self, name='VacancyContractor')
        
        self.dialog_not_net = DialogNoNet(
            subtitle='Não foi possível se conectar. Verifique sua internet e tente novamente',
            callback=lambda: self.signcontroller.retry_signup(self.upload_employees)
        )
        
        self.dialog_error_delete = DialogNoNet(
            subtitle='Não foi possível deletar. Verifique sua internet e tente novamente',
            callback=lambda *_: self.signcontroller.retry_delete(
            lambda: self.perform_debounced_search(None)
        )
        )
        
        self.dialog_not_net_database = DialogNoNet(
            subtitle='Não foi carregar funções. Verifique sua internet e tente novamente',
            callback=lambda *_: self.signcontroller.retry_handle(
                lambda *_: self.delete_employee_no_found(self.key)
            )
        )

        self.dialog_error_unknown = DialogErrorUnknow(screen=f'{self.name}')

    # ==================== TOKEN MANAGEMENT ====================
    def verific_token(self, *args):
        """Verifica se o token ainda é válido"""
        if not self.get_parent_window():
            return
            
        UrlRequest(
            f"{self.FIREBASE_URL}/Users/{self.local_id}.json?auth={self.token_id}",
            on_success=self.on_token_success,
            on_failure=self.on_token_failure,
            on_error=self.on_token_failure,
            method="GET"
        )

    def on_token_success(self, req, result):
        """Token válido"""
        pass
    def on_token_failure(self, req, result):
        """Token inválido, tenta renovar"""
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

    def on_refresh_failure(self, req, result):
        """Falha ao renovar token"""
        self.show_error('O token não foi renovado')
        Clock.schedule_once(
            lambda dt: self.show_error('Refaça login no aplicativo'), 
            1
        )

    # ==================== EMPLOYEE LOADING ====================
    def upload_employees(self):
        """Carrega lista de funcionários"""
        self.ids.main_scroll.clear_widgets()
        url = f'{self.FIREBASE_URL}/requets.json?auth={self.token_id}'

        UrlRequest(
            url,
            on_success=self.prepare_employees,
            on_error=self.signcontroller.handle_signup_error,
            on_failure=self.signcontroller.handle_signup_failure
        )

    def prepare_employees(self, req, employees):
        """Prepara e filtra a lista de funcionários"""
        self.all_employees = []
        self.loaded_employee_keys = []
        self.current_page = 0
        self.cont = 0
        
        if not employees:
            self._show_empty_state()
            return

        try:
            for key, employee in employees.items():
                self.cont += 1
                
                # Pula primeiro item (bug conhecido)
                """ if self.cont == 1:
                    continue """
                
                # Verifica se já enviou solicitação
                requests = ast.literal_eval(employee.get('requests', '[]'))
                if self.local_id in requests:
                    continue
                
                # Adiciona funcionário à lista
                employee_data = {
                    'key': key,
                    'employee_key': employee.get('key', ''),
                    'employee_name': employee.get('employee_name', 'Sem nome'),
                    'employee_function': employee.get('employee_function', 'Sem função'),
                    'avatar': employee.get('avatar', ''),
                    'rating': 3
                }
                self.all_employees.append(employee_data)

            # Verifica se tem funcionários
            if not self.all_employees:
                self._show_empty_state()
            else:
                self.load_more_employees()
                
        except Exception as e:
            self.dialog_error_unknown.open()

    def load_more_employees(self):
        """Carrega mais funcionários (paginação)"""
        start_index = self.current_page * self.items_per_page
        end_index = start_index + self.items_per_page

        # Verifica se ainda há itens
        if start_index >= len(self.all_employees):
            return False

        # Adiciona cards
        loaded_count = 0
        for item in self.all_employees[start_index:end_index]:
            # Evita duplicatas
            if item['key'] in self.loaded_employee_keys:
                continue
                
            card = self.create_profile_card(
                name=item['employee_name'],
                profession=item['employee_function'],
                rating=item.get('rating', 3),
                avatar=item['avatar'],
                key_employee=item['employee_key'],
                request_key=item['key']
            )
            
            self.ids.main_scroll.add_widget(card)
            self.loaded_employee_keys.append(item['key'])
            loaded_count += 1

        self.current_page += 1
        self.signcontroller.close_all_dialogs()
        return True

    def check_scroll(self, scroll_view, *args):
        """Verifica se chegou ao fim do scroll para carregar mais"""
        if self.add and not self.on_search:
            if scroll_view.scroll_y <= 0:
                more_items = self.load_more_employees()
                if not more_items:
                    pass

    def _show_empty_state(self):
        """Exibe mensagem quando não há funcionários"""
        self.ids.main_scroll.clear_widgets()
        
        empty_label = MDLabel(
            text='\n\n\n\n\nO banco de funcionários está vazio',
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint_x=0.8,
            halign='center',
            theme_text_color='Custom',
            text_color='grey'
        )
        self.ids.main_scroll.add_widget(empty_label)

    # ==================== SEARCH FUNCTIONALITY ====================
    def search(self, instance, text):
        """Realiza busca com debounce"""
        self.search_trigger.cancel()
        self.on_search = True
        
        # Se vazio, reseta para lista original
        if not text or text.strip() == '':
            self.reset_cards()
            return

        self.text_search = text.strip().lower()
        self.search_trigger()

    def reset_cards(self, dt=None):
        """Reseta para lista original de funcionários"""
        self.ids.main_scroll.clear_widgets()
        self.current_page = 0
        self.on_search = False
        self.add = True
        self.upload_employees()

    def perform_debounced_search(self, dt):
        """Executa busca após debounce"""
        self.ids.main_scroll.clear_widgets()
        self.show_loading_indicator()
        Clock.schedule_once(self.fetch_search_results, 0)

    def fetch_search_results(self, dt):
        """Busca resultados no Firebase"""
        url = f"{self.FIREBASE_URL}/requets/.json?auth={self.token_id}"

        UrlRequest(
            url,
            on_success=self.process_search_results,
            on_error=self.signcontroller.handle_delete_error,
            on_failure=self.signcontroller.handle_delete_failure,
            timeout=10
        )

    def process_search_results(self, instance, data):
        """Processa resultados da busca"""
        Clock.schedule_once(
            lambda dt: self.filter_and_display_results(data), 
            0
        )

    def filter_and_display_results(self, data):
        """Filtra e exibe resultados da busca"""
        self.hide_loading_indicator()

        MAX_RESULTS = 30
        matched_results = []
        
        for key, item in list(data.items())[:MAX_RESULTS]:
            # Lógica de correspondência
            match_condition = False
            
            if self.type == 'loc':
                match_condition = (
                    self.text_search in item.get('city', '').lower() or
                    self.text_search in item.get('state', '').lower()
                )
            elif self.type == 'func':
                match_condition = (
                    self.text_search in item.get('employee_function', '').lower()
                )

            # Verifica se corresponde e não enviou solicitação
            if match_condition:
                requests = ast.literal_eval(item.get('requests', '[]'))
                if self.local_id not in requests:
                    card = self.create_profile_card(
                        name=item.get('employee_name', 'Sem nome'),
                        profession=item.get('employee_function', 'Sem função'),
                        rating=item.get('rating', 3),
                        avatar=item.get('avatar', ''),
                        key_employee=item.get('key', ''),
                        request_key=key
                    )
                    matched_results.append(card)

                    if len(matched_results) >= MAX_RESULTS:
                        break

        Clock.schedule_once(
            lambda dt: self.update_search_view(matched_results), 
            0
        )

    def update_search_view(self, matched_results):
        """Atualiza view com resultados da busca"""
        self.ids.main_scroll.clear_widgets()

        if matched_results:
            for card in matched_results:
                self.ids.main_scroll.add_widget(card)
            self.scroll_to_top()
        else:
            self.show_no_results_message()
            
        self.signcontroller.close_all_dialogs()
        self.on_search = True

    def show_loading_indicator(self):
        """Exibe indicador de carregamento"""
        loading_label = MDLabel(
            text="\nBuscando...",
            halign="center",
            theme_text_color="Secondary"
        )
        self.ids.main_scroll.clear_widgets()
        self.ids.main_scroll.add_widget(loading_label)

    def hide_loading_indicator(self):
        """Remove indicador de carregamento"""
        self.ids.main_scroll.clear_widgets()

    def show_no_results_message(self):
        """Exibe mensagem de nenhum resultado"""
        if self.ids.tp.text.strip():
            no_results_label = MDLabel(
                text="\nNenhum resultado encontrado.\nTente outro termo de busca.",
                halign="center",
                theme_text_color="Secondary",
                font_style="Title"
            )
            self.ids.main_scroll.add_widget(no_results_label)

    def scroll_to_top(self):
        """Rola para o topo dos resultados"""
        try:
            self.ids.main_scroll.parent.scroll_y = 1
        except Exception:
            pass

    # ==================== SEARCH TYPE TOGGLES ====================
    def loc(self):
        """Ativa busca por localização"""
        self.type = 'loc'
        self.ids.hint.text = 'Buscar por localização'
        self.ids.tp.focus = True
        self.ids.tp.text = ''
        
        # Estilo botão localização
        self.ids.loc_text.text_color = 'white'
        self.ids.loc.md_bg_color = get_color_from_hex('#7692FF')
        
        # Estilo botão função
        self.ids.func.md_bg_color = 'white'
        self.ids.func.line_color = get_color_from_hex('#49D49D')
        self.ids.func_text.text_color = get_color_from_hex('#49D49D')
        
        self.ids.main_scroll.clear_widgets()

    def func(self):
        """Ativa busca por função"""
        self.type = 'func'
        self.ids.hint.text = 'Buscar por função'
        self.ids.tp.focus = True
        self.ids.tp.text = ''
        
        # Estilo botão função
        self.ids.func.md_bg_color = get_color_from_hex('#49D49D')
        self.ids.func_text.text_color = 'white'
        
        # Estilo botão localização
        self.ids.loc.md_bg_color = 'white'
        self.ids.loc.line_color = get_color_from_hex('#49D49D')
        self.ids.loc_text.text_color = get_color_from_hex('#49D49D')
        
        self.ids.main_scroll.clear_widgets()

    # ==================== UI COMPONENTS ====================
    def create_profile_card(self, name, profession, rating, avatar, 
                           key_employee, request_key):
        """Cria card de perfil do funcionário"""
        card_layout = MDBoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height="180dp",
            padding="15dp",
            radius=20,
            theme_line_color='Custom',
            line_color='grey',
            md_bg_color=(1, 1, 1, 1),
            pos_hint={'center_x': 0.5}
        )

        # Layout info + foto
        info_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=0.8,
            spacing="5dp",
            pos_hint={'center_y': 0.8}
        )
        card_layout.add_widget(info_layout)

        # Foto de perfil
        profile_box = MDBoxLayout(size_hint_x=0.5, padding="5dp")
        profile_image = MDRelativeLayout(size_hint=(1, 1))
        
        avatar_img = FitImage(
            source=avatar,
            size_hint=(1, 0.95),
            radius=[100,]
        )
        profile_image.add_widget(avatar_img)
        profile_box.add_widget(profile_image)
        info_layout.add_widget(profile_box)

        # Informações
        text_layout = MDBoxLayout(
            orientation='vertical',
            size_hint_x=0.75,
            spacing="5dp",
            padding=["5dp", 0, 0, 0],
            pos_hint={'center_y': 0.6}
        )
        info_layout.add_widget(text_layout)

        # Nome
        name_label = MDLabel(
            text=name,
            font_style='Title',
            role='medium',
            bold=True,
            adaptive_height=True
        )
        text_layout.add_widget(name_label)

        # Profissão
        profession_label = MDLabel(
            text=profession,
            font_style='Title',
            role='medium',
            theme_text_color="Secondary",
            adaptive_height=True
        )
        text_layout.add_widget(profession_label)

        # Estrelas
        stars_layout = MDBoxLayout(
            orientation='horizontal',
            adaptive_height=True,
            spacing="2dp"
        )
        text_layout.add_widget(stars_layout)

        for i in range(5):
            star_icon = MDIcon(
                icon="star",
                theme_icon_color="Custom",
                icon_color=(1, 0.8, 0, 1) if i < rating else (0.7, 0.7, 0.7, 1)
            )
            stars_layout.add_widget(star_icon)

        # Botão
        button_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=0.3,
            padding=[0, "10dp", 0, 0],
            pos_hint={'right': 0.95}
        )
        card_layout.add_widget(button_layout)

        spacer = MDBoxLayout(size_hint_x=0.6)
        button_layout.add_widget(spacer)

        profile_button = MDButton(
            MDButtonText(
                text="Ver perfil",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                bold=True
            ),
            style='tonal',
            size_hint_y=None,
            height=dp(40),
            theme_bg_color='Custom',
            md_bg_color=get_color_from_hex('#49D49D'),
            size_hint_x=0.4,
            pos_hint={'center_y': 0.45}
        )
        profile_button.on_release = lambda: self._upload_employee(
            key_employee, 
            request_key
        )
        button_layout.add_widget(profile_button)

        return card_layout

    # ==================== EMPLOYEE PROFILE ====================
    def _upload_employee(self, key, key_request):
        """Carrega dados do funcionário e navega para perfil"""
        self.employee_key = key
        self.request_key = key_request
        
        url = f'{self.FIREBASE_URL}/Funcionarios/{key}/.json?auth={self.token_id}'
        
        UrlRequest(
            url,
            on_success=lambda req, result: self._next_perfil(req, result, key_request),
            on_failure=self.signcontroller.on_failure,
            on_error=self.signcontroller.on_error
        )

    def _next_perfil(self, req, info, key_request, *args):
        """Navega para tela de perfil do funcionário"""
        self.signcontroller.close_all_dialogs()
        
        if not info:
            self.delete_employee_no_found(key_request)
            return

        try:
            app = MDApp.get_running_app()
            screenmanager = app.root
            perfil = screenmanager.get_screen('PerfilEmployee')
            
            # Dados do funcionário
            perfil.avatar = info.get('avatar', '')
            perfil.employee_name = info.get('Name', '')
            perfil.employee_function = info.get('function', '')
            perfil.employee_mail = info.get('email', '')
            perfil.employee_telephone = info.get('telefone', '')
            perfil.key = self.employee_key
            perfil.key_contractor = self.key_contractor
            perfil.key_requests = self.request_key
            perfil.state = info.get('state', '')
            perfil.city = info.get('city', '')
            perfil.employee_summary = info.get('sumary', '')
            perfil.skills = info.get('skills', '[]')
            
            # Auth
            perfil.token_id = self.token_id
            perfil.refresh_token = self.refresh_token
            perfil.api_key = self.api_key
            perfil.local_id = self.local_id
            perfil.can_add = self.can_add
            
            self.cont = 0
            
            screenmanager.transition = SlideTransition(direction='right')
            screenmanager.current = 'PerfilEmployee'
            
        except Exception as e:
            self.dialog_error_unknown.open()

    def delete_employee_no_found(self, key):
        """Remove funcionário não encontrado do banco"""
        url = f'{self.FIREBASE_URL}/requets/{key}/.json?auth={self.token_id}'
        
        UrlRequest(
            url,
            method='DELETE',
            on_success=self.show_delete_snack,
            on_error=self.signcontroller.on_error,
            on_failure=self.signcontroller.on_failure
        )

    def show_delete_snack(self, req, result):
        """Exibe mensagem de funcionário removido"""
        MDSnackbar(
            MDSnackbarText(
                text='A vaga removida, usuario inexistente',
                theme_text_color='Custom',
                halign='center',
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                text_color='white',
                bold=True
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            halign='center',
            size_hint_x=0.9,
            theme_bg_color='Custom',
            background_color='red'
        ).open()

        # Recarrega lista
        self.signcontroller.close_all_dialogs()
        self.upload_employees()

    # ==================== NOTIFICATIONS ====================
    def show_message(self, message, color='#2196F3'):
        """Exibe mensagem via snackbar"""
        MDSnackbar(
            MDSnackbarText(
                text=message,
                theme_text_color='Custom',
                text_color='white',
                bold=True
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            halign='center',
            size_hint_x=0.94,
            theme_bg_color='Custom',
            background_color=get_color_from_hex(color),
            duration=3
        ).open()

    def show_error(self, error_message):
        """Exibe mensagem de erro"""
        self.show_message(error_message, color='#FF0000')

    # ==================== NAVIGATION ====================
    def request(self, *args):
        """Navega para tela de solicitações"""
        try:
            app = MDApp.get_running_app()
            screen_manager = app.root
            bricklayer = screen_manager.get_screen('RequestContractor')
            
            bricklayer.key = self.key_contractor
            bricklayer.api_key = self.api_key
            bricklayer.token_id = self.token_id
            bricklayer.local_id = self.local_id
            bricklayer.refresh_token = self.refresh_token
            bricklayer.name_contractor = self.username
            
            bricklayer.ids.perfil.active = False
            bricklayer.ids.chat.active = False
            bricklayer.ids.search.active = False
            bricklayer.ids.request.active = True
            bricklayer.current_nav_state = 'request'
            
            self.cont = 0
            screen_manager.transition = SlideTransition(direction='right')
            screen_manager.current = 'RequestContractor'
            
        except Exception as e:

            self.dialog_error_unknown.open()

    def passo(self, *args):
        """Navega para tela de perfil"""
        try:
            app = MDApp.get_running_app()
            screen_manager = app.root
            bricklayer = screen_manager.get_screen('Perfil')
            
            bricklayer.username = self.username
            bricklayer.key = self.key_contractor
            bricklayer.token_id = self.token_id
            bricklayer.refresh_token = self.refresh_token
            bricklayer.api_key = self.api_key
            bricklayer.local_id = self.local_id
            
            bricklayer.ids.perfil.active = True
            bricklayer.ids.search.active = False
            bricklayer.ids.request.active = False
            bricklayer.ids.chat.active = False
            bricklayer.current_nav_state = 'perfil'
            
            self.cont = 0
            screen_manager.transition = SlideTransition(direction='left')
            screen_manager.current = 'Perfil'
            
        except Exception as e:
            self.dialog_error_unknown.open()

    def chat(self, *args):
        """Navega para tela de chat"""
        try:
            app = MDApp.get_running_app()
            screen_manager = app.root
            bricklayer = screen_manager.get_screen('ListChatContractor')
            
            bricklayer.token_id = self.token_id
            bricklayer.api_key = self.api_key
            bricklayer.local_id = self.local_id
            bricklayer.username = self.username
            bricklayer.key_contractor = self.local_id
            bricklayer.refresh_token = self.refresh_token
            
            bricklayer.ids.perfil.active = False
            bricklayer.ids.search.active = False
            bricklayer.ids.request.active = False
            bricklayer.ids.perso = 'Contractor'
            bricklayer.ids.chat.active = True
            bricklayer.current_nav_state = 'chat'
            
            screen_manager.transition = SlideTransition(direction='right')
            screen_manager.current = 'ListChatContractor'
            
        except Exception as e:
            self.dialog_error_unknown.open()
