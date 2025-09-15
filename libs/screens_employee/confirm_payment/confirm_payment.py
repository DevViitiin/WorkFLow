import ast
import json
from babel.numbers import format_currency
from kivy.metrics import dp
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty, NumericProperty, Clock, get_color_from_hex
from kivy.uix.screenmanager import SlideTransition
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialogContentContainer, MDDialogSupportingText, MDDialog
from kivymd.uix.divider import MDDivider
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDListItemSupportingText, MDListItemLeadingIcon, MDListItem
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp


class ConfirmPaymentEmployee(MDScreen):
    token_id = StringProperty()
    local_id = StringProperty()
    refresh_token = StringProperty()
    api_key = StringProperty()
    method_salary = StringProperty()
    name_employee = StringProperty()
    date = StringProperty()
    salary_completed = NumericProperty()
    salary_discounted = NumericProperty()
    payments = StringProperty()
    confirm = StringProperty()
    key = StringProperty()
    numb = NumericProperty()
    email = StringProperty()
    telephone = StringProperty()
    valleys = StringProperty()
    FIREBASE_URL = 'https://obra-7ebd9-default-rtdb.firebaseio.com'

    def on_enter(self):
        print('Pagamentos confirmados: ', self.confirm)
        self.verific_token()
        self.event_token = Clock.schedule_interval(self.verific_token, 300)
        """ Carrega as informações principais"""
        self.ids.valleys.clear_widgets()
        box_principal = MDBoxLayout(
            orientation='horizontal',
            theme_bg_color='Custom',
            md_bg_color='white',
            size_hint_x=None,
            size_hint_y=None,
            width=350,
            pos_hint={'center_x': 0.5},
            height=60
        )
        second_box = MDBoxLayout(
            theme_bg_color='Custom',
            padding=[10, 0, 0, 0]
        )
        relative = MDRelativeLayout()
        label = MDLabel(
            text='Salario Bruto',
            theme_text_color='Custom',
            text_color='grey',
            pos_hint={'center_x': 0.6, 'center_y': 0.5},
            halign='left',

        )
        third_box = MDBoxLayout(
            orientation='vertical',
            theme_bg_color='Custom',
            md_bg_color='white'
        )
        second_relative = MDRelativeLayout()
        second_label = MDLabel(
            text='- R$ 180,00',
            theme_text_color='Custom',
            text_color='green',
            theme_font_size='Custom',
            font_size='14sp',
            pos_hint={'center_x': 0.4, 'center_y': 0.5},
            halign='right'
        )
        self.ids['gross_salary'] = second_label
        second_relative.add_widget(second_label)
        third_box.add_widget(second_relative)
        relative.add_widget(label)
        second_box.add_widget(relative)
        box_principal.add_widget(second_box)
        box_principal.add_widget(third_box)

        self.ids.valleys.add_widget(
            box_principal
        )
        self.info_employee()
        self.upload_valleys()

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

    def show_error(self, error_message):
        """Display an error message"""
        self.show_message(error_message, color='#FF0000')
        print(f"Error: {error_message}")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None

    def calling(self):
        self.show_loading_popup()
        # Simula um processo demorado
        Clock.schedule_once(self.process_calling, 30)  # chama depois de 2 segundos

    def process_calling(self, dt):
        # Depois que termina, fecha o popup
        self.hide_loading_popup()

    def show_loading_popup(self):
        if not self.dialog:
            self.dialog = MDDialog(
            MDDialogSupportingText(
                text="Estas são as informações de contato do seu contratante. Recomendamos que entre em contato para tratar e resolver a situação de forma adequada."
            ),

            MDDialogContentContainer(
                MDDivider(),
                MDListItem(
                    MDListItemLeadingIcon(
                        icon="gmail",
                    ),
                    MDListItemSupportingText(
                        text=f"{self.email}",
                    ),
                    theme_bg_color="Custom",
                    md_bg_color=self.theme_cls.transparentColor,
                ),
                MDListItem(
                    MDListItemLeadingIcon(
                        icon="phone-in-talk",
                    ),
                    MDListItemSupportingText(
                        text=f"{self.telephone}",
                    ),
                    theme_bg_color="Custom",
                    md_bg_color=self.theme_cls.transparentColor,
                ),
                MDDivider(),
                orientation="vertical",
            )
            )
        self.dialog.open()

    def hide_loading_popup(self):
        if self.dialog:
            self.disabled = False
            self.dialog.dismiss()

    def info_employee(self):
        """ Colocando as informações do funcionario na tela"""

        # Data ----------------------------------------
        if self.method_salary in ('Semanal', 'Diaria'):
            self.ids.option.text = 'Semana'
            self.ids.month.text = f'{self.numb}'
        else:
            self.ids.option = 'Mês'
            self.ids.month.text = f'{self.numb}'

        self.ids.day.text = f"{self.date[0:2]}"

        # Nome ----------------------------------------
        self.ids.name.text = f'{self.name_employee}'

        # Salario
        self.ids.gross_salary.text = f"{format_currency(self.salary_completed, 'BRL', locale='pt_BR')}"
        self.ids.method.text = f'{self.method_salary}'
        self.ids.remainder.text = f"{format_currency(self.salary_discounted, 'BRL', locale='pt_BR')}"

    def upload_valleys(self):
        valleys = ast.literal_eval(self.valleys)
        for valley in valleys:
            print(valley)
            self.create_valleys(valley['value'], [valley['data']])

    def create_valleys(self, value, redeemed_date):
        # Layout principal
        main_box = MDBoxLayout(
            orientation='horizontal',
            theme_bg_color='Custom',
            md_bg_color='white',
            size_hint_x=None,
            size_hint_y=None,
            width=350,
            height=60,
            pos_hint={'center_x': 0.5}
        )

        # Primeiro box layout (esquerda)
        left_box = MDBoxLayout(
            theme_bg_color='Custom',
            padding=[10, 0, 0, 0]
        )

        left_relative = MDRelativeLayout()

        left_label = MDLabel(
            text='Adiantamento',
            theme_text_color='Custom',
            text_color='grey',
            pos_hint={'center_x': 0.6, 'center_y': 0.5},
            halign='left'
        )

        left_relative.add_widget(left_label)
        left_box.add_widget(left_relative)

        # Segundo box layout (direita)
        right_box = MDBoxLayout(
            orientation='vertical',
            theme_bg_color='Custom',
            md_bg_color='white'
        )

        right_relative = MDRelativeLayout()

        valor_label = MDLabel(
            text=f"- {format_currency(value, 'BRL', locale='pt_BR')}",
            theme_text_color='Custom',
            text_color='red',
            theme_font_size='Custom',
            font_size='14sp',
            pos_hint={'center_x': 0.4, 'center_y': 0.65},
            halign='right'
        )

        data_label = MDLabel(
            text=f'{redeemed_date}',
            theme_text_color='Custom',
            text_color='grey',
            theme_font_size='Custom',
            font_size='12sp',
            pos_hint={'center_x': 0.4, 'center_y': 0.1},
            halign='right'
        )

        right_relative.add_widget(valor_label)
        right_relative.add_widget(data_label)
        right_box.add_widget(right_relative)

        # Adicionando os boxes ao layout principal
        main_box.add_widget(left_box)
        main_box.add_widget(right_box)
        self.ids.valleys.add_widget(main_box)

    def return_(self, *args):
        app = MDApp.get_running_app()
        screenmanager = app.root
        self.new_skills = []  # Limpa a lista de novas habilidades

        # Obtém a tela anterior e atualiza seus dados
        perfil = screenmanager.get_screen('ReviewScreen')
        perfil.token_id = self.token_id
        perfil.local_id = self.local_id
        perfil.api_key = self.api_key
        perfil.refresh_token = self.refresh_token
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'ReviewScreen'

    def confirm_payment(self):
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.local_id}/.json?auth={self.token_id}'
        payments = ast.literal_eval(self.payments)
        print(payments)
        data = {
            'data': f"{self.date}",
            'value': f'{self.salary_discounted}',
            'salary_completed': f'{self.salary_completed}',
            'numb': self.numb,
            'who': 'contractor',
            'Month': f'{self.month}',
            'method': f'{self.method_salary}',
            'valleys': f"{self.valleys}"
        }
        payments.append(data)
        data = {
            'payments': f"{payments}"
        }
        UrlRequest(
            url,
            req_body=json.dumps(data),
            on_success=self.finally_payment,
            method='PATCH'
        )

    def finally_payment(self, req, result):
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.local_id}/.json?auth={self.token_id}'
        UrlRequest(
            url,
            on_success=self.payment
        )

    def payment(self, req, result):
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.local_id}/.json?auth={self.token_id}'
        confirms = ast.literal_eval(result['confirm_payments'])
        confirms.remove(ast.literal_eval(self.confirm))
        data = {
            'confirm_payments': f'{confirms}'
        }
        UrlRequest(
            url,
            req_body=json.dumps(data),
            method='PATCH',
            on_success=self.finally_
        )

    def finally_(self, req, result, *args):
        app = MDApp.get_running_app()
        screenmanager = app.root
        self.new_skills = []  # Limpa a lista de novas habilidades

        # Obtém a tela anterior e atualiza seus dados
        perfil = screenmanager.get_screen('ReviewScreen')
        perfil.token_id = self.token_id
        perfil.local_id = self.local_id
        perfil.api_key = self.api_key
        perfil.refresh_token = self.refresh_token
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'ReviewScreen'

