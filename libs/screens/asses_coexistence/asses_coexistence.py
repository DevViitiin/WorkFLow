import json
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty, NumericProperty, get_color_from_hex
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.screen import MDScreen
from kivy.clock import Clock

class AssesCoexistence(MDScreen):
    api_key = StringProperty()
    employee_name = StringProperty()
    employee_function = StringProperty()
    key = StringProperty()
    avatar = StringProperty()
    contractor = StringProperty()
    method_salary = StringProperty()
    token_id = StringProperty()
    refresh_token = StringProperty()
    local_id = StringProperty()
    salary = StringProperty()
    assess = StringProperty()
    coexistence = NumericProperty()
    punctuality = NumericProperty()
    efficiency = NumericProperty()
    scale = StringProperty()
    days_work = NumericProperty()
    number = 0

     # Firebase url
    FIREBASE_URL = 'https://obra-7ebd9-default-rtdb.firebaseio.com'

    # Definindo as variações de efficiencia
    ASSESSMENT_LEVELS = {
        "coexistence": {
            1: {"text": "Conflituoso(a)", "color": "#FF0000"},
            2: {"text": "Tolerável(a)", "color": "#E06666"},
            3: {"text": "Neutro(a)", "color": "#808080"},
            4: {"text": "Colaborativa(a)", "color": "#008000"},
            5: {"text": "Excelente(a)", "color": "#0044CC"}
        }}

    def on_enter(self):
        self.verific_token()
        self.event_token = Clock.schedule_interval(self.verific_token, 300)
        
    def on_leave(self, *args):
        if hasattr(self, 'event_token'):
            self.event_token.cancel()
            print("⏱️ Clock do token cancelado ao sair da tela")
            
    def verific_token(self, *args):
        if not self.get_parent_window():
            return
        print('🔎 verificando token...')
        UrlRequest(
            f"{self.FIREBASE_URL}/Users/{self.local_id}.json?auth={self.token_id}",
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
    
    def show_error(self, error_message):
        """Display an error message"""
        self.show_message(error_message, color='#FF0000')
        print(f"Error: {error_message}")
    
    def show_message(self, message, color='#2196F3'):
        """Display a snackbar message"""
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


    def update_component(self, indice):
        """Atualiza um componente específico de avaliação"""

        self.ids.asses.text = self.ASSESSMENT_LEVELS['coexistence'][indice]['text']
        self.ids.asses.text_color = get_color_from_hex(self.ASSESSMENT_LEVELS['coexistence'][indice]['color'])

    def back_evaluation(self, *args):
        # Desativando todas as estrelas -------------------------------------------

        # deswativar estrela 5
        self.ids.number_five.icon = 'star-outline'
        self.ids.number_five.icon_color = 'black'

        # desativar estrela 4
        self.ids.number_four.icon = 'star-outline'
        self.ids.number_four.icon_color = 'black'

        # desativar estrela 3
        self.ids.number_three.icon = 'star-outline'
        self.ids.number_three.icon_color = 'black'

        # desativar estrela 2
        self.ids.number_two.icon = 'star-outline'
        self.ids.number_two.icon_color = 'black'

        # Ativar a estrela 1
        self.ids.number_one.icon = 'star-outline'
        self.ids.number_one.icon_color = 'black'

        # limpando o texto
        self.ids.asses.text_color = 'black'
        self.ids.asses.text = ''

        app = MDApp.get_running_app()
        screen_manager = app.root
        self.manager.transition = SlideTransition(direction='right')
        evaluation = screen_manager.get_screen('Evaluation')
        evaluation.employee_name = self.employee_name
        evaluation.employee_function = self.employee_function
        evaluation.avatar = self.avatar
        evaluation.method_salary = self.method_salary
        evaluation.assess = self.assess
        evaluation.api_key = self.api_key
        evaluation.refresh_token = self.refresh_token
        evaluation.local_id = self.local_id
        evaluation.token_id = self.token_id

        if self.number != 0:
            evaluation.coexistence = self.number
        else:
            evaluation.coexistence = self.coexistence

        evaluation.punctuality = self.punctuality
        evaluation.efficiency = self.number
        evaluation.efficiency = self.efficiency
        evaluation.scale = self.scale
        screen_manager.current = 'Evaluation'

    def replace_star(self, numb, *args):
        print(numb)

        if numb == 1:
            # deswativar estrela 5
            self.ids.number_five.icon = 'star-outline'
            self.ids.number_five.icon_color = 'black'

            # desativar estrela 4
            self.ids.number_four.icon = 'star-outline'
            self.ids.number_four.icon_color = 'black'

            # desativar estrela 3
            self.ids.number_three.icon = 'star-outline'
            self.ids.number_three.icon_color = 'black'

            # desativar estrela 2
            self.ids.number_two.icon = 'star-outline'
            self.ids.number_two.icon_color = 'black'

            # Ativar a estrela 1
            self.ids.number_one.icon = 'star'
            self.ids.number_one.icon_color = 'yellow'
            self.update_component(1)

        if numb == 2:
            # ativar a estrela 1
            self.ids.number_one.icon = 'star'
            self.ids.number_one.icon_color = 'yellow'

            # ativar a estrela 2
            self.ids.number_two.icon = 'star'
            self.ids.number_two.icon_color = 'yellow'

            # desativar estrela 3
            self.ids.number_three.icon = 'star-outline'
            self.ids.number_three.icon_color = 'black'

            # desativar estrela 4
            self.ids.number_four.icon = 'star-outline'
            self.ids.number_four.icon_color = 'black'

            # deswativar estrela 5
            self.ids.number_five.icon = 'star-outline'
            self.ids.number_five.icon_color = 'black'
            self.update_component(2)

        if numb == 3:
            # ativar a estrela 1
            self.ids.number_one.icon = 'star'
            self.ids.number_one.icon_color = 'yellow'

            # ativar a estrela 2
            self.ids.number_two.icon = 'star'
            self.ids.number_two.icon_color = 'yellow'

            # ativar a estrela 3
            self.ids.number_three.icon = 'star'
            self.ids.number_three.icon_color = 'yellow'

            # desativar estrela 4
            self.ids.number_four.icon = 'star-outline'
            self.ids.number_four.icon_color = 'black'

            # deswativar estrela 5
            self.ids.number_five.icon = 'star-outline'
            self.ids.number_five.icon_color = 'black'
            self.update_component(3)

        if numb == 4:
            # ativar a estrela 1
            self.ids.number_one.icon = 'star'
            self.ids.number_one.icon_color = 'yellow'

            # ativar a estrela 2
            self.ids.number_two.icon = 'star'
            self.ids.number_two.icon_color = 'yellow'

            # ativar a estrela 3
            self.ids.number_three.icon = 'star'
            self.ids.number_three.icon_color = 'yellow'

            # ativar a estrela 4
            self.ids.number_four.icon = 'star'
            self.ids.number_four.icon_color = 'yellow'

            # deswativar estrela 5
            self.ids.number_five.icon = 'star-outline'
            self.ids.number_five.icon_color = 'black'
            self.update_component(4)

        if numb == 5:
            # ativar a estrela 1
            self.ids.number_one.icon = 'star'
            self.ids.number_one.icon_color = 'yellow'

            # ativar a estrela 2
            self.ids.number_two.icon = 'star'
            self.ids.number_two.icon_color = 'yellow'

            # ativar a estrela 3
            self.ids.number_three.icon = 'star'
            self.ids.number_three.icon_color = 'yellow'

            # ativar a estrela 4
            self.ids.number_four.icon = 'star'
            self.ids.number_four.icon_color = 'yellow'

            # ativar a estrela 5
            self.ids.number_five.icon = 'star'
            self.ids.number_five.icon_color = 'yellow'

            self.update_component(5)

    def step_one(self):
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.key}.json?auth={self.token_id}'
        self.numb = 0 
        # Verificar qual e o icone que está ativado para o numero de estrelas
        if self.ids.number_five.icon == 'star':
            self.number = 5

        elif self.ids.number_four.icon == 'star' and self.ids.number_five.icon != 'star':
            self.number = 4

        elif self.ids.number_three.icon == 'star' and self.ids.number_four.icon != 'star' and self.ids.number_five.icon != 'star':
            self.number = 3

        elif self.ids.number_two.icon == 'star' and self.ids.number_three.icon != 'star' and self.ids.number_four.icon != 'star' and self.ids.number_five.icon != 'star':
            self.number = 2

        else:
            self.number = 1

        print(self.number)
        data = {
            "coexistence": self.number,
            "contractor": self.local_id  # o uid do contratante logado
        }

        UrlRequest(
            url,
            method='PATCH',
            req_body=json.dumps(data),
            req_headers={'Content-Type': 'application/json'},
            on_error=self.error,
            on_failure=self.error,
            on_success=self.step_four
        )


    def step_four(self, req, result, *args):
        print(result)
        self.back_evaluation()
    
    def error(self, req, result):
        print('O error é: ', result)