import requests
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp

# Настройки API
client = {
    "api_key": "ваш ключ",
    "base_url": "https://api.vsegpt.ru/v1"
}

KV = '''
BoxLayout:
    orientation: 'vertical'
    padding: 10
    spacing: 10

    MDTopAppBar:
        title: "Чат с ИИ"
        elevation: 4
        md_bg_color: app.theme_cls.primary_color

    ScrollView:
        id: scroll_view
        do_scroll_x: False
        bar_width: 4
        bar_color: app.theme_cls.primary_color

        MDBoxLayout:
            id: chat_layout
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            padding: [10, 10, 10, 10]
            spacing: 15

    MDBoxLayout:
        size_hint_y: None
        height: "60dp"
        padding: [10, 0, 10, 10]
        spacing: 10

        MDTextField:
            id: user_input
            hint_text: "Введите сообщение"
            mode: "rectangle"
            multiline: False
            on_text_validate: app.send_message()
            radius: [15, 15, 15, 15]

        MDRaisedButton:
            text: "Отправить"
            on_release: app.send_message()
            size_hint: (None, None)
            width: "120dp"
            height: "50dp"
            md_bg_color: app.theme_cls.primary_color

    MDBoxLayout:
        size_hint_y: None
        height: "50dp"
        padding: [10, 0, 10, 0]

        MDFillRoundFlatButton:
            text: "Очистить чат"
            on_release: app.clear_chat()
            md_bg_color: app.theme_cls.error_color
            text_color: 1, 1, 1, 1
'''

class ChatApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.messages = []  # Хранение истории сообщений

    def build(self):
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.theme_style = "Light"
        return Builder.load_string(KV)

    def send_message(self):
        user_input = self.root.ids.user_input
        message = user_input.text.strip()
        if message:
            # Добавляем сообщение пользователя
            self.add_message(f"Вы: {message}", "user")
            self.messages.append({"role": "user", "content": message})
            user_input.text = ""
            
            # Получаем ответ от ИИ
            self.get_response(message)

    def add_message(self, text, sender="user"):
        chat_layout = self.root.ids.chat_layout
        
        # Создаем карточку для сообщения
        card = MDCard(
            size_hint_y=None,
            radius=[15, 15, 15, 15],
            padding="12dp",
            elevation=2,
            md_bg_color=self.theme_cls.bg_light if sender == "user" else self.theme_cls.primary_color
        )
        
        # Создаем метку для текста
        label = MDLabel(
            text=text,
            theme_text_color="Custom",
            text_color=[0, 0, 0, 1] if sender == "user" else [1, 1, 1, 1],
            font_size="16sp",
            size_hint_y=None,
            adaptive_height=True,
            padding=[10, 5, 10, 5]
        )
        
        card.add_widget(label)
        chat_layout.add_widget(card)
        
        # Прокрутка вниз после добавления нового сообщения
        Clock.schedule_once(self.scroll_to_bottom, 0.1)

    def scroll_to_bottom(self, *args):
        scroll_view = self.root.ids.scroll_view
        scroll_view.scroll_y = 0

    def get_response(self, message):
        try:
            # Отображаем "ИИ печатает..."
            thinking_message = "ИИ: Думаю..."
            self.add_message(thinking_message, "ai")
            thinking_card = self.root.ids.chat_layout.children[0]
            
            headers = {
                "Authorization": f"Bearer {client['api_key']}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": message}],
                "temperature": 0.7
            }
            
            response = requests.post(
                f"{client['base_url'].strip()}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            # Удаляем сообщение "Думаю..."
            chat_layout = self.root.ids.chat_layout
            if thinking_card in chat_layout.children:
                chat_layout.remove_widget(thinking_card)
            
            if response.status_code == 200:
                ai_response = response.json()['choices'][0]['message']['content']
                self.add_message(f"ИИ: {ai_response}", "ai")
                self.messages.append({"role": "assistant", "content": ai_response})
            else:
                error_msg = f"ИИ: Ошибка API ({response.status_code})"
                self.add_message(error_msg, "ai")
                
        except Exception as e:
            # Удаляем сообщение "Думаю..." при ошибке
            chat_layout = self.root.ids.chat_layout
            if 'thinking_card' in locals() and thinking_card in chat_layout.children:
                chat_layout.remove_widget(thinking_card)
            
            error_msg = f"ИИ: Ошибка подключения: {str(e)}"
            self.add_message(error_msg, "ai")

    def clear_chat(self):
        """Очищает чат и историю сообщений"""
        chat_layout = self.root.ids.chat_layout
        chat_layout.clear_widgets()
        self.messages.clear()
        # Добавляем приветственное сообщение
        self.add_message("ИИ: Привет! Чем могу помочь?", "ai")

    def on_start(self):
        """Вызывается при запуске приложения"""
        self.add_message("ИИ: Привет! Чем могу помочь?", "ai")


ChatApp().run()