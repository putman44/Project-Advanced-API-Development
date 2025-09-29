class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = (
        "mysql+mysqlconnector://root:Gocolts44@localhost/factory_db"
    )
    DEBUG = True
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300


class TestingConfig:
    pass


class ProductionConfig:
    pass
