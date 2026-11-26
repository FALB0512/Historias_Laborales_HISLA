import threading
import webbrowser

from app import create_app
from app.seed import sembrar_datos

PUERTO = 5000
URL = f"http://127.0.0.1:{PUERTO}/"


def main():
    app = create_app()
    with app.app_context():
        sembrar_datos()
    print(f"HISLA en ejecución: {URL}")
    print("Para cerrar la aplicación, cierre esta ventana.")
    threading.Timer(1.5, webbrowser.open, args=[URL]).start()
    app.run(host="127.0.0.1", port=PUERTO, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
