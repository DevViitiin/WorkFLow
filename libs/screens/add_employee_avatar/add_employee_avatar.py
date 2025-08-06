import json
import cloudinary
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty
from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import SlideTransition
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from plyer import filechooser


class EmployeeAvatar(MDScreen):
    employee_name = StringProperty()
    function = StringProperty()
    password = StringProperty()
    contractor = StringProperty()
    method_salary = StringProperty()
    salary = StringProperty()
    scale = StringProperty()
    perfil = ''
    dont = 'Sim'

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

    def on_enter(self):
        print('Senha ja em hash: ', self.password)
        self.ids.name.text = self.employee_name
        self.ids.scale.text = f'Escala: {self.scale}'
        self.ids.text.text = f'Trabalha de {self.function} ganhando R${self.salary} ({self.method_salary})'

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
            self.post_employee()
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
    def post_employee(self):
        print('Começando cadastro')
        url = 'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios'
        data = {
            'coextistence': 0,
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
            'email': 'Não definido',
            'punctuality': '',
            'state': '',
            'city': '',
            'password': f"{self.password}",
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
            'contractor': self.contractor,
            'method_salary': self.method_salary,
            'scale': self.scale,
        }

        UrlRequest(
            f'{url}/.json',
            req_body=json.dumps(data),
            method='POST',
            on_success=self.added_successfully
        )

    def added_successfully(self, req, result):
        self.perfil = 'https://res.cloudinary.com/dsmgwupky/image/upload/v1726685784/a8da222be70a71e7858bf752065d5cc3-fotor-20240918154039_dokawo.png'
        if self.card.parent:
            self.card.parent.remove_widget(self.card)  # Remove do pai anterior

        self.add_widget(self.card)

    def post_employ_no_avatar(self):
        url = 'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios'

        data = {
            'coextistence': 0,
            'day': "",
            'data_contractor': '',
            'request_payment': 'False',
            'days_work': 0,
            'contractor_month': 1,
            'payments': "[]",
            'password': f"{self.password}",
            'receiveds': "[]",
            'confirm_payments': "[]",
            'request': 'False',
            'effiency': 0,
            'email': 'Não definido',
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
            'contractor': self.contractor,
            'method_salary': self.method_salary,
            'scale': self.scale,
        }

        UrlRequest(
            f'{url}/.json',
            req_body=json.dumps(data),
            method='POST',
            on_success=self.added_successfully
        )

    def back_table(self):
        self.manager.transition = SlideTransition(direction='left')
        self.remove_widget(self.card)
        self.manager.current = 'Table'
