import ast
import json
from datetime import datetime

from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText


class RequestAccept(MDScreen):
    """
    Tela para gerenciar aceitação ou recusa de solicitações de contratação.

    Esta classe permite que um contratante adicione um funcionário à sua equipe
    ou dispense o funcionário, removendo-o da lista de solicitações pendentes.
    Gerencia toda a comunicação com o banco de dados Firebase para manter
    os registros atualizados.

    Attributes:
        key_contractor (StringProperty): Chave única do contratante no banco de dados.
        username (StringProperty): Nome de usuário do contratante.
        company (StringProperty): Nome da empresa do contratante.
        city (StringProperty): Cidade do contratante ou funcionário.
        state (StringProperty): Estado do contratante ou funcionário.
        function (StringProperty): Função/cargo atual ou desejada.
        avatar (StringProperty): Caminho para a imagem de avatar.
        email (StringProperty): Email de contato.
        telefone (StringProperty): Número de telefone de contato.
        contractor (StringProperty): Nome do contratante atual (se houver).
        required_function (StringProperty): Função requerida para a vaga.
        key (StringProperty): Chave única do funcionário no banco de dados.
    """
    # Propriedades que serão compartilhadas entre telas ou com o backend
    key_contractor = StringProperty()
    username = StringProperty()
    company = StringProperty()
    city = StringProperty()
    state = StringProperty()
    function = StringProperty()
    avatar = StringProperty()
    email = StringProperty()
    telefone = StringProperty()
    data_contractor = StringProperty()
    contractor = StringProperty()
    required_function = StringProperty()
    key = StringProperty()

    def _show_snackbar(self, text, bg_color='green'):
        """
        Exibe uma mensagem temporária na parte inferior da tela.

        Args:
            text (str): Texto a ser exibido na mensagem.
            bg_color (str, optional): Cor de fundo da mensagem. Padrão é 'green'.
        """
        MDSnackbar(
            MDSnackbarText(
                text=text,
                theme_text_color='Custom',
                text_color='white',
                bold=True
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            halign='center',
            size_hint_x=0.9,
            theme_bg_color='Custom',
            background_color=bg_color
        ).open()

    def hire_employee(self):
        """
        Adiciona o funcionário à equipe do contratante na base de dados Firebase.

        Define os parâmetros iniciais do contrato como salário, escala e mês de contratação.
        Atualiza o status do funcionário para indicar que agora está vinculado a um contratante.
        """
        try:
            url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.key}/.json'
            month = datetime.today().month
            # Obtém a data atual
            data_atual = datetime.now()

            # Formata no padrão brasileiro
            data_formatada = data_atual.strftime('%d/%m/%Y')
            data = {
                'contractor': self.username,
                'function': self.function,
                'method_salary': 'Mensal',
                'salary': '1500',
                'receiveds': "[]",
                'request': 'False',
                'scale': '5x2',
                'contractor_month': month,
                'data_contractor': f"{data_formatada}"
            }

            self.data_contractor = data_formatada
            self.contractor = self.username

            self._show_snackbar("Adicionando funcionário à equipe...", "blue")

            UrlRequest(
                url,
                req_body=json.dumps(data),
                method='PATCH',
                on_success=self.process_after_hiring,
                on_error=self.on_error,
                on_failure=self.on_failure,
                timeout=10
            )
        except Exception as e:
            print(f"Erro ao recrutar funcionário: {str(e)}")
            self._show_snackbar(f"Erro ao recrutar: {str(e)}", "red")

    def on_error(self, request, error):
        """
        Callback para tratamento de erros de requisição.

        Args:
            request: Objeto de requisição que gerou o erro.
            error: Informações sobre o erro ocorrido.
        """
        print(f"Erro na requisição: {error}")
        self._show_snackbar(f"Erro na operação: {error}", "red")

    def on_failure(self, request, result):
        """
        Callback para tratamento de falhas de conexão.

        Args:
            request: Objeto de requisição que falhou.
            result: Informações sobre a falha.
        """
        self._show_snackbar("Falha na conexão. Verifique sua internet.", "red")

    def process_after_hiring(self, req, result):
        """
        Após o recrutamento, redireciona para a tela 'RequestsVacancy' e inicia a exclusão da requisição.

        Args:
            req: Objeto da requisição HTTP.
            result: Dados retornados pela requisição.
        """
        try:
            app = MDApp.get_running_app()
            screenmanager = app.root
            request = screenmanager.get_screen('RequestsVacancy')

            # Transfere os dados necessários para a próxima tela
            request.key = self.key
            if 'contractor' in result:
                request.contractor = result['contractor']
            else:
                request.contractor = self.username

            # Busca todas as requisições para localizar a que deve ser excluída
            url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/requets/.json'

            self._show_snackbar("Finalizando processo de contratação...", "blue")

            UrlRequest(
                url,
                on_success=self.remove_hiring_request,
                on_error=self.on_error,
                on_failure=self.on_failure,
                timeout=10
            )

            # Navega para a tela de requisições
            screenmanager.transition = SlideTransition(direction='left')
            screenmanager.current = 'RequestsVacancy'
        except Exception as e:
            print(f"Erro ao processar recrutamento: {str(e)}")
            self._show_snackbar(f"Erro no processo: {str(e)}", "red")

    def remove_hiring_request(self, req, result):
        """
        Procura e deleta a requisição associada ao funcionário do banco de dados.

        Esta função identifica a requisição específica do funcionário contratado
        e a remove do banco de dados, já que ela não é mais necessária.

        Args:
            req: Objeto da requisição HTTP.
            result: Dicionário contendo todas as requisições do banco de dados.
        """
        try:
            print('Resultado: ', result)
            if not result:
                print("Nenhuma requisição encontrada")
                self._show_snackbar("Processo finalizado!", "green")
                return

            for key, item in result.items():
                if item.get('key') == self.key:
                    print(f"Requisição encontrada: {key}")

                    # Deleta a requisição associada ao funcionário
                    UrlRequest(
                        f'https://obra-7ebd9-default-rtdb.firebaseio.com/requets/{key}/.json',
                        method='DELETE',
                        on_success=self.handle_successful_deletion,
                        on_error=self.on_error,
                        on_failure=self.on_failure,
                        timeout=10
                    )
                    return

            # Se não encontrou a requisição
            print("Requisição do funcionário não encontrada")
            self._show_snackbar("Funcionário contratado com sucesso", "green")
        except Exception as e:
            print(f"Erro ao finalizar exclusão: {str(e)}")
            self._show_snackbar(f"Erro ao finalizar: {str(e)}", "red")

    def handle_successful_deletion(self, req, result):
        """
        Callback de sucesso para a exclusão da requisição.

        Confirma que o processo de contratação foi finalizado com sucesso.

        Args:
            req: Objeto da requisição HTTP.
            result: Resultado da exclusão (geralmente vazio para DELETE).
        """
        print("Exclusão concluída com sucesso")
        self._show_snackbar("Funcionário contratado com sucesso!", "green")
        self._navigate_back_two()

    def reject_candidate(self):
        """
        Desvincula o funcionário do contratante atual sem aceitá-lo na equipe.

        Inicia o processo de recusa da solicitação de contratação,
        mantendo o funcionário disponível para outros contratantes.
        """
        try:
            url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.key}/.json'

            self._show_snackbar("Processando recusa...", "blue")

            UrlRequest(
                url,
                on_success=self.update_employee_data_after_rejection,
                on_error=self.on_error,
                on_failure=self.on_failure,
                timeout=10
            )
        except Exception as e:
            print(f"Erro ao dispensar funcionário: {str(e)}")
            self._show_snackbar(f"Erro ao recusar: {str(e)}", "red")

    def update_employee_data_after_rejection(self, req, result):
        """
        Após obter os dados do funcionário, remove o contratante da lista de recebidos.

        Args:
            req: Objeto da requisição HTTP.
            result: Dados do funcionário retornados pela requisição.
        """
        try:
            print('Dados do funcionário: ', result)

            # Se não há dados ou campo 'receiveds' não existe
            if not result or 'receiveds' not in result:
                print("Dados do funcionário inválidos ou incompletos")
                self._show_snackbar("Erro: dados do funcionário não encontrados", "red")
                return

            # Converte a string de lista para lista Python
            try:
                rk = ast.literal_eval(result['receiveds'])

                # Remove o contratante da lista
                if self.key_contractor in rk:
                    rk.remove(self.key_contractor)

                data = {
                    'contractor': '',
                    'receiveds': f"{rk}"
                }

                # Atualiza os dados do funcionário
                UrlRequest(
                    f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.key}/.json',
                    req_body=json.dumps(data),
                    method='PATCH',
                    on_success=self.fetch_requests_after_rejection,
                    on_error=self.on_error,
                    on_failure=self.on_failure,
                    timeout=10
                )
            except (SyntaxError, ValueError) as e:
                print(f"Erro ao processar lista 'receiveds': {str(e)}")
                self._show_snackbar("Erro ao processar dados", "red")
        except Exception as e:
            print(f"Erro ao processar próxima etapa: {str(e)}")
            self._show_snackbar(f"Erro no processamento: {str(e)}", "red")

    def fetch_requests_after_rejection(self, req, result):
        """
        Após atualizar os dados do funcionário, busca as requisições para ajustar a lista de recusa.

        Args:
            req: Objeto da requisição HTTP.
            result: Resultado da atualização (geralmente os dados atualizados).
        """
        try:
            UrlRequest(
                f'https://obra-7ebd9-default-rtdb.firebaseio.com/requets/.json',
                on_success=self.process_candidate_rejection,
                on_error=self.on_error,
                on_failure=self.on_failure,
                timeout=10
            )
        except Exception as e:
            print(f"Erro ao buscar requisições: {str(e)}")
            self._show_snackbar(f"Erro ao finalizar recusa: {str(e)}", "red")

    def process_candidate_rejection(self, req, result):
        """
        Marca a requisição como recusada e remove o contratante da lista de solicitações pendentes.

        Args:
            req: Objeto da requisição HTTP.
            result: Dicionário contendo todas as requisições do banco de dados.
        """
        try:
            print('Verificando requisições')

            if not result:
                print("Nenhuma requisição encontrada")
                self._show_snackbar("Funcionário dispensado", "green")
                self._navigate_back()
                return

            for key, item in result.items():
                if item.get('key') == self.key:
                    print('Achei a requisição do funcionário')

                    try:
                        # Adiciona o contratante à lista de recusas
                        data = ast.literal_eval(item.get('declines', '[]'))
                        if self.key_contractor not in data:
                            data.append(self.key_contractor)

                        # Remove o contratante da lista de solicitações
                        request = ast.literal_eval(item.get('requests', '[]'))
                        if self.key_contractor in request:
                            request.remove(self.key_contractor)

                        date = {
                            'declines': f"{data}",
                            'requests': f"{request}"
                        }

                        # Atualiza a requisição
                        UrlRequest(
                            f'https://obra-7ebd9-default-rtdb.firebaseio.com/requets/{key}/.json',
                            method='PATCH',
                            req_body=json.dumps(date),
                            on_success=self.handle_successful_rejection,
                            on_error=self.on_error,
                            on_failure=self.on_failure,
                            timeout=10
                        )
                        return
                    except (SyntaxError, ValueError) as e:
                        print(f"Erro ao processar listas da requisição: {str(e)}")
                        self._show_snackbar("Erro ao processar dados da requisição", "red")
                        self._navigate_back()
                        return

            # Se não encontrou a requisição
            print("Requisição do funcionário não encontrada")
            self._show_snackbar("Funcionário dispensado", "green")
            self._navigate_back()
        except Exception as e:
            print(f"Erro ao dispensar: {str(e)}")
            self._show_snackbar(f"Erro ao dispensar: {str(e)}", "red")
            self._navigate_back()

    def _navigate_back(self):
        """
        Método auxiliar para navegar de volta à tela de requisições.
        """
        app = MDApp.get_running_app()
        screenmanager = app.root
        request = screenmanager.get_screen('RequestsVacancy')
        request.key = self.key
        print('rs contractor: ',self.data_contractor)
        request.data_contractor = self.data_contractor
        request.contractor = ''
        screenmanager.transition = SlideTransition(direction='left')
        screenmanager.current = 'RequestsVacancy'

    def _navigate_back_two(self):
        """
        Método auxiliar para navegar de volta à tela de requisições.
        """
        app = MDApp.get_running_app()
        screenmanager = app.root
        request = screenmanager.get_screen('RequestsVacancy')
        request.key = self.key
        print('rs contractor: ',self.data_contractor)
        print('Nome do contratante: ', self.contractor)
        request.data_contractor = self.data_contractor
        request.contractor = self.contractor
        screenmanager.transition = SlideTransition(direction='left')
        screenmanager.current = 'RequestsVacancy'

    def handle_successful_rejection(self, req, result):
        """
        Conclui a dispensa do funcionário com sucesso, redirecionando de volta para a tela de requisições.

        Args:
            req: Objeto da requisição HTTP.
            result: Resultado da atualização (geralmente os dados atualizados).
        """
        print('Finalizado com sucesso')
        self._show_snackbar("Funcionário dispensado com sucesso", "green")
        self._navigate_back()
