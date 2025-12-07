from kivymd.uix.boxlayout import MDBoxLayout
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.core.clipboard import Clipboard
from kivy.clock import Clock
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.uix.modalview import ModalView
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
from kivymd.uix.label import MDIcon

class DialogErrorUnknow(ModalView):
    def __init__(self, screen='', **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.9, None)
        self.height = dp(450)
        self.background_color = (0, 0, 0, 0)
        self.background = ""
        card = MDCard(
            size_hint=(1, 1),
            radius=[15, 15, 15, 15],
            theme_bg_color='Custom',
            md_bg_color=(1, 1, 1, 1),
            elevation=6,
        )
        layout = MDRelativeLayout()
        # Barra azul superior
        top_bar = MDBoxLayout(
            size_hint=(1, None),
            height=dp(10),
            pos_hint={'top': 1},
            md_bg_color=get_color_from_hex("#5F0F40"),
        )
        top_bar.radius = [15, 15, 0, 0]
        layout.add_widget(top_bar)

        # Ícone animado
        self.icon = MDIcon(
            icon='alert-circle-outline',
            theme_icon_color='Custom',
            icon_color=get_color_from_hex("#5F0F40"),
            theme_font_size='Custom',
            font_size='65dp',
            pos_hint={'center_x': 0.5, 'center_y': 0.87},
        )
        layout.add_widget(self.icon)

        # Título
        content_label = MDLabel(
            text=f"Erro desconhecido",
            font_style='Title',
            role='large',
            bold=True,
            theme_text_color='Custom',
            text_color='black',
            halign="center",
            pos_hint={'center_x': 0.5, 'center_y': 0.76},
        )
        layout.add_widget(content_label)

        # Subtítulo
        subtitle = MDLabel(
            text=f"Ocorreu um erro inesperado na tela {screen}. Por favor, entre em contato com o suporte.",
            font_style='Label',
            role='small',
            theme_text_color='Custom',
            text_color='black',
            size_hint_x=0.85,
            halign="center",
            pos_hint={'center_x': 0.5, 'center_y': 0.68},
        )
        layout.add_widget(subtitle)

        # ============= suporte email =========================
        container_email = MDBoxLayout(
            orientation='vertical',
            size_hint=(0.9, 0.16),
            theme_bg_color='Custom',
            radius=[15,],
            theme_line_color='Custom',
            line_color=get_color_from_hex('#E5E7EB'),
            pos_hint={'center_x': 0.5, 'center_y': 0.51}
        )

        # Header com texto "E-mail de suporte"
        header_box_email = MDBoxLayout(
            theme_bg_color='Custom',
            md_bg_color=get_color_from_hex('#F9FAFB'),
            size_hint_y=0.35,
            radius=[15, 15, 0, 0]
        )

        header_relative_email = MDRelativeLayout()
        header_label_email = MDLabel(
            text='E-mail de suporte:',
            font_style='Body',
            role='medium',
            halign='center',
            theme_text_color='Custom',
            text_color='black',
            bold=False,
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        header_relative_email.add_widget(header_label_email)
        header_box_email.add_widget(header_relative_email)

        # Box horizontal com email e botão
        content_box_email = MDBoxLayout(
            orientation='horizontal',
            theme_bg_color='Custom',
            md_bg_color=get_color_from_hex('#F9FAFB')
        )

        # Box do email
        email_box = MDBoxLayout(
            theme_bg_color='Custom',
            md_bg_color=get_color_from_hex('#F9FAFB')
        )

        email_relative = MDRelativeLayout()
        email_label = MDLabel(
            text='suportemaodeobra@gmail.com',
            theme_text_color='Custom',
            font_style='Body',
            role='small',
            text_color='black',
            bold=True,
            halign='left',
            pos_hint={'center_x': 0.55, 'center_y': 0.5}
        )
        email_relative.add_widget(email_label)
        email_box.add_widget(email_relative)

        # Box do botão copiar email
        button_box_email = MDBoxLayout(
            theme_bg_color='Custom',
            md_bg_color=get_color_from_hex('#F9FAFB'),
            size_hint_x=0.45
        )

        button_relative_email = MDRelativeLayout()
        self.button_card_email = MDCard(
            theme_bg_color='Custom',
            md_bg_color=get_color_from_hex('#5F0F40'),
            size_hint=(0.9, 0.5),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        button_card_relative_email = MDRelativeLayout()
        self.icon_copy_email = MDIcon(
            icon='content-copy',
            theme_font_size='Custom',
            font_size='14dp',
            theme_icon_color='Custom',
            icon_color='white',
            pos_hint={'center_x': 0.26, 'center_y': 0.5}
        )

        self.text_copy_email = MDLabel(
            text='Copiar',
            font_style='Label',
            role='medium',
            theme_text_color='Custom',
            text_color='white',
            halign='center',
            pos_hint={'center_x': 0.65, 'center_y': 0.5}
        )

        button_card_relative_email.add_widget(self.icon_copy_email)
        button_card_relative_email.add_widget(self.text_copy_email)
        self.button_card_email.add_widget(button_card_relative_email)
        button_relative_email.add_widget(self.button_card_email)
        button_box_email.add_widget(button_relative_email)

        # Bind do clique no botão email
        self.button_card_email.bind(on_release=self.copy_email)

        # Montando a estrutura email
        content_box_email.add_widget(email_box)
        content_box_email.add_widget(button_box_email)

        container_email.add_widget(header_box_email)
        container_email.add_widget(content_box_email)
        layout.add_widget(container_email)

        # ============= suporte whatsapp =========================
        container_whatsapp = MDBoxLayout(
            orientation='vertical',
            size_hint=(0.9, 0.16),
            theme_bg_color='Custom',
            radius=[15,],
            theme_line_color='Custom',
            line_color=get_color_from_hex('#BBF7D0'),
            pos_hint={'center_x': 0.5, 'center_y': 0.32}
        )

        # Header com texto "WhatsApp de suporte"
        header_box_whatsapp = MDBoxLayout(
            theme_bg_color='Custom',
            md_bg_color=get_color_from_hex('#F0FDF4'),
            size_hint_y=0.35,
            radius=[15, 15, 0, 0]
        )

        header_relative_whatsapp = MDRelativeLayout()
        header_label_whatsapp = MDLabel(
            text='WhatsApp de suporte:',
            font_style='Body',
            role='medium',
            halign='center',
            theme_text_color='Custom',
            text_color='black',
            bold=False,
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        header_relative_whatsapp.add_widget(header_label_whatsapp)
        header_box_whatsapp.add_widget(header_relative_whatsapp)

        # Box horizontal com whatsapp e botão
        content_box_whatsapp = MDBoxLayout(
            orientation='horizontal',
            theme_bg_color='Custom',
            md_bg_color=get_color_from_hex('#F0FDF4')
        )

        # Box do whatsapp
        whatsapp_box = MDBoxLayout(
            theme_bg_color='Custom',
            md_bg_color=get_color_from_hex('#F0FDF4')
        )

        whatsapp_relative = MDRelativeLayout()
        whatsapp_label = MDLabel(
            text='+55 62 98765-4321',
            theme_text_color='Custom',
            font_style='Body',
            role='small',
            text_color='black',
            bold=True,
            halign='left',
            pos_hint={'center_x': 0.55, 'center_y': 0.5}
        )
        whatsapp_relative.add_widget(whatsapp_label)
        whatsapp_box.add_widget(whatsapp_relative)

        # Box do botão copiar whatsapp
        button_box_whatsapp = MDBoxLayout(
            theme_bg_color='Custom',
            md_bg_color=get_color_from_hex('#F0FDF4'),
            size_hint_x=0.45
        )

        button_relative_whatsapp = MDRelativeLayout()
        self.button_card_whatsapp = MDCard(
            theme_bg_color='Custom',
            md_bg_color=get_color_from_hex('#16A34A'),
            size_hint=(0.9, 0.5),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        button_card_relative_whatsapp = MDRelativeLayout()
        self.icon_copy_whatsapp = MDIcon(
            icon='content-copy',
            theme_font_size='Custom',
            font_size='14dp',
            theme_icon_color='Custom',
            icon_color='white',
            pos_hint={'center_x': 0.26, 'center_y': 0.5}
        )

        self.text_copy_whatsapp = MDLabel(
            text='Copiar',
            font_style='Label',
            role='medium',
            theme_text_color='Custom',
            text_color='white',
            halign='center',
            pos_hint={'center_x': 0.65, 'center_y': 0.5}
        )

        button_card_relative_whatsapp.add_widget(self.icon_copy_whatsapp)
        button_card_relative_whatsapp.add_widget(self.text_copy_whatsapp)
        self.button_card_whatsapp.add_widget(button_card_relative_whatsapp)
        button_relative_whatsapp.add_widget(self.button_card_whatsapp)
        button_box_whatsapp.add_widget(button_relative_whatsapp)

        # Bind do clique no botão whatsapp
        self.button_card_whatsapp.bind(on_release=self.copy_whatsapp)

        # Montando a estrutura whatsapp
        content_box_whatsapp.add_widget(whatsapp_box)
        content_box_whatsapp.add_widget(button_box_whatsapp)

        container_whatsapp.add_widget(header_box_whatsapp)
        container_whatsapp.add_widget(content_box_whatsapp)
        layout.add_widget(container_whatsapp)

        # Botão "entendi"
        ok = MDCard(
            MDLabel(
                text="entendi",
                theme_text_color='Custom',
                text_color='black',
                font_style='Body',
                role='large',
                halign='center',
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
            ),
            pos_hint={'center_x': 0.5, 'center_y': 0.12},
            radius=[5,],
            size_hint=(0.85, 0.09),
            theme_line_color='Custom',
            line_color='grey',
            md_bg_color='white',
        )
        ok.bind(on_release=lambda x: self.dismiss())
        layout.add_widget(ok)
        card.add_widget(layout)
        self.add_widget(card)

    def copy_email(self, instance):
        """Copia o email para a área de transferência"""
        Clipboard.copy('suportemaodeobra@gmail.com')
        
        # Muda o ícone e texto para "Copiado"
        self.icon_copy_email.icon = 'check'
        self.text_copy_email.text = 'Copiado!'
        
        # Volta ao normal após 1 segundo
        Clock.schedule_once(lambda dt: self.reset_email_button(), 1)
    
    def reset_email_button(self):
        """Reseta o botão de email ao estado original"""
        self.icon_copy_email.icon = 'content-copy'
        self.text_copy_email.text = 'Copiar'
    
    def copy_whatsapp(self, instance):
        """Copia o WhatsApp para a área de transferência"""
        Clipboard.copy('+55 62 98765-4321')
        
        # Muda o ícone e texto para "Copiado"
        self.icon_copy_whatsapp.icon = 'check'
        self.text_copy_whatsapp.text = 'Copiado!'
        
        # Volta ao normal após 1 segundo
        Clock.schedule_once(lambda dt: self.reset_whatsapp_button(), 1)
    
    def reset_whatsapp_button(self):
        """Reseta o botão de whatsapp ao estado original"""
        self.icon_copy_whatsapp.icon = 'content-copy'
        self.text_copy_whatsapp.text = 'Copiar'

class DialogInfinityUpload(ModalView):
    def __init__(self, title='Dados não encontrados', subtitle='Nenhum dado acerca da pesquisa foi encontrado', **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.9, None)
        self.height = dp(230)
        self.background_color = (0, 0, 0, 0)
        self.background = ""
        # Card
        card = MDCard(
            size_hint=(0.6, 0.6),
            radius=[15, 15, 15, 15],
            md_bg_color=(1, 1, 1, 1),
            elevation=6,
        )

        layout = MDRelativeLayout()

        self.upload = MDIcon(
            icon='reload',
            theme_font_size='Custom',
            font_size='75dp',
            theme_icon_color='Custom',
            icon_color='blue',
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        layout.add_widget(self.upload)
        card.add_widget(layout)
        self.add_widget(card)
        
        # Inicia a animação após adicionar o widget
        self.create_animation()

    def create_animation(self):
        """Cria a animação necessaria pro icon girar"""
        from kivy.animation import Animation
        from kivy.graphics import PushMatrix, Rotate, PopMatrix
        
        # Adiciona transformação de rotação ao canvas do ícone
        with self.upload.canvas.before:
            PushMatrix()
            self.rotation = Rotate(angle=0, origin=self.upload.center)
        
        with self.upload.canvas.after:
            PopMatrix()
        
        # Atualiza a origem quando o ícone mudar de posição/tamanho
        def update_rotation_origin(instance, value):
            self.rotation.origin = instance.center
        
        self.upload.bind(pos=update_rotation_origin, size=update_rotation_origin)
        
        # Cria e inicia a animação
        def repeat_animation(animation, widget):
            # Incrementa 360 graus ao invés de resetar
            anim = Animation(angle=widget.angle + 360, duration=1.5)
            anim.bind(on_complete=repeat_animation)
            anim.start(widget)
        
        # Inicia a primeira rotação
        anim = Animation(angle=360, duration=1.5)
        anim.bind(on_complete=repeat_animation)
        anim.start(self.rotation)

class DialogNoResult(ModalView):
    def __init__(self, title='Dados não encontrados', subtitle='Nenhum dado acerca da pesquisa foi encontrado', **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.9, None)
        self.height = dp(230)
        self.background_color = (0, 0, 0, 0)
        self.background = "white"

        # Card
        card = MDCard(
            size_hint=(1, 1),
            radius=[15, 15, 15, 15],
            md_bg_color=(1, 1, 1, 1),
            elevation=6,
        )

        layout = MDRelativeLayout()

        # Barra azul superior
        top_bar = MDBoxLayout(
            size_hint=(1, None),
            height=dp(10),
            pos_hint={'top': 1},
            md_bg_color=get_color_from_hex("#525252"),
        )
        top_bar.radius = [15, 15, 0, 0]
        layout.add_widget(top_bar)

        # Ícone animado
        self.icon = MDIcon(
            icon='alert-circle-outline',
            theme_icon_color='Custom',
            icon_color=get_color_from_hex("#525252"),
            theme_font_size='Custom',
            font_size='45dp',
            pos_hint={'center_x': 0.5, 'center_y': 0.75},
        )
        layout.add_widget(self.icon)

        # Título
        content_label = MDLabel(
            text=f"{title}",
            font_style='Title',
            role='large',
            bold=True,
            theme_text_color='Custom',
            text_color='black',
            halign="center",
            pos_hint={'center_x': 0.5, 'center_y': 0.53},
        )
        layout.add_widget(content_label)

        # Subtítulo
        subtitle = MDLabel(
            text=f"{subtitle}",
            font_style='Label',
            role='small',
            theme_text_color='Custom',
            text_color='black',
            size_hint_x=0.85,
            halign="center",
            pos_hint={'center_x': 0.5, 'center_y': 0.4},
        )
        layout.add_widget(subtitle)

        # Botão "entendi"
        ok = MDCard(
            MDLabel(
                text="entendi",
                theme_text_color='Custom',
                text_color='black',
                font_style='Body',
                role='large',
                halign='center',
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
            ),
            pos_hint={'center_x': 0.5, 'center_y': 0.15},
            radius=[5,],
            size_hint=(0.7, 0.16),
            md_bg_color='white',
            theme_line_color='Custom',
            line_color='grey',
        )
        ok.bind(on_release=lambda x: self.dismiss())
        layout.add_widget(ok)

        card.add_widget(layout)
        self.add_widget(card)

class DialogReload(ModalView):
    def __init__(self, title='', subtitle='', **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.9, None)
        self.height = dp(230)
        self.background_color = (0, 0, 0, 0)
        self.background = ""

        # Card
        card = MDCard(
            size_hint=(1, 1),
            radius=[15, 15, 15, 15],
            md_bg_color=(1, 1, 1, 1),
            elevation=6,
        )

        layout = MDRelativeLayout()

        # Barra azul superior
        top_bar = MDBoxLayout(
            size_hint=(1, None),
            height=dp(10),
            pos_hint={'top': 1},
            md_bg_color=get_color_from_hex("#3B82F6"),
        )
        top_bar.radius = [15, 15, 0, 0]
        layout.add_widget(top_bar)

        # Ícone animado
        self.icon = MDIcon(
            icon='reload',
            theme_icon_color='Custom',
            icon_color=get_color_from_hex("#3B82F6"),
            theme_font_size='Custom',
            font_size='45dp',
            pos_hint={'center_x': 0.5, 'center_y': 0.75},
        )
        layout.add_widget(self.icon)

        # Título
        content_label = MDLabel(
            text=f"{title}",
            font_style='Title',
            role='large',
            bold=True,
            theme_text_color='Custom',
            text_color='black',
            halign="center",
            pos_hint={'center_x': 0.5, 'center_y': 0.53},
        )
        layout.add_widget(content_label)

        # Subtítulo
        subtitle = MDLabel(
            text=f"{subtitle}",
            font_style='Label',
            role='small',
            theme_text_color='Custom',
            text_color='black',
            size_hint_x=0.85,
            halign="center",
            pos_hint={'center_x': 0.5, 'center_y': 0.4},
        )
        layout.add_widget(subtitle)

        # Botão "entendi"
        ok = MDCard(
            MDLabel(
                text="entendi",
                theme_text_color='Custom',
                text_color='black',
                font_style='Body',
                role='large',
                halign='center',
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
            ),
            pos_hint={'center_x': 0.5, 'center_y': 0.15},
            radius=[5,],
            size_hint=(0.7, 0.16),
            md_bg_color='white',
            theme_line_color='Custom',
            line_color='grey',
        )
        ok.bind(on_release=lambda x: self.dismiss())
        layout.add_widget(ok)

        card.add_widget(layout)
        self.add_widget(card)


class DialogNoNet(ModalView):
    def __init__(self, subtitle='', callback=None, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.9, None)
        self.height = dp(230)
        self.background_color = (0, 0, 0, 0)  # escurece fundo
        self.background = ""  # remove imagem padrão

        # Card principal
        card = MDCard(
            size_hint=(1, 1),
            radius=[15, 15, 15, 15],  # todas as bordas arredondadas
            md_bg_color=(1,1,1,1),    # cor de fundo do card
            elevation=6,              # sombra leve, não muito escura
        )

        # Layout interno
        layout = MDRelativeLayout()

        # Barra azul arredondada apenas nas pontas de cima
        top_bar = MDBoxLayout(
            size_hint=(1, None),
            height=dp(10),
            pos_hint={'top': 1},
            md_bg_color=get_color_from_hex("#FF0000")
        )
        top_bar.radius = [15, 15, 0, 0]  # apenas canto superior esquerdo e direito arredondados

        layout.add_widget(top_bar)

        # Exemplo de conteúdo central
        content_label = MDLabel(
            text="Sem conexão",
            font_style='Title',
            role='large',
            bold=True,
            theme_text_color='Custom',
            text_color='black',
            halign="center",
            pos_hint={'center_x':0.5, 'center_y':0.53},
        )
        
        subtitle = MDLabel(
            text=f"{subtitle}",
            font_style='Label',
            role='small',
            theme_text_color='Custom',
            text_color='black',
            size_hint_x=0.85,
            halign="center",
            pos_hint={'center_x':0.5, 'center_y':0.4},
        )

        cancel = MDCard(
            MDLabel(
                text='Cancelar',
                theme_text_color='Custom',
                text_color='black',
                font_style='Body',
                role='medium',
                bold=True,
                halign='center',
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            ),
            pos_hint={'center_x': 0.77, 'center_y': 0.15},
            theme_bg_color='Custom',
            radius=[5,],
            size_hint=(0.34, 0.16),
            md_bg_color='white',
            theme_line_color='Custom',
            line_color='grey'
        )
        cancel.bind(on_release=lambda dt: self.dismiss())
        try_again = MDCard(
            MDLabel(
                text='Tentar novamente',
                theme_text_color='Custom',
                text_color='white',
                font_style='Body',
                role='medium',
                bold=True,
                halign='center',
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            ),
            pos_hint={'center_x': 0.32, 'center_y': 0.15},
            theme_bg_color='Custom',
            md_bg_color='red',
            radius=[5,],
            size_hint=(0.49, 0.16),
            theme_line_color='Custom',
            line_color='red'
        )
        try_again.bind(on_release=lambda x: callback() if callback else self.dismiss())
        layout.add_widget(content_label)
        layout.add_widget(subtitle)
        layout.add_widget(cancel)
        layout.add_widget(try_again)

        icon = MDIcon(
            icon='wifi-off',
            theme_icon_color='Custom',
            icon_color='red',
            theme_font_size='Custom',
            font_size='45dp',
            pos_hint={'center_x': 0.5, 'center_y': 0.75}
        )
        layout.add_widget(icon)
        card.add_widget(layout)
        self.add_widget(card)

        
def firebase_url():
    return 'https://obra-7ebd9-default-rtdb.firebaseio.com/'
