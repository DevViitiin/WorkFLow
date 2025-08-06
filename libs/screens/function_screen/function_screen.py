import json
from kivy.metrics import dp
from kivy.properties import StringProperty, get_color_from_hex
from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import SlideTransition
from kivymd.uix.button import MDIconButton, MDButton, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivy.network.urlrequest import UrlRequest
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from libs.screens.function_screen.citys import *


class FunctionScreen(MDScreen):
    contractor = StringProperty()
    email = StringProperty()
    local_id = StringProperty()
    token_id = StringProperty()
    refresh_token = StringProperty()
    telephone = StringProperty()
    company = StringProperty()
    key = StringProperty()
    dialy = 0
    undertakes = 0
    encargo = False
    salario = False
    local = False
    method = ''

    def on_enter(self, *args):
        print('Local id do usuario: ', self.local_id)
        print('Token id do usuario: ', self.token_id)
        self.menu_states()
        self.menu_citys()
        self.menu_functions()

    def menu_functions(self):
        # Abrir um popup de menu para a pessoa escolher o seu estado
        states = [
                "Mestre de Obras", "Engenheiro Civil", "Técnico em Edificações", "Pedreiro",
                "Servente de Pedreiro", "Eletricista", "Encanador", "Carpinteiro",
                "Armador de Ferragem", "Pintor de Obras", "Gesseiro", "Azulejista",
                "Marmorista", "Marceneiro", "Serralheiro", "Vidraceiro", "Operador de Betoneira",
                "Operador de Grua", "Topógrafo", "Geotécnico", "Calceteiro", "Pavimentador",
                "Refrigeração e Climatização", "Técnico em Segurança do Trabalho", "Paisagista"
            ]

        menu_itens = []
        position = 0
        for state in states:
            position += 1
            row = {'text': state, 'on_release': lambda x=state: self.replace_function(x)}
            menu_itens.append(row)

        self.menu2 = MDDropdownMenu(
            caller=self.ids.card_function,
            items=menu_itens,
            position='bottom',
            width_mult=5,
            max_height='400dp',
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            # Adicionando personalizações estéticas
            elevation=8,
            radius=[10, 10, 10, 10],
            border_margin=12,
            ver_growth="down",
            hor_growth="right",
        )

        # Estilizando os itens do menu
        for item in menu_itens:
            item["font_style"] = "Subtitle1"
            item["height"] = dp(56)
            # Adicione ícones aos itens
            if "icon" not in item:
                item["icon"] = "checkbox-marked-circle-outline"
            item["divider"] = "Full"

    def replace_function(self, text):
        self.ids.function.text = text
        self.ids.function.text_color = get_color_from_hex('#FFFB46')
        self.menu2.dismiss()

    def screen_finalize(self):
        # Cria o MDCard
        self.card = MDCard(
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            line_color=(0.5, 0.5, 0.5, 1),  # Cor da borda
            theme_bg_color='Custom',
            md_bg_color='white',
            md_bg_color_disabled="white",

        )

        # Cria o layout relativo para organizar os elementos dentro do card
        relative_layout = MDRelativeLayout()

        # Adiciona a AsyncImage (imagem assíncrona)
        async_image = AsyncImage(
            source='https://res.cloudinary.com/dsmgwupky/image/upload/v1739053352/image_1_hkgebk.png',
            size_hint=(0.5, 0.5),
            pos_hint={'center_x': 0.5, 'center_y': 0.65}
        )
        relative_layout.add_widget(async_image)

        # Adiciona o primeiro MDLabel ("Tudo certo!!")
        label_title = MDLabel(
            text='Tudo certo!!',
            bold=True,
            halign='center',
            font_style='Headline',  # Equivalente a 'Headline'
            pos_hint={'center_x': 0.5, 'center_y': 0.47},
            theme_text_color='Custom',
            text_color=(0, 0, 0, 1)  # Cor preta
        )
        relative_layout.add_widget(label_title)

        # Adiciona o segundo MDLabel (mensagem de sucesso)
        label_message = MDLabel(
            text='Sua solicitação foi enviada para o banco de vagas.',
            font_style='Label',  # Equivalente a 'Label'
            halign='center',
            pos_hint={'center_x': 0.5, 'center_y': 0.4},
            padding=(20, 0),
            theme_text_color='Custom',
            text_color=(0.5, 0.5, 0.5, 1)  # Cor cinza
        )
        relative_layout.add_widget(label_message)

        # adiciona o botão para proxima pagina
        button = MDButton(
            MDButtonText(
                text='Ok',
                theme_text_color='Custom',
                text_color='white',
                halign='center',
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                font_style='Title',
                role='medium',
                bold=True
            ),
            theme_width='Custom',
            size_hint_x=.3,
            theme_bg_color='Custom',
            md_bg_color=[0.0, 1.0, 0.0, 1.0],
            pos_hint={'center_x': 0.5, 'center_y': 0.3},
        )
        self.ids['ok'] = button
        self.ids.ok.on_release = self.functions
        relative_layout.add_widget(button)
        # Adiciona o layout relativo ao card
        self.card.add_widget(relative_layout)

    def functions(self):
        # Get all the information
        state = self.ids.state.text
        city = self.ids.city.text
        profession = self.ids.function.text
        option_payment = self.method
        remunaration = self.ids.salary.text
        # apagando dados do state
        self.ids.state.text = 'Selecione um Estado'
        self.ids.state.text_color = 'white'

        # apagando dados do city
        self.ids.city.text = 'Selecione uma cidade'
        self.ids.city.text_color = 'white'

        # apagando dados da profissão
        self.ids.function.text = 'Selecione uma profissão'

        self._reset_payment_cards()

        # apagando dados do salario
        self.ids.salary.text = ''
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'FunctionsScreen'

    def menu_citys(self):
        menu_itens = []
        payments = ['Cidades indisponiveis']
        for payment in payments:
            row = {'text': payment, 'text_color': 'red'}
            menu_itens.append(row)

        self.menu_city = MDDropdownMenu(
            caller=self.ids.card_city,
            items=menu_itens,
            position='bottom'
        )

    def menu_states(self):
        # Abrir um popup de menu para a pessoa escolher o seu estado
        states = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS',
                  'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP',
                  'SE', 'TO'
                  ]


        menu_itens = []
        position = 0
        for state in states:
            position += 1
            row = {'text': state, 'on_release': lambda x=state: self.replace_state(x)}
            menu_itens.append(row)

        self.menu = MDDropdownMenu(
            caller=self.ids.card_state,
            items=menu_itens,
            position='bottom',
            pos_hint={'center_x': 0.5}
        )

    def replace_state(self, state):
        self.ids.city.text_color = 'white'
        self.ids.city.text = 'Selecione uma cidade'
        self.ids.state.text_color = get_color_from_hex('#FFFB46')
        self.ids.state.text = f'{state}'
        self.menu.dismiss()
        self.create_menu(state)

    def create_menu(self, state):

        menu_items = []

        state_functions = {
                'AC': acre,
                'AL': alagoas,
                'AP': amapa,
                'AM': amazonas,
                'BA': bahia,
                'CE': ceara,
                'DF': distrito_federal,
                'ES': espirito_santo,
                'GO': goias,
                'MA': maranhao,
                'MT': mato_grosso,
                'MS': mato_grosso_do_sul,
                'MG': minas_gerais,
                'PA': para,
                'PB': paraiba,
                'PR': parana,
                'PE': pernambuco,
                'PI': piaui,
                'RJ': rio_de_janeiro,
                'RN': rio_grande_do_norte,
                'RS': rio_grande_do_sul,
                'RO': rondonia,
                'RR': roraima,
                'SC': santa_catarina,
                'SP': sao_paulo,
                'SE': sergipe,
                'TO': tocantins
        }

        if state in state_functions:
            cities = state_functions[state]()
            for city in cities:
                row = {'text': city, 'on_release': lambda x=city: self.replace_city(x)}
                menu_items.append(row)
        else:
            print(f"Estado '{state}' não encontrado!")

        self.menu_city.clear_widgets()
        self.menu_city = MDDropdownMenu(
            caller=self.ids.card_city,
            items=menu_items,
            position='bottom',
            pos_hint={'center_x': 0.5}
        )

    def step_one(self):
        if self.ids.state.text in 'Selecione um Estado':
            self.menu.open()
            return

        if self.ids.city.text in 'Selecione uma cidade':
            self.menu_city.open()
            return

        if self.ids.function.text in 'Selecione uma profissão':
            self.menu2.open()
            return

        if not self.ids.salary.text:
            self.ids.salary.focus = True
            return

        if not self.method:
            self.show_snackbar()
            return

        print('Esta tudo preenchido', self.method)
        self.step_two()

    def show_snackbar(self) -> None:
        """Exibe um Snackbar informativo."""
        MDSnackbar(
            MDSnackbarText(
                text="Por favor preencha o metodo de pagamento",
                theme_text_color='Custom',
                text_color='black',
                bold=True
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            halign='center',
            size_hint_x=0.88,
            theme_bg_color='Custom',
            background_color=get_color_from_hex('#F3DE8A')
        ).open()

    def step_two(self):
        # Get all the information
        state = self.ids.state.text
        city = self.ids.city.text
        option_payment = self.method
        remunaration = self.ids.salary.text
        salary = 0
        if option_payment not in 'Negociar':
            salary = int(remunaration)

        # Pass the information to a database
        data = {
            'Contractor': self.contractor,
            'State': state,
            'key': f'{self.key}',
            'IdLocal': f"{self.local_id}",
            'City': city,
            'Option Payment': option_payment,
            'Salary': salary,
            'occupation': self.ids.function.text,
            'requests': "[]",
            "decline": "[]",
            'email': self.email,
            'telephone': self.telephone,
            'company': self.company
        }
        # Make a request to the database passing the dictionary
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Functions/.json?auth={self.token_id}'
        UrlRequest(
            url,
            method='POST',
            req_body=json.dumps(data),
            req_headers={'Content-Type': 'Application/json'},
            on_success=self.finalize
        )

    def _reset_payment_cards(self) -> None:
        """Reseta as cores de todos os cartões de método de pagamento."""
        cards = ['card_week', 'card_day', 'card_month', 'card_bricklayer']
        for card in cards:
            self.ids[card].line_color = (255, 255, 255, 0.2)

    def _update_payment_method(self, method: str) -> None:
        """Atualiza o método de pagamento e destaca o cartão correspondente."""
        self._reset_payment_cards()
        self.method = method

        # Mapeia método para ID do cartão correspondente
        card_map = {
            'Diaria': 'card_day',
            'Semanal': 'card_week',
            'Mensal': 'card_month',
            'Empreita': 'card_bricklayer'
        }

        # Destaca o cartão selecionado
        if method in card_map:
            self.ids[card_map[method]].line_color = 'white'

    # Métodos para seleção de método de pagamento
    def click_day(self) -> None:
        """Seleciona método de pagamento diário."""
        self._update_payment_method('Diaria')

    def click_week(self) -> None:
        """Seleciona método de pagamento semanal."""
        self._update_payment_method('Semanal')

    def click_month(self) -> None:
        """Seleciona método de pagamento mensal."""
        self._update_payment_method('Mensal')

    def click_bricklayer(self) -> None:
        """Seleciona método de pagamento por empreita."""
        self._update_payment_method('Empreita')

    def finalize(self, req, result):
        self.functions()

    def replace_city(self, city):
        self.ids.city.text_color = get_color_from_hex('#FFFB46')
        self.ids.city.text = city
        self.menu_city.dismiss()

    def page(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'FunctionsScreen'
