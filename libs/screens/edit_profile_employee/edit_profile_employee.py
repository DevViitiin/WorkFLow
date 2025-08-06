import json
import locale
from typing import Dict, Any
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.properties import (
    StringProperty,
    NumericProperty,
    ObjectProperty
)
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
import cloudinary
from plyer import filechooser


class EditProfileEmployee(MDScreen):
    """Tela de edição de perfil de funcionário."""

    # Propriedades do funcionário
    employee_name = StringProperty('Usuario Não encontrado')
    scale = StringProperty()
    method_salary = StringProperty()
    salary = NumericProperty()
    key = StringProperty()
    dont = 'Sim'
    avatar = StringProperty('https://res.cloudinary.com/dsmgwupky/image/upload/v1741648625/Samuel.jpg')
    new_salary = NumericProperty()
    # Atributos internos
    method = StringProperty('')
    menu = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        """Inicializa a tela de edição de perfil."""
        super().__init__(*args, **kwargs)
        self._setup_scale_menu()
        cloudinary.config(
            cloud_name="dsmgwupky",
            api_key="256987432736353",
            api_secret="K8oSFMvqA6N2eU4zLTnLTVuArMU"
        )

    # Funções de imagem ------------------------------------------------------------------------------------------------
    def recortar_imagem_circular(self, imagem_path):
        try:
            # Upload da imagem com corte circular
            print(self.ids.name.text)
            response = cloudinary.uploader.upload(
                imagem_path,
                public_id=self.ids.name.text,
                overwrite=True,
                transformation=[
                    {'width': 1000, 'height': 1000, 'crop': 'thumb', 'gravity': 'face', 'radius': 'max'}
                ]
            )
            print(self.key)
            url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.key}/.json'
            data = {
                'avatar': response['secure_url']
            }

            UrlRequest(
                url,
                method='PATCH',
                req_body=json.dumps(data),
                on_success=self.saved_successfully
            )
            self.ids.perfil.source = response['secure_url']  # Retorna o URL da imagem cortada
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

    def _setup_scale_menu(self) -> None:
        """Configura o menu dropdown para a escala de trabalho."""
        print(self.method_salary)
        if self.menu is None:
            scales = ['6x1', '5x2', '4x3']
            menu_items = [
                {'text': scale, 'on_release': lambda x=scale: self.replace_scale(x)}
                for scale in scales
            ]

            self.menu = MDDropdownMenu(
                caller=self.ids.scale,
                items=menu_items,
                position='bottom',
                width_mult=2,
                max_height='400dp',
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )

            # Vincular evento de foco ao campo de escala
            self.ids.scale.bind(focus=self.on_scale_focus)

    def on_enter(self) -> None:
        """Método chamado quando a tela é exibida. Preenche os dados do funcionário."""
        # Preencher campos com dados do funcionário
        self.ids.name.text = self.employee_name
        self.ids.scale.text = self.scale
        self.ids.salary.text = str(self.salary)
        self.new_salary = self.salary
        # Configurar o método de pagamento
        self.method = self.method_salary
        self._reset_payment_cards()

        if self.method_salary in 'Empreita':
            self.ids.salary.disabled = True
        else:
            self.ids.salary.disabled = False
        print(self.method_salary)

        # Destacar o cartão do método de pagamento atual
        if self.method_salary in ('Semanal', 'Diaria'):
            self.ids.card_week.line_color = 'blue' if self.method_salary == 'Semanal' else 'white'
            self.ids.card_day.line_color = 'blue' if self.method_salary == 'Diaria' else 'white'
        elif self.method_salary == 'Mensal':
            self.ids.card_month.line_color = 'blue'
        else:  # 'Empreita'
            self.ids.card_bricklayer.line_color = 'blue'

    def _reset_payment_cards(self) -> None:
        """Reseta as cores de todos os cartões de método de pagamento."""
        cards = ['card_week', 'card_day', 'card_month', 'card_bricklayer']
        for card in cards:
            self.ids[card].line_color = 'white'

    def on_scale_focus(self, instance, value: bool) -> None:
        """Abre o menu dropdown quando o campo de escala recebe foco."""
        if value:  # Campo recebeu foco
            self.menu.open()

    def replace_scale(self, scale: str) -> None:
        """Atualiza o texto do campo de escala e fecha o menu."""
        self.ids.scale.text = scale
        self.menu.dismiss()

    def text(self, instance, text: str) -> None:
        """Valida o texto do campo de escala."""
        if text not in ('6x1', '5x2', '4x3'):
            self.ids.scale.text = ''

    def replace_numbers(self, instance, text: str) -> None:

        """Formata o valor do salário para o padrão brasileiro."""
        try:
            # Try to set locale, but handle the case where it fails
            try:
                locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
                use_locale = True
            except locale.Error:
                use_locale = False

            # Converte o texto para float, substituindo vírgula por ponto
            numero_float = float(text.replace(',', '.'))

            if use_locale:
                # Formata o número no padrão brasileiro usando locale
                formatted_number = locale.currency(numero_float, grouping=True, symbol=None)
            else:
                # Fallback: format manually
                formatted_number = f"{numero_float:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

            self.salary = numero_float
            self.ids.salary.text = formatted_number
        except ValueError:
            # Se o texto não for um número válido, mantém o texto original
            pass

    def on_salary_focus(self, instance, value: bool) -> None:
        """
        Formata o campo de salário conforme o foco:
        - Ao perder foco: formata para exibição
        - Ao ganhar foco: remove formatação para edição
        """
        if not value:  # Campo perdeu foco
            if value != 0:
                self.new_salary = self.ids.salary.text
                self.replace_numbers(instance, self.ids.salary.text)
        else:  # Campo ganhou foco
            try:
                # Remove formatação para facilitar edição
                numero_str = self.ids.salary.text.replace('.', '').replace(',', '.')
                numero_float = float(numero_str)
                self.ids.salary.text = str(numero_float).replace('.', ',')
            except (ValueError, AttributeError):
                pass

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
            self.ids[card_map[method]].line_color = 'blue'

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

    def cancel(self) -> None:
        """Cancela a edição do perfil."""
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'Evaluation'

    def show_snackbar(self) -> None:
        """Exibe um Snackbar informativo."""
        MDSnackbar(
            MDSnackbarText(
                text="Apresente novos dados para atualização",
                theme_text_color='Custom',
                text_color='black',
                bold=True
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            halign='center',
            size_hint_x=0.8,
            theme_bg_color='Custom',
            background_color='cyan'
        ).open()

    def has_changes(self) -> bool:
        """Verifica se houve alterações nos dados do funcionário."""
        return (
                self.ids.name.text != self.employee_name or
                self.ids.scale.text != self.scale or
                str(self.salary) != str(self.ids.salary.text).replace('.', '').replace(',', '.') or
                self.method != self.method_salary
        )

    def save(self) -> None:
        """Salva as alterações no perfil do funcionário."""
        print(self.name, self.ids.name.text)
        if self.employee_name and self.key:
            if self.has_changes():
                if self.ids.name.text != self.employee_name:
                   self.check_name()
                else:
                    self.etapa3()
            else:
                self.show_snackbar()

    def check_name(self):
        url = 'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/.json'
        UrlRequest(
            url,
            method='GET',
            on_success=self.etapa2,
        )

    def etapa2(self, req, result):
        names = []
        for cargo, nome in result.items():
            if nome['Name'] == self.ids.name.text:
                MDSnackbar(
                    MDSnackbarText(
                        text='Esse nome de usuario já esta cadastrado',
                        theme_text_color='Custom',
                        text_color='white',
                        bold=True
                    ),
                    y=dp(24),
                    pos_hint={"center_x": 0.5},
                    halign='center',
                    size_hint_x=0.8,
                    theme_bg_color='Custom',
                    background_color='red'
                ).open()
                names.append(nome['Name'])

        if not names:
            self.etapa3()

    def etapa3(self):
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.key}/.json'
        data = dict()
        if self.scale != self.ids.scale.text or self.method_salary != self.method:
            data = {
                'Name': self.ids.name.text,
                'scale': self.ids.scale.text,
                'method_salary': self.method,
                'salary': self.salary,
                'avatar': self.ids.perfil.source,
                'day': '',
                'week_1': 0,
                'week_2': 0,
                'week_3': 0,
                'week_4': 0,
                'ultimate': '',
                'valleys': "[]",
                'days_work': 0,
                'tot': 0,
                'work_days_week1': '[]',
                'work_days_week2': '[]',
                'work_days_week3': '[]',
                'work_days_week4': '[]'
            }

        else:
            data = {
                'Name': self.ids.name.text,
                'scale': self.ids.scale.text,
                'method_salary': self.method,
                'salary': self.salary,
                'avatar': self.ids.perfil.source
            }

        UrlRequest(
            url,
            method='PATCH',
            req_body=json.dumps(data),
            on_success=self.saved_successfully
        )
    def saved_successfully(self, instance, data: Dict[str, Any]) -> None:
        """Callback executado quando os dados são salvos com sucesso."""
        print(f"Dados salvos com sucesso: {data}")
        app = MDApp.get_running_app()
        screenmanager = app.root
        print(self.ids.salary.text)
        evaluation = screenmanager.get_screen('Evaluation')
        evaluation.avatar = self.ids.perfil.source
        evaluation.method_salary = self.method
        evaluation.salary = self.new_salary
        evaluation.employee_name = self.ids.name.text
        evaluation.scale = self.ids.scale.text

        if self.scale != self.ids.scale.text or self.method_salary != self.method:
            evaluation.work_days_week1 = data['work_days_week1']
            evaluation.work_days_week2 = data['work_days_week2']
            evaluation.work_days_week3 = data['work_days_week3']
            evaluation.work_days_week4 = data['work_days_week4']
            evaluation.day = data['day']
            evaluation.ultimate = data['ultimate']
            evaluation.valleys = "[]"
            evaluation.tot = 0
            evaluation.week_1 = data['week_1']
            evaluation.week_2 = data['week_2']
            evaluation.week_3 = data['week_3']
            evaluation.week_4 = data['week_4']
            evaluation.days_work = 0

        evaluation.transition = SlideTransition(direction='right')
        screenmanager.current = 'Evaluation'

    def back_evaluation(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'Evaluation'

