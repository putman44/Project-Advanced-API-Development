class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = (
        "mysql+mysqlconnector://root:Gocolts44@localhost/factory_db"
    )
    DEBUG = True


class TestingConfig:
    pass


class ProductionConfig:
    pass
