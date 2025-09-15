import ast
import json
from datetime import datetime, timedelta
from kivy.clock import Clock
from babel.dates import format_date
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.properties import NumericProperty, StringProperty, get_color_from_hex
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.list import MDListItem, MDListItemHeadlineText, \
    MDListItemTrailingSupportingText, MDListItemTrailingCheckbox, MDListItemTertiaryText
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText


class WorkingDays(MDScreen):
    token_id = StringProperty()
    local_id = StringProperty()
    api_key = StringProperty()
    refresh_token = StringProperty()
    scale = StringProperty('5x2')
    method_salary = StringProperty()
    employee_name = StringProperty()
    days_work = NumericProperty()
    faults = NumericProperty()
    work_days_week1 = StringProperty()
    contractor = StringProperty()
    key = StringProperty()
    # Firebase url
    FIREBASE_URL = 'https://obra-7ebd9-default-rtdb.firebaseio.com'
    # Variáveis de controle dos dias
    seg = 0
    terc = 0
    quart = 0
    quint = 0
    sex = 0
    sab = 0

    def on_enter(self):
        print('Confirmações de pagamento aqui: ', self.confirm_payments)
        self.verific_token()
        self.event_token = Clock.schedule_interval(self.verific_token, 300)
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
                        text="Aguarde novo periodo para inserir frequência",
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

        self.ids.main_scroll.clear_widgets()
        # Inicializa faltas com base na escala de trabalho
        if self.scale == '6x1':
            self.faults = 6
        elif self.scale == '5x2':
            self.faults = 5
        else:  # 4x3
            self.faults = 4
        self.upload_days()

        self.upload_days_work_week()
        current_week = self.get_week_dates()
        self.ids.week.text = f"{current_week['start_date']} a {current_week['end_date']}"
        
    def on_leave(self, *args):
        if hasattr(self, 'event_token'):
            self.event_token.cancel()
            print("⏱️ Clock do token cancelado ao sair da tela")
            
    def verific_token(self, *args):
        if not self.get_parent_window():
            return
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


    def numb_week(self):
        date = datetime.today()
        first_day = date.replace(day=1)
        dom = first_day.weekday()  # dia da semana do primeiro dia do mês
        adjusted_day = date.day + dom
        return int((adjusted_day - 1) / 7) + 1

    def upload_days_work_week(self):
        print(self.work_days_week1)
        dataframe = ast.literal_eval(self.work_days_week1)
        # Dictionary mapping day names to their variables
        day_mapping = {
            'Segunda-feira': 'seg',
            'Terça-feira': 'terc',
            'Quarta-feira': 'quart',
            'Quinta-feira': 'quint',
            'Sexta-feira': 'sex',
            'Sabado': 'sab',

        }

        if not dataframe:
            print('Semana vazia')
        else:
            for dia in dataframe:
                if dia in day_mapping:
                    # Get the variable name for this day
                    var_name = day_mapping[dia]
                    # Set the variable to 1 to mark it as active
                    setattr(self, var_name, 1)
                    # Increment days_work counter
                    self.days_work += 1
                    self.faults -= 1
                    # Mark the checkbox as active
                    print(self.ids)
                    dia_seguro = dia.replace('-', '_')
                    if f"icon_{dia_seguro}" in self.ids:
                        self.ids[f"icon_{dia_seguro}"].active = True
                        self.ids[f"icon_{dia_seguro}"].icon = 'checkbox-blank-circle'

    def upload_days(self):
        # Lista de dias da semana com seus respectivos índices
        dias_semana = [
            ('Segunda-feira', 0),
            ('Terça-feira', 1),
            ('Quarta-feira', 2),
            ('Quinta-feira', 3),
            ('Sexta-feira', 4),
            ('Sabado', 5),
            ('Domingo', 6)
        ]

        # Obtém os dias da semana
        week = self.upload_week()

        for dia, indice in dias_semana:
            # Verifica se é um dia de folga com base na escala
            is_folga = (self.scale == '6x1' and dia in ('Domingo') or
                        (self.scale == '5x2' and dia in ('Sabado', 'Domingo')) or
                        (self.scale == '4x3' and (dia in ('Sexta-feira', 'Sabado', 'Domingo'))))

            # Obtém a data correspondente
            day_week = str(week[indice]) if indice < len(week) else 'Data não disponível'

            # Cria o item da lista
            list_item = MDListItem(
                MDListItemHeadlineText(
                    text=dia
                ),
                MDListItemTertiaryText(
                    text=day_week
                ),
                pos_hint={'center_x': 0.5},
                size_hint=(1, None),
                theme_bg_color='Custom',
                theme_focus_color='Custom',
                md_bg_color=[1, 1, 1, 1],
                md_bg_color_disabled=[1, 1, 1, 1],
                ripple_color=(1, 1, 1, 1),
                focus_behavior=False,
            )

            safe_dia = dia.replace('-', '_')

            if not is_folga:
                # Cria botão de checkbox
                icon_button = MDListItemTrailingCheckbox(
                    padding=[0, 0, 0, 0],
                    theme_focus_color='Custom',
                    color_active='blue',
                    color_disabled='black',
                    _current_color='purple',
                    focus_behavior=False
                )
                icon_button.icon = 'checkbox-blank-circle-outline'

                # Armazena referência e vincula evento
                self.ids[f"icon_{safe_dia}"] = icon_button
                icon_button.bind(on_release=lambda instance, d=dia: self.on_checkbox_press(d))
                list_item.add_widget(icon_button)
                self.ids.main_scroll.add_widget(list_item)
            else:
                # Cria rótulo "Folga" para dias de folga
                folga_label = MDListItemTrailingSupportingText(
                    text='Folga',
                    theme_text_color='Custom',
                    text_color=[0.0, 1.0, 0.0, 1.0],  # Verde
                    halign='right',
                    padding=[0, 0, 15, 0],
                    valign='center'
                )

                # Armazena referência
                self.ids[f"icon_{safe_dia}"] = folga_label
                list_item.add_widget(folga_label)
                self.ids.main_scroll.add_widget(list_item)

    def upload_week(self, start_date=None):
        """
        Retorna todas as datas de uma semana específica (segunda-feira a domingo)
        no formato brasileiro (dd/mm/aaaa).
        """
        if start_date is None:
            start_date = datetime.now()

        # Encontra a segunda-feira da semana
        week_start = start_date - timedelta(days=start_date.weekday())

        # Lista para armazenar os dias da semana formatados
        week_days = [(week_start + timedelta(days=i)).strftime("%d/%m/%Y") for i in range(7)]

        return week_days

    def get_week_dates(self, start_date=None):
        """Calcula as datas de início e término de uma semana e retorna no formato brasileiro (dd/mm/yyyy)."""

        if start_date is None:
            start_date = datetime.now()

        # Encontra o primeiro dia da semana (segunda-feira)
        week_start = start_date - timedelta(days=start_date.weekday())

        # Calcula o último dia da semana (domingo)
        week_end = week_start + timedelta(days=6)

        # Formata as datas no formato brasileiro (dd/mm/yyyy)
        formatted_start_date = week_start.strftime('%d/%m/%Y')
        formatted_end_date = week_end.strftime('%d/%m/%Y')

        return {
            'start_date': formatted_start_date,  # Data formatada
            'end_date': formatted_end_date,  # Data formatada
            'start_datetime': week_start,  # Objeto datetime original
            'end_datetime': week_end  # Objeto datetime original
        }

    def on_checkbox_press(self, dia):
        # Mapeamento dos nomes dos dias para suas variáveis de controle
        mapa_dias = {
            'Segunda-feira': 'seg',
            'Terça-feira': 'terc',
            'Quarta-feira': 'quart',
            'Quinta-feira': 'quint',
            'Sexta-feira': 'sex',
            'Sabado': 'sab'
        }

        # Obtém o valor atual para este dia
        var_dia = mapa_dias.get(dia)
        if var_dia:
            valor_atual = getattr(self, var_dia)
            dia_seguro = dia.replace('-', '_')

            if valor_atual == 0:
                # Marca como trabalhado
                setattr(self, var_dia, 1)
                self.days_work += 1
                self.faults -= 1
                self.ids[f"icon_{dia_seguro}"].icon = 'checkbox-blank-circle'
            else:
                # Marca como não trabalhado
                setattr(self, var_dia, 0)
                self.days_work -= 1
                self.faults += 1
                self.ids[f"icon_{dia_seguro}"].icon = 'checkbox-blank-circle-outline'

    def back_evaluation(self, *args):
        screen_name = 'Evaluation'
        app = MDApp.get_running_app()
        screen_manager = app.root
        screen_manager.transition = SlideTransition(direction="right")

        target_screen = screen_manager.get_screen(screen_name)

        # Transfere todos os dados relevantes
        attributes = [
            "employee_name", "employee_function", "avatar", "contractor",
            "method_salary", "assess", "coexistence", "punctuality",
            "efficiency", "scale", "days_work"
        ]

        for attr in attributes:
            setattr(target_screen, attr, getattr(self, attr))

        print(self.days_work)
        self.seg = 0
        self.terc = 0
        self.quart = 0
        self.quint = 0
        self.sex = 0
        self.upload_database()
        self.on_enter()
        self.manager.current = 'Evaluation'

    def upload_database(self):
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.key}/.json?auth={self.token_id}'

        # Create a list of tuples with day names and their values
        days_info = [
            ('seg', self.seg),
            ('terc', self.terc),
            ('quart', self.quart),
            ('quint', self.quint),
            ('sex', self.sex),
            ('sab', self.sab)
        ]

        week = []
        mapa_dias = {
            'seg': 'Segunda-feira',
            'terc': 'Terça-feira',
            'quart': 'Quarta-feira',
            'quint': 'Quinta-feira',
            'sex': 'Sexta-feira',
            'sab': 'Sabado'
        }

        # Check each day's value and append the day name to week if the value is >= 1
        for day_key, day_value in days_info:
            if day_value >= 1:
                # Get the full day name from mapa_dias
                var_dia = mapa_dias.get(day_key)
                print(var_dia)
                # Append the day name to the week list
                week.append(var_dia)

        data = {
            'week_1': self.days_work,
            'work_days_week1': f'{week}'
        }

        UrlRequest(
            url,
            method='PATCH',
            req_body=json.dumps(data),
            on_success=self.finnaly_step
        )

    def finnaly_step(self, req, result, *args):
        '''Voltar para a tela de mes e passar os dias trabalhados dessa semana para ela'''
        print(result)
        app = MDApp.get_running_app()
        screen_manager = app.root
        working = screen_manager.get_screen('Evaluation')
        working.week_1 = self.days_work
        working.work_days_week1 = result['work_days_week1']
        working.local_id = self.local_id
        working.token_id = self.token_id
        working.refresh_token = self.refresh_token
        working.api_key = self.api_key
        # Reset day counters
        self.seg = 0
        self.terc = 0
        self.quart = 0
        self.quint = 0
        self.sex = 0
        self.sab = 0
        # Reset work counters
        self.days_work = 0
        self.days = 0
        # Use SlideTransition for consistency
        screen_manager.transition = SlideTransition(direction='right')
        screen_manager.current = 'Evaluation'

    def cancel(self):
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.key}/.json?{self.token_id}'
        data = {
            'week_1': 0,
            'work_days_week1': '[]',
            'tot': 0,
            'valleys': "{}"
        }

        UrlRequest(
            url,
            method='PATCH',
            on_success=self.success,
            req_body=json.dumps(data)
        )

    def success(self, instance, result, *args):
        app = MDApp.get_running_app()
        screenmanager = app.root
        evaluation = screenmanager.get_screen('Evaluation')
        evaluation.days_work = 0
        evaluation.week_1 = 0
        evaluation_work_days_week1 = "[]"
        evaluation.tot = 0
        evaluation.valleys = '{}'
        evaluation.work_days_week1 = '[]'
        evaluation.api_key = self.api_key
        evaluation.local_id = self.local_id
        evaluation.refresh_token = self.refresh_token
        evaluation.token_id = self.token_id
        screenmanager.transition = SlideTransition(direction='right')
        screenmanager.current = 'Evaluation'

    def bye(self, *args):
        app = MDApp.get_running_app()
        screenmanager = app.root
        evaluation = screenmanager.get_screen('Evaluation')
        evaluation.api_key = self.api_key
        evaluation.local_id = self.local_id
        evaluation.refresh_token = self.refresh_token
        evaluation.token_id = self.token_id
        screenmanager.transition = SlideTransition(direction='right')
        screenmanager.current = 'Evaluation'