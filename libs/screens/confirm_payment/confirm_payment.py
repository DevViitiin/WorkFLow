import ast
import json
from datetime import datetime

from babel.dates import format_date
from babel.numbers import format_currency
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, get_color_from_hex, Clock
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText


class ConfirmPayment(MDScreen):
    method_salary = StringProperty()
    name_employee = StringProperty()
    tot = NumericProperty()
    valleys = StringProperty()
    salary = NumericProperty()
    confirm_payments = StringProperty()
    salary_completed = NumericProperty()
    key = StringProperty()
    request_payment = StringProperty()

    def on_enter(self):
        print('Pagamentos confirmados: ', self.confirm_payments)
        print('Os respectivos salario são: ', f'[{self.salary}, {self.salary_completed}]')
        self.ids.valleys.clear_widgets()
        value = format_currency(self.salary_completed, 'BRL', locale='pt_BR')
        card = self.criar_saldo_bruto_box('Salario bruto', f"{value}")
        self.ids.valleys.add_widget(card)

        self.valley()
        self.info_employee()

        test = self.already_paid_this_period(ast.literal_eval(self.confirm_payments), self.method_salary)
        print(test)
        data = datetime.today()
        month = format_date(data, "MMMM", locale='pt_BR').capitalize()
        numb = 0
        if self.method_salary in ('Diaria', 'Semanal'):
            numb = self.numb_week()
        else:
            numb = datetime.today().month

        print('Numero do mes ou semana :   ', numb)
        print('Mes: ', month)
        have = []
        if self.confirm_payments:
            """Significa que a lista de pagamentos confirmados pelo contratante
               Não está vazia"""
            for confirm in ast.literal_eval(self.confirm_payments):
                print(confirm)
                if confirm['numb'] == numb and confirm['Month'] == month:
                    have.append('yes')
            if have:
                print('Foi confirmado o pagamento')
                self.ids.button.md_bg_color = get_color_from_hex('#0197F6')
                self.ids.label_button.text = 'Confirmação enviada'
                self.ids.button.disabled = True
                """Exibe um Snackbar informativo."""
                MDSnackbar(
                    MDSnackbarText(
                        text="Aguarde novo periodo para outra confirmação",
                        theme_text_color='Custom',
                        text_color='black',
                        pos_hint={'center_x': 0.5, 'center_y': 0.5},
                        halign='center',
                        bold=True
                    ),
                    y=dp(24),
                    pos_hint={"center_x": 0.5},
                    halign='center',
                    size_hint_x=0.9,
                    theme_bg_color='Custom',
                    background_color=get_color_from_hex('#41EAD4')
                ).open()
            else:
                self.ids.button.disabled = False
                print('O pagamento foi confirmado')
        else:
            """Significa que pode confirmar ja que a lista de confirmações está nula"""
            self.ids.button.disabled = False
            print('O pagamento foi confirmado')


    def week_of_month(self, data=None):
        if data is None:
            data = datetime.today()

        primeiro_dia = data.replace(day=1)
        ajuste = (primeiro_dia.weekday() + 1) % 7  # segunda=0 ... domingo=6
        return ((data.day + ajuste - 1) // 7) + 1

    def already_paid_this_period(self, valleys: list, method_salary: str) -> bool:
        """
        Verifica se o último pagamento registrado está no mesmo período atual
        (mensal, semanal ou diário), baseado no método de pagamento.

        Parâmetros:
        - valleys: lista de pagamentos (cada item é um dicionário com pelo menos a chave 'data' no formato "DD/MM/YYYY")
        - method_salary: string indicando o tipo de pagamento ('Mensal', 'Semanal', 'Diaria')

        Retorna:
        - True se já há pagamento neste período
        - False se pode prosseguir com novo pagamento
        """
        if not valleys:
            return False  # Nenhum pagamento ainda

        last_payment = valleys[-1]
        last_date_str = last_payment.get("data")

        if not last_date_str:
            return False

        try:
            last_date = datetime.strptime(last_date_str, "%d/%m/%Y")
        except ValueError:
            return False  # Data inválida

        today = datetime.today()

        if method_salary == "Mensal":
            return last_date.year == today.year and last_date.month == today.month
        elif method_salary == "Semanal":
            return last_date.isocalendar()[1] == today.isocalendar()[1] and last_date.year == today.year
        elif method_salary == "Diaria":
            return last_date.date() == today.date()

        return False  # Caso o tipo de salário seja inválido

    def criar_saldo_bruto_box(self, texto_label='Salario Bruto', valor='- R$ 180,00'):
        mdbox = MDBoxLayout(
            orientation='horizontal',
            theme_bg_color='Custom',
            md_bg_color='white',
            size_hint=(1, None),
            height=dp(60),
            pos_hint={'center_x': 0.5},
        )

        # Primeiro bloco com o texto "Salario Bruto"
        esquerda = MDBoxLayout(
            theme_bg_color='Custom',
            padding=(dp(10), 0, 0, 0)
        )
        relative_esquerda = MDRelativeLayout()
        label_texto = MDLabel(
            text=texto_label,
            theme_text_color='Custom',
            text_color='grey',
            pos_hint={'center_x': 0.6, 'center_y': 0.5},
            halign='left'
        )
        relative_esquerda.add_widget(label_texto)
        esquerda.add_widget(relative_esquerda)

        # Segundo bloco com o valor
        direita = MDBoxLayout(
            orientation='vertical',
            theme_bg_color='Custom',
            md_bg_color='white',
        )
        relative_direita = MDRelativeLayout()
        label_valor = MDLabel(
            text=valor,
            theme_text_color='Custom',
            text_color='red',
            font_size='14sp',
            pos_hint={'center_x': 0.4, 'center_y': 0.5},
            halign='right'
        )
        relative_direita.add_widget(label_valor)
        direita.add_widget(relative_direita)

        # Adiciona os dois blocos ao layout principal
        mdbox.add_widget(esquerda)
        mdbox.add_widget(direita)

        return mdbox

    def confirmar_pagamento(self):
        valleys = [{'data': '16/04/2025', 'value': '1380.0', 'numb': 3, 'method': 'Semanal'}]  # Exemplo de dados
        metodo_pagamento = 'Semanal'  # Método de pagamento, pode ser 'Mensal', 'Semanal' ou 'Diaria'

        if self.already_paid_this_period(valleys, metodo_pagamento):
            MDSnackbar(
                MDSnackbarText(
                    text="Pagamento já confirmado neste período",
                    theme_text_color='Custom',
                    text_color='black',
                    bold=True
                ),
                y=dp(24),
                pos_hint={"center_x": 0.5},
                halign='center',
                size_hint_x=0.9,
                theme_bg_color='Custom',
                background_color=get_color_from_hex('#FF6F61')
            ).open()
        else:
            # Aqui você segue com a lógica de confirmação do pagamento
            self.get_valleys()

    def info_employee(self):
        self.ids.method.text = str(self.method_salary)
        if self.method_salary in ('Diaria', 'Semanal'):
            self.ids.option.text = 'Semana'
            numb_week = self.numb_week()
            self.ids.month.text = f"{numb_week}"
        else:
            self.ids.option.text = 'Més'
            numb_month = datetime.today().month
            self.ids.month.text = f"{numb_month}"

        day = datetime.today().day
        month = datetime.today().month
        self.ids.day.text = f"{day}"
        self.ids.name.text = f"{self.name_employee}"
        discounted = self.salary_completed - self.tot
        print(discounted)
        # Display the original salary (before deductions)
        try:
            self.ids.gross_salary.text = f"{format_currency(discounted, 'BRL', locale='pt_BR', format='#,##0.00')}"

        except:
            pass

    def valley(self):
        data = ast.literal_eval(self.valleys)
        discounted_salary = float(self.tot)
        salary = self.salary_completed

        # Calculate the remainder (gross salary minus valleys)
        remainder = salary - discounted_salary

        # Format the remainder as currency
        formatted_remainder = format_currency(remainder, 'BRL', locale='pt_BR', format='#,##0.00')
        self.ids.remainder.text = f"{formatted_remainder}"

        # Keep track of the total deduction
        self.tot = discounted_salary

        # Display each valley entry
        for valley in data:
            self.create_valleys(str(valley['value']), valley['data'])

    def create_valleys(self, value, redeemed_date):
        # Layout principal
        main_box = MDBoxLayout(
            orientation='horizontal',
            theme_bg_color='Custom',
            md_bg_color='white',
            size_hint_x=1,
            size_hint_y=None,
            height=60,
            pos_hint={'center_x': 0.5}
        )

        # Primeiro box layout (esquerda)
        left_box = MDBoxLayout(
            theme_bg_color='Custom',
            halign=[10, 0, 0, 0]
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
            md_bg_color='white',
            spacing=5
        )

        right_relative = MDRelativeLayout()
        text = f"R${format_currency(value, 'BRL', locale='pt_BR', format='#,##0.00')}"
        valor_label = MDLabel(
            text=f'- {text}',
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
            pos_hint={'center_x': 0.4, 'center_y': 0.35},
            halign='right'
        )

        right_relative.add_widget(valor_label)
        right_relative.add_widget(data_label)
        right_box.add_widget(right_relative)

        # Adicionando os boxes ao layout principal
        main_box.add_widget(left_box)
        main_box.add_widget(right_box)
        self.ids.valleys.add_widget(main_box)

    def get_valleys(self):
        print(type(self.request_payment))
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.key}/.json'
        UrlRequest(
            url,
            on_success=self.confirm_payment
        )

    def numb_week(self):
        date = datetime.today()
        first_day = date.replace(day=1)
        dom = first_day.weekday()  # dia da semana do primeiro dia do mês
        adjusted_day = date.day + dom
        return int((adjusted_day - 1) / 7) + 1

    def confirm_payment(self, req, result):
        valleys = ast.literal_eval(result['confirm_payments'])
        today = datetime.today().strftime('%d/%m/%Y')
        numb_month = datetime.today().month
        told = datetime.today()
        name_month = format_date(told, "LLLL", locale='pt_BR')
        numb_week = self.numb_week()
        data = {}
        if self.method_salary in ('Semanal', 'Diaria'):

            data = {
                'data': f"{today}",
                'value': f"{self.salary}",
                'salary_completed': f"{self.salary_completed}",
                'numb': numb_week,
                'Month': f'{name_month.capitalize()}',
                'method': f'{self.method_salary}',
                'valleys': f"{self.valleys}"

            }
        else:
            data = {
                'data': f"{today}",
                'value': f"{self.salary}",
                'salary_completed': f"{self.salary_completed}",
                'numb': numb_month,  # Fixed to use month number for monthly payments
                'Month': f'{name_month.capitalize()}',
                'method': f'{self.method_salary}',
                'valleys': f"{self.valleys}"

            }
        valleys.append(data)
        data = {
            'confirm_payments': f"{valleys}",
            'request_payment': 'True',
        }
        self.request_payment = 'True'
        UrlRequest(
            url=f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.key}/.json',
            method='PATCH',
            req_body=json.dumps(data),
            on_success=self.completed
        )

    def completed(self, req, result):
        """Exibe um Snackbar informativo."""
        MDSnackbar(
            MDSnackbarText(
                text="Confirmação enviada",
                theme_text_color='Custom',
                text_color='black',
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                halign='center',
                bold=True
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            halign='center',
            size_hint_x=0.65,
            theme_bg_color='Custom',
            background_color=get_color_from_hex('#41EAD4')
        ).open()
        self.confirm_payments = result['confirm_payments']
        Clock.schedule_once(self.return_screen, 1.5)

    def return_screen(self, *args):
        app = MDApp.get_running_app()
        screenmanager = app.root
        evaluation = screenmanager.get_screen('Evaluation')
        evaluation.request_payment = self.request_payment
        evaluation.confirm_payments = self.confirm_payments
        screenmanager.transition = SlideTransition(direction='left')
        screenmanager.current = 'Evaluation'

    def return_(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'Evaluation'