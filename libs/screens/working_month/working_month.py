import ast
import json
from datetime import datetime

from babel.dates import format_date
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.screenmanager import SlideTransition
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
from kivy.metrics import dp
from kivymd.uix.snackbar import MDSnackbarText, MDSnackbar


class PizzaWidget(Widget):
    def __init__(self, dias_trabalhados=1, dias_falta=0, total_dias=0, **kwargs):
        super().__init__(**kwargs)
        self.dias_trabalhados = dias_trabalhados
        self.dias_falta = dias_falta
        self.total_dias = total_dias
        self.calcular_porcentagens()
        self.bind(size=self.redraw_pizza)
        self.bind(pos=self.redraw_pizza)  # Redesenha quando a posição muda também

    def calcular_porcentagens(self):
        total_dias = self.total_dias
        if total_dias > 0:  # Previne divisão por zero
            self.freq_presenca = (self.dias_trabalhados / total_dias) * 100
        else:
            self.freq_presenca = 0
        self.freq_faltas = 100 - self.freq_presenca

    def redraw_pizza(self, *args):
        self.canvas.clear()
        self.draw_pizza()

    def draw_pizza(self):
        angulo_presenca = (self.freq_presenca / 100) * 360
        angulo_faltas = 360 - angulo_presenca

        with self.canvas:
            # Calcula o tamanho da pizza apropriadamente com base nas dimensões do widget
            pizza_size = min(self.width, self.height) * 0.8
            center_x = self.center_x - pizza_size / 12  # Centraliza a pizza horizontalmente
            center_y = self.center_y - pizza_size / 2  # Centraliza a pizza verticalmente

            # Desenha a parte verde (presença)
            Color(0, 0, 1, 1)  # Verde
            Ellipse(pos=(center_x, center_y), size=(pizza_size, pizza_size), angle_start=0, angle_end=angulo_presenca)

            # Desenha a parte vermelha (faltas)
            Color(234/255, 43/255, 31/255, 1)  # Vermelho
            Ellipse(pos=(center_x, center_y), size=(pizza_size, pizza_size), angle_start=angulo_presenca, angle_end=360)


class WorkingMonth(MDScreen):
    employee_name = StringProperty()
    contractor = StringProperty()
    key = StringProperty()
    confirm_payments = StringProperty()

    # Os dias que o funcionario trabalhou em cada semana
    work_days_week1 = StringProperty()
    work_days_week2 = StringProperty()
    work_days_week3 = StringProperty()
    work_days_week4 = StringProperty()

    # Quantos dias o funcionario trabalhou em cada semana
    week_1 = NumericProperty(4)
    week_2 = NumericProperty(2)
    week_3 = NumericProperty(3)
    week_4 = NumericProperty(5)

    scale = StringProperty()
    avatar = StringProperty()
    days_work = NumericProperty()
    cont_pizza = NumericProperty()

    def on_enter(self):
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
                self.ids.first_week.disabled = True
                self.ids.second_week.disabled = True
                self.ids.third_week.disabled = True
                self.ids.fourth_week.disabled = True
                self.ids.again.disabled = True

                """Exibe um Snackbar informativo."""
                MDSnackbar(
                    MDSnackbarText(
                        text="Aguarde novo periodo para inserir frequência",
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
                self.ids.first_week.disabled = False
                self.ids.second_week.disabled = False
                self.ids.third_week.disabled = False
                self.ids.fourth_week.disabled = False
                self.ids.again.disabled = False

        else:
            """Significa que pode confirmar ja que a lista de confirmações está nula"""
            self.ids.first_week.disabled = False
            self.ids.second_week.disabled = False
            self.ids.third_week.disabled = False
            self.ids.fourth_week.disabled = False
            self.ids.again.disabled = False

        print('A sua chave é {}'.format(self.key))
        print(self.employee_name, self.contractor, self.scale)
        print(self.employee_name, self.contractor, self.scale)
        self.cont_pizza += 1
        self.days_work = self.week_1 + self.week_2 + self.week_3 + self.week_4
        self.ids.graphic.clear_widgets()
        self.upload_graphic()
        self.upload_percenteges()

    def numb_week(self):
        date = datetime.today()
        first_day = date.replace(day=1)
        dom = first_day.weekday()  # dia da semana do primeiro dia do mês
        adjusted_day = date.day + dom
        return int((adjusted_day - 1) / 7) + 1

    def upload_percenteges(self):
        """Calcular a porcentagem de dias trabalhados de cada funcionario"""
        numb_days = 0
        if self.scale in '6x1':
            numb_days = 6
        elif self.scale in '5x2':
            numb_days = 20 / 4
        else:
            numb_days = 16 / 4

        freq_week1 = (self.week_1 / numb_days) * 100
        freq_week2 = (self.week_2 / numb_days) * 100
        freq_week3 = (self.week_3 / numb_days) * 100
        freq_week4 = (self.week_4 / numb_days) * 100
        print(freq_week3, freq_week4, freq_week2, freq_week1)
        self.ids.week_1.text = '{:.2f}%'.format(freq_week1)
        self.ids.progress_1.value = freq_week1
        self.ids.week_2.text = '{:.2f}%'.format(freq_week2)
        self.ids.progress_2.value = freq_week2
        self.ids.week_3.text = '{:.2f}%'.format(freq_week3)
        self.ids.progress_3.value = freq_week3
        self.ids.week_4.text = '{:.2f}%'.format(freq_week4)
        self.ids.progress_4.value = freq_week4

    def get_days_month(self):
        """Retorna quantos dias um mes possui"""
        import datetime
        from calendar import monthrange

        year = datetime.date.today().year
        month = datetime.date.today().month

        s, tot_day = monthrange(year, month)
        return tot_day

    def calculate_work_days(self, total_days, work_schedule):
        """ Calcular quantos dias o funcionario vai trabalhar de acordo com
        a escala de trabalho e o total de dias do mes

        :param total_days:
        :param work_schedule:
        :return: days_work
        """
        schedule_base_days = {
            '6x1': 26 if total_days == 24 else 24 if total_days == 30 else 24,
            '5x2': 20 if total_days == 31 else 20 if total_days == 30 else 20,
            'default': 16 if total_days == 31 else 16 if total_days == 30 else 16
        }

        # Return the calculated working days based on schedule
        return schedule_base_days.get(work_schedule, schedule_base_days['default'])

    def calcular_porcentagens(self):
        tot_day_work = self.calculate_work_days(self.get_days_month(), self.scale)
        print(tot_day_work)

        if tot_day_work > 0:  # Previne divisão por zero
            self.freq_presenca = (self.days_work / tot_day_work) * 100
        else:
            self.freq_presenca = 0
        self.freq_faltas = 100 - self.freq_presenca

    def upload_graphic(self):
        # Cria o widget do gráfico de pizza
        tot_day_work = self.calculate_work_days(self.get_days_month(), self.scale)
        pizza_widget = PizzaWidget(dias_trabalhados=self.days_work, dias_falta=22 - self.days_work, total_dias=tot_day_work)

        # Define tamanho fixo e desativa redimensionamento automático
        pizza_widget.size_hint = (None, None)
        pizza_widget.size = (dp(180), dp(180))  # Tamanho ajustado para melhores proporções

        # Centraliza o widget no layout
        pizza_widget.pos_hint = {'center_x': 0.3, 'center_y': 0.5}

        # Adiciona ao layout
        self.ids.graphic.add_widget(pizza_widget)
        # Calcular a porra das porcentagens
        self.calcular_porcentagens()

    def navigate_to_screen(self, screen_name, direction='left'):
        app = MDApp.get_running_app()
        root = app.root

        # Special case for the Evaluation screen
        if screen_name == 'Evaluation':
            target_screen = root.get_screen(screen_name)
            target_screen.work_days_week1 = self.work_days_week1
            target_screen.work_days_week2 = self.work_days_week2
            target_screen.work_days_week3 = self.work_days_week3
            target_screen.work_days_week4 = self.work_days_week4
            target_screen.week_1 = self.week_1
            target_screen.week_2 = self.week_2
            target_screen.week_3 = self.week_3
            target_screen.week_4 = self.week_4
        else:
            # For week screens
            target_screen = root.get_screen(screen_name)
            if screen_name in 'FirstWeek':
                target_screen.work_days_week1 = self.work_days_week1
            elif screen_name in 'SecondWeek':
                target_screen.work_days_week2 = self.work_days_week2
            elif screen_name in 'ThirdWeek':
                target_screen.work_days_week3 = self.work_days_week3
            else:
                target_screen.work_days_week4 = self.work_days_week4
            target_screen.key = self.key
            target_screen.scale = self.scale
            target_screen.employee_name = self.employee_name
            target_screen.contractor = self.contractor

        root.transition = SlideTransition(direction=direction)
        root.current = screen_name

    def cancel(self):
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.key}/.json'
        data = {
            'week_1': 0,
            'week_2': 0,
            'week_3': 0,
            'week_4': 0,
            'work_days_week1': '[]',
            'work_days_week2': '[]',
            'work_days_week3': '[]',
            'work_days_week4': '[]',
            'days_work': 0,
            'valleys': "{}",
            'tot': 0

        }

        UrlRequest(
            url,
            method='PATCH',
            on_success=self.success,
            req_body=json.dumps(data)
        )

    def success(self, instance, result):
        app = MDApp.get_running_app()
        screenmanager = app.root
        evaluation = screenmanager.get_screen('Evaluation')
        evaluation.week_1 = 0
        evaluation.tot = 0
        evaluation.valleys = "{}"
        evaluation.work_days_week1 = "[]"
        evaluation.week_2 = 0
        evaluation.work_days_week2 = "[]"
        evaluation.week_3 = 0
        evaluation.work_days_week3 = "[]"
        evaluation.week_4 = 0
        evaluation.work_days_week4 = "[]"
        evaluation.days_work = 0
        screenmanager.transition = SlideTransition(direction='right')
        screenmanager.current = 'Evaluation'

    def bye(self):
        app = MDApp.get_running_app()
        screenmanager = app.root
        evaluation = screenmanager.get_screen('Evaluation')
        evaluation.week_1 = self.week_1
        evaluation.work_days_week1 = self.work_days_week1
        evaluation.week_2 = self.week_2
        evaluation.work_days_week2 = self.work_days_week2
        evaluation.week_3 = self.week_3
        evaluation.work_days_week3 = self.work_days_week3
        evaluation.week_4 = self.week_4
        evaluation.work_days_week4 = self.work_days_week4
        screenmanager.transition = SlideTransition(direction='right')
        screenmanager.current = 'Evaluation'

    def back_evaluation(self):
        self.navigate_to_screen('Evaluation', 'right')

    def _next_first_week(self):
        self.navigate_to_screen('FirstWeek')

    def _next_second_week(self):
        self.navigate_to_screen('SecondWeek')

    def _next_third_week(self):
        self.navigate_to_screen('ThirdWeek')

    def _next_fourth_week(self):
        self.navigate_to_screen('FourthWeek')
