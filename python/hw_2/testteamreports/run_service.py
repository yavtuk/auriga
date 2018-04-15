from testteamreports.service import app
from testteamreports.settings import APP_HOST, APP_PORT
from testteamreports.settings import CERTIFICATE_FILE, CERTIFICATE_KEY_FILE

if __name__ == '__main__':
    app.run(host=APP_HOST,
            port=APP_PORT,
            ssl_context=(CERTIFICATE_FILE, CERTIFICATE_KEY_FILE))
