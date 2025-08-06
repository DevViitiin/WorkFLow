import json
import logging
from typing import List, Dict, Any, Optional, Union, Callable

from libs.screens.function_screen.citys import *
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.properties import get_color_from_hex, StringProperty
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.button import MDButtonText, MDButton
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText


class EditEmployeeTwo(MDScreen):
    """
    Tela para edição de informações adicionais do funcionário.

    Esta tela permite editar informações como localização, resumo profissional
    e habilidades do funcionário. É a segunda parte do fluxo de edição de perfil.

    Attributes:
        employee_name (StringProperty): Nome do funcionário.
        employee_function (StringProperty): Função do funcionário.
        employee_mail (StringProperty): Email do funcionário.
        employee_telephone (StringProperty): Telefone do funcionário.
        avatar (StringProperty): Caminho para a imagem de avatar do funcionário.
        city (StringProperty): Cidade do funcionário.
        state (StringProperty): Estado do funcionário.
        key (StringProperty): Chave identificadora do funcionário no Firebase.
        employee_summary (StringProperty): Resumo profissional do funcionário.
        skills (StringProperty): String JSON contendo as habilidades do funcionário.
        skill_add (int): Contador para controle de adição de habilidades.
        new_skills (list): Lista para armazenar as novas habilidades adicionadas.
        FIREBASE_URL (str): URL base do Firebase para requisições.
    """

    employee_name = StringProperty()
    employee_function = StringProperty()
    employee_mail = StringProperty()
    employee_telephone = StringProperty()
    avatar = StringProperty()
    city = StringProperty()
    state = StringProperty()
    key = StringProperty()
    employee_summary = StringProperty()
    skills = StringProperty('[]')
    skill_add = 0
    FIREBASE_URL = 'https://obra-7ebd9-default-rtdb.firebaseio.com'
    new_skills = []

    def __init__(self, **kwargs):
        """
        Inicializa a tela EditEmployeeTwo.

        Configura o botão padrão para quando não há habilidades adicionadas.

        Args:
            **kwargs: Argumentos adicionais passados para a classe pai.
        """
        super().__init__(**kwargs)
        # Configurar logger para registro de eventos
        self.logger = logging.getLogger('EditEmployeeTwo')

        # Botão padrão para quando não há habilidades
        self.button = MDButton(
            MDButtonText(
                text=f'Nenhuma habilidade foi adicionada',
                theme_text_color='Custom',
                text_color='white',
                bold=True
            ),
            theme_bg_color='Custom',
            md_bg_color=get_color_from_hex('#0047AB')
        )
        self.ids['not_add'] = self.button

        # Inicializar menus como None para verificação posterior
        self.menu = None
        self.menu_city = None

    def on_enter(self):
        """
        Método chamado quando a tela é exibida.

        Inicializa os menus de estados e cidades, carrega as habilidades
        do funcionário e configura os campos com os valores atuais.
        """
        try:
            self.skill_add += 1
            self.menu_citys()
            self.menu_states()

            # Configura os campos de estado e cidade
            if self.state:
                self.ids.state.text = self.state

            if self.city:
                self.ids.city.text = self.city

            # Carrega as habilidades existentes
            try:
                skills = eval(self.skills)
                if not isinstance(skills, list):
                    self.logger.error(f"Skills não é uma lista válida: {self.skills}")
                    skills = []
            except (SyntaxError, TypeError, ValueError) as e:
                self.logger.error(f"Erro ao avaliar skills: {e}")
                skills = []

            # Popula a lista de novas habilidades
            if skills:
                self.new_skills = [skill for skill in skills]

            # Configura o resumo profissional
            if self.employee_summary and self.employee_summary != 'Não definido':
                self.ids.sumary.text = self.employee_summary

            # Adiciona as habilidades à interface
            if self.skill_add == 1:
                self.add_skills(skills)
            else:
                self.ids.main_scroll.clear_widgets()
                self.skill_add = 0
                self.add_skills(skills)

        except Exception as e:
            self.logger.error(f"Erro em on_enter: {e}")
            self.show_error(f"Erro ao carregar dados: {str(e)}")

    def menu_citys(self):
        """
        Inicializa o menu dropdown de cidades.

        Cria um menu padrão com uma mensagem de indisponibilidade.
        Este menu será atualizado posteriormente quando um estado for selecionado.
        """
        try:
            menu_itens = []
            payments = ['Cidades indisponiveis']
            for payment in payments:
                row = {'text': payment, 'text_color': 'red'}
                menu_itens.append(row)

            self.menu_city = MDDropdownMenu(
                caller=self.ids.card_city,
                items=menu_itens,
                position='bottom',
                pos_hint={'center_x': 0.5, 'center_y': 0.35}
            )
        except Exception as e:
            self.logger.error(f"Erro ao criar menu de cidades: {e}")
            self.show_error("Erro ao inicializar menu de cidades")

    def menu_states(self):
        """
        Inicializa o menu dropdown de estados.

        Cria um menu com todos os estados brasileiros para seleção.
        """
        try:
            # Lista de estados brasileiros
            states = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS',
                      'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP',
                      'SE', 'TO']

            menu_itens = []
            for state in states:
                # Cria um item de menu para cada estado
                row = {'text': state, 'on_release': lambda x=state: self.replace_state(x)}
                menu_itens.append(row)

            self.menu = MDDropdownMenu(
                caller=self.ids.card_state,
                items=menu_itens,
                position='bottom',
                pos_hint={'center_x': 0.5}
            )
        except Exception as e:
            self.logger.error(f"Erro ao criar menu de estados: {e}")
            self.show_error("Erro ao inicializar menu de estados")

    def replace_state(self, state: str):
        """
        Atualiza o estado selecionado e recria o menu de cidades correspondente.

        Args:
            state (str): Sigla do estado selecionado.
        """
        try:
            if not state:
                self.logger.warning("Estado vazio selecionado")
                return

            # Atualiza a interface com o estado selecionado
            self.ids.city.text_color = 'white'
            self.ids.city.text = 'Selecione uma cidade'
            self.ids.state.text_color = get_color_from_hex('#FFFB46')
            self.ids.state.text = f'{state}'

            # Fecha o menu de estados
            if self.menu:
                self.menu.dismiss()

            # Cria o menu de cidades para o estado selecionado
            self.create_menu(state)
        except Exception as e:
            self.logger.error(f"Erro ao selecionar estado: {e}")
            self.show_error(f"Erro ao selecionar estado: {str(e)}")

    def create_menu(self, state: str):
        """
        Cria o menu dropdown de cidades para o estado selecionado.

        Args:
            state (str): Sigla do estado para o qual criar o menu de cidades.
        """
        try:
            menu_items = []

            # Mapeamento de estados para suas respectivas funções de cidades
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

            # Obter cidades para o estado selecionado
            if state in state_functions:
                try:
                    cities = state_functions[state]()
                    if not cities:
                        self.logger.warning(f"Nenhuma cidade encontrada para o estado {state}")
                        cities = ["Nenhuma cidade disponível"]

                    for city in cities:
                        row = {'text': city, 'on_release': lambda x=city: self.replace_city(x)}
                        menu_items.append(row)
                except Exception as city_error:
                    self.logger.error(f"Erro ao obter cidades para o estado {state}: {city_error}")
                    menu_items = [{'text': 'Erro ao carregar cidades', 'text_color': 'red'}]
            else:
                self.logger.error(f"Estado '{state}' não encontrado!")
                menu_items = [{'text': 'Estado inválido', 'text_color': 'red'}]

            # Recria o menu de cidades
            if hasattr(self, 'menu_city') and self.menu_city:
                self.menu_city.dismiss()

            self.menu_city = MDDropdownMenu(
                caller=self.ids.card_city,
                items=menu_items,
                position='bottom',
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
        except Exception as e:
            self.logger.error(f"Erro ao criar menu para o estado {state}: {e}")
            self.show_error(f"Erro ao carregar cidades: {str(e)}")

    def replace_city(self, city: str):
        """
        Atualiza a cidade selecionada na interface.

        Args:
            city (str): Nome da cidade selecionada.
        """
        try:
            if not city:
                self.logger.warning("Cidade vazia selecionada")
                return

            self.ids.city.text_color = get_color_from_hex('#FFFB46')
            self.ids.city.text = city

            if self.menu_city:
                self.menu_city.dismiss()
        except Exception as e:
            self.logger.error(f"Erro ao selecionar cidade: {e}")
            self.show_error(f"Erro ao selecionar cidade: {str(e)}")

    def limitate(self, instance, text: str):
        """
        Limita o texto do resumo a 120 caracteres.

        Args:
            instance: Instância do widget que chamou a função.
            text (str): Texto atual do campo.
        """
        try:
            # Limita o texto a 120 caracteres
            limited_text = text[:120] if text else ""
            self.ids.sumary.text = limited_text
        except Exception as e:
            self.logger.error(f"Erro ao limitar texto: {e}")
            self.show_error("Erro ao processar texto")

    def add_skill(self):
        """
        Adiciona uma nova habilidade à lista de habilidades.

        Obtém o texto do campo de habilidade, adiciona à lista de habilidades
        e atualiza a interface.
        """
        try:
            skill = self.ids.skill.text.strip()

            if not skill:
                self.show_message("Digite uma habilidade para adicionar", color='#FFA500')
                return

            # Verifica se a habilidade já existe na lista
            if skill in self.new_skills:
                self.show_message("Esta habilidade já foi adicionada", color='#FFA500')
                return

            # Limpa o widget de rolagem e adiciona a nova habilidade
            self.ids.main_scroll.clear_widgets()
            self.new_skills.append(f'{skill}')

            # Adiciona todas as habilidades à interface
            for k in self.new_skills:
                button = MDButton(
                    MDButtonText(
                        text=f'{k}',
                        theme_text_color='Custom',
                        text_color='white',
                        bold=True
                    ),
                    theme_bg_color='Custom',
                    md_bg_color=get_color_from_hex('#0047AB')
                )
                self.ids.main_scroll.add_widget(button)

            # Limpa o campo de entrada
            self.ids.skill.text = ''
        except Exception as e:
            self.logger.error(f"Erro ao adicionar habilidade: {e}")
            self.show_error(f"Erro ao adicionar habilidade: {str(e)}")

    def add_skills(self, skills: List[str]):
        """
        Adiciona as habilidades existentes à interface.

        Args:
            skills (List[str]): Lista de habilidades para adicionar.
        """
        try:
            if not isinstance(skills, list):
                self.logger.error(f"Skills não é uma lista: {type(skills)}")
                skills = []

            # Se houver habilidades, adiciona cada uma à interface
            if skills:
                self.ids.main_scroll.clear_widgets()
                for skill in skills:
                    button = MDButton(
                        MDButtonText(
                            text=f'{skill}',
                            theme_text_color='Custom',
                            text_color='white',
                            bold=True
                        ),
                        theme_bg_color='Custom',
                        md_bg_color=get_color_from_hex('#0047AB')
                    )
                    self.ids.main_scroll.add_widget(button)
            else:
                # Se não houver habilidades, mostra o botão padrão
                self.ids.main_scroll.add_widget(self.button)
        except Exception as e:
            self.logger.error(f"Erro ao adicionar habilidades: {e}")
            self.show_error(f"Erro ao exibir habilidades: {str(e)}")

    def show_message(self, message: str, color: str = '#2196F3'):
        """
        Exibe uma mensagem na interface usando um snackbar.

        Args:
            message (str): Mensagem a ser exibida.
            color (str, opcional): Cor de fundo do snackbar. Padrão é '#2196F3' (azul).
        """
        try:
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
        except Exception as e:
            self.logger.error(f"Erro ao exibir mensagem: {e}")
            print(f"Erro ao exibir mensagem: {e}")

    def show_error(self, error_message: str):
        """
        Exibe uma mensagem de erro na interface.

        Args:
            error_message (str): Mensagem de erro a ser exibida.
        """
        self.show_message(error_message, color='#FF0000')
        self.logger.error(f"Error: {error_message}")

    def step_one(self):
        """
        Valida os campos do formulário e envia se forem válidos.

        Verifica se todos os campos obrigatórios estão preenchidos e
        inicia o processo de atualização no banco de dados.
        """
        try:
            # Verifica se há pelo menos 3 habilidades
            try:
                current_skills = eval(self.skills) if self.skills else []
                if not isinstance(current_skills, list):
                    current_skills = []
            except (SyntaxError, TypeError, ValueError):
                current_skills = []

            if len(current_skills) < 3 and len(self.new_skills) < 3:
                self.show_error('Obrigatório adicionar pelo menos 3 habilidades')
                return

            # Verifica se o resumo profissional foi preenchido
            if not self.ids.sumary.text or self.ids.sumary.text.strip() == "":
                self.show_error('Resumo profissional obrigatório*')
                return

            # Verifica se o estado foi selecionado
            if self.ids.state.text in ['Selecione um Estado', '']:
                self.show_message('Selecione um estado', color='#FFA500')
                if self.menu:
                    self.menu.open()
                return

            # Verifica se a cidade foi selecionada
            if self.ids.city.text in ['Selecione uma cidade', '']:
                self.show_message('Selecione uma cidade', color='#FFA500')
                if self.menu_city:
                    self.menu_city.open()
                return

            # Inicia a atualização no banco de dados
            self.update_database()
        except Exception as e:
            self.logger.error(f"Erro ao validar formulário: {e}")
            self.show_error(f"Erro ao processar dados: {str(e)}")

    def restart(self):
        """
        Reinicia apenas as habilidades do usuário no Firebase.

        Esta função é usada para limpar a lista de habilidades.
        """
        try:
            if not self.key:
                self.show_error("Chave do funcionário não definida")
                return

            url = f'{self.FIREBASE_URL}/Funcionarios/{self.key}'

            data = {
                'skills': f"{self.new_skills}"
            }

            # Envia a requisição para atualizar as habilidades
            UrlRequest(
                f'{url}/.json',
                method='PATCH',
                req_body=json.dumps(data),
                on_success=self.clear_main,
                on_error=self.on_request_error,
                on_failure=self.on_request_failure,
                timeout=10
            )
        except Exception as e:
            self.logger.error(f"Erro ao reiniciar habilidades: {e}")
            self.show_error(f"Erro ao atualizar habilidades: {str(e)}")

    def clear_main(self, instance, result):
        """
        Limpa a interface após uma atualização bem-sucedida.

        Args:
            instance: Instância da requisição.
            result: Resultado da requisição.
        """
        try:
            self.ids.main_scroll.clear_widgets()
            self.new_skills = []
            self.add_skills([])
            self.show_message("Habilidades atualizadas com sucesso", color='#4CAF50')
        except Exception as e:
            self.logger.error(f"Erro ao limpar interface: {e}")
            self.show_error(f"Erro ao atualizar interface: {str(e)}")

    def update_database(self):
        """
        Atualiza os dados do funcionário no Firebase.

        Envia uma requisição PATCH para atualizar os dados do funcionário
        com as informações atualizadas na interface.
        """
        try:
            if not self.key:
                self.show_error("Chave do funcionário não definida")
                return

            url = f'{self.FIREBASE_URL}/Funcionarios/{self.key}'

            # Prepara os dados para atualização
            data = {
                'Name': self.employee_name,
                'email': self.employee_mail,
                'avatar': self.avatar,
                'telefone': self.employee_telephone,
                'function': self.employee_function,
                'sumary': self.ids.sumary.text.strip(),
                'skills': f"{self.new_skills}",
                'state': f"{self.ids.state.text}",
                'city': f"{self.ids.city.text}"
            }

            # Envia a requisição para atualizar os dados
            UrlRequest(
                f'{url}/.json',
                method='PATCH',
                req_body=json.dumps(data),
                on_success=self.database_success,
                on_error=self.on_request_error,
                on_failure=self.on_request_failure,
                timeout=10
            )
        except Exception as e:
            self.logger.error(f"Erro ao atualizar banco de dados: {e}")
            self.show_error(f"Erro ao salvar dados: {str(e)}")

    def on_request_error(self, request, error):
        """
        Manipula erros de requisição.

        Args:
            request: Objeto da requisição.
            error: Informações sobre o erro.
        """
        self.logger.error(f"Erro na requisição: {error}")
        self.show_error(f"Erro na comunicação com o servidor: {error}")

    def on_request_failure(self, request, result):
        """
        Manipula falhas de requisição.

        Args:
            request: Objeto da requisição.
            result: Resultado da requisição.
        """
        self.logger.error(f"Falha na requisição: {result}")
        self.show_error("Falha ao comunicar com o servidor")

    def database_success(self, req, result):
        """
        Manipula o sucesso da atualização no banco de dados.

        Após a atualização bem-sucedida, navega para a tela de perfil
        do funcionário com os dados atualizados.

        Args:
            req: Objeto da requisição.
            result: Resultado da requisição contendo os dados atualizados.
        """
        try:
            # Verifica se o resultado contém os dados necessários
            required_fields = ['Name', 'function', 'email', 'telefone', 'sumary', 'skills', 'city', 'state']
            for field in required_fields:
                if field not in result:
                    self.logger.error(f"Campo {field} ausente no resultado")
                    self.show_error(f"Dados incompletos recebidos do servidor")
                    return

            app = MDApp.get_running_app()
            self.new_skills = []  # Limpa a lista de novas habilidades

            # Obtém o gerenciador de telas e a tela de perfil
            screenmanager = app.root
            perfil = screenmanager.get_screen('PrincipalScreenEmployee')

            # Atualiza os dados da tela de perfil
            perfil.employee_name = result['Name']
            perfil.employee_function = result['function']
            perfil.employee_mail = result['email']
            perfil.employee_telephone = result['telefone']
            perfil.employee_summary = result['sumary']
            perfil.skills = result['skills']
            perfil.city = result['city']
            perfil.state = result['state']

            # Navega para a tela de perfil
            screenmanager.transition = SlideTransition(direction='right')
            screenmanager.current = 'PrincipalScreenEmployee'

            self.show_message("Perfil atualizado com sucesso", color='#4CAF50')
        except Exception as e:
            self.logger.error(f"Erro ao processar sucesso do banco de dados: {e}")
            self.show_error(f"Erro ao finalizar atualização: {str(e)}")

    def previous_page(self):
        """
        Navega para a tela anterior de edição.

        Transfere os dados atuais para a tela anterior e navega para ela.
        """
        try:
            app = MDApp.get_running_app()
            screenmanager = app.root
            self.new_skills = []  # Limpa a lista de novas habilidades

            # Obtém a tela anterior e atualiza seus dados
            perfil = screenmanager.get_screen('EditEmployee')
            perfil.employee_name = self.employee_name
            perfil.employee_function = self.employee_function
            perfil.employee_mail = self.employee_mail
            perfil.employee_telephone = self.employee_telephone
            perfil.key = self.key
            perfil.avatar = self.avatar
            perfil.city = self.city
            perfil.state = self.state

            # Navega para a tela anterior
            screenmanager.transition = SlideTransition(direction='right')
            screenmanager.current = 'EditEmployee'
        except Exception as e:
            self.logger.error(f"Erro ao navegar para a página anterior: {e}")
            self.show_error(f"Erro ao voltar para a página anterior: {str(e)}")
