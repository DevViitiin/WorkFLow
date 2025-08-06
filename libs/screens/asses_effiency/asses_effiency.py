import json

from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty, NumericProperty, get_color_from_hex
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen


class AssesEffiency(MDScreen):
    employee_name = StringProperty()
    employee_function = StringProperty()
    avatar = StringProperty()
    contractor = StringProperty()
    method_salary = StringProperty()
    salary = StringProperty()
    assess = StringProperty()
    coexistence = NumericProperty()
    punctuality = NumericProperty()
    efficiency = NumericProperty()
    scale = StringProperty()
    days_work = NumericProperty()
    number = 0

    # Definindo as variações de efficiencia
    ASSESSMENT_LEVELS = {"efficiency": {
            1: {"text": "Ineficiente(a)", "color": "#FF0000"},
            2: {"text": "Baixa Eficiência(a)", "color": "#E06666"},
            3: {"text": "Razoável(a)", "color": "#808080"},
            4: {"text": "Eficiente(a)", "color": "#008000"},
            5: {"text": "Altamente Eficiente(a)", "color": "#0044CC"}
        }}

    def update_component(self, indice):
        """Atualiza um componente específico de avaliação"""

        self.ids.asses.text = self.ASSESSMENT_LEVELS['efficiency'][indice]['text']
        self.ids.asses.text_color = get_color_from_hex(self.ASSESSMENT_LEVELS['efficiency'][indice]['color'])

    def back_evaluation(self):
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
        evaluation.coexistence = self.coexistence
        evaluation.punctuality = self.punctuality

        if self.number != 0:
            evaluation.efficiency = self.number
        else:
            evaluation.efficiency = self.efficiency

        evaluation.scale = self.scale
        screen_manager.current = 'Evaluation'

    def replace_star(self, numb):
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
        url = 'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios'

        UrlRequest(
            f'{url}/.json',
            on_success=self.step_two
        )

    def step_two(self, req, result):

        for item, value in result.items():
            if value['Name'] == self.employee_name:
                print(item)
                self.step_three(item)
                break

    def step_three(self, item):
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{item}/.json'
        self.numb = 0
        # Verificar qual e o icone que está ativado para o numero de estrelas
        if self.ids.number_five.icon == 'star':
            self.number = 5
            print('cinco')

        elif self.ids.number_four.icon == 'star' and self.ids.number_five.icon != 'star':
            print('rsrs')
            self.number = 4

        elif self.ids.number_three.icon == 'star' and self.ids.number_four.icon != 'star' and self.ids.number_five.icon != 'star':
            self.number = 3

        elif self.ids.number_two.icon == 'star' and self.ids.number_three.icon != 'star' and self.ids.number_four.icon != 'star' and self.ids.number_five.icon != 'star':
            self.number = 2

        else:
            self.number = 1

        print(self.numb)
        date = {'effiency': self.number}

        UrlRequest(
            url,
            method='PATCH',
            req_body=json.dumps(date),
            on_success=self.step_four
        )

    def step_four(self, req, result):
        self.back_evaluation()