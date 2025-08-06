import ast
import json
from ast import literal_eval
from datetime import datetime

from babel.dates import format_date
from babel.numbers import format_currency
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty, NumericProperty, get_color_from_hex
from kivy.uix.screenmanager import SlideTransition
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import MDDialog, MDDialogIcon, MDDialogHeadlineText, MDDialogSupportingText, \
    MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.divider import MDDivider
from kivymd.uix.list import MDListItem, MDListItemHeadlineText, MDListItemLeadingIcon, MDListItemSupportingText
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.textfield import MDTextField


class ReportBricklayer(MDScreen):
    avatar = StringProperty('https://res.cloudinary.com/dsmgwupky/image/upload/v1742170012/Helem.jpg')
    valleys = StringProperty("[]")
    key = StringProperty()
    day = StringProperty()
    confirm_payments = StringProperty()
    remainder = StringProperty()
    employee_name = StringProperty('Helem')
    function = StringProperty('Bombeiro')
    tot = NumericProperty(0)
    salary = NumericProperty()
    two_sala = NumericProperty()
    method_salary = StringProperty()
    scale = StringProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textfield = MDTextField()
        self.textfield.input_filter = "float"
        self.textfield.helper_text = "Digite aqui"
        self.textfield.helper_text_mode = "persistent"
        self.ids['text_field'] = self.textfield

        self.dialog = MDDialog()

        # ----------------------------Icon-----------------------------
        icon = MDDialogIcon(
            icon="refresh",
        )

        # -----------------------Headline text-------------------------
        headline = MDDialogHeadlineText(
            text="Adicionar vale",
        )

        # -----------------------Supporting text-----------------------
        supporting = MDDialogSupportingText(
            text="Digite o valor do vale pego pelo funcionario no campo abaixo",
        )

        # -----------------------Custom content------------------------
        container = MDDialogContentContainer(
            MDDivider(),
            self.textfield,
            MDDivider(),
            orientation="vertical",
        )

        # ---------------------Button container------------------------
        container_two = MDDialogButtonContainer(
            Widget(),
            MDButton(
                MDButtonText(text="Cancelar"),
                style="text",
                focus_behavior=False,
                on_release=lambda x: self.dialog.dismiss(),
            ),
            MDButton(
                MDButtonText(text="Adicionar"),
                style="text",
                focus_behavior=False,
                on_release=lambda x: self.add_valley()
            ),
            spacing="8dp",
        )

        # Add widgets to dialog
        self.dialog.add_widget(icon)
        self.dialog.add_widget(headline)
        self.dialog.add_widget(supporting)
        self.dialog.add_widget(container)
        self.dialog.add_widget(container_two)
        self.two_sala = self.salary

    def show_snackbar(self) -> None:
        """Exibe um Snackbar informativo."""
        self.dialog.dismiss()
        MDSnackbar(
            MDSnackbarText(
                text="Salario insuficiente para cobrir o vale",
                theme_text_color='Custom',
                text_color='black',
                bold=True
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            halign='center',
            size_hint_x=0.8,
            theme_bg_color='Custom',
            background_color=get_color_from_hex('#F3DE8A')
        ).open()

    def on_enter(self, *args):
        print('Confirmações de pagamento aqui: ', self.confirm_payments)

        # fazendo a logica de bloquear o botão o pagamento foi confirmado para esté periodo
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
                    print('Achei a confirmação')
            if have:
                print('Foi confirmado o pagamento')
                self.ids.button_valley.disabled = True
                self.ids.restart_card.disabled = True
                for child in self.ids.button_valley.children:
                    child.disabled = True

                """Exibe um Snackbar informativo."""
                MDSnackbar(
                    MDSnackbarText(
                        text="Aguarde novo periodo para inserir vales",
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
                self.ids.button_valley.disabled = False
                self.ids.restart_card.disabled = False
                for child in self.ids.button_valley.children:
                    child.disabled = False

        else:
            """Significa que pode confirmar ja que a lista de confirmações está nula"""
            self.ids.button_valley.disabled = False
            self.ids.restart_card.disabled = False
            for child in self.ids.button_valley.children:
                child.disabled = False

        # Limpar widgets existentes antes de carregar novos
        self.ids.valleys.clear_widgets()
        self.load_valleys()
        if self.method_salary not in 'Empreita':
            self.ids.remain.text = f'Salario total: {self.salary}'
            self.ids.init.text = f'Escala de trabalho: {self.scale}'
        else:
            self.ids.init.text = f'Prazo inicial: {self.day}'
            self.ids.remain.text = f'Salario total: {self.salary}'

    def numb_week(self):
        date = datetime.today()
        first_day = date.replace(day=1)
        dom = first_day.weekday()  # dia da semana do primeiro dia do mês
        adjusted_day = date.day + dom
        return int((adjusted_day - 1) / 7) + 1

    def get_valleys_dict(self):
        """Método auxiliar para converter a string valleys em um dicionário"""
        try:
            if not self.valleys or self.valleys == "None":
                return []
            valleys_dict = literal_eval(self.valleys)
            # Verificar se o resultado é realmente um dicionário
            if not isinstance(valleys_dict, list):
                print(f"Warning: valleys não é uma lista: {self.valleys}")
                return {}
            return valleys_dict
        except (ValueError, SyntaxError) as e:
            print(f"Erro ao converter valleys para dicionário: {e}, valor: {self.valleys}")
            return {}

    def load_valleys(self):
        valleys = ast.literal_eval(self.valleys)
        total = 0

        if self.valleys:
            for valley in valleys:
                valor_formatado = format_currency(float(valley['value']), 'BRL', locale='pt_BR')
                try:
                    valley_value = f"{format_currency(float(valley['value']), 'BRL', locale='pt_BR')}"
                    total += float(valley['value'])
                    item = MDListItem(
                        MDListItemLeadingIcon(
                            icon='currency-usd',
                        ),
                        MDListItemHeadlineText(
                            text=f'{valley_value}'
                        ),
                        MDListItemSupportingText(
                            text=f"retirado em {valley['data']}"
                        )
                    )
                    self.ids.valleys.add_widget(item)
                except (ValueError, TypeError) as e:
                    print(f"Erro ao processar vale: {e}, data: {valley['data']}, valor: {valley['value']}")

            self.tot = total
            self.ids.tot.text = f'Total: R${total}'

    def create_valleys(self, req, result):
        total = 0
        print(result)
        for data, valley in result.items():
            try:
                valley_value = f"{format_currency(int(valley['value']), 'BRL', locale='pt_BR')}"
                total += int(valley)
                item = MDListItem(
                    MDListItemLeadingIcon(
                        icon='currency-usd',
                    ),
                    MDListItemHeadlineText(
                        text=f'{valley_value}'
                    ),
                    MDListItemSupportingText(
                        text=f'retirado em {data}'
                    )
                )
                self.ids.valleys.add_widget(item)
            except (ValueError, TypeError) as e:
                print(f"Erro ao processar vale: {e}, data: {data}, valor: {valley}")

        self.tot = total
        self.ids.tot.text = f'Total: R${total}'

    def show_dialog(self):
        # Limpar o campo de texto antes de abrir o diálogo
        self.ids.text_field.text = ''
        self.dialog.open()

    def add_valley(self):
        # Verificar se o campo de texto está vazio
        if not self.ids.text_field.text:
            return

        try:
            # Obter o valor do vale como inteiro
            valley = int(self.ids.text_field.text)
            print('O valor do vale é {}'.format(valley))

            # Verificar se adicionar esse vale ultrapassaria o salário
            # Se o total atual + o novo vale for maior que o salário, mostrar mensagem de erro
            print(self.tot + valley)
            if (valley) > int(self.salary):
                self.show_snackbar()
            else:

                today = datetime.today().strftime('%d/%m/%Y')  # Adicionando hora para evitar colisões
                valley_value = f"{format_currency(float(valley), 'BRL', locale='pt_BR')}"
                item = MDListItem(
                    MDListItemLeadingIcon(
                        icon='currency-usd',
                    ),
                    MDListItemHeadlineText(
                        text=f'{valley_value}'
                    ),
                    MDListItemSupportingText(
                        text=f'retirado em {today}'
                    )
                )
                self.ids.valleys.add_widget(item)

                # Atualizar o total
                self.tot += valley
                self.ids.tot.text = f'Total: R${self.tot}'

                self.salary = int(self.salary) - valley
                self.dialog.dismiss()
                # Enviar os dados atualizados para o Firebase
                self.upload_firebase()

        except ValueError:
            print("Valor inválido. Digite um número inteiro.")

    def week_of_month(self, data=None):
        if data is None:
            data = datetime.today()

        primeiro_dia = data.replace(day=1)
        ajuste = (primeiro_dia.weekday() + 1) % 7  # segunda=0 ... domingo=6
        return ((data.day + ajuste - 1) // 7) + 1

    def upload_firebase(self):
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.key}/.json'

        UrlRequest(
            url,
            on_success=self.add_valleys
        )

    def add_valleys(self, req, result):
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.key}/.json'
        valleys = ast.literal_eval(result['valleys'])
        today = datetime.today().strftime('%d/%m/%Y')

        data = {
            'data': f"{today}",
            'value': f"{self.ids.text_field.text}",

            }
        valleys.append(data)
        data = {
            'valleys': f"{valleys}",
            'tot': f"{self.tot}"
        }
        self.valleys = f"{valleys}"
        valleys.append(data)
        UrlRequest(
            url,
            method='PATCH',
            on_success=self.final_upload,
            on_error=self.error,
            req_body=json.dumps(data)
        )

    def error(self, instance, erro):
        print(f"Erro ao enviar dados para o Firebase: {erro}")

    def cancel(self):
        app = MDApp.get_running_app()
        screenmanager = app.root
        e = screenmanager.get_screen('Evaluation')
        e.valleys = self.valleys
        e.tot = self.tot
        self.tot = 0
        self.ids.valleys.clear_widgets()
        screenmanager.transition = SlideTransition(direction='right')
        screenmanager.current = 'Evaluation'

    def final_upload(self, instance, result):
        print(f"Dados enviados com sucesso: {result}")

    def restart_firebase(self):
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.key}/.json'
        json_data = {
            'tot': 0,
            'valleys': "[]"
        }
        UrlRequest(
            url,
            method='PATCH',
            on_success=self.final_restart,
            on_error=self.error,
            req_body=json.dumps(json_data)
        )

    def final_restart(self, instance, result):
        self.ids.valleys.clear_widgets()
        self.tot = 0
        self.valleys = "[]"
        self.salary = self.two_sala
        self.ids.tot.text = f'Total: R$0'
        self.dont = 'Sim'
        app = MDApp.get_running_app()
        screenmanager = app.root
        e = screenmanager.get_screen('Evaluation')
        e.valleys = "[]"
        e.tot = 0
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'Evaluation'
