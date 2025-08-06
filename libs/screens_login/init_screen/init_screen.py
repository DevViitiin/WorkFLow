import ast
import json

import bcrypt
from kivy.metrics import dp
from kivy.properties import get_color_from_hex, StringProperty, Clock
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivy.animation import Animation
from kivymd.uix.screen import MDScreen
from kivy.network.urlrequest import UrlRequest
from kivymd.uix.snackbar import MDSnackbarText, MDSnackbar


class InitScreen(MDScreen):
    """
    Tela inicial do aplicativo que gerencia o login de usuários.

    Permite login como funcionário ou contratante, além de oferecer
    opção para registro de novos usuários.
    """
    carregado = False
    key = StringProperty()
    name = False
    senha = ''
    type = ''

    def on_enter(self, *args):
        """Método chamado quando a tela é exibida."""
        self.state_employee()


    """
    Solução principal para o problema de transição em mobile:
    1. Método de animação para evitar o "flash branco"
    2. Implementação de cache para componentes visuais 
    3. Correção de propriedades incorretas no KV
    """

    # ----- PARTE PYTHON -----

    def state_contractor(self):
        """Seleciona o perfil de contratante e aplica as mudanças visuais."""
        # Aplica todas as mudanças de cores de uma vez
        self.ids.employee_card.line_color = 'white'
        anime = Animation(duration=0.2, line_color=[0, 0, 1, 1])
        anime.start(self.ids.contractor_card)

        # Força uma atualização imediata do canvas
        self.ids.contractor_card.canvas.ask_update()
        self.ids.employee_card.canvas.ask_update()

        # Define o tipo de usuário
        self.type = 'Contratante'

    def state_employee(self):
        """Seleciona o perfil de funcionário e aplica as mudanças visuais."""
        # Aplica todas as mudanças de cores de uma vez

        self.ids.contractor_card.line_color = 'white'
        anime = Animation(duration=0.2, line_color=[0, 0, 1, 1])
        anime.start(self.ids.employee_card)

        # Força uma atualização imediata do canvas
        self.ids.employee_card.canvas.ask_update()
        self.ids.contractor_card.canvas.ask_update()

        # Define o tipo de usuário
        self.type = 'Funcionario'

    def usuarios_carregados(self, req, result):
        """
        Processa os dados dos usuários após carregamento bem-sucedido.

        Verifica se o nome de usuário existe na base de dados.

        Args:
            req: O objeto de requisição
            result: Os dados retornados pelo Firebase
        """
        try:
            if not result:
                self.show_error("Não foi possível carregar os dados de usuários")
                return

            self.name = False
            for cargo, nome in result.items():
                if nome['name'] == str(self.ids.nome.text):
                    self.name = True
                    self.senha = nome['senha']
                    self.key = cargo
                    self.etapa2(self.senha)
                    break

            if not self.name:
                self.ids.nome_errado.text = 'Usuário não cadastrado'
                self.ids.nome.error = True
        except Exception as e:
            self.show_error(f"Erro ao processar dados: {e}")

    def etapa2(self, hashd_password):
        """
        Verifica a senha do usuário.

        Compara a senha fornecida com o hash armazenado no Firebase.

        Args:
            hashd_password: O hash da senha armazenada
        """
        try:
            password_bytes = self.ids.senha.text.encode('utf-8')
            user_password_bytes = hashd_password.encode('utf-8')

            if bcrypt.checkpw(password_bytes, user_password_bytes):
                self.show_message("Login realizado com sucesso!")
            else:
                self.ids.senha_errada.text = 'Senha incorreta'
                self.ids.senha.error = True
        except Exception as e:
            self.show_error(f"Erro na verificação da senha: {e}")

    def register(self):
        """
        Navega para a tela de registro de novo usuário.
        """
        # resetando os cmapos
        self.ids.senha.text = ''
        self.ids.email.text = ''
        self.type = ''

        # Resetando o estado os cards
        self.ids.contractor_card.md_bg_color = 'white'
        self.ids.text_contractor.text_color = 'black'
        self.ids.employee_card.md_bg_color = 'white'
        self.ids.employee_text.text_color = 'black'

        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'ChoiceAccount'

    def go_to_next(self, perfil, name):
        """
        Navega para a próxima tela após o login.

        Args:
            perfil: O tipo de perfil do usuário
            name: O nome do usuário
        """
        self.manager.transition = SlideTransition(direction='left')
        login = self.manager.get_screen('LoginScreen')
        login.perfil = perfil
        login.nome = name
        self.manager.current = 'LoginScreen'

    def show_message(self, message, color='#2196F3'):
        """
        Exibe uma mensagem na interface através de um snackbar.

        Args:
            message: A mensagem a ser exibida
            color: A cor de fundo do snackbar
        """
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
            size_hint_x=0.94,
            theme_bg_color='Custom',
            background_color=get_color_from_hex(color),
            duration=3  # Duração da exibição do snackbar em segundos
        ).open()

    def show_error(self, error_message):
        """
        Exibe uma mensagem de erro através de um snackbar vermelho.

        Args:
            error_message: A mensagem de erro a ser exibida
        """
        self.show_message(error_message, color='#FF0000')

    def etapa1(self):
        """
        Inicia o processo de login verificando os campos preenchidos.

        Valida os campos de entrada e direciona para o fluxo adequado
        baseado no tipo de usuário.
        """
        try:
            # Verifica se um tipo de usuário foi selecionado
            if not self.type:
                self.show_error('Selecione o tipo de conta para efetuar o login')
                return

            # Verifica nome de usuário
            if not self.ids.email.text:
                self.ids.email.focus = True
                self.show_error('Insira seu email de usuário')
                return

            # Verifica senha
            if not self.ids.senha.text:
                self.ids.senha.focus = True
                self.show_error('Insira sua senha')
                return

            # Direciona para o fluxo adequado
            if self.type == 'Contratante':
                self.verificar_senha()
            else:
                self.senha_employee()
        except Exception as e:
            self.show_error(f"Erro ao iniciar login: {e}")

    def senha_employee(self):
        """
        Verifica as credenciais de login para funcionários.
        """
        print('Verificar funcioanario')
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

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
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
        print('Login feito, puxando os dados do funcionário...')
        id_token = result['idToken']
        id_local = result['localId']

        def sucesso(req, data):
            print("Dados encontrados:", data)
            self.data_found(req, data)

        def erro(req, erro_result):
            self.show_error(f"Usuario não encontrado tente como contratante")

        UrlRequest(
            f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{id_local}.json?auth={id_token}',
            method='GET',
            on_success=self.data_found,
            on_error=erro,
            on_failure=erro,
            on_cancel=erro,
            req_headers={"Content-Type": "application/json"}
        )

    def data_found(self, req, result):
        print('Dados do funcionario: ', result)
        self.next_perfil_employee(result)

    def email_exists(self, req, result):
        print('Erro: ', result)
        if result['error']['message'] in 'INVALID_LOGIN_CREDENTIALS':
            self.show_error('As informações inseridas estão incorretas')
        else:
            self.ids.email.error = True
            self.ids.email.text = ''
            self.show_error('Usuario inexistente')

    def senhas_employee(self, req, result):
        """
        Processa os dados dos funcionários e verifica as credenciais.

        Args:
            req: O objeto de requisição
            result: Os dados retornados pelo Firebase
        """
        try:
            if not result:
                self.show_error("Não foi possível carregar os dados de funcionários")
                return

            senha = self.ids.senha.text
            senha_bytes = senha.encode('utf-8')
            usuario_encontrado = False

            for cargo, nome in result.items():
                if nome['Name'] == self.ids.nome.text:
                    usuario_encontrado = True
                    self.ids.nome_errado.text = ''
                    self.ids.nome.error = False

                    try:
                        senha_correta = nome['password'].encode('utf-8')
                        if bcrypt.checkpw(senha_bytes, senha_correta):
                            self.ids.senha.error = False
                            self.ids.senha_errada.text = ''
                            self.key = cargo
                            self.show_message("Login realizado com sucesso!")

                            # Carrega o perfil do funcionário
                            UrlRequest(
                                url=f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{cargo}/.json',
                                on_success=self.next_perfil_employee,
                                on_error=self.on_request_error,
                                on_failure=self.on_request_failure,
                                timeout=10
                            )
                        else:
                            self.ids.senha.error = True
                            self.ids.senha_errada.text = 'A senha inserida está incorreta'
                    except Exception as e:
                        self.show_error(f"Erro na verificação da senha: {e}")
                    break

            if not usuario_encontrado:
                self.ids.nome_errado.text = 'Usuário não cadastrado'
                self.ids.nome.error = True
        except Exception as e:
            self.show_error(f"Erro ao processar dados: {e}")

    def next_perfil_employee(self, result):
        """
        Prepara a tela de perfil do funcionário após login bem-sucedido.

        Args:
            instance: O objeto de requisição
            result: Os dados do perfil do funcionário
        """
        try:
            if not result:
                self.show_error("Não foi possível carregar, tente como contratante")
                return

            app = MDApp.get_running_app()
            screenmanager = app.root
            perfil = screenmanager.get_screen('PrincipalScreenEmployee')

            # Atribui os dados do funcionário à tela de perfil
            perfil.employee_name = result.get('Name', '')
            perfil.contractor = result.get('contractor', '')
            perfil.employee_function = result.get('function', '')
            perfil.employee_mail = result.get('email', '')
            perfil.request = ast.literal_eval(result.get('request', '[]'))
            perfil.employee_telephone = result.get('telefone', '')
            perfil.avatar = result.get('avatar', '')
            perfil.city = result.get('city', '')
            perfil.salary = result['salary']
            perfil.data_contractor = result['data_contractor']
            perfil.state = result.get('state', '')
            perfil.employee_summary = result.get('sumary', '')
            perfil.skills = result.get('skills', '[]')
            perfil.key = self.key

            # Navega para a tela principal do funcionário
            screenmanager.transition = SlideTransition(direction='right')
            screenmanager.current = 'PrincipalScreenEmployee'
        except Exception as e:
            print(e)
            self.show_error(f"Erro ao carregar perfil: {e}")

    def verificar_senha(self):
        """
        Verifica as credenciais de login para funcionários.
        """
        print('Verificar funcioanario')
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

        def erro(req, erro_result):
            self.show_error(f"Usuario não encontrado tente como Funcionário")

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        UrlRequest(
            url,
            req_body=json.dumps(payload),
            req_headers=headers,
            method='POST',
            on_success=self.contractors,
            on_error=erro,
            on_failure=erro,
            on_cancel=erro
        )

    def contractors(self, req, result):
        print('Login feito, puxando os dados do funcionário...')
        print(result)
        refresh = result['refreshToken']
        id_token = result['idToken']
        id_local = result['localId']
        print('Refresh token: ', refresh)

        def sucesso(req, data):
            print("Dados encontrados:", data)
            self.data_found(req, data)

        def erro(req, erro_result):
            self.show_error(f"Usuario não encontrado tente como contratante")

        UrlRequest(
            f'https://obra-7ebd9-default-rtdb.firebaseio.com/Users/{id_local}.json?auth={id_token}',
            method='GET',
            on_success=lambda req, result, token_id=id_token, local_id=id_local, refresh_token=refresh: self.date(req, result, token_id, local_id,refresh_token),
            on_error=erro,
            on_failure=erro,
            on_cancel=erro,
            req_headers={"Content-Type": "application/json"}
        )

    def date(self, req, result, token_id, local_id, refresh_token):
        print('Os resultados são: ', result)
        self.next_perfil(result, token_id, local_id, refresh_token)

    def next_perfil(self, result, token_id, local_id, refresh_token):
        """
        Prepara a tela de perfil do contratante após login bem-sucedido.

        Args:
            instance: O objeto de requisição
            result: Os dados do perfil do contratante
        """
        try:
            if not result:
                self.show_error("Conexão indisponivel, tente como funcionário")
                return

            app = MDApp.get_running_app()
            screen_manager = app.root
            perfil = screen_manager.get_screen('Perfil')

            # Atribui os dados do contratante à tela de perfil
            perfil.function = result.get('function', '')
            perfil.username = result.get('name', '')
            perfil.avatar = result.get('perfil', '')
            perfil.telefone = result.get('telefone', '')
            perfil.state = result.get('state', '')
            perfil.city = result.get('city', '')
            perfil.company = result.get('company', '')
            perfil.email = result.get('email', '')
            perfil.local_id = local_id
            perfil.token_id = token_id
            perfil.refresh_token = refresh_token
            perfil.key = self.key

            self.type = result.get('type', '')
            self.login_variables()
        except Exception as e:
            self.show_error(f"Erro ao carregar perfil: {e}")

    def login_variables(self):
        """
        Redireciona para a tela apropriada após o login.

        Verifica o tipo de usuário e navega para a tela correspondente.
        """
        if self.type in 'contractor':
            self.manager.current = 'Perfil'

    def page(self, instance):
        """
        Navega para a tela de perfil.

        Args:
            instance: O widget que iniciou a navegação
        """
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'Perfil'
