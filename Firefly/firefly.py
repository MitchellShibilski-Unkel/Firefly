import os
import json
import flask
import shutil
import ffmpeg


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
    
    def secondsToTime(self, seconds):
        minutes, secs = divmod(int(float(seconds)), 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02}:{minutes:02}:{secs:02}"
    
    def getMovieInformation(self, dist: str):
        info = ffmpeg.probe(os.path.join(os.getcwd(), "media/movies", dist))
        info_dict = {"length": self.secondsToTime(info["format"]["duration"]), "year": info["format"]["tags"].get("creation_time", "Unknown")[:4], }
        return info_dict
    
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
    
    def loadMovie(self, title: str, dist: str = "movies.json"):
        with open(os.path.join(os.getcwd(), dist), "r") as f:
            movies = json.load(f)
        for movie in movies:
            if movie["title"] == title:
                return movie
            
        return None
    
    def loadTVShow(self, title: str, dist: str = "tv.json"):
        with open(os.path.join(os.getcwd(), dist), "r") as f:
            tv_shows = json.load(f)
        for show in tv_shows:
            if show["title"] == title:
                return show
            
        return None
    
    def addMovie(self, filename: str, title: str = "Unknown"):
        shutil.move(filename, os.path.join(os.getcwd(), "media/movies", filename))
        with open(os.path.join(os.getcwd(), "movies.json"), "r") as f:
            movies = json.load(f)
        movies.append({"title": title, "filename": filename})
        with open(os.path.join(os.getcwd(), "movies.json"), "w") as f:
            json.dump(movies, f)
        return "Added"

    def addTVShow(self, filename: str, title: str = "Unknown", season: int = 1, episode: int = 1):
        shutil.move(filename, os.path.join(os.getcwd(), "media/tv", filename))
        with open(os.path.join(os.getcwd(), "tv.json"), "r") as f:
            shows = json.load(f)
        shows.append({"title": title, "filename": filename, "season": season, "episode": episode})
        with open(os.path.join(os.getcwd(), "tv.json"), "w") as f:
            json.dump(shows, f)
        return "Added"
    
    def run(self, host: str = "127.0.0.1", port: int = 5000):
        app = flask.Flask(__name__, template_folder=os.path.join(os.getcwd(), self.directory), static_folder=os.path.join(os.getcwd(), "static"))
        
        @app.route("/", methods=["GET", "POST"])
        def index():
            movies = self.getMovies()
            shows = self.getTVShows()
            return flask.render_template(self.index, movies=movies, shows=shows)
        
        @app.route("/index", methods=["GET", "POST"])
        def home():
            movies = self.getMovies()
            shows = self.getTVShows()
            return flask.render_template(self.index, movies=movies, shows=shows)
        
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
        
        @app.route("/upload", methods=["POST"])
        def upload():
            file = flask.request.files.get("file")
            mediaType = flask.request.form.get("type", "movie")
            title = flask.request.form.get("title", "Unknown")
            if not file or file.filename == "":
                return "No file selected", 400
            os.makedirs(os.path.join(os.getcwd(), "media/movies"), exist_ok=True)
            os.makedirs(os.path.join(os.getcwd(), "media/tv"), exist_ok=True)
            savePath = os.path.join(os.getcwd(), "media/movies" if mediaType == "movie" else "media/tv", file.filename)
            file.save(savePath)
            if mediaType == "movie":
                self.addMovie(savePath, title)
            else:
                self.addTVShow(savePath, title)
            return flask.redirect("/")
        
        @app.route("/info/<movie>", methods=["GET", "POST"])
        def info(movie):
            movie_info = self.loadMovie(movie)
            if not movie_info:
                return "Movie not found", 404
            metadata = self.getMovieInformation(movie_info["filename"])
            return flask.render_template(self.info, movie=movie_info["title"], time=metadata["length"], year=metadata["year"])
        
        app.run(host=host, port=port, debug=self.debug)