import os
import json
import flask
import shutil
import tmdbv3api


class Firefly:
    def __init__(self, debug: bool = False, tmdbv3api_key: str = ""):
        self.debug = debug
        self.index = ""
        self.style = ""
        self.directory = "templates"
        self.apiKey = tmdbv3api_key
        if self.apiKey:
            self.tmdb = tmdbv3api.TMDb()
            self.tmdb.api_key = self.apiKey
            self.search = tmdbv3api.Search()
        else:
            self.tmdb = None
            self.search = None
        
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
    
    def getMovieInformation(self, title: str):
        if not self.search:
            return {"length": "Unknown", "release": "Unknown", "poster": "", "overview": ""}
        try:
            results = self.search.movie(query=title)
            if not results:
                return {"length": "Unknown", "release": "Unknown", "poster": "", "overview": ""}
            movie = results[0]
            movie_obj = tmdbv3api.Movie().details(movie.id)
            poster_path = movie.poster_path if hasattr(movie, 'poster_path') else ""
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
            return {"length": self.secondsToTime(movie_obj.runtime * 60) if hasattr(movie_obj, 'runtime') else "Unknown", "release": movie.release_date if hasattr(movie, 'release_date') else "Unknown", "poster": poster_url, "overview": movie.overview if hasattr(movie, 'overview') else ""}
        except Exception as e:
            return {"length": "Unknown", "release": "Unknown", "poster": "", "overview": ""}
    
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
    
    def addMovie(self, filename: str, title: str = "Unknown", date: str = "Unknown"):
        shutil.move(filename, os.path.join(os.getcwd(), "media/movies", filename))
        with open(os.path.join(os.getcwd(), "movies.json"), "r") as f:
            movies = json.load(f)
        movie_info = self.getMovieInformation(title) if self.search else {"length": "Unknown", "release": date or "Unknown", "poster": "", "overview": ""}
        movies.append({"title": title, "filename": filename, "release": movie_info.get("release", date), "poster": movie_info.get("poster", ""), "overview": movie_info.get("overview", "")})
        with open(os.path.join(os.getcwd(), "movies.json"), "w") as f:
            json.dump(movies, f)
        return "Added"

    def addTVShow(self, filename: str, title: str = "Unknown", date: str = "Unknown", season: int = 1, episode: int = 1):
        shutil.move(filename, os.path.join(os.getcwd(), "media/tv", filename))
        with open(os.path.join(os.getcwd(), "tv.json"), "r") as f:
            shows = json.load(f)
        shows.append({"title": title, "filename": filename, "season": season, "episode": episode, "release": date})
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
            releaseDate = flask.request.form.get("date", "Unknown")
            try:
                season = int(flask.request.form.get("season", 1))
                episode = int(flask.request.form.get("episode", 1))
            except ValueError:
                season = 1
                episode = 1
            if not file or file.filename == "":
                return "No file selected", 400
            os.makedirs(os.path.join(os.getcwd(), "media/movies"), exist_ok=True)
            os.makedirs(os.path.join(os.getcwd(), "media/tv"), exist_ok=True)
            savePath = os.path.join(os.getcwd(), "media/movies" if mediaType == "movie" else "media/tv", file.filename)
            file.save(savePath)
            if mediaType == "movie":
                self.addMovie(savePath, title, releaseDate)
            else:
                self.addTVShow(savePath, title, releaseDate, season, episode)
            return flask.redirect("/")
        
        @app.route("/info/<movie>", methods=["GET", "POST"])
        def info(movie):
            movie_info = self.loadMovie(movie)
            if not movie_info:
                return "Movie not found", 404
            metadata = self.getMovieInformation(movie_info["title"])
            return flask.render_template(self.info, movie=movie, title=movie_info["title"], description=movie_info.get("overview", metadata.get("overview", "Unknown")), genre=movie_info.get("genre", "Unknown"), time=metadata["length"], release=metadata["release"], poster=metadata["poster"])
        
        @app.route("/player/<movie>", methods=["GET", "POST"])
        def player(movie):
            movie_info = self.loadMovie(movie)
            if not movie_info:
                return "Movie not found", 404
            return flask.render_template("player.html", movie=movie, title=movie_info["title"], filename=os.path.basename(movie_info["filename"]))

        @app.route("/media/<path:filename>")
        def media(filename):
            movie_info_list = json.load(open(os.path.join(os.getcwd(), "movies.json")))
            for m in movie_info_list:
                if os.path.basename(m["filename"]) == filename:
                    return flask.send_from_directory(os.path.dirname(m["filename"]), filename)
            return flask.send_from_directory(os.path.join(os.getcwd(), "media"), filename)
        
        app.run(host=host, port=port, debug=self.debug)