import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', '8c393fd817a4b941036fe00f5a79f7f9de0bb9fa0a05d8df')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', '3de4ef0c6b2e64196ceba40f40e29882bd2bebb1d66a5f6e')
    MONGO_URI = os.getenv('MONGO_URI', "mongodb+srv://saich019:sai12345@cluster0.rb7etho.mongodb.net/personal_budget?retryWrites=true&w=majority&appName=Cluster0")

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    DATABASE_URI = 'sqlite:///dev.db'

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    """Production configuration."""
    DATABASE_URI = 'sqlite:///prod.db'

# Select the appropriate configuration based on the environment variable
config_name = os.getenv('FLASK_CONFIG', 'DevelopmentConfig')
app_config = globals()[config_name]