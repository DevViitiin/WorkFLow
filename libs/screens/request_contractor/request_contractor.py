import ast

from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty
from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.fitimage import FitImage
from kivymd.uix.label import MDIcon, MDLabel
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen


class RequestContractor(MDScreen):
    key = StringProperty()
    username = StringProperty()
    tab_nav_state = StringProperty('request')
    name_contractor = StringProperty()
    current_nav_state = StringProperty('request')
    click = 0

    def on_enter(self, *args):
        print(self.name_contractor)
        self.ids.main_scroll.clear_widgets()
        if self.tab_nav_state in 'received':
            self.receiveds()
            return

        self.requests()

    def receiveds(self):
        url = 'https://obra-7ebd9-default-rtdb.firebaseio.com/Functions/.json'
        UrlRequest(
            url,
            on_success=self.add_receiveds
        )

    def add_receiveds(self, req, resulti):
        self.ids.main_scroll.clear_widgets()
        showed = []
        for key, received in resulti.items():
            if self.key in received['key']:
                """ significa que essa função e requisição minha"""
                requests = ast.literal_eval(received['requests'])

                for request in requests:
                    showed.append(request)
                    UrlRequest(
                        f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{request}/.json',
                        on_success=lambda req, result, employee_key=request, r=key,
                                          result_function=received: self.employee(req, result, employee_key, r,
                                                                                  result_function)
                    )
        if not showed:
            self.show_no_requests_found()

    def show_no_requests_found(self):
        """Common method to display the 'no requests found' message and image"""
        self.ids.main_scroll.clear_widgets()

        # Create a container for centered content
        container = MDBoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height="300dp",
            pos_hint={'center_x': 0.5}
        )

        # Add image
        image = AsyncImage(
            source='https://res.cloudinary.com/dsmgwupky/image/upload/v1746223701/aguiav2_pnq6bl.png',
            size_hint=(0.65, 0.65),
            pos_hint={'center_x': 0.5, 'center_y': 0.2}
        )
        container.add_widget(image)
        self.ids.main_scroll.add_widget(container)

    def employee(self, req, result, key_employee, request_key, resulti):
        """Adiciona um card com as informações do funcionario"""
        try:
            card = self.create_profile_card(
                result['Name'],
                result['function'],
                4,
                result['avatar'],
                result['email'],
                result['city'],
                result['skills'],
                result['state'],
                result['sumary'],
                result['telefone'],
                key_employee,
                request_key,
                resulti
            )
            self.ids.main_scroll.add_widget(card)
        except:
            print('Resultado vazio')

    def create_profile_card(self, name, profession, rating, av, email, city, skills, state, sumary, telephone,
                            key_employee, key_request, resulti):
        # Card principal com bordas arredondadas
        card_layout = MDBoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height="180dp",
            padding="15dp",
            radius=20,
            theme_line_color='Custom',
            line_color='grey',
            md_bg_color=(1, 1, 1, 1),
            pos_hint={'center_x': 0.5}
        )

        # Layout para informações e foto
        info_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=0.8,
            spacing="5dp",
            pos_hint={'center_y': 0.8}
        )
        card_layout.add_widget(info_layout)

        # Foto de perfil
        profile_box = MDBoxLayout(
            size_hint_x=0.5,
            padding="5dp"
        )
        info_layout.add_widget(profile_box)

        # Imagem circular
        profile_image = MDRelativeLayout(
            size_hint=(1, 1)
        )

        # Avatar - usando FitImage para imagem circular
        avatar = FitImage(
            source=f"{av}",  # Substitua pelo caminho da sua imagem
            size_hint=(1, 0.95),
            radius=[100, ]  # Valor para tornar a imagem circular
        )
        profile_image.add_widget(avatar)
        profile_box.add_widget(profile_image)

        # Informações do profissional
        text_layout = MDBoxLayout(
            orientation='vertical',
            size_hint_x=0.75,
            spacing="5dp",
            padding=["5dp", 0, 0, 0],
            pos_hint={'center_y': 0.6}
        )
        info_layout.add_widget(text_layout)

        # Nome do profissional
        name_label = MDLabel(
            text=name,
            font_style='Title',
            role='medium',
            bold=True,
            adaptive_height=True
        )
        text_layout.add_widget(name_label)

        # Profissão
        profession_label = MDLabel(
            text=profession,
            font_style='Title',
            role='medium',
            theme_text_color="Secondary",
            adaptive_height=True
        )
        text_layout.add_widget(profession_label)

        # Layout para estrelas
        stars_layout = MDBoxLayout(
            orientation='horizontal',
            adaptive_height=True,
            spacing="2dp"
        )
        text_layout.add_widget(stars_layout)

        # Adicionar estrelas com base na avaliação (de 0 a 5)
        for i in range(5):
            star_icon = MDIcon(
                icon="star",
                theme_icon_color="Custom",
                icon_color=(1, 0.8, 0, 1) if i < rating else (0.7, 0.7, 0.7, 1)
                # Amarelo para estrelas preenchidas, cinza para vazias
            )
            stars_layout.add_widget(star_icon)

        # Layout para o botão
        button_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=0.3,
            padding=[0, "10dp", 0, 0],
            pos_hint={'right': 1}
        )
        card_layout.add_widget(button_layout)

        # Espaço vazio à esquerda para alinhar o botão à direita
        spacer = MDBoxLayout(
            size_hint_x=0.6
        )
        button_layout.add_widget(spacer)

        # Botão "Ver perfil"
        profile_button = MDButton(
            MDButtonText(
                text="Ver perfil",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
            ),
            theme_bg_color='Custom',
            md_bg_color=(0.16, 0.44, 0.95, 1),  # Azul como na imagem
            size_hint_x=0.4,
            pos_hint={'center_y': 0.4}
        )
        profile_button.on_release = lambda name_employee=name, perfil=av, city_employee=city, function=profession, email_employee=email, skill=skills, state_employee=state, summary=sumary, telefone=telephone, key_employees=key_employee, keys=key_request,result=resulti: self._upload_employee(name_employee, perfil, city_employee,
                                                                                 function, email_employee, skills,
                                                                                 state_employee, summary, telefone,
                                                                                 key_employees, keys, result)
        button_layout.add_widget(profile_button)

        return card_layout

    def _upload_employee(self, name, avatar, city, profession, email, skills, state, sumary, telefone, key_employee,
                         key_request, result):
        app = MDApp.get_running_app()
        screenmanager = app.root
        hiring = screenmanager.get_screen('HiringProfile')
        # Informações da função
        hiring.salary = f"{result['Salary']}"
        hiring.function = result['occupation']
        hiring.method_salary = result['Option Payment']
        hiring.scale = '5x2'

        # Informações do funcionario
        hiring.avatar = avatar
        hiring.employee_name = name
        hiring.employee_function = profession
        hiring.employee_mail = email
        hiring.employee_telephone = telefone
        hiring.key = key_employee
        hiring.key_contractor = self.key
        hiring.username = self.name_contractor
        hiring.key_requests = key_request
        hiring.state = state
        hiring.city = city
        hiring.employee_summary = sumary
        hiring.skills = skills
        screenmanager.transtion = SlideTransition(direction='right')
        screenmanager.current = 'HiringProfile'

    def workflow(self, screen):
        self.click += 1

        # Impede recarregar widgets se já estiver na aba certa
        if screen == self.tab_nav_state:
            return

        # Atualiza o estado da aba atual
        self.tab_nav_state = screen
        self.ids.main_scroll.clear_widgets()

        # Chama a função correta conforme a aba
        if screen == 'received':
            self.receiveds()

        elif screen == 'decline':
            self.decline_requests()

        elif screen == 'request':
            self.requests()

        # Reinicia o contador de clique
        self.click = 0

    def requests(self):
        url = 'https://obra-7ebd9-default-rtdb.firebaseio.com/requets/.json'
        UrlRequest(
            url,
            on_success=self.add_requests
        )

    def add_requests(self, req, result):
        self.ids.main_scroll.clear_widgets()
        print('Solicitações: ', result)
        solict = []
        for key, request in result.items():
            requests = ast.literal_eval(request['requests'])
            print('Aqui está as requisições: ', requests)
            print('Aqui está a minha key: ', self.key)
            if requests:
                if self.key in requests:
                    print(self.key)
                    solict.append(self.key)
                    """ significa que essa eu enviei uma solicitação para este homen/ser/funcionario/excelente"""
                    print('não aceito')
                    UrlRequest(
                        f"https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{request['key']}/.json",
                        on_success=self.request_employee
                    )

        if not solict:
            self.show_no_requests_found()

    def request_employee(self, req, result):
        """ Adiciona as vagas que foram recusadas"""
        if result:
            card = self.create_pending_profile_card(result['Name'], result['function'])
            self.ids.main_scroll.add_widget(card)

    def create_pending_profile_card(self, name, profession, status="Solicitação enviada"):
        # Card principal com bordas arredondadas - mudando para um tema amarelo/laranja suave
        card_layout = MDBoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height="180dp",
            padding="15dp",
            radius=20,
            theme_line_color='Custom',
            line_color='#FFA726',  # Laranja/âmbar para indicar pendente
            md_bg_color=(1, 0.98, 0.94, 1),  # Fundo levemente amarelado
            pos_hint={'center_x': 0.5}
        )

        # Layout para informações e foto
        info_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=0.8,
            spacing="5dp",
            pos_hint={'center_y': 0.8}
        )
        card_layout.add_widget(info_layout)

        # Foto de perfil com borda amarela
        profile_box = MDBoxLayout(
            size_hint_x=0.5,
            padding="5dp"
        )
        info_layout.add_widget(profile_box)

        # Container da imagem
        profile_image = MDRelativeLayout(
            size_hint=(1, 1)
        )

        # Borda laranja para o avatar
        avatar_border = MDCard(
            size_hint=(1, 0.95),
            radius=[100, ],
            md_bg_color=(0.98, 0.65, 0.15, 1),  # Laranja/âmbar
            padding="2dp"
        )

        # Avatar normal
        avatar_image = AsyncImage(
            source=f"https://res.cloudinary.com/dsmgwupky/image/upload/v1744418245/image__2_-removebg-preview_szaoip.png",
            size_hint=(1, 1),
        )

        avatar_border.add_widget(avatar_image)
        profile_image.add_widget(avatar_border)
        profile_box.add_widget(profile_image)

        # Ícone de pendente sobreposto ao avatar
        pending_icon = MDIcon(
            icon="clock",
            theme_icon_color="Custom",
            icon_color=(0.98, 0.65, 0.15, 0.9),
            pos_hint={"center_x": 0.85, "center_y": 0.85},
            font_size="24sp"
        )
        profile_image.add_widget(pending_icon)

        # Informações do profissional
        text_layout = MDBoxLayout(
            orientation='vertical',
            size_hint_x=0.75,
            spacing="5dp",
            padding=["5dp", 0, 0, 0],
            pos_hint={'center_y': 0.6}
        )
        info_layout.add_widget(text_layout)

        # Nome do profissional
        name_label = MDLabel(
            text=name,
            font_style='Title',
            role='medium',
            bold=True,
            theme_text_color="Custom",
            text_color=(0.4, 0.4, 0.4, 1),  # Texto normal (escuro)
            adaptive_height=True
        )
        text_layout.add_widget(name_label)

        # Profissão
        profession_label = MDLabel(
            text=profession,
            font_style='Title',
            role='medium',
            theme_text_color="Secondary",
            adaptive_height=True
        )
        text_layout.add_widget(profession_label)

        # Status da solicitação
        status_layout = MDBoxLayout(
            orientation='horizontal',
            adaptive_height=True,
            spacing="2dp",
        )
        text_layout.add_widget(status_layout)

        # Ícone de relógio
        status_icon = MDIcon(
            icon="email-send",
            theme_icon_color="Custom",
            icon_color=(0.98, 0.65, 0.15, 1)  # Laranja/âmbar
        )
        status_layout.add_widget(status_icon)

        # Texto de status
        status_label = MDLabel(
            text=status,
            theme_text_color="Custom",
            text_color=(0.98, 0.65, 0.15, 1),  # Laranja/âmbar
            adaptive_height=True,
            bold=True,
            theme_font_size='Custom',
            font_size='12sp'
        )
        status_layout.add_widget(status_label)

        # Layout para o botão
        button_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=0.3,
            padding=[0, "10dp", 0, 0],
            pos_hint={'right': 1}
        )
        card_layout.add_widget(button_layout)

        # Espaço vazio à esquerda para alinhar o botão à direita
        spacer = MDBoxLayout(
            size_hint_x=0.6
        )
        button_layout.add_widget(spacer)

        # Botão "Aguardando resposta" em vez de "Buscar outro"
        profile_button = MDButton(
            MDButtonText(
                text="Aguardando",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
            ),
            theme_bg_color='Custom',
            md_bg_color=(0.98, 0.65, 0.15, 1),  # Laranja/âmbar
            size_hint_x=0.4,
            pos_hint={'center_y': 0.4}
        )
        button_layout.add_widget(profile_button)

        return card_layout

    def decline_requests(self):
        url = 'https://obra-7ebd9-default-rtdb.firebaseio.com/requets/.json'
        UrlRequest(
            url,
            on_success=self.add_requests_decline
        )

    def add_requests_decline(self, req, result):
        dc = []
        self.ids.main_scroll.clear_widgets()
        for key, decline in result.items():
            declines = ast.literal_eval(decline['declines'])
            print(declines)

            if self.key in declines:
                """ significa que essa eu fui recusado pelo funcionario"""
                print('não aceito')
                dc.append(self.key)
                UrlRequest(
                    f"https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{decline['key']}/.json",
                    on_success=self.decline_employee
                )
        if not dc:
            self.show_no_requests_found()

    def decline_employee(self, req, result):
        """ Adiciona as vagas que foram recusadas"""
        if result:
            card = self.create_negative_profile_card(result['Name'], result['function'])
            self.ids.main_scroll.add_widget(card)

    def create_negative_profile_card(self, name, profession, reason="Recusou a solicitação"):
        # Card principal com bordas arredondadas - mudando para um tema vermelho suave
        card_layout = MDBoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height="180dp",
            padding="15dp",
            radius=20,
            theme_line_color='Custom',
            line_color='#FF5252',  # Vermelho para indicar recusa
            md_bg_color=(1, 0.95, 0.95, 1),  # Fundo levemente avermelhado
            pos_hint={'center_x': 0.5}
        )

        # Layout para informações e foto
        info_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=0.8,
            spacing="5dp",
            pos_hint={'center_y': 0.8}
        )
        card_layout.add_widget(info_layout)

        # Foto de perfil com borda vermelha
        profile_box = MDBoxLayout(
            size_hint_x=0.5,
            padding="5dp"
        )
        info_layout.add_widget(profile_box)

        # Container da imagem
        profile_image = MDRelativeLayout(
            size_hint=(1, 1)
        )

        # Borda vermelha para o avatar
        avatar_border = MDCard(
            size_hint=(1, 0.95),
            radius=[100, ],
            md_bg_color=(0.9, 0.2, 0.2, 1),  # Vermelho
            padding="2dp"
        )

        # Avatar em escala de cinza para indicar indisponibilidade
        avatar_image = AsyncImage(
            source=f"https://res.cloudinary.com/dsmgwupky/image/upload/v1744416471/image_1_gifxvm.png",
            size_hint=(1, 1),
        )

        avatar_border.add_widget(avatar_image)
        profile_image.add_widget(avatar_border)
        profile_box.add_widget(profile_image)

        # Ícone de recusa sobreposto ao avatar
        decline_icon = MDIcon(
            icon="close-circle",
            theme_icon_color="Custom",
            icon_color=(0.9, 0.2, 0.2, 0.9),
            pos_hint={"center_x": 0.85, "center_y": 0.85},
            font_size="24sp"
        )
        profile_image.add_widget(decline_icon)

        # Informações do profissional
        text_layout = MDBoxLayout(
            orientation='vertical',
            size_hint_x=0.75,
            spacing="5dp",
            padding=["5dp", 0, 0, 0],
            pos_hint={'center_y': 0.6}
        )
        info_layout.add_widget(text_layout)

        # Nome do profissional
        name_label = MDLabel(
            text=name,
            font_style='Title',
            role='medium',
            bold=True,
            theme_text_color="Custom",
            text_color=(0.7, 0.1, 0.1, 1),  # Vermelho escuro
            adaptive_height=True
        )
        text_layout.add_widget(name_label)

        # Profissão
        profession_label = MDLabel(
            text=profession,
            font_style='Title',
            role='medium',
            theme_text_color="Secondary",
            adaptive_height=True
        )
        text_layout.add_widget(profession_label)

        # Motivo da recusa
        reason_layout = MDBoxLayout(
            orientation='horizontal',
            adaptive_height=True,
            spacing="2dp",

        )
        text_layout.add_widget(reason_layout)

        # Ícone de recusa
        decline_label_icon = MDIcon(
            icon="cancel",
            theme_icon_color="Custom",
            icon_color=(0.9, 0.2, 0.2, 1)
        )
        reason_layout.add_widget(decline_label_icon)

        # Texto de recusa
        reason_label = MDLabel(
            text=reason,
            theme_text_color="Custom",
            text_color=(0.9, 0.2, 0.2, 1),
            adaptive_height=True,
            bold=True,
            theme_font_size='Custom',
            font_size='12sp'
        )
        reason_layout.add_widget(reason_label)

        # Layout para o botão
        button_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=0.3,
            padding=[0, "10dp", 0, 0],
            pos_hint={'right': 1}
        )
        card_layout.add_widget(button_layout)

        # Espaço vazio à esquerda para alinhar o botão à direita
        spacer = MDBoxLayout(
            size_hint_x=0.6
        )
        button_layout.add_widget(spacer)

        # Botão "Outro profissional" em vez de "Ver perfil"
        profile_button = MDButton(
            MDButtonText(
                text="Buscar outro",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
            ),
            theme_bg_color='Custom',
            md_bg_color=(0.9, 0.2, 0.2, 1),  # Vermelho
            size_hint_x=0.4,
            pos_hint={'center_y': 0.4}
        )
        profile_button.on_release = self._next_vacancy_bank
        button_layout.add_widget(profile_button)

        return card_layout

    def _next_vacancy_bank(self):
        app = MDApp.get_running_app()
        screenmanager = app.root
        bank = screenmanager.get_screen('VacancyContractor')
        bank.key_contractor = self.key
        bank.username = self.name_contractor
        bank.ids.table.active = False
        bank.ids.perfil.active = False
        bank.ids.search.active = True
        bank.ids.request.active = False
        bank.current_nav_state = 'search'
        screenmanager.transtion = SlideTransition(direction='left')
        screenmanager.current = 'VacancyContractor'

    def search(self):
        app = MDApp.get_running_app()
        print('Passando essa key pra tela de search:', self.key)
        screen_manager = app.root
        screen_manager.transition = SlideTransition(direction='right')
        bricklayer = screen_manager.get_screen('VacancyContractor')
        bricklayer.key_contractor = self.key
        bricklayer.username = self.name_contractor
        bricklayer.ids.table.active = False
        bricklayer.ids.perfil.active = False
        bricklayer.ids.search.active = True
        bricklayer.ids.request.active = False
        bricklayer.current_nav_state = 'search'
        screen_manager.current = 'VacancyContractor'

    def bricklayer(self):
        app = MDApp.get_running_app()
        screen_manager = app.root
        screen_manager.transition = SlideTransition(direction='right')
        bricklayer = screen_manager.get_screen('Table')
        bricklayer.key = self.key
        bricklayer.username = self.name_contractor
        bricklayer.ids.table.active = True
        bricklayer.ids.perfil.active = False
        bricklayer.ids.search.active = False
        bricklayer.ids.request.active = False
        bricklayer.current_nav_state = 'table'
        screen_manager.current = 'Table'

    def passo(self):
        app = MDApp.get_running_app()
        print(self.name_contractor, )
        screen_manager = app.root
        bricklayer = screen_manager.get_screen('Perfil')
        bricklayer.key = self.key
        bricklayer.username = self.name_contractor
        bricklayer.ids.table.active = False
        bricklayer.ids.perfil.active = True
        bricklayer.ids.search.active = False
        bricklayer.ids.request.active = False
        bricklayer.current_nav_state = 'perfil'
        screen_manager.transition = SlideTransition(direction='left')
        screen_manager.current = 'Perfil'