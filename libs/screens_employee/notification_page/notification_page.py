import ast
import json
from datetime import datetime

from kivy.network.urlrequest import UrlRequest
from kivy.properties import NumericProperty, StringProperty, Clock
from kivy.uix.screenmanager import SlideTransition
from kivy.uix.widget import Widget
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButtonText, MDButton
from kivymd.uix.dialog import MDDialog, MDDialogIcon, MDDialogHeadlineText, MDDialogSupportingText, \
    MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.divider import MDDivider
from kivymd.uix.list import MDListItem, MDListItemLeadingIcon, MDListItemSupportingText
from kivymd.uix.progressindicator import MDCircularProgressIndicator
from kivymd.uix.screen import MDScreen


class NotificationPage(MDScreen):
    """
    Tela para exibir notificações e gerenciar informações de pagamento.

    Esta classe permite visualizar detalhes de pagamento, confirmar pagamentos
    e mostrar informações de contato do contratante. Gerencia a comunicação
    com o banco de dados Firebase para atualizar registros de pagamento.

    Attributes:
        numb (NumericProperty): Número identificador do pagamento.
        month (StringProperty): Mês de referência do pagamento.
        name_contractor (StringProperty): Nome do contratante.
        salary (NumericProperty): Valor do salário/pagamento.
        email (StringProperty): Email de contato do contratante.
        telephone (StringProperty): Número de telefone do contratante.
        method (StringProperty): Método de pagamento utilizado.
        key (StringProperty): Chave única do funcionário no banco de dados.
    """
    numb = NumericProperty()
    token_id = StringProperty()
    local_id = StringProperty()
    refresh_token = StringProperty()
    api_key = StringProperty()
    month = StringProperty()
    name_contractor = StringProperty()
    salary = NumericProperty()
    email = StringProperty()
    telephone = StringProperty()
    method = StringProperty()
    key = StringProperty()
    FIREBASE_URL = 'https://obra-7ebd9-default-rtdb.firebaseio.com'

    def on_enter(self):
        """
        Método chamado quando a tela é exibida.

        Registra em log as informações do pagamento e contato para fins de depuração.
        """
        print('Token_id: ', self.token_id)
        print('Email: ', self.email)
        print('Telefone: ', self.telephone)
        print('Salario: ', self.salary)
        print('Month: ', self.month)
        print('Numb: ', self.numb)
        print('Metodo: ', self.method)
        self.verific_token()
        self.event_token = Clock.schedule_interval(self.verific_token, 300)


    def verific_token(self):
        print('🔎 verificando token...')
        UrlRequest(
            f"{self.FIREBASE_URL}/Funcionarios/{self.local_id}.json?auth=s{self.token_id}sjwjjdfadsfaesasw",
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
        Clock.schedule_once(lambda dt: self.show_error('Refaça login no aplicativo'), 1)

    def navigate_to_review_screen(self):
        """
        Navega para a tela de revisão.

        Configura a transição para deslizar da direita para a esquerda e
        altera a tela atual para 'ReviewScreen'.
        """
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'ReviewScreen'

    def __init__(self, **kwargs):
        """
        Inicializa a tela de notificações.

        Args:
            **kwargs: Argumentos adicionais passados para a classe pai.
        """
        super().__init__(**kwargs)
        self.dialog = None

    def show_contact_options(self):
        """
        Exibe as opções de contato do contratante.

        Mostra um diálogo com informações de contato e agenda uma chamada
        para processar a solicitação de contato após um intervalo.
        """
        self.show_contact_dialog()
        # Simula um processo demorado
        Clock.schedule_once(self.process_contact_request, 30)  # chama depois de 30 segundos

    def process_contact_request(self, dt):
        """
        Processa a solicitação de contato após o tempo definido.

        Esta função é chamada após o tempo programado por Clock.schedule_once,
        permitindo executar lógica adicional relacionada ao contato.

        Args:
            dt (float): Delta time - tempo decorrido desde a programação.
        """
        # Sua lógica aqui
        print("Chamando algum processo aqui...")

        # Depois que termina, fecha o popup
        self.close_contact_dialog()

    def show_contact_dialog(self):
        """
        Exibe um diálogo com as informações de contato do contratante.

        Cria um diálogo do Material Design mostrando o email e telefone
        do contratante, com ícones apropriados e formatação adequada.
        """
        if not self.dialog:
            self.dialog = MDDialog(
                MDDialogSupportingText(
                    text="Estas são as informações de contato do seu contratante. Recomendamos que entre em contato para tratar e resolver a situação de forma adequada."
                ),

                MDDialogContentContainer(
                    MDDivider(),
                    MDListItem(
                        MDListItemLeadingIcon(
                            icon="gmail",
                        ),
                        MDListItemSupportingText(
                            text=f"{self.email}",
                        ),
                        theme_bg_color="Custom",
                        md_bg_color=self.theme_cls.transparentColor,
                    ),
                    MDListItem(
                        MDListItemLeadingIcon(
                            icon="phone-in-talk",
                        ),
                        MDListItemSupportingText(
                            text=f"{self.telephone}",
                        ),
                        theme_bg_color="Custom",
                        md_bg_color=self.theme_cls.transparentColor,
                    ),
                    MDDivider(),
                    orientation="vertical",
                )
            )
        self.dialog.open()

    def close_contact_dialog(self):
        """
        Fecha o diálogo de informações de contato.

        Verifica se o diálogo existe e o fecha, também reativa
        a interface que pode ter sido desativada.
        """
        if self.dialog:
            self.disabled = False
            self.dialog.dismiss()

    def confirm_payment(self):
        """
        Inicia o processo de confirmação de pagamento.

        Faz uma requisição ao Firebase para obter os dados atuais do funcionário
        antes de processar o registro de pagamento.
        """
        UrlRequest(
            url=f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.local_id}/.json?auth={self.token_id}',
            on_success=self.process_payment_data
        )

    def process_payment_data(self, req, result):
        """
        Processa os dados de pagamento após obter os dados do funcionário.

        Recupera o histórico de pagamentos, adiciona o novo registro com todos os detalhes
        e atualiza os dados no Firebase.

        Args:
            req: Objeto da requisição HTTP.
            result: Dados do funcionário retornados pela requisição.
        """
        try:
            payments = ast.literal_eval(result['payments'])
        except:
            payments = []
            
        data_atual = datetime.now()
        data_formatada = data_atual.strftime("%d/%m/%Y")
        data = {
            'data': f"{data_formatada}",
            'value': self.salary,
            'who': 'funcionario',
            'salary_completed': self.salary,
            'numb': self.numb,
            'Month': f"{self.month}",
            'method': f"{self.method}",
            'valleys': "[]"
        }
        payments.append(data)
        data = {
            'payments': f"{payments}"
        }
        UrlRequest(
            url=f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.local_id}/.json?auth={self.token_id}',
            method='PATCH',
            req_body=json.dumps(data),
            on_success=self.finalize_payment
        )

    def finalize_payment(self, req, result):
        """
        Finaliza o processo de pagamento após a atualização no Firebase.

        Exibe uma mensagem de confirmação e navega de volta para a tela de revisão.

        Args:
            req: Objeto da requisição HTTP.
            result: Resultado da atualização (dados atualizados do funcionário).
        """
        print('Pagamento confirmado: ', result)
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'ReviewScreen'

    def return_(self):
        """
        Voltar para a outra pagina

        :return:
        """
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'ReviewScreen'

