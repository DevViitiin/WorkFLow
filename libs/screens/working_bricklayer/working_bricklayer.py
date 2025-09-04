import ast
import json
from datetime import datetime
from kivy.clock import Clock
from babel.dates import format_date
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty, NumericProperty, get_color_from_hex
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDModalInputDatePicker
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbarText, MDSnackbar


class WorkingBricklayer(MDScreen):
    token_id = StringProperty()
    local_id = StringProperty()
    refresh_token = StringProperty()
    key = StringProperty('-OKmtfC8Am5v51vjif3L')
    salary = NumericProperty(1500)
    employee_function = StringProperty('Analista de Sistemas')
    ultimate = StringProperty()
    confirm_payments = StringProperty()
    observations = StringProperty('Sem observações')
     # Firebase url
    FIREBASE_URL = 'https://obra-7ebd9-default-rtdb.firebaseio.com'

    def on_enter(self, *args):
        self.verific_token()
        self.event_token = Clock.schedule_interval(self.verific_token, 300)
        print('Confirmações de pagamento aqui: ', self.confirm_payments)

        # fazendo a logica de bloquear o botão o pagamento foi confirmado para esté periodo
        data = datetime.today()
        month = format_date(data, "MMMM", locale='pt_BR').capitalize()
        numb = 0
        if self.method_salary in ('Diaria', 'Semanal'):
            numb = self.numb_week()
        else:
            numb = datetime.today().month

        print('Numero do mes ou semana :   ', numb)
        print('Mes: ', month)

        have = []
        if self.confirm_payments:
            """Significa que a lista de pagamentos confirmados pelo contratante
               Não está vazia"""
            for confirm in ast.literal_eval(self.confirm_payments):
                print(confirm)
                if confirm['numb'] == numb and confirm['Month'] == month:
                    have.append('yes')
                    print('Achei a confirmação')
            if have:
                print('Foi confirmado o pagamento')
                self.ids.save.disabled = True
                self.ids.cancel.disabled = True

                """Exibe um Snackbar informativo."""
                MDSnackbar(
                    MDSnackbarText(
                        text="Aguarde novo periodo para inserir vales",
                        theme_text_color='Custom',
                        text_color='black',
                        pos_hint={'center_x': 0.5, 'center_y': 0.5},
                        halign='center',
                        bold=True
                    ),
                    y=dp(24),
                    pos_hint={"center_x": 0.5},
                    halign='center',
                    size_hint_x=0.9,
                    theme_bg_color='Custom',
                    background_color=get_color_from_hex('#41EAD4')
                ).open()
            else:
                self.ids.cancel.disabled = False
                self.ids.save.disabled = False

        else:
            """Significa que pode confirmar ja que a lista de confirmações está nula"""
            self.ids.save.disabled = False
            self.ids.cancel.disabled = False

        """ Criando os principais elementos dessa tela """
        # Carregando os dados
        self.ids.data_picker.text = f'{self.ultimate}'
        self.ids.text_work.text = f'{self.employee_function}'
        self.ids.salary.text = f'{self.salary}'

        # Criando o data picker para gerenciar a data
        self.date_dialog = MDModalInputDatePicker()
        self.date_dialog.bind(on_ok=self.on_ok)

        # Criando o elemento de trabalhos
        self.load_function()
        self.days_work()

    def verific_token(self):
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

    def show_error(self, error_message):
        """Display an error message"""
        self.show_message(error_message, color='#FF0000')
        print(f"Error: {error_message}")
    
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

    def days_work(self):
        # Obtendo a data atual
        try:
            data_atual = datetime.today()
            data_atual = f'{data_atual.day}/{data_atual.month}/{data_atual.year}'

            data_init = datetime.strptime(data_atual, "%d/%m/%Y")
            data_ult = datetime.strptime(self.ids.data_picker.text, '%d/%m/%Y')
            days_work = data_ult - data_init
            print('Numero', days_work)
            return {'day': data_atual, 'days_work': int(days_work.days)}
        except:
            print('zero')
            return {'day': '01/03/2025', 'days_work': 0}

    def load_function(self):
        # Abrir um popup de menu para a pessoa escolher o seu estado
        states = ['Abacaxicultor', 'Administrador', 'Advogado', 'Agricultor', 'Analista de Sistemas', 'Apicultor',
                  'Arquiteto', 'Artista', 'Ator', 'Auditor', 'Auxiliar de Enfermagem', 'Babá', 'Barbeiro',
                  'Bibliotecário', 'Biologista', 'Bombeiro', 'Cabeleireiro', 'Caixa', 'Camareiro', 'Carregador',
                  'Carpinteiro', 'Carteiro', 'Chefe de Cozinha', 'Cientista', 'Cozinheiro', 'Corretor de Imóveis',
                  'Costureira', 'Dançarino', 'Dentista', 'Designer', 'Detetive', 'Diarista', 'Diretor de Cinema',
                  'Eletricista', 'Empresário', 'Enfermeiro', 'Engenheiro', 'Engenheiro Agrônomo', 'Engenheiro Civil',
                  'Engenheiro de Alimentos', 'Engenheiro de Automação', 'Engenheiro de Bioprocessos',
                  'Engenheiro de Controle e Automação', 'Engenheiro de Dados', 'Engenheiro de Energia',
                  'Engenheiro de Hardware', 'Engenheiro de Machine Learning', 'Engenheiro de Manutenção',
                  'Engenheiro de Materiais', 'Engenheiro de Minas', 'Engenheiro de Petróleo', 'Engenheiro de Produção',
                  'Engenheiro de Processos', 'Engenheiro de Projetos', 'Engenheiro de Qualidade', 'Engenheiro de Redes',
                  'Engenheiro de Segurança do Trabalho', 'Engenheiro de Software', 'Engenheiro de Sistemas',
                  'Engenheiro de Telecomunicações', 'Engenheiro de Transportes', 'Engenheiro Elétrico',
                  'Engenheiro Florestal', 'Engenheiro Mecânico', 'Engenheiro Químico', 'Escritor', 'Estilista',
                  'Estudante', 'Farmacêutico', 'Ferramenteiro', 'Físico', 'Fisioterapeuta', 'Fotógrafo', 'Frentista',
                  'Garçom', 'Geólogo', 'Gerente', 'Guia Turístico', 'Heroi', 'Historiador', 'Jardineiro', 'Jornalista',
                  'Juiz', 'Lavrador', 'Locutor', 'Maçom', 'Maqueiro', 'Marceneiro', 'Marinheiro', 'Massagista',
                  'Mecânico', 'Mediador', 'Médico', 'Meteorologista', 'Motorista', 'Músico', 'Nutricionista',
                  'Oceanógrafo', 'Operador de Caixa', 'Operador de Máquinas', 'Pedagogo', 'Pedreiro',
                  'Personal Trainer', 'Pescador', 'Piloto', 'Pintor', 'Pizzaiolo', 'Policial', 'Porteiro',
                  'Professor', 'Programador', 'Psicólogo', 'Publicitário', 'Químico', 'Recepcionista',
                  'Redator', 'Repórter', 'Secretário', 'Segurança', 'Servente', 'Sociólogo', 'Tatuador',
                  'Taxista', 'Técnico de Informática', 'Técnico de Laboratório', 'Técnico de Radiologia',
                  'Técnico de Som', 'Técnico em Eletrônica', 'Técnico em Enfermagem', 'Técnico em Mecânica',
                  'Técnico em Segurança do Trabalho', 'Tradutor', 'Veterinário', 'Vigilante', 'Web Designer',
                  'Zelador', 'Zootecnista']

        menu_itens = []
        position = 0
        for state in states:
            position += 1
            row = {'text': state, 'on_release': lambda x=state: self.replace_function(x)}
            menu_itens.append(row)

        self.menu = MDDropdownMenu(
            caller=self.ids.work,
            items=menu_itens,
            position='bottom',
            width_mult=8,
            max_height='240dp',
            pos_hint={'center_x': 0.5}
        )

    def replace_function(self, text):
        self.menu.dismiss()
        self.ids.text_work.text = text

    def on_ok(self, instance_date_picker):
        try:
            instance_date_picker.dismiss()
            data_obj = instance_date_picker.get_date()[0]
            # Formato brasileiro: dia/mês/ano
            data_formatada = data_obj.strftime("%d/%m/%Y")
            self.ids.data_picker.text = data_formatada

        except Exception as e:
            print('Erro ao carregar a data:', e)

    def numb_week(self):
        date = datetime.today()
        first_day = date.replace(day=1)
        dom = first_day.weekday()  # dia da semana do primeiro dia do mês
        adjusted_day = date.day + dom
        return int((adjusted_day - 1) / 7) + 1

    def show_modal_date_picker(self, *args):
        """Cria e exibe um novo DatePicker toda vez que for chamado"""
        self.date_dialog.open()

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

    def verification_data(self):
        """ Verificando se algum dos dados foi alterado """
        if (self.ultimate != self.ids.data_picker.text
                or self.employee_function != self.ids.text_work.text
                or float(self.salary) != float(self.ids.salary.text)):

            self.load_firebase()

        else:
            self.show_snackbar()

    def load_firebase(self):
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.key}/.json?auth={self.token_id}'
        info = self.days_work()
        print(info)
        data = {
            'function': self.ids.text_work.text,
            'ultimate': self.ids.data_picker.text,
            'salary': float(self.ids.salary.text),
            'days_work': info['days_work'],
            'day': info['day']
        }

        UrlRequest(
            url,
            method='PATCH',
            on_success=self.success_upload,
            req_body=json.dumps(data)
        )

    def success_upload(self, instance, result):
        app = MDApp.get_running_app()
        screenmanager = app.root
        evaluation = screenmanager.get_screen('Evaluation')
        evaluation.salary = self.ids.salary.text
        day = self.days_work()
        evaluation.day = f"{day['day']}"
        evaluation.employee_function = f"{result['function']}"
        evaluation.days_work = f"{int(day['days_work'])}"
        evaluation.ultimate = f'{self.ids.data_picker.text}'
        screenmanager.transition = SlideTransition(direction='right')
        screenmanager.current = 'Evaluation'

    def cancel(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'Evaluation'
