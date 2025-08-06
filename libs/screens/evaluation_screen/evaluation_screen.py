import locale
from datetime import datetime
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.uix.screenmanager import SlideTransition
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen


class EvaluationScreen(MDScreen):
    employee_name = StringProperty("")
    employee_function = StringProperty("")
    avatar = StringProperty("")
    contractor = StringProperty("")
    method_salary = StringProperty("")
    salary = NumericProperty()
    assess = StringProperty("8.4")
    coexistence = NumericProperty(0)
    punctuality = NumericProperty(0)
    efficiency = NumericProperty(0)
    observations = StringProperty()
    ultimate = StringProperty()
    scale = StringProperty("")
    days_work = NumericProperty(0)
    key = StringProperty()
    day = StringProperty()
    valleys = StringProperty()
    confirm_payments = StringProperty()
    tot = NumericProperty()
    two_salary = salary
    remainder = ''
    limite = 0
    request_payment = StringProperty()
    money = NumericProperty()
    harv = NumericProperty()
    # Os dias que o funcionario trabalhou em cada semana
    work_days_week1 = StringProperty()
    work_days_week2 = StringProperty()
    work_days_week3 = StringProperty()
    work_days_week4 = StringProperty()

    # Quantidade de dias que cada semana contem
    week_1 = NumericProperty()
    week_2 = NumericProperty()
    week_3 = NumericProperty()
    week_4 = NumericProperty()
    s = ''

    # Dicionário para mapear escalas a dias úteis no mês
    SCALE_WORKDAYS = {
        "6x1": {"day": 6, "week": 6, "biweekly": 12, "month": 24},
        "5x2": {"day": 5, "week": 5, "biweekly": 10, "month": 20},
        "4x3": {"day": 4, "week": 4, "biweekly": 8, "month": 16}
    }

    # Dicionário para avaliações de funcionários
    ASSESSMENT_LEVELS = {
        "coexistence": {
            1: {"text": "Conflituoso(a)", "color": "#FF0000"},
            2: {"text": "Tolerável(a)", "color": "#E06666"},
            3: {"text": "Neutro(a)", "color": "#808080"},
            4: {"text": "Colaborativa(a)", "color": "#008000"},
            5: {"text": "Excelente(a)", "color": "#0044CC"}
        },
        "efficiency": {
            1: {"text": "Ineficiente(a)", "color": "#FF0000"},
            2: {"text": "Baixa Eficiência(a)", "color": "#E06666"},
            3: {"text": "Razoável(a)", "color": "#808080"},
            4: {"text": "Eficiente(a)", "color": "#008000"},
            5: {"text": "Altamente Eficiente(a)", "color": "#0044CC"}
        },
        "punctuality": {
            1: {"text": "Muito Atrasado(a)", "color": "#FF0000"},
            2: {"text": "Frequentemente Atrasado(a)", "color": "#E06666"},
            3: {"text": "Pontualidade Regular(a)", "color": "#808080"},
            4: {"text": "Pontual(a)", "color": "#008000"},
            5: {"text": "Sempre Pontual/Adiantado(a)", "color": "#0044CC"}
        }
    }

    def __init__(self, *args, **kwargs):
        """Inicializa a tela de edição de perfil."""
        super().__init__(*args, **kwargs)

    def on_enter(self, *args):
        """Inicialização da tela quando ela é exibida"""
        if self.method_salary not in 'Empreita':

            self.days_work = self.week_1 + self.week_2 + self.week_3 + self.week_4
            self.ids.value_salary.text = '{:.0f}'.format(self.salary)
            self.ids.frequency.text = 'Frequencia'
            self._calculate_salary()
            print(self.limite)
            self._finally_work()

        else:
            # Prazo para entrega do serviço
            new_salary = self.salary - self.tot
            self.ids.frequency.text = 'Prazo'
            self.ids.value_salary.text = f'{self.format_salary(new_salary)}'
            self.ids.frequency_text.text = 'Serviço'
            if self.day:
                self.calculate_time()
            else:
                self.ids.percentage.text = 'Não definido'

        self._update_profile_info()
        self._update_components()
        self.star_calculate()

    def format_salary(self, salario):
        """Formata um valor float para o padrão monetário brasileiro."""
        print('O salario ja descontado desse fila da puta é ', salario)
        try:
            self.harv = salario
            locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')  # Define o local como Brasil
            return locale.currency(salario, grouping=True, symbol="R$")
        except locale.Error:
            # Formatação manual caso o locale falhe (comum em Android)
            return self.format_brazilian_currency(salario)

    def format_brazilian_currency(self, valor):
        """Formata um valor para o padrão monetário brasileiro sem usar locale."""
        # Separa parte inteira e decimal
        valor_str = f"{valor:.2f}"
        parte_inteira, parte_decimal = valor_str.split('.')
        print('O salario ja descontado desse fila da puta é ')

        # Formata parte inteira com separador de milhar
        if len(parte_inteira) > 3:
            grupos = []
            while parte_inteira:
                grupos.append(parte_inteira[-3:])
                parte_inteira = parte_inteira[:-3]
            parte_inteira = '.'.join(reversed(grupos))

        # Retorna valor formatado
        return f"R$ {parte_inteira},{parte_decimal}"

    def calculate_time(self):
        data_str = self.day

        # Convertendo a string para um objeto datetime
        data_registrada = datetime.strptime(data_str, "%d/%m/%Y")

        # Obtendo a data atual
        data_atual = datetime.today()

        # Calculando a diferença de dias
        dias_passados = (data_atual - data_registrada).days
        dias_passados = self.days_work - dias_passados
        print(dias_passados)
        if dias_passados < 0:
            self.ids.percentage.text_color = 'white'
            self.ids.percentage.bold = True
            self.ids.percentage.text = 'expirado'
            self.remainder = 'Expirado'

        else:
            self.ids.percentage.text_color = 'white'
            self.ids.percentage.bold = False
            self.ids.percentage.text = f'{dias_passados} dias'
            self.remainder = f'{dias_passados}'

    def star_calculate(self):
        if not self.punctuality or not self.efficiency or not self.coexistence:
            self.ids.asses.text = 'Avaliação: 0.0'
            self.ids.number_one.icon = 'star-outline'
            self.ids.number_two.icon = 'star-outline'
            self.ids.number_three.icon = 'star-outline'
            self.ids.number_four.icon = 'star-outline'
            self.ids.number_five.icon = 'star-outline'
            self.ids.number_one.icon_color = get_color_from_hex('#DB2B39')
            self.ids.number_two.icon_color = get_color_from_hex('#DB2B39')
            self.ids.number_three.icon_color = get_color_from_hex('#DB2B39')
            self.ids.number_one.icon_color = get_color_from_hex('#DB2B39')
            self.ids.number_two.icon_color = get_color_from_hex('#DB2B39')
            self.ids.number_four.icon_color = get_color_from_hex('#DB2B39')
            self.ids.number_five.icon_color = get_color_from_hex('#DB2B39')
            self.ids.asses.text_color = get_color_from_hex('#DB2B39')
        else:
            self.ids.asses.text_color = 'black'
            media = (self.punctuality + self.efficiency + self.coexistence) / 3
            if media > 0:
                self.ids.asses.markup = True  # Ativar suporte a markup
                full_stars = int(media)  # Quantidade de estrelas cheias
                half_star = media - full_stars >= 0.5  # Verifica se tem meia estrela

                star_icons = []  # La para armazenar os íconesist

                # Adiciona estrelas cheias
                for _ in range(full_stars):
                    star_icons.append("star")

                # Adiciona meia estrela (se houver)
                if half_star:
                    star_icons.append("star-half-full")

                # Completa o restante com estrelas vazias
                while len(star_icons) < 5:
                    star_icons.append("star-outline")
                numb = 0
                if media <= 1:
                    self.ids.number_one.icon_color = 'red'
                    self.ids.number_two.icon_color = 'red'
                    self.ids.number_three.icon_color = 'red'
                    self.ids.number_one.icon_color = 'red'
                    self.ids.number_two.icon_color = 'red'
                    self.ids.number_four.icon_color = 'red'
                    self.ids.number_five.icon_color = 'red'
                    self.ids.asses.text = f'Avaliação: [color=#FF0000]{media:.2f}[/color]'
                elif media <= 2:
                    self.ids.number_two.icon_color = get_color_from_hex('#FF8000')
                    self.ids.number_three.icon_color = get_color_from_hex('#FF8000')
                    self.ids.number_one.icon_color = get_color_from_hex('#FF8000')
                    self.ids.number_two.icon_color = get_color_from_hex('#FF8000')
                    self.ids.number_four.icon_color = get_color_from_hex('#FF8000')
                    self.ids.number_five.icon_color = get_color_from_hex('#FF8000')
                    self.ids.asses.text = f'Avaliação: [color=#FF8000]{media:.2f}[/color]'

                elif media <= 3:
                    self.ids.number_three.icon_color = get_color_from_hex('#FFE600')
                    self.ids.number_one.icon_color = get_color_from_hex('#FFE600')
                    self.ids.number_two.icon_color = get_color_from_hex('#FFE600')
                    self.ids.number_four.icon_color = get_color_from_hex('#FFE600')
                    self.ids.number_five.icon_color = get_color_from_hex('#FFE600')
                    self.ids.asses.text = f'Avaliação: [color=#FFE600]{media:.2f}[/color]'

                elif media <= 4:
                    self.ids.number_three.icon_color = get_color_from_hex('#32CD32')
                    self.ids.number_one.icon_color = get_color_from_hex('#32CD32')
                    self.ids.number_two.icon_color = get_color_from_hex('#32CD32')
                    self.ids.number_four.icon_color = get_color_from_hex('#32CD32')
                    self.ids.number_five.icon_color = get_color_from_hex('#32CD32')
                    self.ids.asses.text = f'Avaliação: [color=#32CD32]{media:.2f}[/color]'
                else:
                    self.ids.number_three.icon_color = get_color_from_hex('#007BFF')
                    self.ids.number_one.icon_color = get_color_from_hex('#007BFF')
                    self.ids.number_two.icon_color = get_color_from_hex('#007BFF')
                    self.ids.number_four.icon_color = get_color_from_hex('#007BFF')
                    self.ids.number_five.icon_color = get_color_from_hex('#007BFF')
                    self.ids.asses.text = f'Avaliação: [color=#007BFF]{media:.2f}[/color]'
                for x in star_icons:
                    numb += 1
                    if numb == 1:
                        self.ids.number_one.icon = x
                    elif numb == 2:
                        self.ids.number_two.icon = x
                    elif numb == 3:
                        self.ids.number_three.icon = x
                    elif numb == 4:
                        self.ids.number_four.icon = x
                    else:
                        self.ids.number_five.icon = x

    def _finally_work(self):
        """Verificar forma de recebimento e finalizar o pagamento com base nisso"""
        if self.method_salary in ('Diaria', 'Semanal'):

            data_atual = datetime.today()
            numero_dia = data_atual.weekday()

            dias_semana = {
                0: "Segunda-feira",
                1: "Terça-feira",
                2: "Quarta-feira",
                3: "Quinta-feira",
                4: "Sexta-feira",
                5: "Sábado",
                6: "Domingo"
            }
            dia_hoje = dias_semana[numero_dia]

            if self.scale in '6x1' and dia_hoje in 'Sábado':
                print('Finalizar semana 6x1')
                return

            if self.scale in '5x2' and dia_hoje in 'Sexta-feira':
                print('Finalizar semana 5x2')
                return

            if self.scale in '4x3' and dia_hoje in 'Quinta-feira':
                print('Finalizar semana 4x3')
                return

        elif self.method_salary in 'Quinzenal':

            # Obter a data atual
            data_atual = datetime.today()

            # Obter apenas o dia do mês
            dia_do_mes = data_atual.day

            if dia_do_mes == 15:
                print('Finalizar quinzenal')

        else:
            # Obter a data atual
            data_atual = datetime.today()

            # Obter apenas o dia do mês
            dia_do_mes = data_atual.day

            if dia_do_mes == 3:
                print('Finalizar Mensal')

    def _update_profile_info(self):
        """Atualiza informações de perfil na interface"""
        self.ids.perfil.source = self.avatar
        self.ids.name.text = self.employee_name
        self.ids.function.text = self.employee_function

    def _calculate_salary(self):
        """Calcula o salário com base no método de pagamento e escala"""
        salary_calculators = {
            "Diaria": self._calculate_day,
            "Semanal": self._calculate_week,
            "Quinzenal": self._calculate_biweekly,
            "Mensal": self._calculate_month,
            "Empreita": self._calculate_undertakes
        }

        calculator = salary_calculators.get(self.method_salary)
        if calculator:
            calculator()

    def _get_percentage_and_day_value(self, period_type):
        """Retorna a porcentagem de dias trabalhados e o valor diário"""
        if not self.scale in self.SCALE_WORKDAYS:
            return 0, 0

        workdays = self.SCALE_WORKDAYS[self.scale][period_type]
        percentage = (self.days_work / workdays) * 100

        if period_type == "day":
            day_value = int(self.salary)
        else:
            day_value = int(self.salary) / workdays

        return percentage, day_value

    def _calculate_day(self):
        """Calcula o salário diário"""
        percentage, day_value = self._get_percentage_and_day_value("day")
        self.ids.percentage.text = f"{percentage:.2f}%"
        salary = day_value * self.days_work
        self.money = float(salary - self.tot)
        self.ids.value_salary.text = f"R${int(salary - self.tot):,}"

        self.limite = salary

    def _calculate_week(self):
        """Calcula o salário semanal"""
        percentage, day_value = self._get_percentage_and_day_value("week")
        self.ids.percentage.text = f"{percentage:.2f}%"
        salary = day_value * self.days_work
        self.money = float(salary - self.tot)
        self.ids.value_salary.text = f"R${int(salary - self.tot):,}"
        self.limite = salary

    def _calculate_biweekly(self):
        """Calcula o salário quinzenal"""
        percentage, day_value = self._get_percentage_and_day_value("biweekly")
        self.ids.percentage.text = f"{percentage:.2f}%"
        salary = day_value * self.days_work
        self.money = float(salary - self.tot)
        self.limite = salary
        try:
            # Tenta usar formatação locale
            self.ids.value_salary.text = f"R${salary:,.2f}"
        except:
            # Fallback para formatação manual
            self.ids.value_salary.text = self.format_brazilian_currency(salary)

    def _calculate_month(self):
        """Calcula o salário mensal"""
        percentage, day_value = self._get_percentage_and_day_value("month")
        self.ids.percentage.text = f"{percentage:.2f}%"
        salary = day_value * self.days_work
        self.money = float(salary - self.tot)
        self.limite = salary
        try:
            # Tenta usar formatação locale
            self.ids.value_salary.text = f"R${salary - self.tot:,.2f}"
        except:
            # Fallback para formatação manual
            self.ids.value_salary.text = self.format_brazilian_currency(salary - self.tot)

    def _calculate_undertakes(self):
        """Calcula o salário por empreita"""
        self.ids.frequency.text = "Prazo"
        self.ids.percentage.text = f"{self.days_work}"

    def _update_components(self):
        """Atualiza os componentes de avaliação na interface"""
        self._update_assessment("coexistence")
        self._update_assessment("efficiency")
        self._update_assessment("punctuality")
        self._update_salary_display()

    def _update_assessment(self, assessment_type):
        """Atualiza um componente específico de avaliação"""
        value = getattr(self, assessment_type)

        if not value:
            self.ids[assessment_type].text_color = get_color_from_hex('#DB2B39')
            self.ids[f"text_{assessment_type}"].text = "Não definido"
            return
        else:
            self.ids[assessment_type].text_color = 'green'

        level = int(value)
        assessment_info = self.ASSESSMENT_LEVELS[assessment_type].get(level, {})

        if assessment_info:
            self.ids[f"text_{assessment_type}"].text_color = get_color_from_hex(assessment_info["color"])
            self.ids[f"text_{assessment_type}"].text = assessment_info["text"]

    def _update_salary_display(self):
        """Atualiza a exibição do salário na interface"""
        if not self.salary:
            self.ids.salary.text_color = "red"
            self.ids.text_salary.text = "Não definido"
        else:
            try:
                # Tenta usar formatação locale
                salary_text = f"{int(self.salary):,}"
            except:
                # Fallback para formatação manual simples
                salary_text = str(int(self.salary))
                if len(salary_text) > 3:
                    grupos = []
                    while salary_text:
                        grupos.append(salary_text[-3:])
                        salary_text = salary_text[:-3]
                    salary_text = '.'.join(reversed(grupos))

    def _navigate_to_screen(self, screen_name):
        """Navega para uma tela específica, transferindo dados do funcionário"""
        app = MDApp.get_running_app()
        screen_manager = app.root

        target_screen = screen_manager.get_screen(screen_name)

        # Transfere todos os dados relevantes
        attributes = [
            "employee_name", "employee_function", "avatar", "contractor",
            "method_salary", "assess", "coexistence", "punctuality",
            "efficiency", "scale", "week_1", "week_2", "week_3", "week_4",
            "work_days_week1", "work_days_week2", "work_days_week3", "work_days_week4",
            "key", "confirm_payments"
        ]
        if screen_name in ('EditProfileEmployee', 'WorkingBricklayer'):
            attributes.append("ultimate")
            attributes.append("observations")
            attributes.append("salary")
            attributes.append('day')

        if screen_name == 'WorkingMonth':
            attributes.append('days_work')

        for attr in attributes:
            setattr(target_screen, attr, getattr(self, attr))

        screen_manager.current = screen_name

    def value(self):
        return '{:.2f}'.format(self.salary)

    def back_table(self):
        """Volta para a tela de tabela"""
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = 'Table'

    def next_punctuality(self):
        """Navega para a tela de avaliação de pontualidade"""
        self.manager.transition = SlideTransition(direction="left")
        self._navigate_to_screen("AssesPunctuality")

    def next_efficiency(self):
        """Navega para a tela de avaliação de eficiência"""
        self.manager.transition = SlideTransition(direction="left")
        self._navigate_to_screen("AssesEfficiency")

    def next_coexistence(self):
        """Navega para a tela de avaliação de convivência"""
        self.manager.transition = SlideTransition(direction="left")
        self._navigate_to_screen("AssesCoexistence")

    def next_working_days(self):
        """Navega para a tela de trabalho semanal"""
        if self.method_salary in ('Semanal', 'Diaria'):
            self.manager.transition = SlideTransition(direction='left')
            self._navigate_to_screen('WorkingDays')

        elif self.method_salary in 'Empreita':
            self.next_bricklayer()

        else:
            self.manager.transition = SlideTransition(direction="left")
            self._navigate_to_screen('WorkingMonth')

    def next_edit(self):
        """Navega para a tela de edição do perfil do funcionario"""
        app = MDApp.get_running_app()
        screenmanager = app.root
        edit = screenmanager.get_screen('EditProfileEmployee')
        edit.ultimate = self.ultimate
        edit.method_salary = self.method_salary
        edit.day = self.day
        edit.salary = self.salary
        edit.employee_name = self.employee_name
        edit.scale = self.scale
        edit.avatar = self.avatar
        edit.key = self.key
        edit.observations = self.observations
        self.manager.transition = SlideTransition(direction='left')
        screenmanager.current = 'EditProfileEmployee'

    def next_report(self):
        """Navega para a tela de relatorios do funcionario"""
        app = MDApp.get_running_app()
        screenmanager = app.root
        edit = screenmanager.get_screen('ReportBricklayer')
        edit.avatar = self.avatar
        edit.tot = self.tot
        edit.key = self.key
        edit.valleys = self.valleys
        edit.day = self.day
        edit.remainder = self.remainder
        edit.employee_name = self.employee_name
        edit.function = self.employee_function
        edit.method_salary = self.method_salary
        edit.scale = self.scale
        edit.confirm_payments = self.confirm_payments

        print(self.salary - self.tot)
        if self.method_salary in 'Empreita':
            edit.salary = self.salary - self.tot
        else:
            edit.salary = self.limite
        screenmanager.transition = SlideTransition(direction='left')
        screenmanager.current = 'ReportBricklayer'

    def next_bricklayer(self):
        self.manager.transition = SlideTransition(direction='left')
        self._navigate_to_screen('WorkingBricklayer')

    def _next_confirm_payment(self):
        app = MDApp.get_running_app()
        print('Salario: 1 ', self.salary)
        print('Salario: 2 ', self.salary)
        print('Money: ', self.money)
        print('Salario 3: ', self.limite)

        screenmanager = app.root
        confirm = screenmanager.get_screen('ConfirmPayment')
        confirm.method_salary = self.method_salary
        confirm.name_employee = self.employee_name
        confirm.tot = self.tot
        confirm.key = self.key
        confirm.valleys = self.valleys
        if self.method_salary not in 'Empreita':
            confirm.salary = self.money
            confirm.salary_completed = self.limite
        else:
            print('O salario e este aqui: ', self.salary)
            confirm.salary = self.salary
            confirm.salary_completed = self.salary
        confirm.request_payment = self.request_payment
        confirm.confirm_payments = self.confirm_payments
        screenmanager.transition = SlideTransition(direction='right')
        screenmanager.current = 'ConfirmPayment'

    def back_evaluation(self):
        self.manager.current = 'Evaluation'
