import requests
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.clock import Clock
import requests

client = {
    "api_key": "ваш ключ", #сюда ключ можно вставить, но лучше хранить в отдельном файле
    "base_url": "https://api.vsegpt.ru/v1"
}

KV = '''
BoxLayout:
    orientation: 'vertical'

    MDBoxLayout:
        size_hint_y: None
        height: self.minimum_height
        padding: 10
        spacing: 10

        MDTextField:
            id: user_input
            hint_text: "Введите сообщение"
            mode: "rectangle"
            multiline: False
            on_text_validate: app.send_message()

        MDRaisedButton:
            text: "Отправить"
            on_release: app.send_message()
'''

class ChatApp(MDApp):
    def build(self):
        return Builder.load_string(KV)

    def send_message(self):
        user_input = self.root.ids.user_input
        message = user_input.text
        if message:
            self.add_message("Вы: " + message, "user")
            user_input.text = ""
            self.get_response(message)

    def add_message(self, text, sender="user"):
        chat_layout = self.root.ids.chat_layout
        bubble = MDBoxLayout()
        label = MDLabel()
        label.bind(texture_size=label.setter("size"))
        bubble.add_widget(label)
        chat_layout.add_widget(bubble)

        # Прокрутка вниз после добавления нового сообщения
        Clock.schedule_once(self.scroll_to_bottom, 0.1)

    def scroll_to_bottom(self, *args):
        scroll_view = self.root.ids.scroll_view
        scroll_view.scroll_y = 0  # Прокрутка к нижней части ScrollView

    def get_response(self, message):
        pass

ChatApp().run()
