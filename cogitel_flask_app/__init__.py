from flask import Flask
from backend import BackendBase
app = None

def init_app(confparser, section='app'):
    """Initialize the core application."""
    global app

    host, port = 'localhost', 5000 # Default values

    if not confparser is None:
        config = {}
        if confparser.has_section(section):
            items = confparser.items(section)
            for item in items:
                config[item[0]] = item[1]
        else:
            raise Exception('Section {0} not found in the config file'.format(section))

        try:
            host = config['ip']
            port = int(config['port'])
        except KeyError as e:
            raise Exception(f'Error when reading config file: {e.args[0]} not in config file in section {section}!')
        except ValueError as e:
            raise Exception(f'Error when reading config file: "{config["port"]}" is not a valid port value!')


    app = App(host, port, confparser, instance_relative_config=False)
    #app.config.from_object('config.Config')

    # Initialize Plugins
    # db.init_app(app)
    # r.init_app(app)

    with app.app_context():
        # Include our Routes
        from . import routes

        # Register Blueprints
        # app.register_blueprint(auth.auth_bp)
        # app.register_blueprint(admin.admin_bp)

        return app


class App(Flask):
    def __init__(self, host, port, confparser, *args, **kwargs):
        super().__init__(__name__, *args, **kwargs)
        self._host = host
        self._port = port
        self._backend = BackendBase(confparser=confparser)

    def run(self, **kwargs):
        super().run(host=self._host, port=self._port)