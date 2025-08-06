import ast

from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.properties import get_color_from_hex, StringProperty, ListProperty, NumericProperty, Clock
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButtonText, MDButton
from kivymd.uix.fitimage import FitImage
from kivymd.uix.label import MDIcon, MDLabel
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText


class VacancyContractor(MDScreen):
    current_nav_state = StringProperty('search')
    key_contractor = StringProperty()
    employee_key = StringProperty()
    request_key = StringProperty()
    username = StringProperty()
    on_search = False

    # Lista para armazenar todos os dados
    all_functions = ListProperty([])
    type = ''

    # Controle de paginação
    current_page = NumericProperty(0)
    items_per_page = NumericProperty(3)
    # Tracking loaded function keys to prevent duplicates
    loaded_function_keys = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text_search = None
        self.current_page = 0
        self.items_per_page = 3
        self.all_employees = []
        self.loaded_employee_keys = []
        self.add = True
        self.search_trigger = Clock.create_trigger(self.perform_debounced_search, timeout=0.5)

    def on_enter(self, *args):
        # Limpa qualquer conteúdo anterior
        print('Key recebida: ',self.key_contractor)
        self.type = 'loc'
        self.ids.main_scroll.clear_widgets()

        # Redefine a paginação
        self.current_page = 0
        self.all_functions = []
        self.loaded_function_keys = []
        self.upload_employees()

    def upload_employees(self):
        self.ids.main_scroll.clear_widgets()
        url = 'https://obra-7ebd9-default-rtdb.firebaseio.com/requets/.json'

        UrlRequest(
            url,
            on_success=self.prepare_employees
        )

    def prepare_employees(self, req, employees):
        # Filtra e organiza os funcionários
        self.all_employees = []
        self.loaded_employee_keys = []
        self.current_page = 0

        try:
            for key, employee in employees.items():
                data = ast.literal_eval(employee['requests'])
                print(employee)
                if self.key_contractor not in data:
                    employee_data = {
                        'key': key,
                        'employee_key': employee.get('key', ''),
                        'employee_name': employee.get('employee_name', 'Sem nome'),
                        'employee_function': employee.get('employee_function', 'Sem função'),
                        'avatar': employee.get('avatar', ''),
                        'rating': 3  # Valor padrão para rating
                    }

                    self.all_employees.append(employee_data)

            # Se não houver funcionários disponíveis, adiciona o label
            if not self.all_employees:
                print("Nenhum funcionário encontrado. Adicionando label...")

                if not hasattr(self, "label") or self.label not in self.children:
                    self.label = MDLabel(
                        text='\n\n\n\n\nO banco de funcionários está vazio',
                        pos_hint={'center_x': 0.5, 'center_y': 0.5},
                        size_hint_x=0.8,
                        halign='center',
                        theme_text_color='Custom',
                        text_color='grey'
                    )
                    self.ids.main_scroll.add_widget(self.label)  # Adiciona o label à tela
            else:
                # Remove o label antigo se houver funcionários disponíveis
                if hasattr(self, "label") and self.label in self.children:
                    self.remove_widget(self.label)
                    del self.label  # Remove a referência ao label

                # Limpa os widgets existentes (se estiver recarregando)
                if hasattr(self, 'container'):
                    self.ids.main_scroll.clear_widgets()

                # Carrega a primeira página de cards
                self.load_more_employees()

        except Exception as e:
            print("Erro inesperado:", e)

    def load_more_employees(self):

        # Calcula o índice de início e fim
        start_index = self.current_page * self.items_per_page
        end_index = start_index + self.items_per_page

        # Verifica se ainda há itens para carregar
        if start_index >= len(self.all_employees):
            return False

        # Função para adicionar cards com um pequeno atraso
        def add_cards_with_delay(dt=None):
            loaded_count = 0
            for item in self.all_employees[start_index:end_index]:
                # Verifica se este funcionário já foi carregado
                if item['key'] not in self.loaded_employee_keys:
                    print(self.loaded_employee_keys, item['key'])
                    print(item)
                    card = self.create_profile_card(
                        item['employee_name'],
                        item['employee_function'],
                        item.get('rating', 3),
                        item['avatar'],
                        item['employee_key'],
                        item['key']
                    )
                    self.ids.main_scroll.add_widget(card)  # Substitua por seu container adequado
                    self.loaded_employee_keys.append(item['key'])
                    loaded_count += 1

                    # Pequeno atraso entre cada card
                    Clock.schedule_once(lambda dt: None, 0.1 * loaded_count)
                else:
                    self.ids.main_scroll.clear_widgets()

        # Agenda a adição de cards
        Clock.schedule_once(add_cards_with_delay, 0)

        # Incrementa o número da página
        self.current_page += 1
        return True

    def check_scroll(self, scroll_view, *args):
        # Verifica se está no final do scroll e não está em modo de pesquisa
        if self.add and not self.on_search:
            if scroll_view.scroll_y <= 0:
                # Tenta carregar mais cards
                more_items = self.load_more_employees()

                # Se não há mais itens, volta o scroll para o topo
                if not more_items:
                    print('Acabaram os funcionários')

    def on_size(self, *args):
        # Método para carregar mais cards quando o layout é pequeno
        if hasattr(self, 'scroll_view'):
            # Verifica se o conteúdo é menor que a altura da scroll view
            if (self.container.height <= self.scroll_view.height and
                    self.current_page * self.items_per_page < len(self.all_employees)):
                self.upload_employees()

    def create_profile_card(self, name, profession, rating, avatar, key_employee, request_key):
        # Card principal com bordas arredondadas
        card_layout = MDBoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height="180dp",
            padding=[15,],
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
        profile_box = MDBoxLayout(
            size_hint_x=0.5,
            padding="5dp"
        )
        info_layout.add_widget(profile_box)

        # Imagem circular
        profile_image = MDRelativeLayout(
            size_hint=(1, 1)
        )

        # Avatar - usando FitImage para imagem circular
        avatar = FitImage(
            source=f"{avatar}",  # Substitua pelo caminho da sua imagem
            size_hint=(1, 0.95),
            radius=[100, ]  # Valor para tornar a imagem circular
        )
        profile_image.add_widget(avatar)
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

        # Nome do profissional
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

        # Layout para estrelas
        stars_layout = MDBoxLayout(
            orientation='horizontal',
            adaptive_height=True,
            spacing="2dp"
        )
        text_layout.add_widget(stars_layout)

        # Adicionar estrelas com base na avaliação (de 0 a 5)
        for i in range(5):
            star_icon = MDIcon(
                icon="star",
                theme_icon_color="Custom",
                icon_color=(1, 0.8, 0, 1) if i < rating else (0.7, 0.7, 0.7, 1)
                # Amarelo para estrelas preenchidas, cinza para vazias
            )
            stars_layout.add_widget(star_icon)

        # Layout para o botão
        button_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=0.3,
            padding=[0, "10dp", 0, 0],
            pos_hint={'right': 0.95}
        )
        card_layout.add_widget(button_layout)

        # Espaço vazio à esquerda para alinhar o botão à direita
        spacer = MDBoxLayout(
            size_hint_x=0.6
        )
        button_layout.add_widget(spacer)

        # Botão "Ver perfil"
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
            md_bg_color=get_color_from_hex('#49D49D'),  # Azul como na imagem
            size_hint_x=0.4,
            pos_hint={'center_y': 0.45}
        )
        profile_button.on_release = lambda key=key_employee, key_request=request_key: self._upload_employee(key, key_request)
        button_layout.add_widget(profile_button)
        return card_layout

    def _upload_employee(self, key, key_request):
        self.employee_key = key
        self.request_key = key_request
        print(key, key_request)
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{key}/.json'
        try:
            UrlRequest(
                url,
                on_success=lambda req, result, k=key_request: self._next_perfil(req, result, k)
            )
        except:
            print('Funcionario inexistente')

    # Produzindo a logica de pesquisa ---------------------------------
    def search(self, instance, text):
        self.search_trigger.cancel()
        self.on_search = True
        # Se texto estiver vazio, recarrega cards originais
        if not text or text.strip() == '':
            self.current_page = 0
            self.loaded_function_keys = []
            Clock.schedule_once(self.reset_cards, 0)
            return

        # Agenda nova busca com debounce
        self.text_search = text.strip().lower()
        self.search_trigger()

    def reset_cards(self, dt=None):
        self.ids.main_scroll.clear_widgets()
        self.current_page = 0
        self.on_search = False  # Desativa o modo de pesquisa
        self.upload_employees()
        self.add = True  # Permite carregar mais cards no modo normal

    def perform_debounced_search(self, dt):
        # Limpa resultados anteriores
        self.ids.main_scroll.clear_widgets()
        # Mostra indicador de carregamento
        self.show_loading_indicator()

        # Agenda busca na thread principal
        Clock.schedule_once(self.fetch_search_results, 0)

    def fetch_search_results(self, dt):
        url = f"https://obra-7ebd9-default-rtdb.firebaseio.com/requets/.json"

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
        print(data)
        for key, item in list(data.items())[:MAX_RESULTS]:
            # Lógica de correspondência baseada em type
            print(item)
            if self.type == 'loc':
                match_condition = (
                        self.text_search in item['city'].lower() or
                        self.text_search in item['state'].lower()
                )
            elif self.type == 'func':
                match_condition = (
                        self.text_search in item['employee_function'].lower()
                )
            else:
                match_condition = False

            # Processa itens correspondentes
            if match_condition:
                requests = ast.literal_eval(item['requests'])
                if self.key_contractor not in requests:
                    # Cria card de oportunidade
                    employee_data = {
                        'key': key,
                        'employee_key': data.get('key', ''),
                        'employee_name': data.get('employee_name', 'Sem nome'),
                        'employee_function': data.get('employee_function', 'Sem função'),
                        'avatar': data.get('avatar', ''),
                        'rating': 3  # Valor padrão para rating
                    }
                    card = self.create_profile_card(
                        item['employee_name'],
                        item['employee_function'],
                        item.get('rating', 3),
                        item['avatar'],
                        item['key'],
                        key
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

        # Mantém a flag de pesquisa ativa
        self.on_search = True
        # Não redefina self.add para True aqui, para evitar carregar cards não relacionados

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
        # Não redefina self.add para True aqui, mantenha o estado da pesquisa

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
        if self.ids.tp.text not in '':
            self.ids.main_scroll.clear_widgets()
            no_results_label = MDLabel(
                text="\nTente outro termo de busca.",
                halign="center",
                theme_text_color="Secondary",
                font_style="Title"
            )
            # Mantenha o modo de pesquisa ativo, não redefina self.add
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
        self.ids.func.line_color = get_color_from_hex('#49D49D')
        self.ids.func_text.text_color = get_color_from_hex('#49D49D')
        self.ids.tp.text = ''
        self.ids.main_scroll.clear_widgets()

    def func(self):
        self.type = 'func'
        self.ids.hint.text = 'Buscar por função'
        self.ids.tp.focus = True
        self.ids.func.md_bg_color = get_color_from_hex('#49D49D')
        self.ids.func_text.text_color = 'white'

        self.ids.loc.md_bg_color = 'white'
        self.ids.loc.line_color = get_color_from_hex('#49D49D')
        self.ids.loc_text.text_color = get_color_from_hex('#49D49D')
        self.ids.tp.text = ''
        self.ids.main_scroll.clear_widgets()

    def _next_perfil(self, reqs, info, key):
        print(info)

        if info:
            app = MDApp.get_running_app()
            screenmanager = app.root
            perfil = screenmanager.get_screen('PerfilEmployee')
            perfil.avatar = info['avatar']
            perfil.employee_name = info['Name']
            perfil.employee_function = info['function']
            perfil.employee_mail = info['email']
            perfil.employee_telephone = info['telefone']
            perfil.key = self.employee_key
            perfil.key_contractor = self.key_contractor
            perfil.key_requests = self.request_key
            perfil.state = info['state']
            perfil.city = info['city']
            perfil.employee_summary = info['sumary']
            perfil.skills = info['skills']
            screenmanager.transition = SlideTransition(direction='right')
            screenmanager.current ='PerfilEmployee'
        else:
            print('Não tem porra de funcionario com o caralhos dessa key:  ',key)

            UrlRequest(
                url=f'https://obra-7ebd9-default-rtdb.firebaseio.com/requets/{key}/.json',
                method='DELETE',
                on_success=self.snack
            )

    def snack(self, req, result):
        MDSnackbar(
            MDSnackbarText(
                text='A vaga foi removida porque o funcionário associado não está mais disponível',
                theme_text_color='Custom',
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

        self.ids.main_scroll.clear_widgets()
        url = 'https://obra-7ebd9-default-rtdb.firebaseio.com/requets/.json'

        UrlRequest(
            url,
            on_success=self.prepare_employees
        )
    def bricklayer(self):
        app = MDApp.get_running_app()
        screen_manager = app.root
        screen_manager.transition = SlideTransition(direction='right')
        bricklayer = screen_manager.get_screen('Table')
        bricklayer.key = self.key_contractor
        bricklayer.username = self.username
        bricklayer.ids.table.active = True
        bricklayer.ids.perfil.active = False
        bricklayer.ids.search.active = False
        bricklayer.ids.request.active = False
        bricklayer.current_nav_state = 'table'
        screen_manager.current = 'Table'

    def request(self):
        app = MDApp.get_running_app()
        screen_manager = app.root
        screen_manager.transition = SlideTransition(direction='right')
        bricklayer = screen_manager.get_screen('RequestContractor')
        bricklayer.key = self.key_contractor
        bricklayer.ids.table.active = False
        bricklayer.ids.perfil.active = False
        bricklayer.ids.search.active = False
        bricklayer.ids.request.active = True
        bricklayer.current_nav_state = 'request'
        bricklayer.name_contractor = self.username
        screen_manager.current = 'RequestContractor'

    def passo(self):
        app = MDApp.get_running_app()
        screen_manager = app.root
        bricklayer = screen_manager.get_screen('Perfil')
        bricklayer.ids.table.active = False
        bricklayer.ids.perfil.active = True
        bricklayer.ids.search.active = False
        bricklayer.ids.request.active = False
        bricklayer.current_nav_state = 'perfil'
        bricklayer.username = self.username
        bricklayer.key = self.key_contractor
        screen_manager.transition = SlideTransition(direction='left')
        screen_manager.current = 'Perfil'