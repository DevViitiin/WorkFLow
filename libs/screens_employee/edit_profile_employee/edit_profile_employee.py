import json
import re
import logging
import traceback
import cloudinary
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty, get_color_from_hex
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from plyer import filechooser
from kivy.clock import Clock

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class EditEmployee(MDScreen):
    """
    Tela para edição dos dados do funcionário.

    Esta classe gerencia a edição e atualização das informações pessoais e
    profissionais do funcionário, incluindo nome, função, contatos e avatar.

    Attributes:
        employee_name (StringProperty): Nome do funcionário.
        employee_function (StringProperty): Função do funcionário.
        employee_mail (StringProperty): Email do funcionário.
        employee_telephone (StringProperty): Telefone do funcionário.
        avatar (StringProperty): URL da imagem do avatar do funcionário.
        key (StringProperty): Chave única de identificação do funcionário.
        employee_summary (StringProperty): Resumo profissional do funcionário.
        skills (StringProperty): Habilidades do funcionário em formato de string.
        dont (str): Controle de disponibilidade de recursos.
        city (StringProperty): Cidade do funcionário.
        state (StringProperty): Estado do funcionário.
    """
    employee_name = StringProperty()
    employee_function = StringProperty()
    employee_mail = StringProperty()
    token_id = StringProperty()
    local_id = StringProperty()
    api_key = StringProperty()
    refresh_token = StringProperty()
    employee_telephone = StringProperty()
    avatar = StringProperty()
    key = StringProperty()
    employee_summary = StringProperty()
    skills = StringProperty()
    dont = 'Sim'
    city = StringProperty()
    state = StringProperty()

    # Constants
    FIREBASE_URL = 'https://obra-7ebd9-default-rtdb.firebaseio.com'
    CLOUDINARY_CONFIG = {
        "cloud_name": "dsmgwupky",
        "api_key": "256987432736353",
        "api_secret": "K8oSFMvqA6N2eU4zLTnLTVuArMU"
    }

    # Lista de profissões disponíveis
    AVAILABLE_FUNCTIONS = [
            # Profissionais de nível superior
            "Engenheiro Civil",
            "Engenheiro de Produção Civil",
            "Engenheiro de Estruturas",
            "Engenheiro de Transportes",
            "Engenheiro de Geotecnia",
            "Engenheiro de Saneamento",
            "Engenheiro de Segurança do Trabalho",
            "Engenheiro Hidráulico",
            "Engenheiro de Materiais",
            "Engenheiro Ambiental",
            "Arquiteto e Urbanista",
            "Tecnólogo em Construção Civil",
            "Tecnólogo em Estruturas",
            "Tecnólogo em Edificações",

            # Profissionais técnicos
            "Técnico em Edificações",
            "Técnico em Construção Civil",
            "Técnico em Estradas",
            "Técnico em Geoprocessamento",
            "Técnico em Saneamento",
            "Técnico em Segurança do Trabalho",
            "Técnico em Topografia",
            "Técnico em Materiais de Construção",

            # Mão de obra especializada
            "Mestre de Obras",
            "Contramestre de Obras",
            "Pedreiro",
            "Azulejista",
            "Carpinteiro de Obras",
            "Carpinteiro de Esquadrias",
            "Armador de Ferragens",
            "Encanador",
            "Eletricista de Obras",
            "Pintor de Obras",
            "Gesseiro",
            "Vidraceiro",
            "Caldeireiro de Estruturas Metálicas",
            "Montador de Estruturas Metálicas",
            "Soldador de Estruturas",
            "Rejuntador",

            # Outros relacionados
            "Servente de Obras",
            "Operador de Betoneira",
            "Operador de Máquinas Pesadas",
            "Topógrafo",
            "Calceteiro",
            "Impermeabilizador",
            "Escorador",
            "Ladrilheiro",
            "Marceneiro de Obras",
            "Serralheiro",
            "Apontador de Obras",
            "Pavimentador"
        ]

    def __init__(self, **kwargs):
        """
        Inicializa a classe EditEmployee.

        Configura o Cloudinary e inicializa os menus.

        Args:
            **kwargs: Argumentos de palavra-chave para passar para a classe pai.
        """
        try:
            super().__init__(**kwargs)

            # Cloudinary configuration
            cloudinary.config(**self.CLOUDINARY_CONFIG)
            logging.info("Cloudinary configurado com sucesso")

            # Initialize menu
            self.menu2 = None
            self.menu_functions()

        except Exception as e:
            logging.error(f"Erro ao inicializar EditEmployee: {str(e)}")
            logging.error(traceback.format_exc())

    def on_enter(self):
        """
        Método chamado quando a tela é exibida.

        Preenche os campos do formulário com os dados atuais do funcionário.
        """
        print(f'Local id: {self.local_id}')
        try:
            logging.info(f"Entrando na tela de edição para funcionário: {self.employee_name}")

            # Verificar se todos os IDs necessários existem
            required_ids = ['name_user', 'perfil', 'email', 'telefone', 'function']
            for id_name in required_ids:
                if not hasattr(self.ids, id_name):
                    logging.error(f"ID '{id_name}' não encontrado na tela")
                    self.show_error(f"Erro ao carregar interface - ID '{id_name}' ausente")
                    return

            # Preencher campos
            if self.employee_name != "Não definido":
                self.ids.name_user.text = self.employee_name or ""
                
            self.ids.perfil.source = self.avatar or ""

            # Mapear IDs para propriedades
            field_mapping = {
                
                'email': self.employee_mail,
                'telefone': self.employee_telephone,
                'function': self.employee_function
            }

            # Preencher campos se tiverem valores válidos
            for field_id, value in field_mapping.items():
                if value and value != 'Não definido':
                    self.ids[field_id].text = value
                    logging.debug(f"Campo {field_id} preenchido com: {value}")
                else:
                    logging.debug(f"Campo {field_id} não preenchido (valor: {value})")

        except Exception as e:
            logging.error(f"Erro ao carregar dados do funcionário: {str(e)}")
            logging.error(traceback.format_exc())
            self.show_error("Erro ao carregar dados do funcionário")
        
        self.verific_token()
        self.event_token = Clock.schedule_interval(self.verific_token, 300)


    def verific_token(self):
        print('🔎 verificando token...')
        UrlRequest(
            f"{self.FIREBASE_URL}/Funcionarios/{self.local_id}.json?auth={self.token_id}",
            on_success=self.on_success,
            on_failure=self.on_failure,
            on_error=self.on_failure,
            method="GET"
        )

    def on_failure(self, req, result):
        print('❌ Token inválido, tentando atualizar...', result)
        self.refresh_id_token()  # chama atualização

    def on_success(self, req, result):
        print('✅ Token válido, usuário encontrado:')


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

    def menu_functions(self):
        """
        Cria o menu dropdown para seleção de função profissional.

        Configura o menu com as opções de profissões disponíveis.
        """
        try:
            # Verificar se o ID necessário existe
            if not hasattr(self.ids, 'card_function'):
                logging.error("ID 'card_function' não encontrado")
                return

            # Criar itens do menu
            menu_itens = []
            for position, state in enumerate(self.AVAILABLE_FUNCTIONS, 1):
                row = {
                    'text': state,
                    'on_release': lambda x=state: self.replace_function(x),
                    'font_style': "Subtitle1",
                    'height': dp(56),
                    'icon': "checkbox-marked-circle-outline",
                    'divider': "Full"
                }
                menu_itens.append(row)

            # Criar o menu
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

            logging.info("Menu de funções criado com sucesso")

        except Exception as e:
            logging.error(f"Erro ao criar menu de funções: {str(e)}")
            logging.error(traceback.format_exc())
            self.show_error("Erro ao carregar menu de funções")

    def replace_function(self, text):
        """
        Atualiza o campo de função com a opção selecionada.

        Args:
            text (str): Texto da função selecionada.
        """
        try:
            if not hasattr(self.ids, 'function'):
                logging.error("ID 'function' não encontrado")
                return

            self.ids.function.text = text
            self.ids.function.text_color = get_color_from_hex('#FFFB46')

            if self.menu2:
                self.menu2.dismiss()
            else:
                logging.warning("Menu não está inicializado")

        except Exception as e:
            logging.error(f"Erro ao atualizar função: {str(e)}")
            self.show_error("Erro ao selecionar função")

    def step_one(self):
        """
        Valida os campos do formulário e envia para atualização se válidos.

        Verifica se todos os campos obrigatórios estão preenchidos corretamente
        antes de submeter a atualização para o banco de dados.
        """
        try:
            logging.info("Iniciando validação do formulário")

            # Verificar se todos os IDs necessários existem
            required_ids = ['function', 'telefone', 'email', 'name_user']
            for id_name in required_ids:
                if not hasattr(self.ids, id_name):
                    logging.error(f"ID '{id_name}' não encontrado na tela")
                    self.show_error(f"Erro na interface - ID '{id_name}' ausente")
                    return

            # Verificar campo função
            if self.ids.function.text in ['Selecione uma profissão', '']:
                logging.info("Função não selecionada, abrindo menu")
                if self.menu2:
                    self.menu2.open()
                else:
                    self.show_error("Menu de funções não está disponível")
                return

            # Verificar campos obrigatórios
            field_checks = [
                ('telefone', 'telefone'),
                ('email', 'e-mail'),
                ('name_user', 'Nome')
            ]

            for field_id, name in field_checks:
                if not self.ids[field_id].text:
                    self.ids[field_id].focus = True
                    self.show_error(f"Por favor, preencha o campo {name}")
                    return

            # Validar email
            if not self.is_email_valid(self.ids.email.text):
                self.ids.email.focus = True
                self.show_error("Por favor, insira um e-mail válido")
                return

            # Verificar alterações em qualquer campo
            if (self.ids.email.text != self.employee_mail or
                    self.ids.telefone.text != self.employee_telephone or
                    self.ids.name_user.text != self.employee_name or
                    self.ids.function.text != self.employee_function or
                    self.avatar != self.ids.perfil.source):
                logging.info("Dados alterados, enviando atualização")
                self.update_database()
            else:
                logging.info("Nenhuma alteração detectada")
                self.show_message("Apresente novos dados para atualização", color='#00b894')

        except Exception as e:
            logging.error(f"Erro na validação do formulário: {str(e)}")
            logging.error(traceback.format_exc())
            self.show_error("Erro ao processar formulário")

    def update_database(self):
        """
        Atualiza os dados do usuário no Firebase.

        Envia os dados atualizados para o banco de dados Firebase.
        """
        try:
            url = f'{self.FIREBASE_URL}/Funcionarios/{self.local_id}/.json?auth={self.token_id}'

            # Prepara os dados para envio
            data = {
                'Name': str(self.ids.name_user.text).replace(' ', ''),
                'email': self.ids.email.text,
                'avatar': self.ids.perfil.source,
                'telefone': self.ids.telefone.text,
                'function': self.ids.function.text
            }

            logging.info(f"Enviando atualização para Firebase: {url}")
            logging.debug(f"Dados: {data}")

            # Envia a requisição
            UrlRequest(
                f'{url}',
                method='PATCH',
                req_body=json.dumps(data),
                on_success=self.database_success,
                on_error=self.database_error,
                on_failure=self.database_failure,
                timeout=10
            )

            self.show_message("Enviando dados para atualização...", color='#3498db')

        except Exception as e:
            logging.error(f"Erro ao preparar atualização do banco de dados: {str(e)}")
            logging.error(traceback.format_exc())
            self.show_error("Erro ao conectar com o banco de dados")

    def database_success(self, req, result):
        """
        Callback para sucesso na atualização do banco de dados.

        Navega de volta para a tela principal do funcionário com os dados atualizados.

        Args:
            req: O objeto de requisição.
            result: O resultado da requisição.
        """
        try:
            logging.info("Atualização no Firebase concluída com sucesso")

            app = MDApp.get_running_app()
            if not app:
                logging.error("Aplicativo não encontrado")
                self.show_error("Erro ao navegar: aplicativo não encontrado")
                return

            screenmanager = app.root
            if not screenmanager:
                logging.error("Gerenciador de telas não encontrado")
                self.show_error("Erro ao navegar: gerenciador de telas não encontrado")
                return

            try:
                perfil = screenmanager.get_screen('PrincipalScreenEmployee')
            except Exception as e:
                logging.error(f"Tela PrincipalScreenEmployee não encontrada: {str(e)}")
                self.show_error("Erro ao navegar: tela principal não encontrada")
                return

            # Atualiza os dados na tela principal
            perfil.employee_name = self.ids.name_user.text
            perfil.employee_function = self.ids.function.text
            perfil.employee_mail = self.ids.email.text
            perfil.avatar = self.ids.perfil.source
            perfil.employee_telephone = self.ids.telefone.text
            perfil.key = self.key
            perfil.token_id = self.token_id
            perfil.local_id = self.local_id
            perfil.refresh_token = self.refresh_token
            perfil.api_key = self.api_key
            perfil.employee_summary = self.employee_summary
            perfil.skills = self.skills
            perfil.city = self.city
            perfil.state = self.state

            # Navega para a tela principal
            screenmanager.transition = SlideTransition(direction='right')
            screenmanager.current = 'PrincipalScreenEmployee'

            self.show_message("Dados atualizados com sucesso!", color='#00b894')

        except Exception as e:
            logging.error(f"Erro após atualização do banco de dados: {str(e)}")
            logging.error(traceback.format_exc())
            self.show_error("Erro ao processar resposta do servidor")

    def database_error(self, req, error):
        """
        Callback para erro na requisição ao banco de dados.

        Args:
            req: O objeto de requisição.
            error: O erro ocorrido.
        """
        logging.error(f"Erro na requisição ao Firebase: {error}")
        self.show_error("Erro na comunicação com o servidor")

    def database_failure(self, req, result):
        """
        Callback para falha na requisição ao banco de dados.

        Args:
            req: O objeto de requisição.
            result: O resultado da requisição.
        """
        logging.error(f"Falha na requisição ao Firebase: {result}")
        self.show_error("Falha na comunicação com o servidor")

    def is_email_valid(self, text):
        """
        Valida o formato do email.

        Args:
            text (str): Email a ser validado.

        Returns:
            bool: True se o email for válido, False caso contrário.
        """
        try:
            if not text:
                return False

            email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            return re.match(email_regex, text) is not None

        except Exception as e:
            logging.error(f"Erro ao validar email: {str(e)}")
            return False

    def recortar_imagem_circular(self, imagem_path):
        """
        Faz upload e recorta a imagem em formato circular usando o Cloudinary.

        Args:
            imagem_path (str): Caminho do arquivo de imagem selecionado.

        Returns:
            str or None: URL da imagem processada ou None em caso de erro.
        """
        try:
            if not imagem_path:
                logging.error("Caminho de imagem vazio")
                return None

            logging.info(f"Enviando imagem para Cloudinary: {imagem_path}")

            # Fazer upload e transformar a imagem
            response = cloudinary.uploader.upload(
                imagem_path,
                public_id=self.employee_name,
                overwrite=True,
                transformation=[
                    {'width': 1000, 'height': 1000, 'crop': 'thumb', 'gravity': 'face', 'radius': 'max'}
                ]
            )

            secure_url = response.get('secure_url')
            if not secure_url:
                logging.error("URL segura não recebida do Cloudinary")
                self.show_error("Erro ao processar imagem")
                return None

            logging.info(f"Imagem processada com sucesso: {secure_url}")

            # Atualizar a imagem na interface
            if hasattr(self.ids, 'perfil'):
                self.ids.perfil.source = secure_url
            else:
                logging.error("ID 'perfil' não encontrado")

            # Continuar com a atualização
            self.step_one()
            return secure_url

        except Exception as e:
            logging.error(f"Erro ao processar imagem no Cloudinary: {str(e)}")
            logging.error(traceback.format_exc())
            self.show_error(f"Erro ao processar imagem: {str(e)}")
            return None

    def open_gallery(self):
        """
        Abre a galeria para selecionar uma imagem.

        Utiliza o módulo filechooser para abrir o seletor de arquivos do sistema.
        """
        try:
            if self.dont == 'Não':
                logging.info("Acesso à galeria desativado")
                self.show_message('Galeria não disponível')
                return

            logging.info("Abrindo seletor de arquivos")
            filechooser.open_file(
                filters=["*.jpg", "*.png", "*.jpeg"],
                on_selection=self.select_path
            )

        except Exception as e:
            logging.error(f"Erro ao abrir a galeria: {str(e)}")
            logging.error(traceback.format_exc())
            self.show_error(f"Erro ao abrir a galeria: {str(e)}")

    def show_message(self, message, color='#2196F3'):
        """
        Exibe uma mensagem no snackbar.

        Args:
            message (str): Mensagem a ser exibida.
            color (str, optional): Cor de fundo do snackbar. Padrão é '#2196F3'.
        """
        try:
            logging.info(f"Mensagem: {message}")

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
            logging.error(f"Erro ao exibir mensagem: {str(e)}")
            print(f"Erro ao exibir mensagem: {str(e)}")

    def show_error(self, error_message):
        """
        Exibe uma mensagem de erro.

        Args:
            error_message (str): Mensagem de erro a ser exibida.
        """
        self.show_message(error_message, color='#FF0000')
        logging.error(f"Erro UI: {error_message}")

    def select_path(self, selection):
        """
        Processa o arquivo de imagem selecionado.

        Args:
            selection (list): Lista com o caminho do arquivo selecionado.
        """
        try:
            if not selection:
                logging.warning("Nenhum arquivo selecionado")
                return

            path = selection[0]
            logging.info(f"Arquivo selecionado: {path}")

            # Processa a imagem
            self.recortar_imagem_circular(path)
            self.show_message(f"Processando imagem...")

        except Exception as e:
            logging.error(f"Erro ao processar arquivo selecionado: {str(e)}")
            self.show_error(f"Erro ao processar arquivo: {str(e)}")

    def on_text_two(self, instance, numero):
        """
        Formata o número de telefone.

        Aplica uma máscara ao número de telefone inserido.

        Args:
            instance: A instância do widget.
            numero (str): O número de telefone a ser formatado.
        """
        try:
            # Remove caracteres não numéricos
            numero = re.sub(r'\D', '', numero)

            # Formata o número se tiver o tamanho correto
            if len(numero) == 11:
                formatted = f"({numero[0:2]}) {numero[2:7]}-{numero[7:]}"

                if hasattr(self.ids, 'telefone'):
                    self.ids.telefone.text = formatted
                    self.ids.telefone.focus = False
                    self.ids.telefone.error = False
                else:
                    logging.error("ID 'telefone' não encontrado")
            else:
                if hasattr(self.ids, 'telefone'):
                    self.ids.telefone.error = True
                else:
                    logging.error("ID 'telefone' não encontrado")

        except Exception as e:
            logging.error(f"Erro ao formatar número de telefone: {str(e)}")

    def next_page(self):
        """
        Navega para a segunda página de edição do perfil.

        Transfere os dados atuais para a próxima tela de edição.
        """
        try:
            # Executar ações de pré-saída
            self.on_pre_leave()

            app = MDApp.get_running_app()
            if not app:
                logging.error("Aplicativo não encontrado")
                self.show_error("Erro ao navegar: aplicativo não encontrado")
                return

            screenmanager = app.root
            if not screenmanager:
                logging.error("Gerenciador de telas não encontrado")
                self.show_error("Erro ao navegar: gerenciador de telas não encontrado")
                return

            try:
                perfil = screenmanager.get_screen('EditEmployeeTwo')
            except Exception as e:
                logging.error(f"Tela EditEmployeeTwo não encontrada: {str(e)}")
                self.show_error("Erro ao navegar: próxima tela não encontrada")
                return

            # Transfere os dados para a próxima tela
            perfil.employee_name = self.employee_name
            perfil.employee_function = self.employee_function
            perfil.employee_mail = self.employee_mail
            perfil.employee_telephone = self.employee_telephone
            perfil.key = self.key
            perfil.avatar = self.avatar
            perfil.employee_summary = self.employee_summary
            perfil.skills = self.skills
            perfil.city = self.city
            perfil.state = self.state
            perfil.token_id = self.token_id
            perfil.api_key = self.api_key
            perfil.local_id = self.local_id
            perfil.refresh_token = self.refresh_token

            # Navega para a próxima página
            screenmanager.transition = SlideTransition(direction='left')
            screenmanager.current = 'EditEmployeeTwo'
            logging.info("Navegou para a segunda página de edição")

        except Exception as e:
            logging.error(f"Erro ao navegar para próxima página: {str(e)}")
            logging.error(traceback.format_exc())
            self.show_error("Erro ao navegar para próxima página")

    def login(self):
        """
        Retorna para a tela principal do funcionário.

        Executa as ações de pré-saída e navega de volta para a tela principal.
        """
        try:
            self.on_pre_leave()

            if not self.manager:
                logging.error("Gerenciador de telas não disponível")
                return

            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = 'PrincipalScreenEmployee'
            logging.info("Retornou para a tela principal")

        except Exception as e:
            logging.error(f"Erro ao retornar para tela principal: {str(e)}")
            self.show_error("Erro ao retornar para tela principal")

    def on_pre_leave(self, *args):
        """
        Método chamado antes de sair da tela.

        Realiza ajustes na interface antes de navegar para outra tela.

        Args:
            *args: Argumentos variáveis.
        """
        try:
            if hasattr(self.ids, 'scroll_view'):
                self.ids.scroll_view.scroll_y = 1
            else:
                logging.warning("ID 'scroll_view' não encontrado")

        except Exception as e:
            logging.error(f"Erro no método on_pre_leave: {str(e)}")