import ast
import json
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty, get_color_from_hex, BooleanProperty
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButtonText, MDButton
from kivymd.uix.fitimage import FitImage
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText


class RequestsVacancy(MDScreen):
    """
    Screen to manage vacancy requests sent by contractors and received by employees.
    Provides functionality to view, accept, and manage vacancy requests.
    """
    current_nav_state = StringProperty('notification')
    avatar = StringProperty()
    employee_name = StringProperty()
    employee_function = StringProperty()
    city = StringProperty()
    state = StringProperty()
    contractor = StringProperty()
    employee_mail = StringProperty()
    employee_telephone = StringProperty()
    data_contractor = StringProperty()
    key = StringProperty()
    employee_summary = StringProperty()
    skills = StringProperty()
    tab_nav_state = StringProperty()
    request = BooleanProperty()
    click = 0
    _request_count = 0  # Count of loaded requests to track empty states

    def on_enter(self, *args):
        print('Nome do contratante recebido: ', self.contractor)
        """
        Called when the screen is entered.
        Loads the appropriate data based on the current tab state.
        """
        print('Entered RequestsVacancy with key:', self.key)
        self.ids.main_scroll.clear_widgets()
        self._request_count = 0  # Reset request counter on new screen entry

        if self.tab_nav_state == 'received':
            self.receiveds()
        else:
            self.upload_requests()

    def workflow(self, screen):
        """
        Handles tab navigation and updates content based on selected tab.

        Args:
            screen (str): The tab to navigate to ('received', 'decline', or 'request')
        """
        self.click += 1

        # Prevent reloading widgets if already on the correct tab
        if screen == self.tab_nav_state:
            return

        # Update current tab state
        self.tab_nav_state = screen
        self.ids.main_scroll.clear_widgets()
        self._request_count = 0  # Reset request counter on tab change

        # Call the appropriate function based on the tab
        if screen == 'received':
            self.receiveds()
        elif screen in ['decline', 'request']:
            self.upload_requests()

        # Reset click counter
        self.click = 0

    def receiveds(self):
        """
        Loads and displays received requests from Firebase.
        Shows a message if no requests are found.
        """
        self.ids.main_scroll.clear_widgets()
        self._request_count = 0  # Reset request counter
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.key}/.json'

        # Display loading message while fetching
        loading_label = MDLabel(
            text='\nCarregando solicitações...',
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint_x=0.8,
            halign='center',
            theme_text_color='Custom',
            text_color='grey'
        )
        self.ids.main_scroll.add_widget(loading_label)

        UrlRequest(
            url,
            method='GET',
            on_success=self.add_received,
            on_error=self.handle_request_error,
            on_failure=self.handle_request_error
        )

    def handle_request_error(self, request, error):
        """
        Handles errors when fetching data from Firebase.

        Args:
            request: The request object
            error: The error object
        """
        self.ids.main_scroll.clear_widgets()
        error_label = MDLabel(
            text='\nErro ao carregar dados. Tente novamente.',
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint_x=0.8,
            halign='center',
            theme_text_color='Custom',
            text_color='red'
        )
        self.ids.main_scroll.add_widget(error_label)

        # Show error in snackbar
        snackbar = MDSnackbar(
            MDSnackbarText(
                text="Falha ao carregar dados"
            ),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.8,
        )
        snackbar.open()
        print(f"Error fetching data: {error}")

    def add_received(self, instance, req):
        """
        Processes received requests data and adds contractor profiles to the UI.
        Shows a message if no requests are found.
        """
        self.ids.main_scroll.clear_widgets()
        self._request_count = 0

        try:
            if not req:
                self._show_no_requests_message("Nenhum dado encontrado")
                return

            receiveds_value = req.get('receiveds', '[]')

            if receiveds_value is None:
                receiveds_value = '[]'

            try:
                if isinstance(receiveds_value, str):
                    receiveds_value = receiveds_value.strip()
                    if not receiveds_value or receiveds_value == '[]':
                        self._show_no_requests_message("Nenhuma solicitação")
                        return
                    received = ast.literal_eval(receiveds_value)
                else:
                    received = receiveds_value

                if not isinstance(received, list):
                    self._show_no_requests_message("Formato de dados inválido")
                    return

                if not received:
                    self._show_no_requests_message("Nenhuma solicitação")
                    return

                print('Received contractors list:', received)
                requests_initiated = False

                for contractor in received:
                    if not contractor or not isinstance(contractor, str) or contractor.strip() == "":
                        continue

                    requests_initiated = True
                    self._request_count += 1

                    contractor_url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Users/{contractor}/.json'

                    def process_contractor(req, result, key_contractor=contractor):
                        if not result or not isinstance(result, dict):
                            print(f'Contratante inválido ou inexistente: {key_contractor}')
                            return

                        # Verifique se há dados relevantes para exibição
                        if not result.get('name') and not result.get('avatar'):
                            print(f'Dados incompletos do contratante {key_contractor}')
                            return

                        # Dados válidos, agora adiciona o widget na tela
                        self.cont(req, result, key_contractor)

                    UrlRequest(
                        contractor_url,
                        on_success=process_contractor,
                        on_error=lambda req, error, key=contractor: self.handle_contractor_error(req, error, key),
                        on_failure=lambda req, error, key=contractor: self.handle_contractor_error(req, error, key)
                    )

                if not requests_initiated:
                    self._show_no_requests_message("Nenhuma solicitação válida")

            except (ValueError, SyntaxError) as e:
                print(f"Erro ao analisar receiveds: {e}")
                self._show_no_requests_message("Erro no formato dos dados")
                return

        except Exception as e:
            print(f'Erro no processamento de solicitações recebidas: {e}')
            self._show_no_requests_message(f"Erro: {str(e)}")

    def _show_no_requests_message(self, text='nada'):
        """Helper method to display a message when no requests are found."""
        if not self.ids.main_scroll.children:
            label = MDLabel(
                text='\nNenhuma solicitação',
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                size_hint_x=0.8,
                halign='center',
                theme_text_color='Custom',
                text_color='grey'
            )
            self.ids.main_scroll.add_widget(label)

    def cont(self, instance, result, key_contractor):
        """
        Creates and adds a contractor profile card to the scroll view.

        Args:
            instance: The request instance
            result (dict): The contractor data
            key_contractor (str): The contractor's key in Firebase
        """
        try:
            if not result:  # Check if result is empty or None
                self._request_count -= 1
                if self._request_count == 0:
                    self._show_no_requests_message()
                return

            print('Processing contractor:', key_contractor)

            # Create and add profile card
            card = self.create_profile_card(
                result.get('name', 'Nome não disponível'),
                result.get('function', 'Função não disponível'),
                5,  # Default rating
                result.get('perfil', ''),
                result.get('city', ''),
                result.get('company', ''),
                result.get('email', ''),
                result.get('telefone', ''),
                result.get('state', ''),
                key_contractor
            )
            self.ids.main_scroll.add_widget(card)

        except Exception as e:
            print(f'Error creating contractor card: {e}')
            self._request_count -= 1
            if self._request_count == 0:
                self._show_no_requests_message()

    def upload_requests(self):
        """
        Fetches and displays vacancy requests based on the current tab.
        Shows request/decline cards depending on tab_nav_state.
        """
        self.ids.main_scroll.clear_widgets()
        self._request_count = 0  # Reset request counter

        # Display loading message
        loading_label = MDLabel(
            text='\nCarregando solicitações...',
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint_x=0.8,
            halign='center',
            theme_text_color='Custom',
            text_color='grey'
        )
        self.ids.main_scroll.add_widget(loading_label)

        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Functions/.json'
        UrlRequest(
            url,
            method='GET',
            on_success=self.add_requests,
            on_error=self.handle_request_error,
            on_failure=self.handle_request_error
        )

    def create_profile_card(self, name, profession, rating, avata, city, company, email, telephone, state,
                            key_contractor):
        """
        Creates a profile card for a contractor.

        Args:
            name (str): Contractor's name
            profession (str): Contractor's profession
            rating (int): Rating from 0-5
            avata (str): Avatar image URL
            city (str): Contractor's city
            company (str): Contractor's company
            email (str): Contractor's email
            telephone (str): Contractor's telephone
            state (str): Contractor's state
            key_contractor (str): Contractor's Firebase key

        Returns:
            MDBoxLayout: The complete profile card widget
        """
        # Card principal com bordas arredondadas
        card_layout = MDBoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height="180dp",
            padding="15dp",
            radius=20,
            theme_line_color='Custom',
            line_color='grey',
            md_bg_color=(1, 1, 1, 1),
            pos_hint={'center_x': 0.5}
        )

        # Layout para informações e foto
        info_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=0.8,
            spacing="5dp",
            pos_hint={'center_y': 0.8}
        )
        card_layout.add_widget(info_layout)

        # Profile image section
        profile_box = MDBoxLayout(
            size_hint_x=0.5,
            padding="5dp"
        )
        info_layout.add_widget(profile_box)

        profile_image = MDRelativeLayout(
            size_hint=(1, 1)
        )

        # Handle avatar image - use default if not provided
        avatar_source = avata if avata else "path/to/default_avatar.png"

        avatar = FitImage(
            source=avatar_source,
            size_hint=(1, 0.95),
            radius=[100, ]
        )
        profile_image.add_widget(avatar)
        profile_box.add_widget(profile_image)

        # Information section
        text_layout = MDBoxLayout(
            orientation='vertical',
            size_hint_x=0.75,
            spacing="5dp",
            padding=["5dp", 0, 0, 0],
            pos_hint={'center_y': 0.6}
        )
        info_layout.add_widget(text_layout)

        # Name label
        name_label = MDLabel(
            text=name,
            font_style='Title',
            role='medium',
            bold=True,
            adaptive_height=True
        )
        text_layout.add_widget(name_label)

        # Profession label
        profession_label = MDLabel(
            text=profession,
            font_style='Title',
            role='medium',
            theme_text_color="Secondary",
            adaptive_height=True
        )
        text_layout.add_widget(profession_label)

        # Stars layout for rating
        stars_layout = MDBoxLayout(
            orientation='horizontal',
            adaptive_height=True,
            spacing="2dp"
        )
        text_layout.add_widget(stars_layout)

        # Add stars based on rating
        for i in range(5):
            star_icon = MDIcon(
                icon="star",
                theme_icon_color="Custom",
                icon_color=(1, 0.8, 0, 1) if i < rating else (0.7, 0.7, 0.7, 1)
            )
            stars_layout.add_widget(star_icon)

        # Button section
        button_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=0.3,
            padding=[0, "10dp", 0, 0],
            pos_hint={'right': 1}
        )
        card_layout.add_widget(button_layout)

        # Spacer to align button to right
        spacer = MDBoxLayout(
            size_hint_x=0.6
        )
        button_layout.add_widget(spacer)

        # "View profile" button
        profile_button = MDButton(
            MDButtonText(
                text="Ver perfil",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
            ),
            theme_bg_color='Custom',
            md_bg_color=(0.16, 0.44, 0.95, 1),
            size_hint_x=0.4,
            pos_hint={'center_y': 0.4}
        )

        # Set button callback with contractor data
        profile_button.on_release = lambda name_contractor=name, function=profession, perfil=avata, city_contractor=city, company_contractor=company, email_contractor=email, telephone_contractor=telephone, state_contractor=state,key=key_contractor: self.next_acept(name_contractor, function, perfil, city_contractor, company_contractor,
                                                                           email_contractor, telephone_contractor,
                                                                           state_contractor, key)

        button_layout.add_widget(profile_button)

        return card_layout

    def next_acept(self, name, function, perfil, city, company, email, telephone, state, key):
        """
        Handles navigation to the request acceptance screen.

        Args:
            name (str): Contractor's name
            function (str): Contractor's function/profession
            perfil (str): Profile image URL
            city (str): Contractor's city
            company (str): Contractor's company name
            email (str): Contractor's email
            telephone (str): Contractor's telephone
            state (str): Contractor's state
            key (str): Contractor's key in Firebase
        """
        print(f"Navigating to accept screen for: {name}, {function}, {city}")

        try:
            app = MDApp.get_running_app()
            screen = app.root
            accept = screen.get_screen('RequestAccept')

            # Pass contractor data to the accept screen
            accept.username = name
            accept.company = company
            accept.city = city
            accept.state = state
            accept.function = function
            accept.avatar = perfil
            accept.email = email
            accept.key_contractor = key
            accept.telefone = telephone
            accept.key = self.key
            accept.required_function = self.employee_function

            # Navigate to accept screen
            screen.transition = SlideTransition(direction='right')
            screen.current = 'RequestAccept'

        except Exception as e:
            print(f"Error navigating to accept screen: {e}")
            # Show error snackbar
            snackbar = MDSnackbar(
                MDSnackbarText(
                    text="Erro ao abrir tela de aceitação"
                ),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8,
            )
            snackbar.open()

    def add_requests(self, req, requests):
        """
        Processes and displays requests/decline data based on current tab.

        Args:
            req: The request instance
            requests (dict): The response data containing all function requests
        """
        self.ids.main_scroll.clear_widgets()  # Clear loading messages
        self._request_count = 0  # Reset request counter

        if not requests:  # Handle empty response
            self._show_no_requests_message()
            return

        try:
            # Process each request from Functions database
            for key, request in requests.items():
                if not request:  # Skip empty entries
                    continue

                try:
                    # Safely get and parse requests/decline lists
                    req_str = request.get('requests', '[]')
                    decline_str = request.get('decline', '[]')

                    # Parse strings to lists
                    reqs = ast.literal_eval(req_str) if isinstance(req_str, str) else req_str or []
                    decline = ast.literal_eval(decline_str) if isinstance(decline_str, str) else decline_str or []

                    # Add request cards based on current tab and if user is in the list
                    if self.key in reqs and self.tab_nav_state == 'request':
                        self._request_count += 1
                        self.requests(
                            request.get('occupation', 'Vaga não especificada'),
                            'yellow',
                            'clock-outline',
                            request.get('company', 'Empresa não especificada'),
                            request.get('Option Payment', 'Não especificado'),
                            request.get('Salary', '0'),
                            request.get('email', ''),
                            request.get('telephone', '')
                        )

                    elif self.key in decline and self.tab_nav_state == 'decline':
                        self._request_count += 1
                        self.requests(
                            request.get('occupation', 'Vaga não especificada'),
                            'red',
                            'cancel',
                            request.get('company', 'Empresa não especificada'),
                            request.get('Option Payment', 'Não especificado'),
                            request.get('Salary', '0'),
                            request.get('email', ''),
                            request.get('telephone', '')
                        )

                except Exception as e:
                    print(f"Error processing request {key}: {e}")
                    continue

            # If no matching requests were found, show empty message
            if self._request_count == 0:
                self._show_no_requests_message()

        except Exception as e:
            print(f"Error in add_requests: {e}")
            self._show_no_requests_message()

    def requests(self, function, color, icon, company, method, salary, email, telephone):
        """
        Creates and adds a request card to the scroll view.

        Args:
            function (str): Job function/title
            color (str): Card accent color
            icon (str): Card icon name
            company (str): Company name
            method (str): Payment method
            salary (str): Salary amount
            email (str): Contact email
            telephone (str): Contact telephone
        """
        # Create the card layout
        card_layout = MDBoxLayout(
            orientation='horizontal',
            theme_bg_color='Custom',
            md_bg_color=(1, 1, 1, 1),
            size_hint_y=None,
            size_hint_x=1,
            height='170dp',
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            padding="5dp",
            spacing="5dp"
        )

        # Color indicator on left side
        color_box = MDBoxLayout(
            size_hint_x=0.03,
            theme_bg_color='Custom',
            md_bg_color=f'{color}'
        )
        card_layout.add_widget(color_box)

        # Content layout
        content_layout = MDBoxLayout(
            orientation='vertical',
            size_hint_x=0.95,
            theme_bg_color='Custom',
            md_bg_color=(1, 1, 1, 1)
        )
        card_layout.add_widget(content_layout)

        # Title section
        title_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='30dp',
            theme_bg_color='Custom',
            md_bg_color=(1, 1, 1, 1)
        )
        content_layout.add_widget(title_layout)

        # Title box
        title_box = MDBoxLayout(
            size_hint_x=0.8,
            padding=[10, 0]
        )
        title_layout.add_widget(title_box)

        # Function/job title
        title_label = MDLabel(
            text=f'{function}',
            font_style='Title',
            role='medium',
            bold=True,
            pos_hint={'center_y': 0.5}
        )
        title_box.add_widget(title_label)

        # Status icon box
        icon_box = MDBoxLayout(
            size_hint_x=0.2,
            padding=[10, 0]
        )
        title_layout.add_widget(icon_box)

        # Status icon (clock or cancel)
        status_icon = MDIcon(
            icon=f'{icon}',
            theme_icon_color='Custom',
            icon_color=color,
            pos_hint={'center_y': 0.5}
        )
        icon_box.add_widget(status_icon)

        # Company section
        company_box = MDBoxLayout(
            size_hint_y=None,
            height='20dp',
            theme_bg_color='Custom',
            md_bg_color=(1, 1, 1, 1),
            padding=[10, 0]
        )
        content_layout.add_widget(company_box)

        # Company label
        company_label = MDLabel(
            text=f'{company}',
            theme_text_color='Custom',
            text_color='grey',
            font_style='Title',
            role='small',
            pos_hint={'center_y': 0.5}
        )
        company_box.add_widget(company_label)

        # Information section
        info_box = MDBoxLayout(
            orientation='vertical',
            padding=[10, 0],
            theme_bg_color='Custom',
            md_bg_color=(1, 1, 1, 1)
        )
        content_layout.add_widget(info_box)

        # Payment method section
        payment_box = MDBoxLayout(
            orientation='horizontal',
            theme_bg_color='Custom',
            spacing=5,
            md_bg_color=(1, 1, 1, 1)
        )
        info_box.add_widget(payment_box)

        # Payment icon
        payment_icon = MDIcon(
            icon='credit-card-outline',
            theme_icon_color='Custom',
            icon_color=(0.0, 1.0, 0.0, 1.0)
        )
        payment_box.add_widget(payment_icon)

        # Payment method label
        payment_label = MDLabel(
            text=f'Método de Pagamento: {method}',
            font_style='Label',
            role='medium'
        )
        payment_box.add_widget(payment_label)

        # Salary section
        salary_box = MDBoxLayout(
            orientation='horizontal',
            theme_bg_color='Custom',
            spacing=5,
            md_bg_color=(1, 1, 1, 1)
        )
        info_box.add_widget(salary_box)

        # Salary icon
        salary_icon = MDIcon(
            icon='credit-card-outline',
            theme_icon_color='Custom',
            icon_color='purple',
            pos_hint={'center_y': 0.5}
        )
        salary_box.add_widget(salary_icon)

        # Salary label
        salary_label = MDLabel(
            text=f'Salário: R${salary}',
            font_style='Label',
            role='medium'
        )
        salary_box.add_widget(salary_label)

        # Email section
        email_box = MDBoxLayout(
            orientation='horizontal',
            theme_bg_color='Custom',
            spacing=5,
            md_bg_color=(1, 1, 1, 1)
        )
        info_box.add_widget(email_box)

        # Email icon
        email_icon = MDIcon(
            icon='email',
            theme_icon_color='Custom',
            icon_color=get_color_from_hex('#5BC0EB'),
            pos_hint={'center_y': 0.5}
        )
        email_box.add_widget(email_icon)

        # Email label
        email_label = MDLabel(
            text=f'Email: {email}',
            font_style='Label',
            role='medium'
        )
        email_box.add_widget(email_label)

        # Phone section
        phone_box = MDBoxLayout(
            orientation='horizontal',
            theme_bg_color='Custom',
            spacing=5,
            md_bg_color=(1, 1, 1, 1)
        )
        info_box.add_widget(phone_box)

        # Phone icon
        phone_icon = MDIcon(
            icon='phone',
            theme_icon_color='Custom',
            icon_color=get_color_from_hex('#FF01FB'),
            pos_hint={'center_y': 0.5}
        )
        phone_box.add_widget(phone_icon)

        # Phone label
        phone_label = MDLabel(
            text=f'Telefone: {telephone}',
            font_style='Label',
            role='medium'
        )
        phone_box.add_widget(phone_label)

        # Add the complete card to the scroll view
        self.ids.main_scroll.add_widget(card_layout)

    def vacancy(self):
        """
        Navigates to the vacancy screen and updates navigation state.
        Transfers user data to the target screen.
        """

        try:
            app = MDApp.get_running_app()
            screenmanager = app.root

            # Get vacancy screen and transfer user data
            vac = screenmanager.get_screen('VacancyBank')
            vac.key = self.key
            vac.employee_name = self.employee_name
            vac.employee_function = self.employee_function
            vac.employee_mail = self.employee_mail
            vac.employee_telephone = self.employee_telephone
            vac.avatar = self.avatar
            vac.employee_summary = self.employee_summary
            vac.skills = self.skills
            vac.city = self.city
            vac.data_contractor = self.data_contractor
            vac.state = self.state
            vac.request = self.request
            vac.contractor = self.contractor

            # Update navigation state
            self.current_nav_state = 'vacancy'

            # Update active navigation icons
            vac.ids.vacancy.active = True
            vac.ids.perfil.active = False
            vac.ids.payment.active = False
            vac.ids.notification.active = False

            # Navigate to vacancy screen
            screenmanager.transition = SlideTransition(direction='right')
            screenmanager.current = 'VacancyBank'

        except Exception as e:
            print(f"Error navigating to vacancy screen: {e}")
            # Show error snackbar
            snackbar = MDSnackbar(
                MDSnackbarText(
                    text="Erro ao navegar para banco de vagas"
                ),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8,
            )
            snackbar.open()

    def perfil(self):
        """
        Navigates to the profile screen and updates navigation state.
        Transfers user data to the target screen.
        """
        try:
            app = MDApp.get_running_app()
            screenmanager = app.root

            # Get profile screen and transfer user data
            perfil = screenmanager.get_screen('PrincipalScreenEmployee')
            perfil.key = self.key
            perfil.employee_name = self.employee_name
            perfil.employee_function = self.employee_function
            perfil.employee_mail = self.employee_mail
            perfil.employee_telephone = self.employee_telephone
            perfil.avatar = self.avatar
            perfil.employee_summary = self.employee_summary
            perfil.skills = self.skills
            perfil.request = self.request
            perfil.state = self.state
            perfil.data_contractor = self.data_contractor
            perfil.city = self.city

            perfil.contractor = self.contractor

            # Update navigation state
            perfil.current_nav_state = 'vacancy'
            perfil.ids.notification.active = False
            perfil.ids.vacancy.active = False
            perfil.ids.payment.active = False
            perfil.ids.perfil.active = True

            # Navigate to profile screen
            screenmanager.transition = SlideTransition(direction='right')
            screenmanager.current = 'PrincipalScreenEmployee'

        except Exception as e:
            print(f"Error navigating to profile screen: {e}")
            # Show error snackbar
            snackbar = MDSnackbar(
                MDSnackbarText(
                    text="Erro ao navegar para perfil"
                ),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8,
            )
            snackbar.open()

    def req(self):
        """
        Handles navigation to payment/request screens based on user state.
        Different screens are shown depending on contractor status and request status.
        """
        print('O nome do contratante está aqui', self.contractor)
        try:
            app = MDApp.get_running_app()
            screen = app.root

            if not self.contractor:
                # User has no contractor associated
                if not self.request:
                    # User has not sent a request yet
                    without = screen.get_screen('WithoutContractor')
                    # Transfer user data
                    without.key = self.key
                    without.tab_nav_state = 'request'
                    without.employee_name = self.employee_name
                    without.employee_function = self.employee_function
                    without.employee_mail = self.employee_mail
                    without.employee_telephone = self.employee_telephone
                    without.ids.vacancy.active = False
                    without.city = self.city
                    without.state = self.state
                    without.data_contractor = self.data_contractor
                    without.ids.perfil.active = False
                    without.ids.payment.active = True
                    without.ids.notification.active = False
                    without.avatar = self.avatar
                    without.employee_summary = self.employee_summary
                    without.skills = self.skills
                    without.request = self.request
                    without.contractor = self.contractor

                    # Navigate to the WithoutContractor screen
                    screen.transition = SlideTransition(direction='left')
                    screen.current = 'WithoutContractor'
                else:
                    # User has already sent a request
                    request_sent = screen.get_screen('RequestSent')
                    # Transfer user data
                    request_sent.key = self.key
                    request_sent.tab_nav_state = 'request'
                    request_sent.employee_name = self.employee_name
                    request_sent.employee_function = self.employee_function
                    request_sent.employee_mail = self.employee_mail
                    request_sent.employee_telephone = self.employee_telephone
                    request_sent.ids.vacancy.active = False
                    request_sent.city = self.city
                    request_sent.state = self.state
                    request_sent.ids.perfil.active = False
                    request_sent.ids.payment.active = True
                    request_sent.ids.notification.active = False
                    request_sent.request = self.request
                    request_sent.avatar = self.avatar
                    request_sent.data_contractor = self.data_contractor
                    request_sent.employee_summary = self.employee_summary
                    request_sent.contractor = self.contractor
                    request_sent.skills = self.skills

                    # Navigate to the RequestSent screen
                    screen.transition = SlideTransition(direction='left')
                    screen.current = 'RequestSent'
            else:
                # User has a contractor associated - show review screen
                review = screen.get_screen('ReviewScreen')
                # Transfer user data
                print('A data em que o mn ai foi contratado é : ', self.contractor)
                review.key = self.key
                review.employee_name = self.employee_name
                review.employee_function = self.employee_function
                review.employee_mail = self.employee_mail
                review.employee_telephone = self.employee_telephone
                review.contractor = self.contractor
                review.request = self.request
                review.avatar = self.avatar
                review.data_contractor = self.data_contractor
                review.employee_summary = self.employee_summary
                review.skills = self.skills
                review.ids.vacancy.active = False
                review.city = self.city
                review.state = self.state
                review.ids.perfil.active = False
                review.ids.payment.active = True
                review.ids.notification.active = False
                review.current_nav_state = 'payment'

                # Navigate to the ReviewScreen
                screen.transition = SlideTransition(direction='left')
                screen.current = 'ReviewScreen'

        except Exception as e:
            print(f"Error navigating from req(): {e}")
            # Show error snackbar
            snackbar = MDSnackbar(
                MDSnackbarText(
                    text="Erro ao navegar para a tela de pagamento"
                ),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8,
            )
            snackbar.open()

    def check_firebase_data(self, key, path, callback=None):
        """
        Utility method to check if data exists in Firebase.

        Args:
            key (str): The Firebase key to check
            path (str): Firebase path
            callback (function): Optional callback function to process result

        Returns:
            bool: True if successful, False otherwise
        """
        if not key:
            print("Error: No key provided to check_firebase_data")
            return False

        try:
            url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/{path}/{key}/.json'

            def on_success(req, result):
                if result:
                    print(f"Data found for {key} at {path}")
                    if callback:
                        callback(result)
                    return True
                else:
                    print(f"No data found for {key} at {path}")
                    return False

            def on_error(req, error):
                print(f"Error fetching data for {key} at {path}: {error}")
                return False

            UrlRequest(
                url,
                method='GET',
                on_success=on_success,
                on_error=on_error,
                on_failure=on_error
            )
            return True
        except Exception as e:
            print(f"Exception in check_firebase_data: {e}")
            return False


    def update_firebase_data(self, key, path, data, success_message=None):
        """
        Utility method to update Firebase data.

        Args:
            key (str): Firebase key
            path (str): Firebase path
            data (dict): Data to update
            success_message (str): Optional message to show on success

        Returns:
            bool: True if update initiated successfully
        """
        if not key or not data:
            print("Error: Missing key or data in update_firebase_data")
            return False

        try:
            url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/{path}/{key}/.json'

            def on_success(req, result):
                print(f"Data updated successfully for {key} at {path}")
                if success_message:
                    snackbar = MDSnackbar(
                        MDSnackbarText(text=success_message),
                        pos_hint={"center_x": 0.5},
                        size_hint_x=0.8,
                    )
                    snackbar.open()
                return True

            def on_error(req, error):
                print(f"Error updating data for {key} at {path}: {error}")
                snackbar = MDSnackbar(
                    MDSnackbarText(text="Erro ao atualizar dados"),
                    pos_hint={"center_x": 0.5},
                    size_hint_x=0.8,
                )
                snackbar.open()
                return False

            UrlRequest(
                url,
                method='PATCH',  # Use PATCH to update specific fields
                req_body=json.dumps(data),
                on_success=on_success,
                on_error=on_error,
                on_failure=on_error
            )
            return True
        except Exception as e:
            print(f"Exception in update_firebase_data: {e}")
            return False

    def safe_parse_list(self, data_str):
        """
        Safely parse a string representation of a list.

        Args:
            data_str: String representation of a list or list itself

        Returns:
            list: Parsed list or empty list if invalid
        """
        if not data_str:
            return []

        if isinstance(data_str, list):
            return data_str

        try:
            return ast.literal_eval(data_str)
        except (ValueError, SyntaxError) as e:
            print(f"Error parsing list: {e}")
            return []

    def show_loading(self, message="Carregando..."):
        """
        Shows a loading message in the scroll view.

        Args:
            message (str): The loading message to display
        """
        self.ids.main_scroll.clear_widgets()
        loading_label = MDLabel(
            text=f'\n{message}',
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint_x=0.8,
            halign='center',
            theme_text_color='Custom',
            text_color='grey'
        )
        self.ids.main_scroll.add_widget(loading_label)


    def show_message(self, message, text_color='grey'):
        """
        Shows a message in the scroll view.

        Args:
            message (str): The message to display
            text_color (str): Color of the message text
        """
        self.ids.main_scroll.clear_widgets()
        message_label = MDLabel(
            text=f'\n{message}',
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint_x=0.8,
            halign='center',
            theme_text_color='Custom',
            text_color=text_color
        )
        self.ids.main_scroll.add_widget(message_label)


    def show_snackbar(self, message):
        """
        Shows a snackbar message.

        Args:
            message (str): Message to display
        """
        snackbar = MDSnackbar(
            MDSnackbarText(text=message),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.8,
        )
        snackbar.open()

    def refresh_current_view(self):
        """
        Refreshes the current view based on tab state.
        """
        self.ids.main_scroll.clear_widgets()
        self._request_count = 0  # Reset request counter

        self.show_loading("Atualizando dados...")

        if self.tab_nav_state == 'received':
            self.receiveds()
        else:
            self.upload_requests()
