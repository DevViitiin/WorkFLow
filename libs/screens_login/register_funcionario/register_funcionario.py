import json

import bcrypt
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import SlideTransition
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
from kivymd.uix.button import MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.progressindicator import MDCircularProgressIndicator
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText


class RegisterFuncionario(MDScreen):
    lobo = ''

    def on_enter(self, *args):
        # Definindo o ícone de erro para as telas
        icone_erro = MDIconButton(
            icon='alert-circle',
            theme_font_size='Custom',
            font_size='55sp',
            theme_icon_color='Custom',
            pos_hint={'center_x': .5, 'center_y': .6},
            icon_color='red'  # Cor vermelha para representar o erro
        )
        self.ids['error'] = icone_erro

        # Definindo o ícone de acerto para as telas
        icone_acerto = AsyncImage(
            source='https://res.cloudinary.com/dsmgwupky/image/upload/v1732733742/image_1_blzg3r.png',
            size_hint=(None, None),
            size=("100dp", "150dp"),
            pos_hint={"center_x": 0.5, "center_y": 0.65},
            allow_stretch=True
        )
        self.ids['acerto'] = icone_acerto

        # Definindo o MDCard onde vai ficar todo o corpo do layout
        self.card = MDCard(
            id='carregando',
            style='elevated',
            size_hint=(1, 1),
            pos_hint={"center_y": 0.5, "center_x": 0.5},
            padding="16dp",
            md_bg_color=(1, 1, 1, 1),
            theme_bg_color="Custom",
            theme_shadow_offset="Custom",
            shadow_offset=(1, -2),
            theme_shadow_softness="Custom",
            shadow_softness=1,
            theme_elevation_level="Custom",
            elevation_level=2
        )
        self.ids['card'] = self.card
        self.card.bind(on_release=self.page)

        # Definindo o RelativeLayout onde todo o corpo será posicionado
        relative = MDRelativeLayout()
        self.ids['relative'] = relative

        # Definindo o CircularProgressIndicator onde o usuário vai ter o carregamento visual
        circle = MDCircularProgressIndicator(
            size_hint=(None, None),
            size=("60dp", "60dp"),
            pos_hint={'center_x': .5, 'center_y': .6}
        )
        self.ids['progress'] = circle

        # Definindo o Label com texto carregando onde o usuário vai ter o indicador visual
        label = MDLabel(
            text='Carregando...',
            font_style='Title',
            halign='center',
            bold=True,
            text_color='black',
            pos_hint={'center_x': .5, 'center_y': .5}
        )
        self.ids['texto_carregando'] = label
        relative.add_widget(circle)
        relative.add_widget(label)
        self.card.add_widget(relative)

    def etapa1(self):
        if self.ids.email.text == '':
            print('Não esta errado o formato')
            MDSnackbar(
                MDSnackbarText(
                    text='O formato do email não e valido',
                    theme_text_color='Custom',
                    text_color='white',
                    bold=True,
                    halign='right',
                    pos_hint={'center_x': 0.5, 'center_y': 0.5}

                ),
                duration=3,
                size_hint_x=.75,
                radius=[dp(20), dp(20), dp(20), dp(20)],
                pos_hint={'center_x': 0.5, 'center_y': 0.03},
                theme_bg_color='Custom',
                background_color=get_color_from_hex('#00b894')
            ).open()

        else:
            if not self.ids.email.error:
                if self.ids.senha.text == '':
                    self.ids.senha.focus = True

                else:
                    print('Preenchidos')
                    self.pre_step()
            else:
                print('Não esta errado o formato')
                MDSnackbar(
                    MDSnackbarText(
                        text='O formato do email não e valido'
                    ),
                    duration=3,
                    theme_bg_color='Custom',
                    md_bg_color=get_color_from_hex('#7DDF64')
                ).open()

    def pre_step(self):
        print('Iniciando a requisição')
        api_key = "AIzaSyA3vFR2WgCdBsyIIL1k9teQNZTi4ZAzhtg"
        email = f"{self.ids.email.text}"
        password = f"{self.ids.senha.text}"

        login_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        headers = {"Content-Type": "application/json"}

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
        UrlRequest(
            url,
            req_body=json.dumps(payload),
            req_headers=headers,
            method='POST',
            on_success=self.get_name,
            on_error=self.email_exists,
            on_failure=self.email_exists,
            on_cancel=self.email_exists
        )

    def email_exists(self, req, result):
        print('Erro: ', result)
        self.ids.email.error = True
        self.ids.email.text = ''

        MDSnackbar(
            MDSnackbarText(
                text='Usuario ja existente',
                theme_text_color='Custom',
                text_color='white',
                bold=True,
                halign='right',
                pos_hint={'center_x': 0.5, 'center_y': 0.5}

            ),
            duration=3,
            size_hint_x=.75,
            radius=[dp(20),dp(20),dp(20),dp(20)],
            pos_hint={'center_x': 0.5, 'center_y': 0.03},
            theme_bg_color='Custom',
            background_color=get_color_from_hex('#00b894')
        ).open()

    def get_name(self, req, result):
        """Agora que eu ja criei a conta vou criar o local onde vai ficar os dados do funcioanrio no /users"""

        id_token = result['idToken']
        id_local = result['localId']
        print('Informações: ', result)
        self.etapa2(id_token, id_local)

    def etapa2(self, id_token, local_id):
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{local_id}.json?auth={id_token}'
        hashed_password = self.ids.senha.text.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password=hashed_password, salt=salt).decode('utf-8')
        data = {"Name": 'Não definido',
                'avatar': 'https://res.cloudinary.com/dsmgwupky/image/upload/v1726685784/a8da222be70a71e7858bf752065d5cc3-fotor-20240918154039_dokawo.png',
                'coextistence': 0,
                'contractor': '',
                'day': "",
                'data_contractor': '',
                'request_payment': 'False',
                'days_work': 0,
                'contractor_month': 1,
                'payments': "[]",
                'receiveds': "[]",
                'confirm_payments': "[]",
                'request': 'False',
                'effiency': 0,
                'email': f'{self.ids.email.text}',
                'function': 'Não definido',
                'method_salary': '',
                'punctuality': '',
                'state': '',
                'city': '',
                'salary': 0,
                'scale': '',
                'skills': "[]",
                'sumary': 'Não definido',
                'telefone': 'Não definido',
                'tot': 0,
                'ultimate': '',
                'valleys': "[]",
                'week_1': 0,
                'week_2': 0,
                'week_3': 0,
                'week_4': 0,
                'work_days_week1': "[]",
                'work_days_week2': "[]",
                'work_days_week3': "[]",
                'work_days_week4': "[]",
                }

        UrlRequest(
            f'{url}',
            method='PUT',
            on_success=self.cadastrado,
            req_body=json.dumps(data),
            req_headers={'Content-Type': 'application/json'}
        )

    def cadastrado(self, req, result):
        app = MDApp.get_running_app()
        print(self.lobo)
        screenmanager = app.root
        perfil = screenmanager.get_screen('PrincipalScreenEmployee')
        perfil.employee_name = result['Name']
        perfil.employee_function = result['function']
        perfil.employee_mail = result['email']
        perfil.employee_telephone = result['telefone']
        perfil.avatar = result['avatar']
        perfil.employee_summary = result['sumary']
        perfil.skills = result['skills']
        perfil.request = eval(result['request'])
        perfil.city = result['city']
        perfil.state = result['state']
        perfil.contractor = result['contractor']
        perfil.key = self.lobo
        print('key passada pra base ', self.lobo)
        self.lobo = ''
        screenmanager.transition = SlideTransition(direction='right')
        screenmanager.current = 'PrincipalScreenEmployee'

    def page(self, instance):
        print('passo')

    def voltar(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'ChoiceAccount'
