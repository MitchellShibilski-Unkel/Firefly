import os
import flask


class Firefly:
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.index = ""
        self.style = ""
        self.directory = "templates"
        
    def homeFile(self, filename: str = "index.html", directory: str = "templates"):
        self.index = filename
        self.directory = directory
        return self.index, self.directory
    
    def moviesFile(self, filename: str = "movies.html", directory: str = "templates"):
        self.movies = filename
        self.directory = directory
        return self.movies, self.directory
    
    def tvFile(self, filename: str = "tv.html", directory: str = "templates"):
        self.tv = filename
        self.directory = directory
        return self.tv, self.directory
    
    def infoPage(self, filename: str = "info.html", directory: str = "templates"):
        self.info = filename
        self.directory = directory
        return self.info, self.directory
    
    def run(self, host: str = "127.0.0.1", port: int = 5000):
        app = flask.Flask(__name__)
        
        @app.route("/", methods=["GET", "POST"])
        def home():
            return flask.send_from_directory(os.path.join(os.getcwd(), self.directory), self.index)
        
        @app.route("/movies", methods=["GET", "POST"])
        def movies():
            return flask.send_from_directory(os.path.join(os.getcwd(), self.directory), self.movies)
        
        @app.route("/tv", methods=["GET", "POST"])
        def tv():
            return flask.send_from_directory(os.path.join(os.getcwd(), self.directory), self.tv)
        
        @app.route("/info", methods=["GET", "POST"])
        def info():
            return flask.send_from_directory(os.path.join(os.getcwd(), self.directory), self.info)
        
        app.run(host=host, port=port, debug=self.debug)