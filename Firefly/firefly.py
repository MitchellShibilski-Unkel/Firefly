import os
import json
import flask
import shutil
import mediameta as mm


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
    
    def getMovieInformation(self, dist: str):
        return mm.VideoMetadata(os.path.join(os.getcwd(), dist))
    
    def getMovies(self, dist: str = "movies.json"):
        with open(os.path.join(os.getcwd(), dist), "r") as f:         
            movies = json.load(f)
        
        getTitles = lambda x: x["title"]
        return list(map(getTitles, movies))
    
    def getTVShows(self, dist: str = "tv.json"):
        with open(os.path.join(os.getcwd(), dist), "r") as f:         
            tv_shows = json.load(f)
        
        getTitles = lambda x: x["title"]
        return list(map(getTitles, tv_shows))
    
    def addMovie(self, filename: str, title: str = "Unknown"):
        addFile = shutil.move(filename, os.path.join(os.getcwd(), "media/movies", filename))
        addMovieToJSON = lambda x: {"title": title, "filename": filename}
        with open(os.path.join(os.getcwd(), "movies.json"), "w") as f:
            json.dump(addMovieToJSON(filename), f)
            
        return "Added"
    
    def addTVShow(self, filename: str, title: str = "Unknown", season: int = 1, episode: int = 1):
        addFile = shutil.move(filename, os.path.join(os.getcwd(), "media/tv", filename))
        addTVShowToJSON = lambda x: {"title": title, "filename": filename, "season": season, "episode": episode}
        with open(os.path.join(os.getcwd(), "tv.json"), "w") as f:
            json.dump(addTVShowToJSON(filename), f)
            
        return "Added"
    
    def run(self, host: str = "127.0.0.1", port: int = 5000):
        app = flask.Flask(__name__, template_folder=os.path.join(os.getcwd(), self.directory), static_folder=os.path.join(os.getcwd(), "static"))
        
        @app.route("/", methods=["GET", "POST"])
        def index():
            return flask.render_template(self.index)
        
        @app.route("/index", methods=["GET", "POST"])
        def home():
            return flask.render_template(self.index)
        
        @app.route("/search", methods=["GET", "POST"])
        def search():
            search_term = flask.request.args.get("q", "")
            movies = self.getMovies()
            shows = self.getTVShows()
            search_results = []
            for movie in movies:
                if search_term.lower() in movie.lower():
                    search_results.append(movie)
            for show in shows:
                if search_term.lower() in show.lower():
                    search_results.append(show)
            return flask.render_template("search.html", search_results=search_results)
        
        @app.route("/addMedia", methods=["GET", "POST"])
        def addMedia():
            return flask.render_template("addMedia.html")
        
        @app.route("/info/<movie>", methods=["GET", "POST"])
        def info(movie):
            movie_info = self.getMovieInformation(movie)
            return flask.render_template(self.info, title=movie_info.title, description=movie_info.description, genre=movie_info.genre, release_year=movie_info.release_year)
        
        app.run(host=host, port=port, debug=self.debug)