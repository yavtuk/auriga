from testteamreports.data.model import db
from testteamreports.data import operations as ops

from testteamreports.settings import ADMIN_LOGIN

if __name__ == '__main__':
    destructive = True

    db.connect()
    try:
        if destructive:
            ops.recreate_db()

        assert ops.get_all_logins() == [ADMIN_LOGIN], "Admin user created"

    finally:
        db.close()
