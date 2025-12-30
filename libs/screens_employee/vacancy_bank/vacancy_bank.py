import ast
from kivy.network.urlrequest import UrlRequest
from kivy.properties import (StringProperty, NumericProperty, ListProperty, ObjectProperty,
                            BooleanProperty, Clock)
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from configurations import (firebase_url, DialogNoNet, DialogInfinityUpload, 
                           DialogErrorUnknow, SignController)
import json
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.chip import MDChip, MDChipText
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.snackbar import MDSnackbarText, MDSnackbar


class OpportunityCard(MDBoxLayout):
    """Card que exibe oportunidades de trabalho"""
    
    # Propriedades de autenticação
    api_key = StringProperty()
    token_id = StringProperty()
    local_id = StringProperty()
    
    # Propriedades da vaga
    contractor = StringProperty()
    function = StringProperty('')
    city = StringProperty('')
    state = StringProperty('')
    salary = StringProperty('')
    method = StringProperty('Diaria')
    company = StringProperty('')
    email = StringProperty('')
    telephone = StringProperty('')
    
    # Propriedades do chip
    text_chip = StringProperty('Candidatar-se')
    color_divider = StringProperty()
    icon = StringProperty('clock-outline')
    
    # Chaves
    function_key = StringProperty()
    employee_key = StringProperty()
    request = ObjectProperty()

    def __init__(self, **kwargs):
        # Configurações de tamanho
        kwargs['size_hint_y'] = None
        kwargs['height'] = dp(225)
        kwargs['size_hint_x'] = 1
        kwargs['pos_hint'] = {'center_x': 0.5, 'center_y': 0.5}
        kwargs['padding'] = "5dp"
        kwargs['spacing'] = "5dp"

        # Processa salário
        salary = kwargs.get('salary', '')
        kwargs['salary'] = str(salary).replace('.', ',') if salary else ''

        # Extrai propriedades customizadas
        self.function = kwargs.pop('function', '')
        self.city = kwargs.pop('city', '')
        self.token_id = kwargs.pop('token_id', '')
        self.local_id = kwargs.pop('local_id', '')
        self.state = kwargs.pop('state', '')
        self.salary = kwargs.pop('salary', '')
        self.method = kwargs.pop('method', 'Diaria')
        self.text_chip = kwargs.pop('text_chip', 'Candidatar-se')
        self.color_divider = kwargs.pop('color_divider', get_color_from_hex('#7692FF'))
        self.company = kwargs.pop('company', 'Empresa')
        self.icon = kwargs.pop('icon', 'clock-outline')
        self.email = kwargs.pop('email', '')
        self.telephone = kwargs.pop('telephone', '')

        # Configurações do card
        kwargs.update({
            'orientation': 'horizontal',
            'theme_bg_color': 'Custom',
            'md_bg_color': (1, 1, 1, 1),
        })

        super().__init__(**kwargs)
        self.build()

    def build(self):
        """Constrói a interface do card"""
        self.clear_widgets()

        # Barra colorida lateral
        color_bar = MDBoxLayout(
            size_hint_x=0.03,
            theme_bg_color='Custom',
            md_bg_color=self.color_divider
        )
        self.ids['metadinha'] = color_bar
        self.add_widget(color_bar)

        # Layout principal
        content_layout = MDBoxLayout(
            orientation='vertical',
            size_hint_x=0.97,
            theme_bg_color='Custom',
            md_bg_color=(1, 1, 1, 1),
            padding=[10, 5],
            spacing=dp(2)
        )
        self.add_widget(content_layout)

        # Adiciona seções
        self._add_header(content_layout)
        self._add_company(content_layout)
        self._add_info(content_layout)
        self._add_chip(content_layout)

    def _add_header(self, parent):
        """Adiciona cabeçalho com título e ícone"""
        title_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='30dp',
            theme_bg_color='Custom',
            md_bg_color=(1, 1, 1, 1)
        )
        parent.add_widget(title_layout)

        # Título
        title_box = MDBoxLayout(size_hint_x=0.8)
        title_layout.add_widget(title_box)
        
        title_label = MDLabel(
            text=self.function,
            font_style='Title',
            role='medium',
            bold=True,
            pos_hint={'center_y': 0.5}
        )
        title_box.add_widget(title_label)

        # Ícone
        icon_box = MDBoxLayout(size_hint_x=0.2)
        title_layout.add_widget(icon_box)
        
        icon = MDIcon(
            icon=self.icon,
            theme_icon_color='Custom',
            icon_color=self.color_divider,
            pos_hint={'center_y': 0.5}
        )
        icon_box.add_widget(icon)

    def _add_company(self, parent):
        """Adiciona nome da empresa"""
        company_box = MDBoxLayout(
            size_hint_y=None,
            height='20dp',
            theme_bg_color='Custom',
            md_bg_color=(1, 1, 1, 1)
        )
        parent.add_widget(company_box)

        company_label = MDLabel(
            text=self.company,
            theme_text_color='Custom',
            text_color='grey',
            font_style='Title',
            role='small',
            pos_hint={'center_y': 0.5}
        )
        company_box.add_widget(company_label)

    def _add_info(self, parent):
        """Adiciona informações da vaga"""
        info_box = MDBoxLayout(
            orientation='vertical',
            theme_bg_color='Custom',
            md_bg_color=(1, 1, 1, 1),
            spacing=dp(2)
        )
        parent.add_widget(info_box)

        # Localização
        self._add_info_row(
            info_box, 
            'map-marker', 
            get_color_from_hex('#FFA500'),
            f'Localização: {self.city}, {self.state}'
        )

        # Método de pagamento
        self._add_info_row(
            info_box,
            'credit-card-outline',
            (0.0, 1.0, 0.0, 1.0),
            f'Método de Pagamento: {self.method}'
        )

        # Salário
        self._add_info_row(
            info_box,
            'credit-card-outline',
            'purple',
            f'Salário: R${self.salary}'
        )

        # Email
        self._add_info_row(
            info_box,
            'email',
            get_color_from_hex('#5BC0EB'),
            f'Email: {self.email}'
        )

        # Telefone
        self._add_info_row(
            info_box,
            'phone',
            get_color_from_hex('#FF01FB'),
            f'Telefone: {self.telephone}'
        )

    def _add_info_row(self, parent, icon_name, icon_color, text):
        """Adiciona uma linha de informação"""
        row = MDBoxLayout(
            orientation='horizontal',
            theme_bg_color='Custom',
            spacing=5,
            md_bg_color=(1, 1, 1, 1)
        )
        parent.add_widget(row)

        icon = MDIcon(
            icon=icon_name,
            theme_icon_color='Custom',
            icon_color=icon_color,
            pos_hint={'center_y': 0.5}
        )
        row.add_widget(icon)

        label = MDLabel(
            text=text,
            font_style='Label',
            role='medium'
        )
        row.add_widget(label)

    def _add_chip(self, parent):
        """Adiciona botão de ação"""
        bottom_box = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='30dp',
            padding=[0, 5]
        )
        parent.add_widget(bottom_box)

        # Espaçador
        spacer = MDBoxLayout(size_hint_x=0.55)
        bottom_box.add_widget(spacer)

        # Container do chip
        chip_box = MDBoxLayout(size_hint_x=0.3)
        bottom_box.add_widget(chip_box)

        # Chip
        chip_text = MDChipText(
            text='Solicitar chat',
            theme_text_color='Custom',
            text_color='white',
            font_style='Label',
            role='medium',
            bold=True
        )
        self.ids['text_chip'] = chip_text

        chip = MDChip(
            chip_text,
            type="input",
            theme_bg_color='Custom',
            theme_line_color='Custom',
            line_color=get_color_from_hex('#7692FF'),
            md_bg_color=self.color_divider,
            _no_ripple_effect=True,
        )
        self.ids['chip'] = chip
        chip.bind(on_release=lambda instance: self.add_key(self.function_key))
        chip_box.add_widget(chip)

    def add_key(self, key):
        """Adiciona solicitação de vaga"""
        if self.text_chip not in 'Enviado':
            new_request = self.request.copy()

            if self.employee_key not in new_request:
                new_request.append(self.local_id)
                data = {'requests': f"{new_request}"}

                self.ids.chip.disabled = True
                
                def check_vacancy_exists(req, result):
                    """Verifica se a vaga ainda existe antes de enviar solicitação"""
                    if not result:
                        self._show_snackbar('Esta vaga não está mais disponível', 'red')
                        # Remove o card da tela
                        if self.parent:
                            self.parent.remove_widget(self)
                        return
                    
                    # Se a vaga existe, envia a solicitação
                    UrlRequest(
                        url=f'https://obra-7ebd9-default-rtdb.firebaseio.com/Functions/{key}/.json?auth={self.token_id}',
                        method='PATCH',
                        req_body=json.dumps(data),
                        on_success=self.successful,
                    )
                
                # Primeiro verifica se a vaga ainda existe
                UrlRequest(
                    url=f'https://obra-7ebd9-default-rtdb.firebaseio.com/Functions/{key}/.json?auth={self.token_id}',
                    method='GET',
                    on_success=check_vacancy_exists,
                )

    def successful(self, instance, result):
        """Callback de sucesso"""
        self.ids.chip.md_bg_color = get_color_from_hex('#44CF6C')
        self.ids.metadinha.md_bg_color = get_color_from_hex('#44CF6C')
        self.ids.text_chip.text = 'Enviado'
        self.ids.text_chip.text_color = 'white'

    def _show_snackbar(self, text, bg_color='green'):
        """Exibe mensagem na tela"""
        MDSnackbar(
            MDSnackbarText(
                text=text,
                theme_text_color='Custom',
                text_color='white',
                bold=True
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            halign='center',
            size_hint_x=0.9,
            theme_bg_color='Custom',
            background_color=bg_color
        ).open()
        
class VacancyBank(MDScreen):
    """Tela do banco de vagas"""
    
    # Propriedades de autenticação
    token_id = StringProperty()
    local_id = StringProperty()
    api_key = StringProperty()
    refresh_token = StringProperty()
    
    # Propriedades do usuário
    key = StringProperty()
    city = StringProperty()
    state = StringProperty()
    avatar = StringProperty()
    employee_name = StringProperty()
    employee_function = StringProperty()
    employee_mail = StringProperty()
    employee_telephone = StringProperty()
    employee_summary = StringProperty()
    skills = StringProperty()
    contractor = StringProperty()
    
    # Propriedades de controle
    current_nav_state = StringProperty('vacancy')
    request = BooleanProperty()
    cant = True
    add = True
    type = ''
    number = 0
    
    # Paginação
    all_functions = ListProperty([])
    current_page = NumericProperty(0)
    items_per_page = NumericProperty(3)
    loaded_function_keys = ListProperty([])
    
    FIREBASE_URL = firebase_url()

    def on_kv_post(self, base_widget):
        self.text_search = None
        self.search_trigger = Clock.create_trigger(
            self.perform_debounced_search, 
            timeout=0.5
        )

    def on_enter(self, *args):
        """Inicializa a tela"""
        self.type = 'loc'
        self.ids.main_scroll.clear_widgets()
        self.ids.vacancy.active = True
        
        # Reset paginação
        self.current_page = 0
        self.all_functions = []
        self.loaded_function_keys = []

        # Carrega funções
        self.load_functions()
        self.verific_token()
        self.event_token = Clock.schedule_interval(self.verific_token, 300)

    def on_leave(self, *args):
        """Limpa eventos ao sair"""
        if hasattr(self, 'event_token'):
            self.event_token.cancel()

    # ========== VERIFICAÇÃO DE TOKEN ==========
    
    def verific_token(self, *args):
        """Verifica validade do token"""
        if not self.get_parent_window():
            return
            
        UrlRequest(
            f"{self.FIREBASE_URL}/Funcionarios/{self.local_id}.json?auth={self.token_id}",
            on_success=self.on_success_token,
            on_failure=self.on_failure_token,
            on_error=self.on_failure_token,
            method="GET"
        )

    def on_failure_token(self, req, result):
        """Token inválido, tenta atualizar"""
        self.refresh_id_token()

    def on_success_token(self, req, result):
        """Token válido"""

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
        """Token renovado com sucesso"""
        self.token_id = result["id_token"]
        self.refresh_token = result.get("refresh_token", self.refresh_token)

    def on_refresh_failure(self, req, result):
        """Erro ao renovar token"""
        self.show_error('O token não foi renovado')
        Clock.schedule_once(
            lambda dt: self.show_error('Refaça login no aplicativo'), 
            1
        )

    # ========== CARREGAMENTO DE VAGAS ==========
    
    def load_functions(self):
        """Carrega funções do Firebase"""
        url = f"https://obra-7ebd9-default-rtdb.firebaseio.com/Functions/.json?auth={self.token_id}"
        UrlRequest(url, on_success=self.prepare_functions)

    def prepare_functions(self, instance, result):
        """Prepara e filtra funções"""
        filtered_functions = []

        try:
            for key, item in result.items():
                try:
                    requests = ast.literal_eval(item.get('requests', '[]'))
                    declines = ast.literal_eval(item.get('decline', '[]'))

                    if not isinstance(requests, list):
                        requests = []
                    if not isinstance(declines, list):
                        declines = []

                except (ValueError, SyntaxError) as e:
                    requests = []
                    declines = []

                # Filtra vagas que o usuário não solicitou nem recusou
                if self.local_id not in requests and self.local_id not in declines:
                    function_data = {
                        'key': key,
                        'requests': requests,
                        'decline': declines,
                        'email': item.get('email', 'Não definido'),
                        'telephone': item.get('telephone', 'Não definido'),
                        'company': item.get('company', 'Não definido'),
                        'occupation': item.get('occupation', 'N/A'),
                        'City': item.get('City', 'N/A'),
                        'State': item.get('State', 'N/A'),
                        'Salary': item.get('Salary', 'N/A'),
                        'Option Payment': item.get('Option Payment', 'N/A'),
                    }
                    filtered_functions.append(function_data)

            self.all_functions = filtered_functions

            # Mostra mensagem se não houver vagas
            if not filtered_functions:
                self._show_empty_message()
            else:
                self._hide_empty_message()
                self.load_more_functions()

        except Exception as e:
            pass

    def _show_empty_message(self):
        """Mostra mensagem de banco vazio"""
        if not hasattr(self, "label") or self.label not in self.children:
            self.label = MDLabel(
                text='O banco de vagas está vazio',
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                size_hint_x=0.8,
                halign='center',
                theme_text_color='Custom',
                text_color='grey'
            )
            self.add_widget(self.label)

    def _hide_empty_message(self):
        """Remove mensagem de banco vazio"""
        if hasattr(self, "label") and self.label in self.children:
            self.remove_widget(self.label)
            del self.label

    def load_more_functions(self):
        """Carrega mais vagas com paginação"""
        start_index = self.current_page * self.items_per_page
        end_index = start_index + self.items_per_page

        if start_index >= len(self.all_functions):
            return False

        def add_cards_with_delay(dt=None):
            loaded_count = 0
            
            for item in self.all_functions[start_index:end_index]:
                if item['key'] not in self.loaded_function_keys:
                    # Determina status da vaga
                    is_submitted = self.local_id in item['requests']
                    
                    card = OpportunityCard(
                        function=item['occupation'],
                        city=item['City'],
                        token_id=self.token_id,
                        local_id=self.local_id,
                        state=item['State'],
                        salary=item['Salary'],
                        contractor=self.contractor,
                        method=item['Option Payment'],
                        text_chip='Submetido' if is_submitted else 'Candidatar-se',
                        color_divider='green' if is_submitted else 'blue',
                        function_key=item['key'],
                        employee_key=self.key,
                        request=item['requests'],
                        email=item['email'],
                        telephone=item['telephone'],
                        company=item['company']
                    )
                    
                    self.ids.main_scroll.add_widget(card)
                    self.loaded_function_keys.append(item['key'])
                    loaded_count += 1
                    
                    Clock.schedule_once(lambda dt: None, 0.1 * loaded_count)

        Clock.schedule_once(add_cards_with_delay, 0)
        self.current_page += 1
        return True

    # ========== BUSCA ==========
    
    def search(self, instance, text):
        """Realiza busca com debounce"""
        if hasattr(self, 'label'):
            self.remove_widget(self.label)
            
        self.search_trigger.cancel()

        if not text or text.strip() == '':
            Clock.schedule_once(self.reset_cards, 0)
            return

        self.text_search = text.strip().lower()
        self.search_trigger()

    def reset_cards(self, dt=None):
        """Reseta cards para estado original"""
        self.ids.main_scroll.clear_widgets()
        self.current_page = 0
        self.loaded_function_keys = []
        self.load_more_functions()
        self.add = True
        if hasattr(self, 'label'):
            self.add_widget(self.label)

    def perform_debounced_search(self, dt):
        """Executa busca após delay"""
        self.ids.main_scroll.clear_widgets()
        self.show_loading_indicator()
        Clock.schedule_once(self.fetch_search_results, 0)

    def fetch_search_results(self, dt):
        """Busca resultados no Firebase"""
        url = f"https://obra-7ebd9-default-rtdb.firebaseio.com/Functions/.json?auth={self.token_id}"
        UrlRequest(
            url,
            on_success=self.process_search_results,
            on_failure=self.handle_search_error,
            timeout=10
        )

    def process_search_results(self, instance, data):
        """Processa resultados da busca"""
        Clock.schedule_once(lambda dt: self.filter_and_display_results(data), 0)

    def filter_and_display_results(self, data):
        """Filtra e exibe resultados"""
        self.hide_loading_indicator()
        
        MAX_RESULTS = 30
        matched_results = []

        for key, item in list(data.items())[:MAX_RESULTS]:
            # Critério de busca baseado no tipo
            if self.type == 'loc':
                match = (self.text_search in item['City'].lower() or 
                        self.text_search in item['State'].lower())
            elif self.type == 'func':
                match = self.text_search in item['occupation'].lower()
            else:
                match = False

            if match:
                requests = ast.literal_eval(item.get('requests', '[]'))
                declines = ast.literal_eval(item.get('decline', '[]'))
                
                if self.local_id not in requests and self.local_id not in declines:
                    if hasattr(self, 'label'):
                        self.remove_widget(self.label)

                    is_submitted = self.key in requests
                    
                    card = OpportunityCard(
                        function=item['occupation'],
                        city=item['City'],
                        token_id=self.token_id,
                        local_id=self.local_id,
                        state=item['State'],
                        contractor=self.contractor,
                        salary=item['Salary'],
                        method=item['Option Payment'],
                        text_chip='Submetido' if is_submitted else 'Candidatar-se',
                        color_divider='green' if is_submitted else 'blue',
                        function_key=key,
                        employee_key=self.key,
                        request=requests,
                        email=item['email'],
                        telephone=item['telephone'],
                        company=item['company']
                    )
                    
                    matched_results.append(card)
                    
                    if len(matched_results) >= MAX_RESULTS:
                        break

        Clock.schedule_once(
            lambda dt: self.update_search_view(matched_results), 
            0
        )

    def update_search_view(self, matched_results):
        """Atualiza visualização com resultados"""
        self.ids.main_scroll.clear_widgets()

        if matched_results:
            for card in matched_results:
                self.ids.main_scroll.add_widget(card)
            self.scroll_to_top()
        else:
            self.show_no_results_message()

        self.add = True

    def handle_search_error(self, instance, error):
        """Trata erros de busca"""
        Clock.schedule_once(self.show_search_error, 0)

    # ========== FILTROS DE BUSCA ==========
    
    def loc(self, *args):
        """Ativa busca por localização"""
        self.type = 'loc'
        self.ids.hint.text = 'Buscar por localização'
        self.ids.tp.focus = True
        self.ids.loc_text.text_color = 'white'
        self.ids.loc.md_bg_color = get_color_from_hex('#7692FF')
        
        self.ids.func.md_bg_color = 'white'
        self.ids.func.line_color = get_color_from_hex('#7692FF')
        self.ids.func_text.text_color = get_color_from_hex('#7692FF')
        self.ids.tp.text = ''

    def func(self, *args):
        """Ativa busca por função"""
        self.type = 'func'
        self.ids.hint.text = 'Buscar por função'
        self.ids.tp.focus = True
        self.ids.func.md_bg_color = get_color_from_hex('#7692FF')
        self.ids.func_text.text_color = 'white'
        
        self.ids.loc.md_bg_color = 'white'
        self.ids.loc.line_color = get_color_from_hex('#7692FF')
        self.ids.loc_text.text_color = get_color_from_hex('#7692FF')
        self.ids.tp.text = ''

    # ========== NAVEGAÇÃO ==========
    
    def chat(self, *args):
        """Navega para tela de chat"""
        app = MDApp.get_running_app()
        perfil = app.root.get_screen('ListChat')
        
        # Transfere dados
        perfil.employee_name = self.employee_name
        perfil.employee_function = self.employee_function
        perfil.employee_mail = self.employee_mail
        perfil.employee_telephone = self.employee_telephone
        perfil.key = self.key
        perfil.api_key = self.api_key
        perfil.avatar = self.avatar
        perfil.employee_summary = self.employee_summary
        perfil.skills = self.skills
        perfil.token_id = self.token_id
        perfil.local_id = self.local_id
        perfil.refresh_token = self.refresh_token
        perfil.city = self.city
        perfil.state = self.state
        perfil.perso = 'Employee'
        perfil.contractor = self.contractor
        perfil.request = self.request
        perfil.current_nav_state = 'chat'
        
        # Atualiza ícones
        if hasattr(perfil.ids, 'chat'):
            perfil.ids.chat.active = True
        if hasattr(perfil.ids, 'vacancy'):
            perfil.ids.vacancy.active = False
        if hasattr(perfil.ids, 'perfil'):
            perfil.ids.perfil.active = False
        if hasattr(perfil.ids, 'notification'):
            perfil.ids.notification.active = False
        
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'ListChat'

    def perfil(self, *args):
        """Navega para tela de perfil"""
        app = MDApp.get_running_app()
        perfil = app.root.get_screen('PrincipalScreenEmployee')
        
        perfil.key = self.key
        perfil.employee_name = self.employee_name
        perfil.employee_function = self.employee_function
        perfil.employee_mail = self.employee_mail
        perfil.employee_telephone = self.employee_telephone
        perfil.avatar = self.avatar
        perfil.employee_summary = self.employee_summary
        perfil.skills = self.skills
        perfil.state = self.state
        perfil.api_key = self.api_key
        perfil.token_id = self.token_id
        perfil.local_id = self.local_id
        perfil.refresh_token = self.refresh_token
        perfil.city = self.city
        perfil.current_nav_state = 'perfil'
        
        perfil.ids.vacancy.active = False
        perfil.ids.perfil.active = True
        perfil.ids.notification.active = False
        
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'PrincipalScreenEmployee'

    def req(self, *args):
        """Navega para tela de requisições"""
        app = MDApp.get_running_app()
        vac = app.root.get_screen('RequestsVacancy')
        
        vac.key = self.key
        vac.tab_nav_state = 'request'
        vac.employee_name = self.employee_name
        vac.employee_function = self.employee_function
        vac.employee_mail = self.employee_mail
        vac.employee_telephone = self.employee_telephone
        vac.avatar = self.avatar
        vac.employee_summary = self.employee_summary
        vac.skills = self.skills
        vac.token_id = self.token_id
        vac.local_id = self.local_id
        vac.refresh_token = self.refresh_token
        vac.api_key = self.api_key
        vac.request = self.request
        vac.city = self.city
        vac.state = self.state
        vac.contractor = self.contractor
        
        vac.ids.vacancy.active = False
        vac.ids.perfil.active = False
        vac.ids.notification.active = True
        
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'RequestsVacancy'

    def requests(self, *args):
        """Navega para tela de solicitações ou avaliações"""
        app = MDApp.get_running_app()
        
        if not self.contractor:
            if not self.request:
                screen_name = 'WithoutContractor'
            else:
                screen_name = 'ReviewScreen'
        else:
            screen_name = 'ReviewScreen'
            
        screen = app.root.get_screen(screen_name)
        
        # Transfere dados comuns
        screen.key = self.key
        screen.employee_name = self.employee_name
        screen.employee_function = self.employee_function
        screen.employee_mail = self.employee_mail
        screen.employee_telephone = self.employee_telephone
        screen.avatar = self.avatar
        screen.employee_summary = self.employee_summary
        screen.skills = self.skills
        screen.city = self.city
        screen.state = self.state
        screen.token_id = self.token_id
        screen.local_id = self.local_id
        screen.api_key = self.api_key
        screen.refresh_token = self.refresh_token
        screen.contractor = self.contractor
        screen.request = self.request
        
        # Atualiza ícones
        screen.ids.vacancy.active = False
        screen.ids.perfil.active = False
        screen.ids.notification.active = False
        
        if screen_name == 'ReviewScreen':
            screen.current_nav_state = 'payment'
        else:
            if hasattr(screen, 'tab_nav_state'):
                screen.tab_nav_state = 'request'
        
        app.root.current = screen_name

    # ========== UTILITÁRIOS ==========
    
    def check_scroll(self, scroll_view, *args):
        """Verifica scroll para carregar mais"""
        if self.add and (not hasattr(self, 'text_search') or 
                        self.ids.tp.text.strip() == ''):
            if scroll_view.scroll_y <= 0:
                more_items = self.load_more_functions()
                if not more_items:
                    pass

    def on_size(self, *args):
        """Carrega mais cards se necessário"""
        scroll_view = self.ids.main_scroll.parent
        
        if (self.ids.main_scroll.height <= scroll_view.height and
                self.current_page * self.items_per_page < len(self.all_functions)):
            self.load_more_functions()

    def show_loading_indicator(self):
        """Mostra indicador de carregamento"""
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
        """Mostra mensagem sem resultados"""
        no_results_label = MDLabel(
            text="\nTente outro termo de busca.",
            halign="center",
            theme_text_color="Secondary",
            font_style="Title"
        )
        self.add = True
        self.ids.main_scroll.add_widget(no_results_label)

    def show_search_error(self, dt=None):
        """Mostra erro de busca"""
        self.show_message(
            'Erro na busca. Verifique sua conexão.', 
            color='#FF6B6B'
        )
        self.add = True

    def scroll_to_top(self):
        """Rola para o topo"""
        try:
            self.ids.main_scroll.parent.scroll_y = 1
        except Exception:
            pass

    def show_message(self, message, color='#2196F3'):
        """Exibe mensagem"""
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
            size_hint_x=0.8,
            theme_bg_color='Custom',
            background_color=get_color_from_hex(color)
        ).open()

    def show_error(self, error_message):
        """Exibe mensagem de erro"""
        self.show_message(error_message, color='#FF0000')
