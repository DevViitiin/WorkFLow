import ast

from babel.numbers import format_currency
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.screenmanager import SlideTransition
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen


class ViewPaymentCompleted(MDScreen):
    method_salary = StringProperty('Semanal')
    name_employee = StringProperty('Shinomiya')
    date = StringProperty('17/04/2025')
    salary_completed = NumericProperty(1500)
    salary_discounted = NumericProperty(1380)
    numb = NumericProperty(3)
    valleys = StringProperty("[{'data': '16/04/2025', 'value': '120'}]")

    def on_enter(self):
        """
        Inicializa a tela de pagamento concluído carregando o layout principal
        e as informações necessárias quando a tela é exibida.
        """
        self.ids.valleys.clear_widgets()
        box_principal = MDBoxLayout(
            orientation='horizontal',
            theme_bg_color='Custom',
            md_bg_color='white',
            size_hint_x=1,
            size_hint_y=None,
            pos_hint={'center_x': 0.5},
            height=60
        )
        second_box = MDBoxLayout(
            theme_bg_color='Custom',
            halign=[10, 0, 0, 0]
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
        self.load_employee_info()
        self.load_advances()

    def load_employee_info(self):
        """
        Carrega e exibe as informações do funcionário na tela,
        incluindo nome, data, método de pagamento e valores salariais.
        """
        # Data ----------------------------------------
        if self.method_salary in ('Semanal', 'Diaria'):
            self.ids.option.text = 'Semana'
            self.ids.month.text = f'{self.numb}'

        self.ids.day.text = f"{self.date[0:2]}"
        print('Dia do mês', self.date[0:2])

        # Nome ----------------------------------------
        self.ids.name.text = f'{self.name_employee}'

        # Salario
        self.ids.gross_salary.text = f"{format_currency(self.salary_completed, 'BRL', locale='pt_BR')}"
        self.ids.method.text = f'{self.method_salary}'
        self.ids.remainder.text = f"{format_currency(self.salary_discounted, 'BRL', locale='pt_BR')}"

    def load_advances(self):
        """
        Carrega a lista de adiantamentos (vales) do funcionário
        e cria os elementos visuais correspondentes.
        """
        valleys = ast.literal_eval(self.valleys)
        for advance in valleys:
            print(advance)
            self.create_advance_item(advance['value'], [advance['data']])

    def create_advance_item(self, value, redeemed_date):
        """
        Cria um item visual para representar um adiantamento (vale) na interface.

        Args:
            value (float): Valor do adiantamento
            redeemed_date (list): Lista com a data do adiantamento
        """
        # Layout principal
        main_box = MDBoxLayout(
            orientation='horizontal',
            theme_bg_color='Custom',
            md_bg_color='white',
            size_hint_x=1,
            size_hint_y=0.5,
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
            md_bg_color='white'
        )

        right_relative = MDRelativeLayout()

        valor_label = MDLabel(
            text=f'- {format_currency(value, "BRL", locale="pt_BR")}',
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

    def return_to_review(self):
        """
        Retorna para a tela de revisão (ReviewScreen) com uma
        transição deslizante para a esquerda.
        """
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'ReviewScreen'