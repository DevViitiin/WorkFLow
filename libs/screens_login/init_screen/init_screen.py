import ast
import json
from functools import partial
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
    logo = "https://res.cloudinary.com/dh7ixbnzc/image/upload/v1757715627/ChatGPT_Image_12_de_set._de_2025_19_20_23_f5n3ij.png"
    carregado = False
    api1 = "AIzaSyA3vFR2WgCdB"
    api2 = "syIIL1k9teQNZTi4ZAzhtg"
    api_key = (api1 + api2 + 's')[:-1]
    key = StringProperty()
    name = False
    senha = ''
    type = ''

    def on_enter(self, *args):
        """Método chamado quando a tela é exibida."""
        self.ids.image.source = self.logo
        self.state_employee()


    """
    Solução principal para o problema de transição em mobile:
    1. Método de animação para evitar o "flash branco"
    2. Implementação de cache para componentes visuais 
    3. Correção de propriedades incorretas no KV
    """

    # ----- PARTE PYTHON -----

    def send_password_verification(self, *args):
        if not self.ids.email.text:
            self.show_error('Por favor preencha o email que será usado')
            Clock.schedule_once(lambda dt: self.show_error('Para enviar a troca de senha'), 1.5)
            return
        
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={self.api_key}"
        payload = {
            "requestType": "PASSWORD_RESET",
            "email": self.ids.email.text
        }

        headers = {
            "Content-Type": "application/json",
            "X-Firebase-Locale": "pt-BR"   # força idioma português
        }

        def success(req, result):
            self.show_success("E-mail de redefinição enviado em português!")

        def error(req, error):
            self.show_error(f"Erro: {error}")

        def failure(req, result):
            self.show_error(f"Falha: {result}")

        UrlRequest(
            url,
            req_body=json.dumps(payload),
            req_headers=headers,
            on_success=success,
            on_error=error,
            on_failure=failure
        )

        headers = {"Content-Type": "application/json"}

        def sucesso(req, resultado):
            print("Email de redefinição enviado:", resultado)
            self.show_message('Solicitação enviada com sucesso', "#00ff15")
            Clock.schedule_once(lambda dt: self.show_message('Verifique seu email', "#00ff15"), 1.5)
            # aqui você pode mostrar um Snackbar ou Popup avisando o usuário

        def erro(req, erro):
            print("Erro na requisição:", erro)

        def falha(req, resultado):
            print("Falha ao enviar:", resultado)

        UrlRequest(
            url,
            req_body=json.dumps(payload),
            req_headers=headers,
            on_success=sucesso,
            on_error=erro,
            on_failure=falha
        )

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
        refresh = result['refreshToken']

        def sucesso(req, data):
            print("Dados encontrados:", data)
            self.data_found(req, data)

        def erro(req, erro_result):
            self.show_error(f"Usuario não encontrado tente como contratante")

        UrlRequest(
            f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{id_local}.json?auth={id_token}',
            method='GET',
            on_success=partial(self.next_perfil_employee, token_id=id_token, local_id=id_local, refresh_token=refresh),
            on_error=erro,
            on_failure=erro,
            on_cancel=erro,
            req_headers={"Content-Type": "application/json"}
        )
        
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
            on_success=self.employees,
            on_error=erro,
            on_failure=erro,
            on_cancel=erro
        )

    def employees(self, req, result):
        print('Login feito, puxando os dados do funcionário...')
        print(result)
        refresh = result['refreshToken']
        id_token = result['idToken']
        id_local = result['localId']
        print('Refresh token: ', refresh)

        def sucesso(req, data):
            print("Dados encontrados:", data)
            self.next_perfil_employee(result, self.id_token, self.local_id, self.refresh_token)

        def erro(req, erro_result):
            self.show_error(f"Usuario não encontrado tente como contratante")

        UrlRequest(
            f'https://obra-7ebd9-default-rtdb.firebaseio.com/Users/{id_local}.json?auth={id_token}',
            method='GET',
            on_success=partial(self.next_perfil_employee, token_id=id_token, local_id=id_local, refresh_token=refresh),
            on_error=erro,
            on_failure=erro,
            on_cancel=erro,
            req_headers={"Content-Type": "application/json"}
        )

    def next_perfil_employee(self, req, result, token_id, local_id, refresh_token):
        """
        Prepara a tela de perfil do funcionário após login bem-sucedido.

        Args:
            instance: O objeto de requisição
            result: Os dados do perfil do funcionário
        """
        print('Consegui o token id eu sou o cara: ', local_id)
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
            perfil.api_key = self.api_key
            perfil.salary = result['salary']
            perfil.data_contractor = result['data_contractor']
            perfil.state = result.get('state', '')
            perfil.employee_summary = result.get('sumary', '')
            perfil.skills = result.get('skills', '[]')
            perfil.key = self.key
            perfil.refresh_token = refresh_token
            perfil.token_id = token_id
            perfil.local_id = local_id
            

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
        print('rsrs:   ',result)
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
            perfil.api_key = self.api_key

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
