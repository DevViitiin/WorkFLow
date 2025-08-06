import ast
import json

from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, DictProperty
from kivy.uix.screenmanager import SlideTransition
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.chip import MDChipText, MDChip
from kivymd.uix.label import MDLabel
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from babel.numbers import format_currency


class PaymentCard(MDBoxLayout):
    """
    A card widget that displays payment information with a green indicator,
    payment details, and a "Details" button.
    """
    current_data = StringProperty()
    month = StringProperty()
    payment_status = StringProperty()
    payment_type = StringProperty()
    numb = NumericProperty()
    payment_date = StringProperty()
    payment_amount = StringProperty()
    salary = NumericProperty()
    unpaid_payment_amount = StringProperty()
    name_employee = StringProperty()
    color = StringProperty()
    text_color = StringProperty()
    color_line = StringProperty()
    info = DictProperty()
    key = StringProperty()

    def __init__(self, **kwargs):
        # Extract custom properties
        self.week = kwargs.pop('current_data', 'Semana 1')
        self.month = kwargs.pop('month', 'Janeiro')
        self.payment_status = kwargs.pop('payment_status', 'Pago')
        self.payment_type = kwargs.pop('payment_type', 'semanal')
        self.payment_date = kwargs.pop('payment_date', '13/05/2009')
        self.payment_amount = kwargs.pop('payment_amount', 'R$13.400')


        # Set default card settings
        kwargs.update({
            'orientation': 'horizontal',
            'size_hint_y': None,
            'height': dp(150),
            'theme_bg_color': 'Custom',
        })

        super().__init__(**kwargs)
        self.build()

    def build(self):
        print(self.key)
        self.clear_widgets()

        # Green indicator box on left
        green_box = MDBoxLayout(
            theme_bg_color='Custom',
            radius=[15, 0, 0, 15],
            md_bg_color=self.color_line
        )
        self.add_widget(green_box)

        # Content area on right
        content_layout = MDBoxLayout(
            orientation='vertical',
            theme_bg_color='Custom',
            radius=[0, 15, 15, 0],
            size_hint_x=None,
            width=dp(290)
        )
        self.add_widget(content_layout)

        # Header area with title and status chip
        header_layout = MDBoxLayout(
            orientation='horizontal',
            theme_bg_color='Custom',
            md_bg_color='white',
            spacing=10,
            padding=[2, ]
        )
        content_layout.add_widget(header_layout)

        # Title box
        title_box = MDBoxLayout(
            orientation='horizontal',
            theme_bg_color='Custom',
            padding=[5]
        )
        header_layout.add_widget(title_box)

        # Title label
        title_label = MDLabel(
            text=f'{self.week}',
            font_style='Label',
            role='large',
            theme_text_color='Custom',
            text_color='black',
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            halign='left'
        )
        title_box.add_widget(title_label)

        # Status chip container
        status_box = MDBoxLayout(
            orientation='horizontal',
            theme_bg_color='Custom'
        )
        header_layout.add_widget(status_box)

        # Status chip
        status_layout = MDRelativeLayout()
        status_box.add_widget(status_layout)

        chip_text = MDChipText(
            text=self.payment_status,
            theme_text_color='Custom',
            text_color=get_color_from_hex(self.text_color),
            pos_hint={'center_x': 0.45, 'center_y': 0.5},
            halign='center',
            bold=True
        )

        status_chip = MDChip(
            chip_text,
            size_hint=(0.4, 0.75),
            theme_bg_color='Custom',
            md_bg_color=get_color_from_hex(self.color),
            pos_hint={"right": .9, "center_y": .5}
        )
        status_layout.add_widget(status_chip)

        # Middle info section
        info_layout = MDBoxLayout(
            orientation='horizontal',
            theme_bg_color='Custom',
            padding=[5, 0, 0, 0]
        )
        content_layout.add_widget(info_layout)

        # Type info
        type_box = MDBoxLayout(
            orientation='vertical',
            theme_bg_color='Custom',
            padding=[5]
        )
        info_layout.add_widget(type_box)

        type_label = MDLabel(
            text='Tipo',
            font_style='Body',
            role='small',
            theme_text_color='Custom',
            text_color='grey',
            pos_hint={'center_x': 0.5, 'center_y': 0.8},
            halign='left'
        )
        type_box.add_widget(type_label)

        type_value = MDLabel(
            text=self.payment_type,
            font_style='Body',
            role='medium',
            theme_text_color='Custom',
            text_color=get_color_from_hex('#41463D'),
            pos_hint={'center_x': 0.5, 'center_y': 0.4},
            halign='left'
        )
        type_box.add_widget(type_value)

        # Date info
        date_box = MDBoxLayout(
            orientation='vertical',
            theme_bg_color='Custom',
            padding=[5]
        )
        info_layout.add_widget(date_box)

        date_label = MDLabel(
            text='data',
            font_style='Body',
            role='small',
            theme_text_color='Custom',
            text_color='grey',
            pos_hint={'center_x': 0.4, 'center_y': 0.8},
            halign='right'
        )
        date_box.add_widget(date_label)

        date_value = MDLabel(
            text=self.payment_date,
            font_style='Body',
            role='medium',
            theme_text_color='Custom',
            text_color=get_color_from_hex('#41463D'),
            pos_hint={'center_x': 0.4, 'center_y': 0.4},
            halign='right'
        )
        date_box.add_widget(date_value)

        # Amount section
        amount_box = MDBoxLayout(
            theme_bg_color='Custom',
            padding=[10, 0, 0, 0]
        )
        content_layout.add_widget(amount_box)

        amount_label = MDLabel(
            text=self.payment_amount,
            font_style='Title',
            role='medium',
            theme_text_color='Custom',
            text_color='black',
            bold=True,
            pos_hint={'center_x': 0.5, 'center_y': 0.4},
            halign='left'
        )
        amount_box.add_widget(amount_label)

        # Details button section
        details_box = MDBoxLayout(
            theme_bg_color='Custom'
        )
        content_layout.add_widget(details_box)

        details_layout = MDRelativeLayout()
        details_box.add_widget(details_layout)

        details_text = MDChipText(
            text="Detalhes",
            theme_text_color='Custom',
            text_color='black',
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            halign='center',
            bold=True
        )

        details_chip = MDChip(
            details_text,
            theme_bg_color='Custom',
            md_bg_color=[1, 1, 1, 1],
            pos_hint={"center_x": .5, "center_y": .5}
        )
        details_layout.add_widget(details_chip)

        # Bind click event for details button
        details_chip.bind(on_release=self.on_details_click)

    def on_details_click(self, instance):
        """Handle click on the Details button"""
        if self.payment_status in 'Pendente':
            print(f"Details clicked for payment: {self.week} - {self.month}, {self.payment_amount}")
            print(f'Key do funcionario: {self.key}')
            UrlRequest(
                url=f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.key}/.json',
                on_success=self.confirm_payments

            )
        else:
            app = MDApp.get_running_app()
            screenmanager = app.root
            view = screenmanager.get_screen('ViewPaymentCompleted')
            view.method_salary = self.info['method']
            view.name_employee = self.name_employee
            view.date = self.info['data']
            view.salary_completed = self.info['salary_completed']
            view.salary_discounted = self.info['value']
            view.numb = self.info['numb']
            view.valleys = self.info['valleys']
            screenmanager.transition = SlideTransition(direction='right')
            screenmanager.current = 'ViewPaymentCompleted'
        # Add additional functionality here as needed

    def confirm_payments(self, req, result):
        accept = []
        print('confirme')
        try:
            confirm = ast.literal_eval(result['confirm_payments'])
            if confirm:
                for payment in confirm:
                    print(f'pagamentos aguardando confirmação: {payment}')
                    print(payment['numb'], payment['Month'])
                    print(self.numb, self.month)
                    if self.numb == payment['numb'] and self.month in payment['Month']:
                        print('Pagamento confirmado pelo contratante')
                        UrlRequest(
                            url=f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.key}/contractor/.json',
                            on_success=lambda req, result, data=payment: self.two_confirm(req, result, data)

                        )
                        break
                    else:
                        print('Pagamento não confirmado pelo contratante')
                        UrlRequest(
                            url=f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.key}/contractor/.json',
                            on_success=self.confirm_name_contractor

                        )
                        break
            else:
                print('Pagamento não confirmado pelo contratante')
                UrlRequest(
                    url=f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.key}/contractor/.json',
                    on_success=self.confirm_name_contractor

                )

        except Exception as e:
            print('Error inesperado aconteceu: {}'.format(e))

    def two_confirm(self, req, resulti, info):
        print(f'O nome do contratante é {resulti}')
        UrlRequest(
            url=f'https://obra-7ebd9-default-rtdb.firebaseio.com/Users/.json',
            on_success=lambda req, result, name=resulti, inf=info: self.get_name_two(req, result, name, inf)

        )

    def get_name_two(self, req, result, name, info):
        telephone = ''
        email = ''
        for key, person in result.items():
            if person['name'] in name:
                telephone = person['telefone']
                email = person['email']
                print('rs', telephone)
                print('rs', email)
                """Agora eu vou pegar os dados do funcionario e mandar pra proxima tela"""
                UrlRequest(
                    url=f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.key}/.json',
                    on_success=lambda req, result, telepho=telephone, mail=email, inf=info: self.finally_screen(req, result, telepho, mail, inf)

                )

    def finally_screen(self, req, result, telephone, email, info):
        print('Contato do contratante: ', telephone, email)
        print('Informações do funcionario: ', result)
        print('Informações da confirmação: ', info)
        app = MDApp.get_running_app()
        screenmanager = app.root
        confirm = screenmanager.get_screen('ConfirmPaymentEmployee')
        confirm.method_salary = info['method']
        confirm.name_employee = result['Name']
        confirm.date = info['data']
        confirm.salary_completed = self.salary
        confirm.salary_discounted = float(info['value'])
        confirm.payments = result['payments']
        confirm.numb = info['numb']
        confirm.month = self.month
        confirm.confirm = f"{info}"
        confirm.email = email
        confirm.telephone = telephone
        confirm.valleys = info['valleys']
        confirm.key = self.key
        screenmanager.transition = SlideTransition(direction='left')
        screenmanager.current = 'ConfirmPaymentEmployee'

    def confirm_name_contractor(self, req, resulti):
        print(f'O nome do contratante é {resulti}')
        UrlRequest(
            url=f'https://obra-7ebd9-default-rtdb.firebaseio.com/Users/.json',
            on_success=lambda req, result, name=resulti: self.get_name(req, result, name)

        )

    def get_name(self, req, result, name):
        print(name)
        for key, person in result.items():
            if person['name'] in name:
                print('Achei o contratante')
                app = MDApp.get_running_app()
                screenmanager = app.root
                view = screenmanager.get_screen('NotificationPage')
                view.month = self.month
                view.numb = self.numb
                view.name_contractor = name
                view.salary = self.salary
                view.email = person['email']
                view.method = self.payment_type
                view.key = self.key
                view.telephone = person['telefone']
                screenmanager.transition = SlideTransition(direction='left')
                screenmanager.current = 'NotificationPage'


class ReviewScreen(MDScreen):
    current_nav_state = StringProperty('revision')
    key = StringProperty()
    avatar = StringProperty()
    employee_name = StringProperty()
    employee_function = StringProperty()
    method_salary = StringProperty()
    city = StringProperty()
    state = StringProperty()
    employee_mail = StringProperty()
    salary = NumericProperty()
    employee_telephone = StringProperty()
    employee_summary = StringProperty()
    data_contractor = StringProperty()
    skills = StringProperty()
    tot_salary = NumericProperty()
    contractor_month = NumericProperty(6)
    contractor = StringProperty()
    request = BooleanProperty()

    def on_enter(self):
        print(self.salary)
        print('Data de contratação: ', self.data_contractor)
        # Lista fixa dos meses do ano
        self.months_year = [
            "Janeiro", "Fevereiro", "Março", "Abril",
            "Maio", "Junho", "Julho", "Agosto",
            "Setembro", "Outubro", "Novembro", "Dezembro"
        ]

        self.dados_teste = [
            {'Payment Type': 'Mensal', 'Paid Salary': '19000', 'numb': '3', 'Month': 'Janeiro',
             'Data': '31/05/2009'},
            {'Payment Type': 'Semanal', 'Paid Salary': '19000', 'numb': '5', 'Month': 'Maio',
             'Data': '31/05/2009'}
        ]

        from datetime import datetime
        self.month = datetime.today().month
        self.ids.main_scroll.clear_widgets()
        self.upload_payments()

    def upload_payments(self):
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.key}/.json'
        UrlRequest(
            url,
            on_success=self.add_payments,
            on_error=self.usar_dados_teste,
            on_failure=self.usar_dados_teste
        )

    def add_payments(self, instance, response):
        # Verificar se 'payments' existe no response
        self.contractor_month = response['contractor_month']
        if 'payments' not in response:
            print("Chave 'payments' não encontrada na resposta!")
            return self.usar_dados_teste()

        # Mostrar o valor bruto de 'payments'
        print(f"Valor bruto de 'payments': {response['payments']}")
        print(f"Tipo de 'payments': {type(response['payments'])}")

        # Processar com base no tipo
        if isinstance(response['payments'], str):
            try:
                # Usar ast.literal_eval em vez de eval (mais seguro)
                clean_json = response['payments'].strip()
                print(f"Tentando analisar: {clean_json[:100]}...")  # Mostrar início da string
                payments = ast.literal_eval(clean_json)
            except (SyntaxError, ValueError) as e:
                print(f"Erro ao analisar string: {e}")
                # Se falhar com ast.literal_eval, tente json.loads
                try:
                    payments = json.loads(clean_json)
                except json.JSONDecodeError as e:
                    print(f"Erro ao decodificar JSON: {e}")
                    # Se falhar, use os dados de teste
                    return self.usar_dados_teste()
        elif isinstance(response['payments'], list):
            payments = response['payments']
        else:
            print(f"Formato inesperado: {type(response['payments'])}")
            return self.usar_dados_teste()

        # Verificar o conteúdo final de payments
        print(f"Pagamentos processados: {payments}")

        # Processar pagamentos
        self.processar_pagamentos(payments)

    def usar_dados_teste(self):
        print("\nUsando dados de teste como fallback:")
        print(self.dados_teste)
        self.processar_pagamentos(self.dados_teste)

    def processar_pagamentos(self, payments):
        # Processar a data de contratação
        from datetime import datetime
        import calendar

        # Usar data de contratação específica para teste
        data_contratacao_str = self.data_contractor  # Exemplo fornecido

        # Convertendo a data de contratação de string para objeto datetime
        try:
            # Formato esperado: DD/MM/YYYY
            data_contratacao = datetime.strptime(data_contratacao_str, '%d/%m/%Y')
            mes_contratacao = data_contratacao.month
            ano_contratacao = data_contratacao.year
            dia_contratacao = data_contratacao.day
        except (ValueError, TypeError):
            # Caso a data seja inválida, usar o primeiro dia do mês atual
            data_atual = datetime.now()
            mes_contratacao = data_atual.month
            ano_contratacao = data_atual.year
            dia_contratacao = 1

        print(f"Data de contratação: {dia_contratacao}/{mes_contratacao}/{ano_contratacao}")

        # Verificar se payments não está vazio
        if not payments:
            print("Nenhum pagamento para processar! Usando dados de teste...")
            payments = self.dados_teste

        # Dicionário para mapear nome do mês para número
        meses_numero = {
            'Janeiro': 1, 'Fevereiro': 2, 'Março': 3, 'Abril': 4,
            'Maio': 5, 'Junho': 6, 'Julho': 7, 'Agosto': 8,
            'Setembro': 9, 'Outubro': 10, 'Novembro': 11, 'Dezembro': 12
        }

        # Inverso para mapear número para nome do mês
        numero_meses = {v: k for k, v in meses_numero.items()}

        # Criar dicionário para rastrear status dos meses com base nos nomes em self.months_year
        status_meses = {mes: False for mes in self.months_year}
        month_payment = {mes: [] for mes in self.months_year}

        # Dicionário para rastrear semanas já pagas por mês
        semanas_pagas = {mes: [] for mes in self.months_year}

        # Processar cada pagamento existente
        for payment in payments:
            if isinstance(payment, dict) and 'Month' in payment:
                mes = payment['Month']
                if mes in self.months_year:
                    status_meses[mes] = True
                    print(f"Mês marcado como pago: {mes}")

                    # Adicionar à lista de pagamentos
                    month_payment[mes].append(payment)

                    # Se for pagamento semanal, registrar que semana foi paga
                    if payment.get('method') == 'Semanal' and 'numb' in payment:
                        semana_num = int(payment['numb']) if isinstance(payment['numb'], str) else payment['numb']
                        if semana_num not in semanas_pagas[mes]:
                            semanas_pagas[mes].append(semana_num)

        print(month_payment)
        print("Semanas pagas por mês:", semanas_pagas)

        # Determinar o método de pagamento predominante
        metodo_predominante = 'Semanal'  # Padrão
        for mes in month_payment:
            for payment in month_payment[mes]:
                if payment.get('method') == 'Mensal':
                    metodo_predominante = 'Mensal'
                    break

        # Mostrar resultado final
        print("\nStatus Final dos Pagamentos:")
        self.tot_salary = 0.0

        # Limpar widgets existentes
        self.ids.main_scroll.clear_widgets()

        ano_atual = datetime.now().year
        mes_atual = datetime.now().month

        # Lista de todos os meses a serem processados
        meses_a_processar = []

        # Adicionar meses desde a contratação até o mês atual
        for ano in range(ano_contratacao, ano_atual + 1):
            for mes_num in range(1, 13):
                # Se for o ano de contratação, começar pelo mês de contratação
                if ano == ano_contratacao and mes_num < mes_contratacao:
                    continue

                # Se for o ano atual, ir até o mês atual
                if ano == ano_atual and mes_num > mes_atual:
                    continue

                mes_nome = numero_meses.get(mes_num)
                if mes_nome and mes_nome in self.months_year:
                    meses_a_processar.append((mes_num, mes_nome))

        # Ordenar meses cronologicamente
        meses_a_processar.sort()

        # Processar cada mês
        for mes_num, mes_nome in meses_a_processar:
            print(f'Processando mês: {mes_nome} ({mes_num})')

            # Definir o número correto de semanas do mês (para método semanal)
            # Padronizando para 4 semanas por mês no sistema de pagamento
            total_semanas = 4

            # Se for o mês de contratação, considerar apenas a partir do dia da contratação
            semana_inicial = 1
            if mes_num == mes_contratacao and ano_atual == ano_contratacao:
                # Calcular em qual semana do mês está o dia de contratação
                semana_inicial = (dia_contratacao - 1) // 7 + 1

            # Verificar se tem pagamentos registrados para este mês
            if status_meses[mes_nome]:
                # Primeiro, adicionar semanas pendentes antes das pagas
                if metodo_predominante == 'Semanal':
                    # Organizar os cartões de pagamento: primeiro pendentes, depois pagos
                    cards_to_add = []

                    # Adicionar semanas pendentes
                    for semana in range(semana_inicial, total_semanas + 1):

                        if semana not in semanas_pagas[mes_nome]:
                            text_numb = f'Semana: {semana} - {mes_nome}'
                            card = PaymentCard(
                                payment_date='Aguardando',
                                payment_type='Semanal',
                                payment_amount=f'R$0.0',
                                payment_status='Pendente',
                                month=f'{mes_nome}',
                                numb=semana,
                                salary=self.salary,
                                current_data=text_numb,
                                color_line='#E3170A',
                                text_color='#ffffff',
                                color='#E3170A',
                                key=self.key
                            )
                            cards_to_add.append((semana, card))

                    # Adicionar semanas pagas
                    for payment in sorted(month_payment[mes_nome],
                                          key=lambda p: int(p['numb']) if isinstance(p['numb'], str) else p['numb']):
                        print(payment)
                        if payment.get('method') == 'Semanal':
                            semana = int(payment['numb']) if isinstance(payment['numb'], str) else payment['numb']
                            text_numb = f"Semana: {payment['numb']} - {payment['Month']}"
                            card = PaymentCard(
                                payment_date=payment['data'],
                                payment_type=payment['method'],
                                payment_amount=f"{format_currency(payment['value'], 'BRL', locale='pt_BR')}",
                                payment_status='Pago',
                                month=payment['Month'],
                                numb=payment['numb'],
                                current_data=text_numb,
                                color_line='#68D89B',
                                text_color='#ffffff',
                                color='#68D89B',
                                info=payment,
                                name_employee=self.employee_name,
                                key=self.key
                            )
                            cards_to_add.append((semana, card))
                            self.tot_salary += float(payment['value'])

                    # Ordenar cartões por número de semana e adicionar ao layout
                    for _, card in sorted(cards_to_add, key=lambda x: x[0]):
                        self.ids.main_scroll.add_widget(card)

                    # Adicionar pagamentos mensais, se houver
                    for payment in month_payment[mes_nome]:
                        if payment.get('method') == 'Mensal':
                            text_numb = f"Mês: {payment['numb']} - {payment['Month']}"
                            card = PaymentCard(
                                payment_date=payment['data'],
                                payment_type=payment['method'],
                                payment_amount=f"{format_currency(payment['value'], 'BRL', locale='pt_BR')}",
                                payment_status='Pago',
                                month=payment['Month'],
                                numb=payment['numb'],
                                current_data=text_numb,
                                color_line='#68D89B',
                                text_color='#ffffff',
                                color='#68D89B',
                                info=payment,
                                name_employee=self.employee_name,
                                key=self.key
                            )
                            self.ids.main_scroll.add_widget(card)
                            self.tot_salary += float(payment['value'])
                else:
                    # Para método mensal, adicionar pagamentos realizados
                    for payment in month_payment[mes_nome]:
                        text_numb = f"Mês: {payment['numb']} - {payment['Month']}"
                        card = PaymentCard(
                            payment_date=payment['data'],
                            payment_type=payment['method'],
                            payment_amount=f"{format_currency(payment['value'], 'BRL', locale='pt_BR')}",
                            payment_status='Pago',
                            month=payment['Month'],
                            numb=payment['numb'],
                            current_data=text_numb,
                            color_line='#68D89B',
                            text_color='#ffffff',
                            color='#68D89B',
                            info=payment,
                            name_employee=self.employee_name,
                            key=self.key
                        )
                        self.ids.main_scroll.add_widget(card)
                        self.tot_salary += float(payment['value'])
            else:
                # Se não tem pagamentos no mês, adicionar todo o mês como pendente
                if metodo_predominante == 'Mensal':
                    text_numb = f'Mês: {mes_num} - {mes_nome}'

                    card = PaymentCard(
                        payment_date='Aguardando',
                        payment_type='Mensal',
                        payment_amount=f'R$0.0',
                        payment_status='Pendente',
                        month=f'{mes_nome}',
                        numb=mes_num,
                        salary=self.salary,
                        current_data=text_numb,
                        color_line='#E3170A',
                        text_color='#ffffff',
                        color='#E3170A',
                        key=self.key

                    )
                    self.ids.main_scroll.add_widget(card)
                else:  # método semanal
                    for semana in range(semana_inicial, total_semanas + 1):
                        text_numb = f'Semana: {semana} - {mes_nome}'
                        card = PaymentCard(
                            payment_date='Aguardando',
                            payment_type='Semanal',
                            payment_amount=f'R$0.0',
                            payment_status='Pendente',
                            month=f'{mes_nome}',
                            numb=semana,
                            salary=self.salary,
                            current_data=text_numb,
                            color_line='#E3170A',
                            text_color='#ffffff',
                            color='#E3170A',
                            key=self.key

                        )
                        self.ids.main_scroll.add_widget(card)

        # Atualizar o total recebido
        self.ids.received.text = f"{format_currency(self.tot_salary, 'BRL', locale='pt_BR')}"

    def vacancy(self):
        """
        Navega para a tela de vagas e ajusta o estado global de navegação
        """
        app = MDApp.get_running_app()
        screenmanager = app.root

        # Obtém a tela de vagas
        vac = screenmanager.get_screen('VacancyBank')

        # Transfere os dados do usuário
        vac.key = self.key
        print(self.key)
        vac.employee_name = self.employee_name
        vac.employee_function = self.employee_function
        vac.employee_mail = self.employee_mail
        vac.employee_telephone = self.employee_telephone
        vac.avatar = self.avatar
        vac.employee_summary = self.employee_summary
        vac.skills = self.skills
        vac.request = self.request
        vac.data_contractor = self.data_contractor
        vac.contractor = self.contractor
        vac.state = self.state
        vac.city = self.city
        # Define o estado de navegação global
        self.current_nav_state = 'vacancy'

        # Garante que apenas o ícone de vagas esteja ativo
        vac.ids.vacancy.active = True
        vac.ids.perfil.active = False
        vac.ids.notification.active = False
        vac.ids.payment.active = False

        self.tot_salary = 0

        # Navega para a tela de vagas
        screenmanager.transition = SlideTransition(direction='right')
        screenmanager.current = 'VacancyBank'

    def req2(self):
        """
        Navega para a tela de vagas e ajusta o estado global de navegação
        """
        app = MDApp.get_running_app()
        screenmanager = app.root

        # Obtém a tela de vagas
        vac = screenmanager.get_screen('RequestsVacancy')

        # Transfere os dados do usuário
        vac.key = self.key
        vac.tab_nav_state = 'request'
        vac.employee_name = self.employee_name
        vac.employee_function = self.employee_function
        vac.employee_mail = self.employee_mail
        vac.employee_telephone = self.employee_telephone
        vac.avatar = self.avatar
        vac.employee_summary = self.employee_summary
        vac.skills = self.skills
        vac.data_contractor = self.data_contractor
        vac.request = self.request
        vac.contractor = self.contractor
        vac.state = self.state
        vac.city = self.city

        # Garante que apenas o ícone de vagas esteja ativo
        vac.ids.vacancy.active = False
        vac.ids.perfil.active = False
        vac.ids.payment.active = False
        vac.ids.notification.active = True

        # Navega para a tela de vagas
        screenmanager.transition = SlideTransition(direction='right')
        screenmanager.current = 'RequestsVacancy'

    def req(self):
        """
        Navega para a tela de vagas e ajusta o estado global de navegação
        """
        app = MDApp.get_running_app()
        screenmanager = app.root

        # Obtém a tela de vagas
        vac = screenmanager.get_screen('RequestsVacancy')

        # Transfere os dados do usuário
        vac.key = self.key
        vac.tab_nav_state = 'request'
        vac.state = self.state
        vac.city = self.city
        vac.employee_name = self.employee_name
        vac.employee_function = self.employee_function
        vac.employee_mail = self.employee_mail
        vac.employee_telephone = self.employee_telephone
        vac.avatar = self.avatar
        vac.employee_summary = self.employee_summary
        vac.skills = self.skills
        vac.data_contractor = self.data_contractor
        vac.contractor = self.contractor
        vac.request = self.request

        # Garante que apenas o ícone de vagas esteja ativo
        vac.ids.vacancy.active = False
        vac.ids.perfil.active = False
        vac.ids.payment.active = False
        vac.ids.notification.active = True

        self.tot_salary = 0

        # Navega para a tela de vagas
        screenmanager.transition = SlideTransition(direction='right')
        screenmanager.current = 'RequestsVacancy'

    def perfil(self):
        """
        Navega para a tela de perfil e ajusta o estado global de navegação
        """
        app = MDApp.get_running_app()
        screenmanager = app.root

        # Obtém a tela de perfil
        perfil = screenmanager.get_screen('PrincipalScreenEmployee')

        # Transfere os dados do usuário
        perfil.key = self.key
        print('Key passada para perfil: ', self.key)
        perfil.employee_name = self.employee_name
        perfil.employee_function = self.employee_function
        perfil.employee_mail = self.employee_mail
        perfil.employee_telephone = self.employee_telephone
        perfil.avatar = self.avatar
        perfil.city = self.city
        perfil.contractor = self.contractor
        perfil.state = self.state
        perfil.data_contractor = self.data_contractor
        perfil.employee_summary = self.employee_summary
        perfil.skills = self.skills

        # Define o estado de navegação global
        perfil.ids.payment.active = False
        perfil.ids.vacancy.active = False
        perfil.ids.notification.active = False
        perfil.ids.perfil.active = True
        perfil.current_nav_state = 'perfil'

        self.tot_salary = 0
        # Navega para a tela de perfil
        screenmanager.transition = SlideTransition(direction='right')
        screenmanager.current = 'PrincipalScreenEmployee'

    def back(self):
        print('back')
