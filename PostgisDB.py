import psycopg2
import configparser
from .tools import config
from qgis.PyQt.QtWidgets import QMessageBox


class PostGisDB:
    """Класс используется для подключения к БД 
    и получения результатов запроса, а также тестирования доступности БД
    """
    def __init__(self):
        self.cf = config.Configurer("dbconnection")
        self.connection = self.setConnection()

    def setConnection(self):
        try:
            btsettings = self.cf.readConfigs()
            self.user = btsettings.get("user")
            self.password = btsettings.get("password")
            self.host = btsettings.get("host")
            self.port = btsettings.get("port")
            self.database = btsettings.get("database")
        except Exception as e:
            QMessageBox.information(None, "Ошибка", e)
            # raise e
            # print(str(e))
        try:
            return psycopg2.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                database=self.database,
            )
        except Exception as e:
            return False

    def getQueryResult(self, query, as_dict=False, no_result=False):
        connection = self.setConnection()
        if connection:
            curPGSQL = connection.cursor()
            curPGSQL.execute(query)

            if as_dict:
                result_list = []
                keys = [desc[0] for desc in curPGSQL.description]
                values = curPGSQL.fetchall()
                for value in values:
                    result_list.append(dict(zip(keys, value)))
                if not len(result_list):
                    return [{}]
                return result_list

            connection.commit()
            if not no_result:
                return curPGSQL.fetchall()
        return []

    def testConnection(self, *args, **kwargs):
        try:
            psycopg2.connect(
                user=kwargs["user"],
                password=kwargs["password"],
                host=kwargs["host"],
                port=kwargs["port"],
                database=kwargs["database"],
            )
            return True
        except:
            return False

    def IsDataBaseActual(self):
        try:
            cur = self.setConnection().cursor()
            cur.execute("SELECT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename  = 'damaged_plants')")
            if cur.fetchone()[0]:
                return True
        except:
            return False

    def __del__(self):
        if self.connection:
            self.connection.close()
