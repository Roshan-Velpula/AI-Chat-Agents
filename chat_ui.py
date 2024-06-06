from nicegui import ui
from datetime import datetime
from tools import get_tasks, execute_tasks, auto_respond

messages = []
usernames = ['Roshan', 'David']



@ui.refreshable
def chat_messages(current_user):
    for message in messages:
        user_name = message['user']
        avatar = message['avatar']
        text = message['text']
        timestamp = message['timestamp']
        ui.chat_message(avatar=avatar, text=f"{text}", sent=user_name == current_user, stamp=f'{timestamp}', name=f'{user_name}')

@ui.page('/')
def index():
    def select_user(selected_user):
        user = selected_user
        avatar = f'https://robohash.org/{user}?bgset=bg2'


        def send():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = {
                'user': user,
                'avatar': avatar,
                'text': text.value,
                'timestamp': timestamp,
            }
            messages.append(message)
            chat_messages.refresh()
            text.value = ''
            
        def trigger_auto_respond():
            response = auto_respond(messages, user)
            text.value = response

        def send_message_history():
            global functions
            if select1.visible:
                select1.visible = False
            else:
                tasks, functions = get_tasks(messages, user)
                if tasks:
                    select1.options=tasks
                    select1.visible = True
                else:
                    ui.notify("No Tasks to show")
                return functions

        with ui.column().classes('w-full items-stretch'):
            chat_messages(user)

        with ui.footer().classes('bg-white'):
            with ui.row().classes('w-full items-center'):
                with ui.avatar():
                    ui.image(avatar)
                text = ui.input(placeholder='message') \
                    .props('rounded outlined').classes('flex-grow') \
                    .on('keydown.enter', send)
                ui.button('Send').on('click', send)
                ui.button('?').on('click', send_message_history)
                ui.button('AI').on('click', trigger_auto_respond)
                select1 = ui.select(
                    label='Select a task', 
                    options=[], 
                    on_change=lambda e: execute_tasks(e.value, select1, functions, text)
                ).props('outlined').classes('flex-grow')
                select1.visible = False

    with ui.column().classes('w-full items-center'):
        ui.label('Select User')
        for username in usernames:
            ui.button(username).on('click', lambda username=username: select_user(username))

ui.run()
