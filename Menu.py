import threading
import time

# Simulación de una base de datos de chats activos
active_chats = {"1": ["Chat de grupo 1", "Usuario1", "Usuario2"],
                "2": ["Chat de grupo 2", "Usuario1", "Usuario3"]}


# Clase para manejar la interfaz de usuario
class UserInterface:
    def __init__(self, username):
        self.username = username

    def show_options(self):
        print("1. Connect chat")
        print("2. Subscribe to group chat")
        print("3. Discover chats")
        print("4. Access insult channel")

    def connect_chat(self, chat_id):
        # Simulación de la conexión al chat
        print(f"Conectado al chat {chat_id}")

    def subscribe_to_group_chat(self, chat_id):
        # Simulación de la suscripción al chat de grupo
        print(f"Suscrito al chat de grupo {chat_id}")

    def discover_chats(self):
        # Simulación de la obtención de chats activos
        print("Chats activos:")
        for chat_id, chat_info in active_chats.items():
            print(f"ID: {chat_id}, Nombre: {chat_info[0]}")

    def access_insult_channel(self):
        # Simulación de acceso al canal de insultos
        print("Acceso al canal de insultos")


# Función para manejar la entrada del usuario y ejecutar las opciones
def handle_input(ui):
    while True:
        ui.show_options()
        option = input("Ingrese el número de la opción deseada: ")

        if option == "1":
            chat_id = input("Ingrese el ID del chat al que desea conectarse: ")
            ui.connect_chat(chat_id)
        elif option == "2":
            chat_id = input("Ingrese el ID del grupo al que desea suscribirse: ")
            ui.subscribe_to_group_chat(chat_id)
        elif option == "3":
            ui.discover_chats()
        elif option == "4":
            ui.access_insult_channel()
        else:
            print("Opción no válida")


# Función principal
def main():
    username = input("Ingrese su nombre de usuario: ")
    ui = UserInterface(username)

    # Iniciar un hilo para manejar la entrada del usuario
    input_thread = threading.Thread(target=handle_input, args=(ui,))
    input_thread.start()

    # Simulación de la ejecución del cliente
    while True:
        # Simulación de otras tareas que el cliente podría realizar en segundo plano
        time.sleep(5)


if __name__ == "__main__":
    main()
