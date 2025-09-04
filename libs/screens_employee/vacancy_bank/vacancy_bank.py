import ast
import json
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.properties import get_color_from_hex, ObjectProperty, ListProperty, NumericProperty, Clock, BooleanProperty
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.chip import MDChip, MDChipText
from kivy.utils import get_color_from_hex
from kivy.properties import StringProperty
from kivymd.uix.snackbar import MDSnackbarText, MDSnackbar


class OpportunityCard(MDBoxLayout):
    api_key = StringProperty()
    token_id = StringProperty()
    local_id = StringProperty()
    contractor = StringProperty()
    function = StringProperty('')
    city = StringProperty('')
    state = StringProperty('')
    salary = StringProperty('')
    method = StringProperty('Diaria')
    text_chip = StringProperty('Candidatar-se')
    color_divider = StringProperty()
    function_key = StringProperty()
    employee_key = StringProperty()
    request = ObjectProperty()
    FIREBASE_URL = 'https://obra-7ebd9-default-rtdb.firebaseio.com'

    # Adicionando propriedades para compatibilidade com o novo layout
    company = StringProperty('')
    icon = StringProperty('clock-outline')
    email = StringProperty('')
    telephone = StringProperty('')

    def __init__(self, **kwargs):
        # Set explicit sizing
        kwargs['size_hint_y'] = None
        kwargs['height'] = dp(225)  # Altura compatível com o segundo código
        kwargs['size_hint_x'] = 1
        kwargs['pos_hint'] = {'center_x': 0.5, 'center_y': 0.5}
        kwargs['padding'] = "5dp"
        kwargs['spacing'] = "5dp"

        # Process salary
        salary = kwargs.get('salary', '')
        kwargs['salary'] = str(salary).replace('.', ',') if salary is not None else ''

        # Extract and remove custom properties
        self.function = kwargs.pop('function', '')
        self.city = kwargs.pop('city', '')
        self.token_id = kwargs.pop('token_id', '')
        self.local_id = kwargs.pop('local_id', '')
        self.state = kwargs.pop('state', '')
        self.salary = kwargs.pop('salary', '')
        self.method = kwargs.pop('method', 'Diaria')
        self.text_chip = kwargs.pop('text_chip', 'Candidatar-se')
        self.color_divider = kwargs.pop('color_divider', get_color_from_hex('#7692FF'))

        # Extraindo propriedades adicionais
        self.company = kwargs.pop('company', 'Empresa')
        self.icon = kwargs.pop('icon', 'clock-outline')
        self.email = kwargs.pop('email', '')
        self.telephone = kwargs.pop('telephone', '')

        print('Confirmando se recebi: ', self.local_id)
        # Default card settings
        kwargs.update({
            'orientation': 'horizontal',
            'theme_bg_color': 'Custom',
            'md_bg_color': (1, 1, 1, 1),
        })

        super().__init__(**kwargs)
        self.build()

    def build(self):
        self.clear_widgets()

        # Barra colorida à esquerda (substitui o divider vertical)
        color_bar = MDBoxLayout(
            size_hint_x=0.03,
            theme_bg_color='Custom',
            md_bg_color=self.color_divider
        )
        self.ids['metadinha'] = color_bar
        self.add_widget(color_bar)

        # Layout de conteúdo principal
        content_layout = MDBoxLayout(
            orientation='vertical',
            size_hint_x=0.97,
            theme_bg_color='Custom',
            md_bg_color=(1, 1, 1, 1),
            padding=[10, 5],
            spacing=dp(2)
        )
        self.add_widget(content_layout)

        # Seção do título com ícone
        title_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='30dp',
            theme_bg_color='Custom',
            md_bg_color=(1, 1, 1, 1)
        )
        content_layout.add_widget(title_layout)

        # Box para o título
        title_box = MDBoxLayout(
            size_hint_x=0.8,
        )
        title_layout.add_widget(title_box)

        # Label do título
        title_label = MDLabel(
            text=self.function,
            font_style='Title',
            role='medium',
            bold=True,
            pos_hint={'center_y': 0.5}
        )
        title_box.add_widget(title_label)

        # Box para o ícone
        icon_box = MDBoxLayout(
            size_hint_x=0.2,
        )
        title_layout.add_widget(icon_box)

        # Ícone
        icon = MDIcon(
            icon=self.icon,
            theme_icon_color='Custom',
            icon_color=self.color_divider,
            pos_hint={'center_y': 0.5}
        )
        icon_box.add_widget(icon)

        # Box para empresa
        company_box = MDBoxLayout(
            size_hint_y=None,
            height='20dp',
            theme_bg_color='Custom',
            md_bg_color=(1, 1, 1, 1)
        )
        content_layout.add_widget(company_box)

        # Label da empresa
        company_label = MDLabel(
            text=self.company,
            theme_text_color='Custom',
            text_color='grey',
            font_style='Title',
            role='small',
            pos_hint={'center_y': 0.5}
        )
        company_box.add_widget(company_label)

        # Box para informações
        info_box = MDBoxLayout(
            orientation='vertical',
            theme_bg_color='Custom',
            md_bg_color=(1, 1, 1, 1),
            spacing=dp(2)
        )
        content_layout.add_widget(info_box)

        # Box para localização
        location_box = MDBoxLayout(
            orientation='horizontal',
            theme_bg_color='Custom',
            spacing=5,
            md_bg_color=(1, 1, 1, 1)
        )
        info_box.add_widget(location_box)

        # Ícone de localização
        location_icon = MDIcon(
            icon='map-marker',
            theme_icon_color='Custom',
            icon_color=get_color_from_hex('#FFA500'),  # Laranja para localização
            pos_hint={'center_y': 0.5}
        )
        location_box.add_widget(location_icon)

        # Label de localização
        location_label = MDLabel(
            text=f'Localização: {self.city}, {self.state}',
            font_style='Label',
            role='medium'
        )
        location_box.add_widget(location_label)

        # Box para método de pagamento
        payment_box = MDBoxLayout(
            orientation='horizontal',
            theme_bg_color='Custom',
            spacing=5,
            md_bg_color=(1, 1, 1, 1)
        )
        info_box.add_widget(payment_box)

        # Ícone de pagamento
        payment_icon = MDIcon(
            icon='credit-card-outline',
            theme_icon_color='Custom',
            icon_color=(0.0, 1.0, 0.0, 1.0)
        )
        payment_box.add_widget(payment_icon)

        # Label de pagamento
        payment_label = MDLabel(
            text=f'Método de Pagamento: {self.method}',
            font_style='Label',
            role='medium'
        )
        payment_box.add_widget(payment_label)

        # Box para salário
        salary_box = MDBoxLayout(
            orientation='horizontal',
            theme_bg_color='Custom',
            spacing=5,
            md_bg_color=(1, 1, 1, 1)
        )
        info_box.add_widget(salary_box)

        # Ícone de salário
        salary_icon = MDIcon(
            icon='credit-card-outline',
            theme_icon_color='Custom',
            icon_color='purple',
            pos_hint={'center_y': 0.5}
        )
        salary_box.add_widget(salary_icon)

        # Label de salário
        salary_label = MDLabel(
            text=f'Salário: R${self.salary}',
            font_style='Label',
            role='medium'
        )
        salary_box.add_widget(salary_label)

        # Box para email (sempre incluído)
        email_box = MDBoxLayout(
            orientation='horizontal',
            theme_bg_color='Custom',
            spacing=5,
            md_bg_color=(1, 1, 1, 1)
        )
        info_box.add_widget(email_box)

        # Ícone de email
        email_icon = MDIcon(
            icon='email',
            theme_icon_color='Custom',
            icon_color=get_color_from_hex('#5BC0EB'),
            pos_hint={'center_y': 0.5}
        )
        email_box.add_widget(email_icon)

        # Label de email
        email_label = MDLabel(
            text=f'Email: {self.email}',
            font_style='Label',
            role='medium'
        )
        email_box.add_widget(email_label)

        # Box para telefone (sempre incluído)
        phone_box = MDBoxLayout(
            orientation='horizontal',
            theme_bg_color='Custom',
            spacing=5,
            md_bg_color=(1, 1, 1, 1)
        )
        info_box.add_widget(phone_box)

        # Ícone de telefone
        phone_icon = MDIcon(
            icon='phone',
            theme_icon_color='Custom',
            icon_color=get_color_from_hex('#FF01FB'),
            pos_hint={'center_y': 0.5}
        )
        phone_box.add_widget(phone_icon)

        # Label de telefone
        phone_label = MDLabel(
            text=f'Telefone: {self.telephone}',
            font_style='Label',
            role='medium'
        )
        phone_box.add_widget(phone_label)

        # Container horizontal para o chip na parte inferior
        bottom_box = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='30dp',
            padding=[0, 5]
        )
        content_layout.add_widget(bottom_box)

        # Espaçador à esquerda para empurrar o chip para direita
        spacer = MDBoxLayout(
            size_hint_x=0.7
        )
        bottom_box.add_widget(spacer)

        # Container para o chip
        chip_box = MDBoxLayout(
            size_hint_x=0.3
        )
        bottom_box.add_widget(chip_box)

        # Criar o chip
        chip_text = MDChipText(
            text=self.text_chip,
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
        chip.bind(
            on_release=lambda instance, key=self.function_key: self.add_key(key)
        )

        chip_box.add_widget(chip)

    def add_key(self, key):
        if not self.contractor:
            if self.text_chip not in 'Submetido':
                # Check if employee_key is already in the request list before adding it
                new_request = self.request.copy()  # Create a copy to avoid modifying the original

                # Only add the key if it's not already in the list
                if self.employee_key not in new_request:
                    new_request.append(self.local_id)

                    data = {
                        'requests': f"{new_request}"
                    }

                    # Disable the chip during request to prevent multiple clicks
                    self.ids.chip.disabled = True

                    UrlRequest(
                        url=f'https://obra-7ebd9-default-rtdb.firebaseio.com/Functions/{key}/.json?auth={self.token_id}',
                        method='PATCH',
                        req_body=json.dumps(data),
                        on_success=self.sucefful,

                    )
        else:
            self._show_snackbar(f"Você ja foi contratado não pode solicitar vagas", "red")

    def _show_snackbar(self, text, bg_color='green'):
        """
        Exibe uma mensagem temporária na parte inferior da tela.

        Args:
            text (str): Texto a ser exibido na mensagem.
            bg_color (str, optional): Cor de fundo da mensagem. Padrão é 'green'.
        """
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

    def sucefful(self, instance, result):
        self.ids.chip.md_bg_color = get_color_from_hex('#44CF6C')
        self.ids.metadinha.md_bg_color = get_color_from_hex('#44CF6C')  # Mudado de color para md_bg_color para funcionar com o novo layout
        self.ids.text_chip.text = 'Submetido'
        self.ids.text_chip.text_color = 'white'


class VacancyBank(MDScreen):
    cant = True
    token_id = StringProperty()
    local_id = StringProperty()
    api_key = StringProperty()
    refresh_token = StringProperty()
    current_nav_state = StringProperty('vacancy')
    add = True
    type = ''
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
    request = BooleanProperty()
    contractor = StringProperty()
    number = 0
    FIREBASE_URL = 'https://obra-7ebd9-default-rtdb.firebaseio.com'

    # Lista para armazenar todos os dados
    all_functions = ListProperty([])

    # Controle de paginação
    current_page = NumericProperty(0)
    items_per_page = NumericProperty(3)

    # Tracking loaded function keys to prevent duplicates
    loaded_function_keys = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Cria um evento de debounce que pode ser cancelado
        self.text_search = None
        self.search_trigger = Clock.create_trigger(self.perform_debounced_search, timeout=0.5)

    def on_enter(self, *args):
        print(self.request)
        # Limpa qualquer conteúdo anterior
        self.type = 'loc'
        self.ids.main_scroll.clear_widgets()
        self.ids.vacancy.active = True
        # Redefine a paginação
        self.current_page = 0
        self.all_functions = []
        self.loaded_function_keys = []  # Reset loaded keys

        # Carrega funções do Firebase
        self.load_functions()
        self.verific_token()
        self.event_token = Clock.schedule_interval(self.verific_token, 300)


    def verific_token(self):
        print('🔎 verificando token...')
        UrlRequest(
            f"{self.FIREBASE_URL}/Funcionarios/{self.local_id}.json?auth=s{self.token_id}sjwjjdfadsfaesasw",
            on_success=self.on_success,
            on_failure=self.on_failure,
            on_error=self.on_failure,
            method="GET"
        )

    def on_failure(self, req, result):
        print('❌ Token inválido, tentando atualizar...', result)
        self.refresh_id_token()  # chama atualização

    def on_success(self, req, result):
        print('✅ Token válido, usuário encontrado:')


    # --- ATUALIZAÇÃO DO TOKEN ---
    def refresh_id_token(self):
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
        self.refresh_token = result["refresh_token"]  # Firebase pode mandar de novo
        print("🔄 Token renovado com sucesso:", self.token_id)

    def on_refresh_failure(self, req, result):
        print("❌ Erro ao renovar token:", result)
        self.show_error('O token não foi renovado')
        Clock.schedule_once(lambda dt: self.show_error('Refaça login no aplicativo'), 1)

    def load_functions(self):
        url = f"https://obra-7ebd9-default-rtdb.firebaseio.com/Functions/.json?auth={self.token_id}"
        UrlRequest(
            url,
            on_success=self.prepare_functions
        )

    import ast
    from kivymd.uix.label import MDLabel

    def prepare_functions(self, instance, result):
        # Filtra e organiza as funções
        filtered_functions = []

        try:
            for key, item in result.items():
                try:
                    # Usa ast.literal_eval() para evitar riscos de segurança
                    requests = ast.literal_eval(item['requests'])
                    declines = ast.literal_eval(item['decline'])

                    # Garante que requests e declines sejam listas
                    if not isinstance(requests, list):
                        requests = []
                    if not isinstance(declines, list):
                        declines = []

                except (ValueError, SyntaxError) as e:
                    print(f"Erro ao processar dados em {key}: {e}")
                    requests = []  # Define valores padrão e continua
                    declines = []

                # Verifica se o usuário não está nem em requests nem em declines
                if self.local_id not in requests and self.local_id not in declines:
                    function_data = {
                        'key': key,
                        'requests': requests,
                        'decline': declines,  # Adicionei a lista decline aos dados da função
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

            # Atualiza a lista de funções
            self.all_functions = filtered_functions

            # Se não houver funções disponíveis, adiciona o label
            if not filtered_functions:
                print("Nenhuma vaga encontrada. Adicionando label...")

                if not hasattr(self, "label") or self.label not in self.children:
                    self.label = MDLabel(
                        text='O banco de vagas está vazio',
                        pos_hint={'center_x': 0.5, 'center_y': 0.5},
                        size_hint_x=0.8,
                        halign='center',
                        theme_text_color='Custom',
                        text_color='grey'
                    )
                    self.add_widget(self.label)  # Adiciona o label à tela

            else:
                # Remove o label antigo se houver vagas disponíveis
                if hasattr(self, "label") and self.label in self.children:
                    self.remove_widget(self.label)
                    del self.label  # Remove a referência ao label

                self.load_more_functions()

        except Exception as e:
            print("Erro inesperado:", e)

    def load_more_functions(self):
        # Calcula o índice de início e fim
        start_index = self.current_page * self.items_per_page
        end_index = start_index + self.items_per_page

        # Verifica se ainda há itens para carregar
        if start_index >= len(self.all_functions):
            return False

        # Função para adicionar cards com um pequeno atraso
        def add_cards_with_delay(dt=None):
            loaded_count = 0
            print(self.all_functions)
            for item in self.all_functions[start_index:end_index]:
                # Check if this function key has already been loaded
                print(item)
                if self.local_id not in self.loaded_function_keys:
                    card = OpportunityCard(
                        function=item['occupation'],
                        city=item['City'],
                        token_id=self.token_id,
                        local_id=self.local_id,
                        state=item['State'],
                        salary=item['Salary'],
                        contractor=self.contractor,
                        method=item['Option Payment'],
                        text_chip='Candidatar-se',
                        color_divider='blue',
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
                else:
                    card = OpportunityCard(
                        function=item['occupation'],
                        city=item['City'],
                        contractor=self.contractor,
                        token_id=self.token_id,
                        local_id=self.local_id,
                        state=item['State'],
                        salary=item['Salary'],
                        method=item['Option Payment'],
                        text_chip='Submetido',
                        color_divider='green',
                        function_key=item['key'],
                        employee_key=self.key,
                        request=item['requests'],
                        email=item['email'],
                        telephone=item['telephone'],
                        company=item['company'],

                    )
                    self.ids.main_scroll.add_widget(card)
                    self.loaded_function_keys.append(item['key'])
                    loaded_count += 1

                # Pequeno atraso entre cada card
                Clock.schedule_once(lambda dt: None, 0.1 * loaded_count)

        # Agenda a adição de cards
        Clock.schedule_once(add_cards_with_delay, 0)

        # Incrementa o número da página
        self.current_page += 1
        return True

    def on_size(self, *args):
        # Método para carregar mais cards quando o layout é pequeno
        scroll_view = self.ids.main_scroll.parent

        # Verifica se o conteúdo é menor que a altura da scroll view
        if (self.ids.main_scroll.height <= scroll_view.height and
                self.current_page * self.items_per_page < len(self.all_functions)):
            self.load_more_functions()

    def check_scroll(self, scroll_view, *args):
        # Verifica se está no final do scroll E não está em modo de busca
        if self.add and (not hasattr(self, 'text_search') or self.ids.tp.text.strip() == ''):
            if scroll_view.scroll_y <= 0:
                # Tenta carregar mais cards
                more_items = self.load_more_functions()

                # Se não há mais itens, volta o scroll para o topo
                if not more_items:
                    print('Acabaram os widgets')

    def search(self, instance, text):
        self.remove_widget(self.label)
        # Cancela qualquer busca pendente
        self.search_trigger.cancel()

        # Se texto estiver vazio, recarrega cards originais
        if not text or text.strip() == '':
            Clock.schedule_once(self.reset_cards, 0)
            return

        # Agenda nova busca com debounce
        self.text_search = text.strip().lower()
        self.search_trigger()

    def reset_cards(self, dt=None):
        self.ids.main_scroll.clear_widgets()
        self.current_page = 0
        self.loaded_function_keys = []
        self.load_more_functions()
        self.add = True
        self.add_widget(self.label)

    def perform_debounced_search(self, dt):
        # Limpa resultados anteriores
        self.ids.main_scroll.clear_widgets()

        # Mostra indicador de carregamento
        self.show_loading_indicator()

        # Agenda busca na thread principal
        Clock.schedule_once(self.fetch_search_results, 0)

    def fetch_search_results(self, dt):
        url = f"https://obra-7ebd9-default-rtdb.firebaseio.com/Functions/.json?auth={self.token_id}"

        UrlRequest(
            url,
            on_success=self.process_search_results,
            on_failure=self.handle_search_error,
            timeout=10
        )

    def process_search_results(self, instance, data):
        Clock.schedule_once(lambda dt: self.filter_and_display_results(data), 0)

    def filter_and_display_results(self, data):
        # Hide loading indicator
        self.hide_loading_indicator()

        # Limitar o número de resultados
        MAX_RESULTS = 30
        matched_results = []

        for key, item in list(data.items())[:MAX_RESULTS]:
            # Lógica de correspondência baseada em type
            if self.type == 'loc':
                match_condition = (
                        self.text_search in item['City'].lower() or
                        self.text_search in item['State'].lower()
                )
            elif self.type == 'func':
                match_condition = (
                        self.text_search in item['occupation'].lower()
                )
            else:
                match_condition = False

            # Processa itens correspondentes
            if match_condition:
                requests = ast.literal_eval(item['requests'])
                declines = ast.literal_eval(item['decline'])
                if self.local_id not in requests and self.local_id not in declines:
                    self.remove_widget(self.label)

                    # Determina texto e cor do chip
                    chip_text = 'Candidatar-se' if self.key not in requests else 'Submetido'
                    divider_color = 'blue' if self.key not in requests else 'green'

                    # Cria card de oportunidade
                    card = OpportunityCard(
                        function=item['occupation'],
                        city=item['City'],
                        token_id=self.token_id,
                        local_id=self.local_id,
                        state=item['State'],
                        contractor=self.contractor,
                        salary=item['Salary'],
                        method=item['Option Payment'],
                        text_chip=chip_text,
                        color_divider=divider_color,
                        function_key=key,
                        employee_key=self.key,
                        request=requests ,
                        email=item['email'],
                        telephone=item['telephone'],
                        company=item['company']
                    )

                    matched_results.append(card)

                    # Para se atingir limite máximo
                    if len(matched_results) >= MAX_RESULTS:
                        break

        # Atualiza visualização
        Clock.schedule_once(lambda dt: self.update_search_view(matched_results), 0)

    def update_search_view(self, matched_results):
        # Limpa widgets anteriores
        self.ids.main_scroll.clear_widgets()

        if matched_results:
            for card in matched_results:
                self.ids.main_scroll.add_widget(card)
            self.scroll_to_top()
        else:
            self.show_no_results_message()

        # Reativa busca
        self.add = True

    def handle_search_error(self, instance, error):
        # Tratar erros de busca
        Clock.schedule_once(self.show_search_error, 0)

    def show_search_error(self, dt=None):
        MDSnackbar(
            MDSnackbarText(
                text='Erro na busca. Verifique sua conexão.',
                theme_text_color='Custom',
                text_color='white',
                bold=True
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            halign='center',
            size_hint_x=0.8,
            theme_bg_color='Custom',
            background_color=get_color_from_hex('#FF6B6B')
        ).open()
        self.add = True

    def show_loading_indicator(self):
        # Create and show a loading spinner or message
        loading_label = MDLabel(
            text="\nBuscando...",
            halign="center",
            theme_text_color="Secondary"
        )
        self.ids.main_scroll.clear_widgets()
        self.ids.main_scroll.add_widget(loading_label)

    def hide_loading_indicator(self):
        # Clear loading indicator
        self.ids.main_scroll.clear_widgets()

    def show_no_results_message(self):
        # Display a user-friendly "no results" message
        no_results_label = MDLabel(
            text="\nTente outro termo de busca.",
            halign="center",
            theme_text_color="Secondary",
            font_style="Title"
        )
        self.add = True
        self.ids.main_scroll.add_widget(no_results_label)

    def show_no_input_warning(self):
        # Show a warning if no search input is provided
        MDSnackbar(
            MDSnackbarText(
                text='Coloque um termo para a busca',
                theme_text_color='Custom',
                text_color='white',
                bold=True
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            halign='center',
            size_hint_x=0.8,
            theme_bg_color='Custom',
            background_color=get_color_from_hex('#2F6690')
        ).open()

    def scroll_to_top(self):
        # Scroll to the top of the results (if scroll view supports it)
        try:
            self.ids.main_scroll.parent.scroll_y = 1
        except Exception:
            pass

    def loc(self):
        self.type = 'loc'
        self.ids.hint.text = 'Buscar por localização'
        self.ids.tp.focus = True
        self.ids.loc_text.text_color = 'white'
        self.ids.loc.md_bg_color = get_color_from_hex('#7692FF')

        self.ids.func.md_bg_color = 'white'
        self.ids.func.line_color = get_color_from_hex('#7692FF')
        self.ids.func_text.text_color = get_color_from_hex('#7692FF')
        self.ids.tp.text = ''

    def func(self):
        self.type = 'func'
        self.ids.hint.text = 'Buscar por função'
        self.ids.tp.focus = True
        self.ids.func.md_bg_color = get_color_from_hex('#7692FF')
        self.ids.func_text.text_color = 'white'

        self.ids.loc.md_bg_color = 'white'
        self.ids.loc.line_color = get_color_from_hex('#7692FF')
        self.ids.loc_text.text_color = get_color_from_hex('#7692FF')
        self.ids.tp.text = ''

    def perfil(self):
        """
        Navega para a tela de perfil e ajusta o estado global de navegação
        """
        app = MDApp.get_running_app()
        screenmanager = app.root

        # Obtém a tela de perfil
        perfil = screenmanager.get_screen('PrincipalScreenEmployee')

        # Transfere os dados do usuário
        perfil.key = self.key
        perfil.employee_name = self.employee_name
        perfil.employee_function = self.employee_function
        perfil.employee_mail = self.employee_mail
        perfil.employee_telephone = self.employee_telephone
        perfil.avatar = self.avatar
        perfil.employee_summary = self.employee_summary
        perfil.skills = self.skills
        perfil.ids.vacancy.active = False
        perfil.ids.perfil.active = True
        perfil.ids.payment.active = False
        perfil.state = self.state
        perfil.api_key = self.api_key
        perfil.token_id = self.token_id
        perfil.local_id = self.local_id
        perfil.refresh_token = self.refresh_token
        perfil.city = self.city
        perfil.ids.notification.active = False

        # Define o estado de navegação global
        perfil.current_nav_state = 'perfil'

        # Navega para a tela de perfil
        screenmanager.transition = SlideTransition(direction='right')
        screenmanager.current = 'PrincipalScreenEmployee'

    def req(self):
        """
        Navega para a tela de vagas e ajusta o estado global de navegação
        """
        app = MDApp.get_running_app()
        screenmanager = app.root

        # Obtém a tela de vagas
        vac = screenmanager.get_screen('RequestsVacancy')

        # Transfere os dados do usuário
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

        # Garante que apenas o ícone de vagas esteja ativo
        vac.ids.vacancy.active = False
        vac.ids.perfil.active = False
        vac.ids.payment.active = False
        vac.ids.notification.active = True

        # Navega para a tela de vagas
        screenmanager.transition = SlideTransition(direction='right')
        screenmanager.current = 'RequestsVacancy'

    def requests(self):
        if not self.contractor:

            if not self.request:
                app = MDApp.get_running_app()
                screen = app.root
                without = screen.get_screen('WithoutContractor')
                # Transfere os dados do usuário
                without.key = self.key
                without.tab_nav_state = 'request'
                without.ids.vacancy.active = False
                without.ids.perfil.active = False
                without.ids.payment.active = True
                without.ids.notification.active = False
                without.employee_name = self.employee_name
                without.employee_function = self.employee_function
                without.employee_mail = self.employee_mail
                without.employee_telephone = self.employee_telephone
                without.avatar = self.avatar
                without.employee_summary = self.employee_summary
                without.skills = self.skills
                without.city = self.city
                without.state = self.state
                without.contractor = self.contractor
                without.request = self.request
                screen.current = 'WithoutContractor'
            else:
                app = MDApp.get_running_app()
                screen = app.root
                without = screen.get_screen('RequestSent')
                # Transfere os dados do usuário
                without.key = self.key
                without.ids.vacancy.active = False
                without.ids.perfil.active = False
                without.ids.payment.active = True
                without.ids.notification.active = False
                without.token_id = self.token_id
                without.local_id = self.local_id
                without.api_key = self.api_key
                without.refresh_token = self.refresh_id_token
                without.tab_nav_state = 'request'
                without.employee_name = self.employee_name
                without.employee_function = self.employee_function
                without.employee_mail = self.employee_mail
                without.employee_telephone = self.employee_telephone
                without.avatar = self.avatar
                without.city = self.city
                without.state = self.state
                without.employee_summary = self.employee_summary
                without.skills = self.skills
                without.contractor = self.contractor
                without.request = self.request
                screen.current = 'RequestSent'

        else:
            app = MDApp.get_running_app()
            screen = app.root
            without = screen.get_screen('ReviewScreen')
            # Transfere os dados do usuário
            without.key = self.key
            without.employee_name = self.employee_name
            without.employee_function = self.employee_function
            without.employee_mail = self.employee_mail
            without.employee_telephone = self.employee_telephone
            without.avatar = self.avatar
            without.employee_summary = self.employee_summary
            without.skills = self.skills
            without.request = self.request
            without.contractor = self.contractor
            without.ids.vacancy.active = False
            without.ids.perfil.active = False
            without.ids.payment.active = True
            without.city = self.city
            without.state = self.state
            without.token_id = self.token_id
            without.local_id = self.local_id
            without.api_key = self.api_key
            without.refresh_token = self.refresh_token
            without.ids.notification.active = False
            without.current_nav_state = 'payment'
            screen.current = 'ReviewScreen'
