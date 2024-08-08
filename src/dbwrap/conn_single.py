import psycopg2

class PostgresSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = psycopg2.connect(
                host="db-thymela.cfak28agap23.eu-west-1.rds.amazonaws.com", 
                port=5432, 
                database="thymeladatabase", 
                user="thymelaadmin", 
                password="This_Is_My_Database_There_Are_Many_Like_It_But_This_One_Is_Mine" # REMOVE TODO
            )
        return cls._instance

    def get_connection(self):
        return self.connection