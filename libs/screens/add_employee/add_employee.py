from kivy.core.image import Texture
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty, Clock, get_color_from_hex
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText


class MDBoxLayoutWithGradient(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self._update_rect, pos=self._update_rect)
        # Initial drawing of gradient
        self._update_rect()

    def _update_rect(self, *args):
        # Clear previous canvas drawings
        self.canvas.before.clear()

        with self.canvas.before:
            # Gradiente vertical
            self.gradient_texture = Texture.create(size=(2, 1))
            # Cores do Tailwind:
            # indigo-600: #4f46e5 = (79/255, 70/255, 229/255) = (0.31, 0.275, 0.898)
            # purple-600: #9333ea = (147/255, 51/255, 234/255) = (0.576, 0.2, 0.918)
            buf = bytes([
                int(0.31 * 255), int(0.275 * 255), int(0.898 * 255), 255,  # indigo-600
                int(0.576 * 255), int(0.2 * 255), int(0.918 * 255), 255  # purple-600
            ])
            self.gradient_texture.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')

            # Desenhar retângulo arredondado com o gradiente
            Color(1, 1, 1, 1)  # Branco para não afetar a textura
            RoundedRectangle(size=self.size, pos=self.pos, radius=[15, 15, 15, 15],
                             texture=self.gradient_texture)


class MDCardWithGradientTwo(MDCard):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self._update_rect, pos=self._update_rect)
        # Set line_color to transparent to avoid conflicts with gradient
        self.line_color = (0, 0, 0, 0)
        # Initial drawing of gradient
        Clock.schedule_once(self._update_rect, 0)

    def _update_rect(self, *args):
        # Clear previous canvas drawings
        self.canvas.before.clear()

        with self.canvas.before:
            # Vertical gradient
            self.gradient_texture = Texture.create(size=(1, 2))
            # Tailwind colors:
            # indigo-600: #4f46e5 = (79/255, 70/255, 229/255) = (0.31, 0.275, 0.898)
            # purple-600: #9333ea = (147/255, 51/255, 234/255) = (0.576, 0.2, 0.918)
            buf = bytes([
                int(0.31 * 255), int(0.275 * 255), int(0.898 * 255), 255,  # indigo-600
                int(0.576 * 255), int(0.2 * 255), int(0.918 * 255), 255  # purple-600
            ])
            self.gradient_texture.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
            self.gradient_texture.wrap = 'repeat'
            self.gradient_texture.mag_filter = 'linear'

            # Draw rounded rectangle with gradient
            Color(1, 1, 1, 1)  # White to not affect texture
            RoundedRectangle(
                size=self.size,
                pos=self.pos,
                texture=self.gradient_texture,
                radius=self.radius if hasattr(self, 'radius') else [10, 10, 10, 10]
            )


class AddEmployee(MDScreen):
    contractor = StringProperty()

    def on_enter(self):
        self.load_salary()
        self.load_function()
        self.load_scale()
        # Schedule the check to run every 0.5 seconds
        self.field_check_event = Clock.schedule_interval(self.check_fields_filled, 0.5)

    def check_fields_filled(self, *args):
        # Check if all required fields have values
        if (self.ids.name.text and
                self.ids.value_salary.text and
                self.ids.salary.text not in ('', 'Ausente', 'Obrigatorio') and
                self.ids.function.text not in ('', 'Ausente', 'Obrigatorio') and
                self.ids.scale.text not in ('', 'Ausente', 'Obrigatorio')):
            self.ids.three.icon_color = 'white'
            self.ids.one.icon_color = get_color_from_hex('#4b5563')
            return

        self.ids.one.icon_color = 'white'
        self.ids.three.icon_color = get_color_from_hex('#4b5563')

    def on_leave(self):
        # Stop the scheduled check when leaving the screen
        if hasattr(self, 'field_check_event'):
            Clock.unschedule(self.field_check_event)

    def load_salary(self):
        # Abrir um popup de menu para a pessoa escolher o seu estado
        states = ['Diaria', 'Semanal', 'Mensal', 'Empreita']

        menu_itens = []
        position = 0
        for state in states:
            position += 1
            row = {'text': state, 'on_release': lambda x=state: self.replace_salary(x)}
            menu_itens.append(row)

        self.menu = MDDropdownMenu(
            caller=self.ids.card_salary,
            items=menu_itens,
            position='bottom',
            width_mult=5,
            max_height='400dp',
            pos_hint={'center_x': 0.5, 'center_y': 0.65},
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

    def load_scale(self):
        # Abrir um popup de menu para a pessoa escolher o seu estado
        states = ['6x1', '5x2', '4x3']

        menu_itens = []
        position = 0
        for state in states:
            position += 1
            row = {'text': state, 'on_release': lambda x=state: self.replace_scale(x)}
            menu_itens.append(row)

        self.menu_scale = MDDropdownMenu(
            caller=self.ids.card_scale,
            items=menu_itens,
            position='bottom',
            width_mult=5,
            max_height='400dp',
            pos_hint={'center_x': 0.5, 'center_y': 0.3},
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

    def replace_scale(self, text):
        self.ids.scale.text = text
        self.ids.scale.text_color = 'white'
        self.menu_scale.dismiss()

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
        self.ids.function.text_color = 'white'
        self.menu2.dismiss()

    def replace_salary(self, texto):
        self.ids.salary.text = texto
        self.ids.salary.text_color = 'white'
        self.menu.dismiss()

    def table_screen(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'Table'

    def checking_empty_fields(self):
        if self.ids.name.text == '':
            self.ids.name.focus = True
            return

        if not self.ids.value_salary.text:
            self.ids.value_salary.focus = True
            return

        if self.ids.salary.text in ('Ausente', 'Obrigatorio') or not self.ids.salary.text:
            self.ids.salary.text = 'Obrigatorio'
            self.ids.salary.text_color = 'red'
            self.menu.open()
            return

        if self.ids.function.text in ('Ausente', 'Obrigatorio') or not self.ids.function.text:
            self.ids.function.text = 'Obrigatorio'
            self.ids.function.text_color = 'red'
            self.menu2.open()
            return

        if self.ids.scale.text in ('Ausente', 'Obrigatorio') or not self.ids.scale.text:
            self.ids.scale.text = 'Obrigatorio'
            self.ids.scale.text_color = 'red'
            self.menu_scale.open()
            return

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
            self.avatar_employee()

    def avatar_employee(self):
        self.manager.transition = SlideTransition(direction='left')
        app = MDApp.get_running_app()
        screen_manager = app.root
        employee_avatar = screen_manager.get_screen('AddEmployeePassword')
        employee_avatar.employee_name = self.ids.name.text
        employee_avatar.function = self.ids.function.text
        employee_avatar.salary = self.ids.value_salary.text
        employee_avatar.contractor = self.contractor
        employee_avatar.method_salary = self.ids.salary.text
        employee_avatar.scale = self.ids.scale.text
        self.ids.name.text = ''
        self.ids.function.text = ''
        self.ids.salary.text = ''
        self.ids.scale.text = ''
        self.ids.value_salary.text = ''
        screen_manager.current = 'AddEmployeePassword'

    def back_table(self):
        self.ids.salary.text = ''
        self.ids.value_salary.text = ''
        self.ids.function.text = ''
        self.ids.name.text = ''
        self.ids.scale.text = ''
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'Table'
