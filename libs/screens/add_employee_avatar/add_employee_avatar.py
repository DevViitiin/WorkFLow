import json
import cloudinary
#from android.permissions import request_permissions, check_permission, Permission
from kivymd.app import MDApp
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty, get_color_from_hex
from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import SlideTransition
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from plyer import filechooser
from datetime import datetime
from kivy.clock import Clock


class EmployeeAvatar(MDScreen):
    employee_name = StringProperty()
    function = StringProperty()
    token_id = StringProperty()
    email = StringProperty()
    api_key = StringProperty()
    local_id = StringProperty()
    refresh_token = StringProperty()
    password = StringProperty()
    method_salary = StringProperty()
    salary = StringProperty()
    scale = StringProperty()
    perfil = ''
    dont = 'Sim'
    # Funcionario
    local_id_employee = StringProperty()
    FIREBASE_URL = 'https://obra-7ebd9-default-rtdb.firebaseio.com'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print('FUnção', self.function)
        print('Metodo de recebimento', self.method_salary)
        print('Valor do salario', self.salary)
        
        print('Escala do trabalho', self.scale)
        cloudinary.config(
            cloud_name="dsmgwupky",
            api_key="256987432736353",
            api_secret="K8oSFMvqA6N2eU4zLTnLTVuArMU"
        )
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
            text='O funcionário foi adicionado com sucesso. Verifique na sua tabela.',
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
        self.ids.ok.on_release = self.back_table
        relative_layout.add_widget(button)
        # Adiciona o layout relativo ao card
        self.card.add_widget(relative_layout)
        #self.check_and_request_permissions()

    # def check_and_request_permissions(self):
    #     # Lista das permissões que você precisa
    #     needed_permissions = [
    #         Permission.WRITE_EXTERNAL_STORAGE,
    #         Permission.READ_EXTERNAL_STORAGE,
    #     ]

    #     #Verifica quais ainda não estão concedidas
    #     missing_permissions = [p for p in needed_permissions if not check_permission(p)]

    # # Se tiver faltando, solicita
    #     if missing_permissions:
    #         request_permissions(missing_permissions)
    #         self.show_error('Conceda as permissões necessarias')
    #         Clock.schedule_once(lambda dt: self.show_error('Para poder definir novas fotos de perfil'), 1.5)
    #         self.ids.image_card.disable = True
    #     else:
    #         print("Todas as permissões já foram concedidas!")  
    #         self.ids.image_card.disable = False

    def on_enter(self):
        self.verific_token()
        self.check_and_request_permissions()
        self.event_token = Clock.schedule_interval(self.verific_token, 300)
        print('Local id: ',self.local_id)
        print('Senha ja em hash: ', self.password)
        self.ids.name.text = self.employee_name
        self.ids.scale.text = f'Escala: {self.scale}'
        self.ids.text.text = f'Trabalha de {self.function} ganhando R${self.salary} ({self.method_salary})'

    # verificando e trocando token_id ----------------------------------------------------------------------------------
    def verific_token(self, *args):
        print('🔎 verificando token...')
        UrlRequest(
            f"{self.FIREBASE_URL}/Users/{self.local_id}.json?auth={self.token_id}",
            on_success=self.on_success,
            on_failure=self.on_failure,
            on_error=self.on_failure,
            method="GET"
        )

    def on_failure(self, req, result):
        print('❌ Token inválido, tentando atualizar...', result)
        self.refresh_id_token()  # chama atualização

    def on_success(self, req, result):
        print('✅ Token válido, usuário encontrado:', result)

    def show_message(self, message, color='#2196F3'):
        """Display a snackbar message"""
        MDSnackbar(
            MDSnackbarText(
                text=message,
                theme_text_color='Custom',
                text_color='white',
                bold=True
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            halign='center',
            size_hint_x=0.8,
            theme_bg_color='Custom',
            background_color=get_color_from_hex(color)
        ).open()

    def show_error(self, error_message):
        """Display an error message"""
        self.show_message(error_message, color='#FF0000')
        print(f"Error: {error_message}")

    # --- ATUALIZAÇÃO DO TOKEN ---
    def refresh_id_token(self):
        refresh_url = f"https://securetoken.googleapis.com/v1/token?key={self.api_key}"
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }
        data = "&".join([f"{k}={v}" for k, v in payload.items()])

        UrlRequest(
            refresh_url,
            on_success=self.on_refresh_success,
            on_failure=self.on_refresh_failure,
            on_error=self.on_refresh_failure,
            req_body=data,
            req_headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST"
        )

    def on_refresh_success(self, req, result):
        self.token_id = result["id_token"]
        self.refresh_token = result["refresh_token"]  # Firebase pode mandar de novo
        print("🔄 Token renovado com sucesso:", self.token_id)

    def on_refresh_failure(self, req, result):
        print("❌ Erro ao renovar token:", result)
        self.show_error('O token não foi renovado')
        Clock.schedule_once(self.show_error('Refaça login no aplicativo'), 1.5)
        
    def back_employee(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'Add'

    # Funções de imagem ------------------------------------------------------------------------------------------------

    def recortar_imagem_circular(self, imagem_path):
        try:
            # Upload da imagem com corte circular
            response = cloudinary.uploader.upload(
                imagem_path,
                public_id=self.employee_name,
                overwrite=True,
                transformation=[
                    {'width': 1000, 'height': 1000, 'crop': 'thumb', 'gravity': 'face', 'radius': 'max'}
                ]
            )
            self.perfil = response['secure_url']  # Retorna o URL da imagem cortada
            self.pre_step()

        except Exception as e:
            print(f"Erro ao cortar a imagem: {e}")
            return None

    def open_gallery(self):
        if self.dont == 'Não':
            print('Galeria não atualizada')
        else:
            '''Abre a galeria para selecionar uma imagem.'''
            try:
                filechooser.open_file(
                    filters=["*.jpg", "*.png", "*.jpeg"],  # Filtra por tipos de arquivo de imagem
                    on_selection=self.select_path  # Chama a função de callback ao selecionar o arquivo
                )
            except Exception as e:
                print("Erro ao abrir a galeria:", e)

    def select_path(self, selection):
        '''
        Callback chamada quando um arquivo é selecionado.

        :param selection: lista contendo o caminho do arquivo selecionado.
        '''
        if selection:
            path = selection[0]  # Obtém o caminho do arquivo
            self.recortar_imagem_circular(path)
            MDSnackbar(
                MDSnackbarText(
                    text=f"Arquivo selecionado: {path}",
                ),
                y=dp(24),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8,
            ).open()

    # manipulando o banco de dados -------------------------------------------------------------------------------------
    def pre_step(self):
        print('Iniciando a requisição')

        login_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.api_key}"
        payload = {
            "email": self.email,
            "password": self.password,
            "returnSecureToken": True
        }

        headers = {"Content-Type": "application/json"}

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.api_key}"
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

    def get_name(self, req, result):
        """Agora que eu ja criei a conta vou criar o local onde vai ficar os dados do funcioanrio no /users"""

        id_token = result['idToken']
        id_local = result['localId']
        self.etapa2(id_token, id_local)
    
    def email_exists(self, req, result):
        MDSnackbar(
            MDSnackbarText(
                text='O email já está cadastrado',
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

    def etapa2(self, id_token, id_local):
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{id_local}.json?auth={id_token}'
        month = datetime.today().month
        # Obtém a data atual
        data_atual = datetime.now()

        # Formata no padrão brasileiro
        data_formatada = data_atual.strftime('%d/%m/%Y')
        data = {
            'coexistence': 0,
            'day': "",
            'data_contractor': f'{data_formatada}',
            'request_payment': 'False',
            'days_work': 0,
            'contractor_month': month,
            'payments': "[]",
            'receiveds': "[]",
            'confirm_payments': "[]",
            'request': 'False',
            'effiency': 0,
            'email': f"{self.email}",
            'punctuality': '',
            'state': '',
            'city': '',
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
            'Name': self.employee_name,
            'function': self.function,
            'salary': self.salary,
            'avatar': self.perfil,
            'contractor': self.local_id,
            'method_salary': self.method_salary,
            'scale': self.scale,
        }

        UrlRequest(
            f'{url}',
            method='PUT',
            on_success=self.added_successfully,
            req_body=json.dumps(data),
            req_headers={'Content-Type': 'application/json'}
        )

    def added_successfully(self, req, result):
        print('Conseguir gerar o mano')
        self.perfil = 'https://res.cloudinary.com/dsmgwupky/image/upload/v1726685784/a8da222be70a71e7858bf752065d5cc3-fotor-20240918154039_dokawo.png'
        if self.card.parent:
            self.card.parent.remove_widget(self.card)  # Remove do pai anterior

        self.add_widget(self.card)

    def post_employ_no_avatar(self):
        print('Iniciando a requisição')

        login_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.api_key}"
        payload = {
            "email": self.email,
            "password": self.password,
            "returnSecureToken": True
        }

        headers = {"Content-Type": "application/json"}

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.api_key}"
        UrlRequest(
            url,
            req_body=json.dumps(payload),
            req_headers=headers,
            method='POST',
            on_success=self.get_name_no_avatar,
            on_error=self.email_exists,
            on_failure=self.email_exists,
            on_cancel=self.email_exists
        )
    def get_name_no_avatar(self, req, result):
        """Agora que eu ja criei a conta vou criar o local onde vai ficar os dados do funcioanrio no /users"""

        id_token = result['idToken']
        id_local = result['localId']
        print('Informações: ', result)
        self.etapa2_no_avatar(id_token, id_local)

    def etapa2_no_avatar(self, id_token, id_local):
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{id_local}.json?auth={id_token}'
        month = datetime.today().month
        # Obtém a data atual
        data_atual = datetime.now()

        # Formata no padrão brasileiro
        data_formatada = data_atual.strftime('%d/%m/%Y')
        data = {
            'coexistence': 0,
            'day': "",
            'contractor': self.local_id,
            'request_payment': 'False',
            'days_work': 0,
            'contractor_month': month,
            'data_contractor': f"{data_formatada}",
            'payments': "[]",
            'password': f"{self.password}",
            'receiveds': "[]",
            'confirm_payments': "[]",
            'request': 'False',
            'effiency': 0,
            'email': f"{self.email}",
            'punctuality': '',
            'state': '',
            'city': '',
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
            'Name': self.employee_name,
            'function': self.function,
            'salary': self.salary,
            'avatar': 'https://res.cloudinary.com/dsmgwupky/image/upload/v1731970845/image_3_uiwlog.png',
            'contractor': self.local_id,
            'method_salary': self.method_salary,
            'scale': self.scale,
        }

        UrlRequest(
            f'{url}',
            method='PUT',
            on_success=self.added_successfully,
            req_body=json.dumps(data),
            req_headers={'Content-Type': 'application/json'}
        )

    def back_table(self, *args):
        self.manager.transition = SlideTransition(direction='left')
        self.remove_widget(self.card)
        self.manager.current = 'Table'

    def back_page(self, *args):
        self.manager.transition = SlideTransition(direction='left')
        app = MDApp.get_running_app()
        screen_manager = app.root
        employee_avatar = screen_manager.get_screen('EmployeeAvatar')
        employee_avatar.employee_name = self.employee_name
        employee_avatar.function = self.function
        employee_avatar.salary = self.salary
        employee_avatar.contractor = self.contractor
        employee_avatar.method_salary = self.method_salary
        employee_avatar.scale = self.scale
        employee_avatar.token_id = self.token_id
        employee_avatar.api_key = self.api_key
        employee_avatar.email = self.email
        employee_avatar.local_id = self.local_id
        employee_avatar.refresh_id = self.refresh_token
        employee_avatar.password = self.password
        screen_manager.current = 'AddEmployeePassword'
