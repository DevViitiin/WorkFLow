import ast
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty, get_color_from_hex
from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.fitimage import FitImage
from kivymd.uix.label import MDIcon, MDLabel
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from configurations import DialogNoNet, DialogInfinityUpload, DialogErrorUnknow, firebase_url, check_error, SignController
from kivy.clock import Clock


class RequestContractor(MDScreen):
    local_id = StringProperty()
    token_id = StringProperty()
    api_key = StringProperty()
    refresh_token = StringProperty()
    key = StringProperty()
    username = StringProperty()
    tab_nav_state = StringProperty('request')
    name_contractor = StringProperty()
    current_nav_state = StringProperty('request')
    FIREBASE_URL = firebase_url()

    def on_enter(self, *args):
        self.verific_token()
        self.event_token = Clock.schedule_interval(self.verific_token, 300)
        
        # ====================== popups =============================
        self.inf_dialog = DialogInfinityUpload()
        self.signcontroller = SignController(screen=self, name=self.name)
        
        self.dialog_not_net = DialogNoNet(
            subtitle='Não foi possível se conectar. Verifique sua internet e tente novamente',
            callback=lambda: self.signcontroller.retry_signup(self.load_current_tab)
        )
        
        self.dialog_error_delete = DialogNoNet(
            subtitle='Não foi possível deletar. Verifique sua internet e tente novamente',
            callback=lambda: self.signcontroller.retry_delete(self.load_current_tab)
        )
        
        self.dialog_not_net_database = DialogNoNet(
            subtitle='Não foi carregar funções. Verifique sua internet e tente novamente',
            callback=lambda: self.signcontroller.retry_handle(self.load_current_tab)
        )

        self.dialog_error_unknown = DialogErrorUnknow(screen=f'{self.name}')
        
        self.ids.main_scroll.clear_widgets()
        self.load_current_tab()
        
    def load_current_tab(self):
        """Carrega a aba atual baseada no tab_nav_state"""
        if self.tab_nav_state == 'received':
            self.receiveds()
        elif self.tab_nav_state == 'decline':
            self.decline_requests()
        else:
            self.requests()
            
    def on_leave(self, *args):
        if hasattr(self, 'event_token'):
            self.event_token.cancel()
            
    def verific_token(self, *args):
        if not self.get_parent_window():
            return

        UrlRequest(
            f"{self.FIREBASE_URL}/Users/{self.local_id}.json?auth={self.token_id}",
            on_success=self.on_success,
            on_failure=self.on_failure,
            on_error=self.on_failure,
            method="GET"
        )

    def on_failure(self, req, result):
        self.refresh_id_token()

    def on_success(self, req, result):
        pass

    def show_message(self, message, color='#2196F3'):
        """Exibe uma mensagem na interface através de um snackbar"""
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
        """Exibe uma mensagem de erro através de um snackbar vermelho"""
        self.show_message(error_message, color='#FF0000')

    def refresh_id_token(self):
        """Atualiza o token de autenticação"""
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
        self.token_id = result["id_token"]
        self.refresh_token = result["refresh_token"]

    def on_refresh_failure(self, req, result):
        self.show_error('O token não foi renovado')
        Clock.schedule_once(lambda dt: self.show_error('Refaça login no aplicativo'), 1)

    # ==================== RECEIVEDS (SOLICITAÇÕES RECEBIDAS) ====================
    def receiveds(self):
        """Busca funções onde o contratante recebeu solicitações usando query"""
        url = f'{self.FIREBASE_URL}/Functions.json?orderBy="IdLocal"&equalTo="{self.local_id}"&auth={self.token_id}'
        UrlRequest(
            url,
            on_success=self.process_receiveds,
            on_error=self.signcontroller.handle_signup_error,
            on_failure=self.signcontroller.handle_signup_failure
        )

    def process_receiveds(self, req, result):
        """Processa as solicitações recebidas"""
        self.ids.main_scroll.clear_widgets()
        
        if not result:
            self.show_no_requests_found()
            return
        
        # Set para evitar duplicatas de funcionários
        processed_employees = set()
        requests_count = 0
        
        for function_key, function_data in result.items():
            try:
                requests_list = ast.literal_eval(function_data.get('requests', '[]'))
                
                # Para cada solicitação, busca os dados do funcionário
                for employee_key in requests_list:
                    # Evita adicionar o mesmo funcionário mais de uma vez
                    if employee_key not in processed_employees:
                        processed_employees.add(employee_key)
                        requests_count += 1
                        self.fetch_employee_data(employee_key, function_key, function_data)
                    
            except Exception as e:
                pass
        
        if requests_count == 0:
            self.show_no_requests_found()

    def fetch_employee_data(self, employee_key, function_key, function_data):
        """Busca dados de um funcionário específico"""
        url = f'{self.FIREBASE_URL}/Funcionarios/{employee_key}.json?auth={self.token_id}'
        UrlRequest(
            url,
            on_success=lambda req, result: self.add_employee_card(
                req, result, employee_key, function_key, function_data
            ),
            on_error=lambda req, error: print(f'Erro ao buscar funcionário {employee_key}: {error}')
        )

    def add_employee_card(self, req, employee_data, employee_key, function_key, function_data):
        """Adiciona card do funcionário à lista"""
        if not employee_data:
            return
            
        try:
            card = self.create_profile_card(
                name=employee_data.get('Name', 'N/A'),
                profession=employee_data.get('function', 'N/A'),
                rating=4,
                avatar=employee_data.get('avatar', ''),
                email=employee_data.get('email', ''),
                city=employee_data.get('city', ''),
                skills=employee_data.get('skills', '[]'),
                state=employee_data.get('state', ''),
                summary=employee_data.get('sumary', ''),
                telephone=employee_data.get('telefone', ''),
                key_employee=employee_key,
                key_request=function_key,
                function_data=function_data
            )
            self.ids.main_scroll.add_widget(card)
        except Exception as e:
            pass

    # ==================== REQUESTS (SOLICITAÇÕES ENVIADAS) ====================
    def requests(self):
        """Busca solicitações enviadas usando query"""
        url = f'{self.FIREBASE_URL}/requets.json?auth={self.token_id}'
        UrlRequest(
            url,
            on_success=self.process_requests,
            on_error=self.signcontroller.handle_signup_error,
            on_failure=self.signcontroller.handle_signup_failure
        )

    def process_requests(self, req, result):
        """Processa as solicitações enviadas"""
        self.ids.main_scroll.clear_widgets()
        
        if not result:
            self.show_no_requests_found()
            return
        
        requests_count = 0
        
        for request_key, request_data in result.items():
            try:
                requests_list = ast.literal_eval(request_data.get('requests', '[]'))
                
                # Verifica se este contratante enviou solicitação
                if self.local_id in requests_list:
                    requests_count += 1
                    employee_key = request_data.get('key')
                    if employee_key:
                        self.fetch_pending_employee(employee_key)
                        
            except Exception as e:
                pass
        
        if requests_count == 0:
            self.show_no_requests_found()

    def fetch_pending_employee(self, employee_key):
        """Busca dados do funcionário para solicitação pendente"""
        url = f"{self.FIREBASE_URL}/Funcionarios/{employee_key}.json?auth={self.token_id}"
        UrlRequest(
            url,
            on_success=self.add_pending_card,
            on_error=lambda req, error: print(f'Erro ao buscar funcionário pendente: {error}')
        )

    def add_pending_card(self, req, employee_data):
        """Adiciona card de solicitação pendente"""
        if employee_data:
            card = self.create_pending_profile_card(
                employee_data.get('Name', 'N/A'),
                employee_data.get('function', 'N/A')
            )
            self.ids.main_scroll.add_widget(card)

    # ==================== DECLINE (SOLICITAÇÕES RECUSADAS) ====================
    def decline_requests(self):
        """Busca solicitações recusadas usando query"""
        url = f'{self.FIREBASE_URL}/requets.json?auth={self.token_id}'
        UrlRequest(
            url,
            on_success=self.process_declines,
            on_error=self.signcontroller.handle_signup_error,
            on_failure=self.signcontroller.handle_signup_failure
        )

    def process_declines(self, req, result):
        """Processa as solicitações recusadas"""
        self.ids.main_scroll.clear_widgets()
        
        if not result:
            self.show_no_requests_found()
            return
        
        declines_count = 0
        
        for decline_key, decline_data in result.items():
            try:
                declines_list = ast.literal_eval(decline_data.get('declines', '[]'))
                
                # Verifica se este contratante foi recusado
                if self.local_id in declines_list:
                    declines_count += 1
                    employee_key = decline_data.get('key')
                    if employee_key:
                        self.fetch_declined_employee(employee_key)
                        
            except Exception as e:
                pass
        
        if declines_count == 0:
            self.show_no_requests_found()

    def fetch_declined_employee(self, employee_key):
        """Busca dados do funcionário que recusou"""
        url = f"{self.FIREBASE_URL}/Funcionarios/{employee_key}.json?auth={self.token_id}"
        UrlRequest(
            url,
            on_success=self.add_declined_card,
            on_error=lambda req, error: print(f'Erro ao buscar funcionário recusado: {error}')
        )

    def add_declined_card(self, req, employee_data):
        """Adiciona card de solicitação recusada"""
        if employee_data:
            card = self.create_negative_profile_card(
                employee_data.get('Name', 'N/A'),
                employee_data.get('function', 'N/A')
            )
            self.ids.main_scroll.add_widget(card)

    # ==================== UI COMPONENTS ====================
    def show_no_requests_found(self):
        """Exibe mensagem quando não há solicitações"""
        self.ids.main_scroll.clear_widgets()

        container = MDBoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height="300dp",
            pos_hint={'center_x': 0.5}
        )

        image = AsyncImage(
            source='https://res.cloudinary.com/dsmgwupky/image/upload/v1746223701/aguiav2_pnq6bl.png',
            size_hint=(0.65, 0.65),
            pos_hint={'center_x': 0.5, 'center_y': 0.2}
        )
        container.add_widget(image)
        self.ids.main_scroll.add_widget(container)

    def create_profile_card(self, name, profession, rating, avatar, email, city, skills, 
                           state, summary, telephone, key_employee, key_request, function_data):
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

        # Layout para informações e foto
        info_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=0.8,
            spacing="5dp",
            pos_hint={'center_y': 0.8}
        )
        card_layout.add_widget(info_layout)

        # Foto de perfil
        profile_box = MDBoxLayout(size_hint_x=0.5, padding="5dp")
        info_layout.add_widget(profile_box)

        profile_image = MDRelativeLayout(size_hint=(1, 1))
        avatar_img = FitImage(
            source=avatar,
            size_hint=(1, 0.95),
            radius=[100,]
        )
        profile_image.add_widget(avatar_img)
        profile_box.add_widget(profile_image)

        # Informações do profissional
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
            pos_hint={'right': 1}
        )
        card_layout.add_widget(button_layout)

        spacer = MDBoxLayout(size_hint_x=0.6)
        button_layout.add_widget(spacer)

        profile_button = MDButton(
            MDButtonText(
                text="Ver perfil",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
            ),
            theme_bg_color='Custom',
            md_bg_color=(0.16, 0.44, 0.95, 1),
            size_hint_x=0.4,
            pos_hint={'center_y': 0.4}
        )
        profile_button.on_release = lambda: self._upload_employee(
            name, avatar, city, profession, email, skills, state, summary, 
            telephone, key_employee, key_request, function_data
        )
        button_layout.add_widget(profile_button)

        return card_layout

    def create_pending_profile_card(self, name, profession, status="Solicitação enviada"):
        """Cria card para solicitação pendente"""
        card_layout = MDBoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height="180dp",
            padding="15dp",
            radius=20,
            theme_line_color='Custom',
            line_color='#FFA726',
            md_bg_color=(1, 0.98, 0.94, 1),
            pos_hint={'center_x': 0.5}
        )

        info_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=0.8,
            spacing="5dp",
            pos_hint={'center_y': 0.8}
        )
        card_layout.add_widget(info_layout)

        # Foto com borda laranja
        profile_box = MDBoxLayout(size_hint_x=0.5, padding="5dp")
        info_layout.add_widget(profile_box)

        profile_image = MDRelativeLayout(size_hint=(1, 1))
        avatar_border = MDCard(
            size_hint=(1, 0.95),
            radius=[100,],
            md_bg_color=(0.98, 0.65, 0.15, 1),
            padding="2dp"
        )

        avatar_image = AsyncImage(
            source="https://res.cloudinary.com/dsmgwupky/image/upload/v1744418245/image__2_-removebg-preview_szaoip.png",
            size_hint=(1, 1),
        )
        avatar_border.add_widget(avatar_image)
        profile_image.add_widget(avatar_border)
        profile_box.add_widget(profile_image)

        # Ícone de pendente
        pending_icon = MDIcon(
            icon="clock",
            theme_icon_color="Custom",
            icon_color=(0.98, 0.65, 0.15, 0.9),
            pos_hint={"center_x": 0.85, "center_y": 0.85},
            font_size="24sp"
        )
        profile_image.add_widget(pending_icon)

        # Informações
        text_layout = MDBoxLayout(
            orientation='vertical',
            size_hint_x=0.75,
            spacing="5dp",
            padding=["5dp", 0, 0, 0],
            pos_hint={'center_y': 0.6}
        )
        info_layout.add_widget(text_layout)

        name_label = MDLabel(
            text=name,
            font_style='Title',
            role='medium',
            bold=True,
            theme_text_color="Custom",
            text_color=(0.4, 0.4, 0.4, 1),
            adaptive_height=True
        )
        text_layout.add_widget(name_label)

        profession_label = MDLabel(
            text=profession,
            font_style='Title',
            role='medium',
            theme_text_color="Secondary",
            adaptive_height=True
        )
        text_layout.add_widget(profession_label)

        status_layout = MDBoxLayout(
            orientation='horizontal',
            adaptive_height=True,
            spacing="2dp",
        )
        text_layout.add_widget(status_layout)

        status_icon = MDIcon(
            icon="email-send",
            theme_icon_color="Custom",
            icon_color=(0.98, 0.65, 0.15, 1)
        )
        status_layout.add_widget(status_icon)

        status_label = MDLabel(
            text=status,
            theme_text_color="Custom",
            text_color=(0.98, 0.65, 0.15, 1),
            adaptive_height=True,
            bold=True,
            theme_font_size='Custom',
            font_size='12sp'
        )
        status_layout.add_widget(status_label)

        # Botão
        button_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=0.3,
            padding=[0, "10dp", 0, 0],
            pos_hint={'right': 1}
        )
        card_layout.add_widget(button_layout)

        spacer = MDBoxLayout(size_hint_x=0.6)
        button_layout.add_widget(spacer)

        profile_button = MDButton(
            MDButtonText(
                text="Aguardando",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
            ),
            theme_bg_color='Custom',
            md_bg_color=(0.98, 0.65, 0.15, 1),
            size_hint_x=0.4,
            pos_hint={'center_y': 0.4}
        )
        button_layout.add_widget(profile_button)

        return card_layout

    def create_negative_profile_card(self, name, profession, reason="Recusou a solicitação"):
        """Cria card para solicitação recusada"""
        card_layout = MDBoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height="180dp",
            padding="15dp",
            radius=20,
            theme_line_color='Custom',
            line_color='#FF5252',
            md_bg_color=(1, 0.95, 0.95, 1),
            pos_hint={'center_x': 0.5}
        )

        info_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=0.8,
            spacing="5dp",
            pos_hint={'center_y': 0.8}
        )
        card_layout.add_widget(info_layout)

        # Foto com borda vermelha
        profile_box = MDBoxLayout(size_hint_x=0.5, padding="5dp")
        info_layout.add_widget(profile_box)

        profile_image = MDRelativeLayout(size_hint=(1, 1))
        avatar_border = MDCard(
            size_hint=(1, 0.95),
            radius=[100,],
            md_bg_color=(0.9, 0.2, 0.2, 1),
            padding="2dp"
        )

        avatar_image = AsyncImage(
            source="https://res.cloudinary.com/dsmgwupky/image/upload/v1744416471/image_1_gifxvm.png",
            size_hint=(1, 1),
        )
        avatar_border.add_widget(avatar_image)
        profile_image.add_widget(avatar_border)
        profile_box.add_widget(profile_image)

        # Ícone de recusa
        decline_icon = MDIcon(
            icon="close-circle",
            theme_icon_color="Custom",
            icon_color=(0.9, 0.2, 0.2, 0.9),
            pos_hint={"center_x": 0.85, "center_y": 0.85},
            font_size="24sp"
        )
        profile_image.add_widget(decline_icon)

        # Informações
        text_layout = MDBoxLayout(
            orientation='vertical',
            size_hint_x=0.75,
            spacing="5dp",
            padding=["5dp", 0, 0, 0],
            pos_hint={'center_y': 0.6}
        )
        info_layout.add_widget(text_layout)

        name_label = MDLabel(
            text=name,
            font_style='Title',
            role='medium',
            bold=True,
            theme_text_color="Custom",
            text_color=(0.7, 0.1, 0.1, 1),
            adaptive_height=True
        )
        text_layout.add_widget(name_label)

        profession_label = MDLabel(
            text=profession,
            font_style='Title',
            role='medium',
            theme_text_color="Secondary",
            adaptive_height=True
        )
        text_layout.add_widget(profession_label)

        reason_layout = MDBoxLayout(
            orientation='horizontal',
            adaptive_height=True,
            spacing="2dp",
        )
        text_layout.add_widget(reason_layout)

        decline_label_icon = MDIcon(
            icon="cancel",
            theme_icon_color="Custom",
            icon_color=(0.9, 0.2, 0.2, 1)
        )
        reason_layout.add_widget(decline_label_icon)

        reason_label = MDLabel(
            text=reason,
            theme_text_color="Custom",
            text_color=(0.9, 0.2, 0.2, 1),
            adaptive_height=True,
            bold=True,
            theme_font_size='Custom',
            font_size='12sp'
        )
        reason_layout.add_widget(reason_label)

        # Botão
        button_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=0.3,
            padding=[0, "10dp", 0, 0],
            pos_hint={'right': 1}
        )
        card_layout.add_widget(button_layout)

        spacer = MDBoxLayout(size_hint_x=0.6)
        button_layout.add_widget(spacer)

        profile_button = MDButton(
            MDButtonText(
                text="Buscar outro",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
            ),
            theme_bg_color='Custom',
            md_bg_color=(0.9, 0.2, 0.2, 1),
            size_hint_x=0.4,
            pos_hint={'center_y': 0.4}
        )
        profile_button.on_release = self._next_vacancy_bank
        button_layout.add_widget(profile_button)

        return card_layout

    # ==================== NAVIGATION ====================
    def _upload_employee(self, name, avatar, city, profession, email, skills, state, 
                        summary, telephone, key_employee, key_request, function_data):
        """Navega para o perfil do funcionário"""
        try:
            skills = f"{skills}"
            app = MDApp.get_running_app()
            screenmanager = app.root
            hiring = screenmanager.get_screen('HiringProfile')
            
            # Informações da função
            salary = f"{function_data.get('Salary')}"
            hiring.salary = salary
            hiring.function = function_data.get('occupation', '')
            hiring.method_salary = function_data.get('Option Payment', '')
            hiring.scale = '5x2'

            # Informações do funcionário
            hiring.avatar = avatar
            hiring.employee_name = name
            hiring.employee_function = profession
            hiring.employee_mail = email
            hiring.employee_telephone = telephone
            hiring.key = key_employee
            hiring.key_contractor = self.key
            hiring.username = self.name_contractor
            hiring.key_requests = key_request
            hiring.state = state
            hiring.token_id = self.token_id
            hiring.api_key = self.api_key
            hiring.local_id = self.local_id
            hiring.refresh_token = self.refresh_token
            hiring.city = city
            hiring.employee_summary = summary
            hiring.skills = skills
            
            screenmanager.transition = SlideTransition(direction='right')
            screenmanager.current = 'HiringProfile'
        except Exception as e:
            self.dialog_error_unknown.open()

    def workflow(self, screen):
        """Gerencia a navegação entre abas"""
        if screen == self.tab_nav_state:
            return

        self.tab_nav_state = screen
        self.ids.main_scroll.clear_widgets()
        self.load_current_tab()

    def _next_vacancy_bank(self, *args):
        """Navega para banco de vagas"""
        try:
            app = MDApp.get_running_app()
            screenmanager = app.root
            bank = screenmanager.get_screen('VacancyContractor')
            bank.key_contractor = self.key
            bank.username = self.name_contractor
            bank.ids.perfil.active = False
            bank.token_id = self.token_id
            bank.local_id = self.local_id
            bank.refresh_token = self.refresh_token
            bank.api_key = self.api_key
            bank.ids.search.active = True
            bank.ids.request.active = False
            bank.ids.chat.active = False
            bank.current_nav_state = 'search'
            screenmanager.transition = SlideTransition(direction='left')
            screenmanager.current = 'VacancyContractor'
        except Exception as e:
            self.dialog_error_unknown.open()

    def search(self, *args):
        """Navega para tela de busca"""
        try:
            app = MDApp.get_running_app()
            screen_manager = app.root
            screen_manager.transition = SlideTransition(direction='right')
            bricklayer = screen_manager.get_screen('VacancyContractor')
            bricklayer.key_contractor = self.key
            bricklayer.username = self.name_contractor
            bricklayer.ids.perfil.active = False
            bricklayer.token_id = self.token_id
            bricklayer.local_id = self.local_id
            bricklayer.refresh_token = self.refresh_token
            bricklayer.api_key = self.api_key
            bricklayer.ids.search.active = True
            bricklayer.ids.request.active = False
            bricklayer.ids.chat.active = False
            bricklayer.current_nav_state = 'search'
            screen_manager.current = 'VacancyContractor'
        except Exception as e:
            self.dialog_error_unknown.open()

    def passo(self, *args):
        """Navega para tela de perfil"""
        try:
            app = MDApp.get_running_app()
            screen_manager = app.root
            bricklayer = screen_manager.get_screen('Perfil')
            bricklayer.key = self.key
            bricklayer.username = self.name_contractor
            bricklayer.ids.perfil.active = True
            bricklayer.token_id = self.token_id
            bricklayer.local_id = self.local_id
            bricklayer.refresh_token = self.refresh_token
            bricklayer.api_key = self.api_key
            bricklayer.ids.search.active = False
            bricklayer.ids.request.active = False
            bricklayer.ids.chat.active = False
            bricklayer.current_nav_state = 'perfil'
            screen_manager.transition = SlideTransition(direction='left')
            screen_manager.current = 'Perfil'
        except Exception as e:
            self.dialog_error_unknown.open()
    
    def chat(self, *args):
        """Navega para tela de chat"""
        try:
            app = MDApp.get_running_app()
            screen_manager = app.root
            screen_manager.transition = SlideTransition(direction='right')
            bricklayer = screen_manager.get_screen('ListChatContractor')
            bricklayer.ids.perfil.active = False
            bricklayer.ids.search.active = False
            bricklayer.ids.request.active = False
            bricklayer.ids.perso = 'Contractor'
            bricklayer.ids.chat.active = True
            bricklayer.current_nav_state = 'chat'
            bricklayer.token_id = self.token_id
            bricklayer.api_key = self.api_key
            bricklayer.local_id = self.local_id
            bricklayer.username = self.username
            bricklayer.key_contractor = self.local_id
            bricklayer.refresh_token = self.refresh_token
            screen_manager.current = 'ListChatContractor'
        except Exception as e:
            self.dialog_error_unknown.open()
            