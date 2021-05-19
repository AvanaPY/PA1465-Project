from flask import Flask, app
from backend import BackendBase

app = None

class App(Flask):
    def __init__(self, host, port, confparser, load_ai=False, *args, **kwargs):
        super().__init__(__name__, *args, **kwargs)
        self._host = host
        self._port = port
        self._backend = BackendBase(confparser=confparser, load_ai=load_ai)

    def run(self, **kwargs):
        super().run(host=self._host, port=self._port, **kwargs)

def init_app(confparser, section='app', load_ai=False, **kwargs) -> App:
    """Initialize the core application."""

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

    global app
    app = App(host, port, confparser, instance_relative_config=False, load_ai=load_ai, **kwargs)

    with app.app_context():
        from . import routes

        from .plotlydash.dashboard import init_dashboard
        app = init_dashboard(app)

        return app