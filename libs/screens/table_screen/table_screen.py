from kivy.properties import StringProperty, BooleanProperty, partial, get_color_from_hex
from kivy.metrics import dp
from kivymd.uix.snackbar import MDSnackbarText, MDSnackbar
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.list import MDListItem, MDListItemLeadingAvatar, MDListItemHeadlineText, MDListItemSupportingText, \
    MDListItemTertiaryText, MDListItemTrailingCheckbox
from kivymd.uix.screen import MDScreen
from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock


class TableScreen(MDScreen):
    cont = 0
    api_key = StringProperty()
    username = StringProperty()
    token_id = StringProperty()
    local_id = StringProperty()
    refresh_token = StringProperty()
    key = StringProperty()
    current_nav_state = StringProperty('table')
    adicionado = 0
    table = BooleanProperty()
    permission = True
    FIREBASE_URL = 'https://obra-7ebd9-default-rtdb.firebaseio.com'

    # conjunto para rastrear os perfis já carregados
    loaded_employees = set()

    def on_enter(self):
        if not self.local_id:
            return 
        self.verific_token()
        self.event_token = Clock.schedule_interval(self.verific_token, 20)

        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios.json'
        query_params = f'?orderBy=%22contractor%22&equalTo=%22{self.local_id}%22'

        UrlRequest(
            url + query_params,
            method='GET',
            on_success=self.load_employees
        )

    def verific_perfil(self):
        if "Não definido" in (self.function, self.email, self.company, self.telefone, self.username, self.city, self.state) or not (self.function, self.email, self.company, self.telefone, self.username, self.city, self.state):
            self.can_add = False
        else:
            self.can_add = True
            
        print('Posso adicionar?: ', self.can_add)

    def on_leave(self, *args):
        if hasattr(self, 'event_token'):
            self.event_token.cancel()
            print("⏱️ Clock do token cancelado ao sair da tela")
            
    def verific_token(self, *args):
        if not self.get_parent_window():
            return
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
        print('✅ Token válido, usuário encontrado:', result)


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
        
    def upload_employees(self):
        self.ids.main_scroll.clear_widgets()
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/requets/.json?auth={self.token_id}'

        UrlRequest(
            url,
            on_success=self.prepare_employees
        )
    def show_message(self, message, color='#2196F3'):
        """
        Exibe uma mensagem na interface através de um snackbar.

        Args:
            message: A mensagem a ser exibida
            color: A cor de fundo do snackbar
        """
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
            duration=3  # Duração da exibição do snackbar em segundos
        ).open()

    def show_error(self, error_message):
        """
        Exibe uma mensagem de erro através de um snackbar vermelho.

        Args:
            error_message: A mensagem de erro a ser exibida
        """
        self.show_message(error_message, color='#FF0000')

    def load_employees(self, req, result):
        print(result)
        self.ids.main_scroll.clear_widgets()
        self.cont = 0
        for employee_key, info in result.items():
            if info['contractor'] == self.local_id:
                # só adiciona se ainda não estiver na lista
                print("Novo funcionário detectado:", employee_key)
                self.cont += 1
                if 'label' in self.ids:
                    self.remove_widget(self.ids.label)

                Clock.schedule_once(
                    lambda dt, inf=info, emp=employee_key: self.add_employee_in_screen(inf, emp, dt),
                    0.01
                )

        self.ids.counter.text = f'{self.cont} funcionarios contratados'

    def add_employee_in_screen(self, info, employee_key, dt):
        print('Novo funcionario detectado: ', employee_key)
        check = MDListItemTrailingCheckbox()
        check.icon = 'trash-can-outline'
        self.ids[info['Name']] = check

        lista = MDListItem(
            MDListItemLeadingAvatar(
                source=info['avatar']
            ),
            MDListItemHeadlineText(
                text=info['Name']
            ),
            MDListItemSupportingText(
                text=info['function']
            ),
            MDListItemTertiaryText(
                text=info['method_salary']
            ),
        )

        inf = info
        lista.bind(
            on_release=lambda instance, info=inf, key=employee_key: self.show_employee_details(info, key)
        )
        self.ids.main_scroll.add_widget(lista)

        # marca como já carregado
        self.loaded_employees.add(employee_key)

    def handle_checkbox_click(self, instance, name, key, *args):
        # Impede a propagação do evento para o MDListItem
        instance.stop_propagation = True
        # Chama a função de exclusão
        self.click(name, key)

        return True

    def show_employee_details(self, info, key, *args):
        # Obtendo o gerenciador de telas
        print('Informações do cara: ', info)
        if self.permission:
            detail_screen = self.manager.get_screen("Evaluation")
            detail_screen.employee_name = info['Name']
            detail_screen.employee_function = info['function']
            detail_screen.avatar = info['avatar']
            detail_screen.salary = info['salary']
            detail_screen.method_salary = info['method_salary']
            try:
                detail_screen.punctuality = info['punctuality']
            except:
                detail_screen.punctuality = '0'
            
            print('Coexistencia: ', info['coexistence'])
            print('Eficiencia: ', info['effiency'])
            print('Pontualidade: ', info['punctuality'])
            detail_screen.coexistence = info['coexistence']
            detail_screen.efficiency = info['effiency']
            detail_screen.days_work = info['days_work']
            detail_screen.scale = info['scale']
            detail_screen.contractor = info['contractor']
            detail_screen.confirm_payments = info['confirm_payments']
            detail_screen.request_payment = info['request_payment']
            detail_screen.work_days_week1 = info['work_days_week1']
            detail_screen.work_days_week2 = info['work_days_week2']
            detail_screen.work_days_week3 = info['work_days_week3']
            detail_screen.work_days_week4 = info['work_days_week4']
            detail_screen.week_1 = info['week_1']
            detail_screen.week_2 = info['week_2']
            detail_screen.week_3 = info['week_3']
            detail_screen.week_4 = info['week_4']
            detail_screen.day = info['day']
            detail_screen.ultimate = info['ultimate']
            detail_screen.valleys = info['valleys']
            detail_screen.tot = info['tot']
            detail_screen.key = key
            detail_screen.token_id = self.token_id
            detail_screen.refresh_token = self.refresh_token
            detail_screen.local_id = self.local_id
            detail_screen.api_key = self.api_key
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = "Evaluation"

    # chama a tela de cadastrar funcionarios
    def add_screen(self, *args):
        self.manager.transition = SlideTransition(direction='left')
        app = MDApp.get_running_app()
        screen_manager = app.root
        perfil = screen_manager.get_screen('Add')
        perfil.token_id = self.token_id
        perfil.api_key = str(self.api_key)
        perfil.local_id = self.local_id
        perfil.refresh_token = self.refresh_token
        perfil.contractor = self.username
        self.manager.current = 'Add'

    def search(self, *args):
        app = MDApp.get_running_app()
        print('Passando essa key pra tela de search:', self.key)
        screen_manager = app.root
        screen_manager.transition = SlideTransition(direction='right')
        bricklayer = screen_manager.get_screen('VacancyContractor')
        bricklayer.key_contractor = self.key
        bricklayer.username = self.username
        bricklayer.ids.table.active = False
        bricklayer.ids.perfil.active = False
        bricklayer.token_id = self.token_id
        bricklayer.loal_id = self.local_id
        bricklayer.refresh_token = self.refresh_token
        bricklayer.api_key = str(self.api_key)
        bricklayer.ids.search.active = True
        bricklayer.ids.request.active = False
        bricklayer.current_nav_state = 'search'
        screen_manager.current = 'VacancyContractor'

    def request(self, *args):
        app = MDApp.get_running_app()
        screen_manager = app.root
        screen_manager.transition = SlideTransition(direction='right')
        bricklayer = screen_manager.get_screen('RequestContractor')
        bricklayer.key = self.key
        bricklayer.ids.table.active = False
        bricklayer.ids.perfil.active = False
        bricklayer.ids.search.active = False
        bricklayer.ids.request.active = True
        bricklayer.token_id = self.token_id
        bricklayer.loal_id = self.local_id
        bricklayer.refresh_token = self.refresh_token
        bricklayer.api_key = str(self.api_key)
        bricklayer.current_nav_state = 'request'
        bricklayer.name_contractor = self.username
        screen_manager.current = 'RequestContractor'

    def passo(self, *args):
        app = MDApp.get_running_app()
        screen_manager = app.root
        bricklayer = screen_manager.get_screen('Perfil')
        bricklayer.username = self.username
        bricklayer.key = self.key
        bricklayer.ids.table.active = False
        bricklayer.ids.perfil.active = True
        bricklayer.ids.search.active = False
        bricklayer.ids.request.active = False
        bricklayer.current_nav_state = 'perfil'
        bricklayer.token_id = self.token_id
        bricklayer.loal_id = self.local_id
        bricklayer.refresh_token = self.refresh_token
        bricklayer.api_key = str(self.api_key)
        screen_manager.transition = SlideTransition(direction='left')
        screen_manager.current = 'Perfil'
