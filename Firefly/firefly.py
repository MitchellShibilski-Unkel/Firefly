import os
import json
import flask
import shutil
from tmdbv3api import TMDb, Movie, TV


class Firefly:
    def __init__(self, debug: bool = False, tmdbv3api_key: str = "", clientPassword: str = ""):
        self.debug = debug
        self.index = ""
        self.style = ""
        self.login = ""
        self.password = clientPassword
        self.directory = "templates"
        self.apiKey = tmdbv3api_key
        if self.apiKey:
            self.tmdb = TMDb()
            self.tmdb.api_key = self.apiKey
            self.movie = Movie()
            self.tvApi = TV()
        else:
            self.tmdb = None
            self.movie = None
            self.tvApi = None
        
    def homeFile(self, filename: str = "index.html", directory: str = "templates"):
        self.index = filename
        self.directory = directory
        return self.index, self.directory
    
    def loginFile(self, filename: str = "login.html", directory: str = "templates"):
        self.login = filename
        self.directory = directory
        return self.login, self.directory
    
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
        if not self.movie:
            return {"length": "Unknown", "release": "Unknown", "poster": "", "overview": "", "genre": "Unknown"}
        try:
            results = self.movie.search(title)
            result = results[0]
            details = self.movie.details(result.id)
            posterUrl = f"https://image.tmdb.org/t/p/w500{details.poster_path}" if details.poster_path else ""
            genres = ", ".join([g.name for g in details.genres]) if details.genres else "Unknown"
            return {"length": self.secondsToTime(details.runtime * 60) if details.runtime else "Unknown", "release": details.release_date, "poster": posterUrl, "overview": details.overview, "genre": genres}
        except Exception as e:
            print(e)
            return {"length": "Unknown", "release": "Unknown", "poster": "", "overview": "", "genre": "Unknown"}
        
    def getTVInformation(self, title: str, season: int, episode: int):
        if not self.tvApi:
            return {"length": "Unknown", "release": "Unknown", "poster": "", "overview": "", "genre": "Unknown", "season": season, "episode": episode}
        try:
            results = self.tvApi.search(title)
            result = results[0]
            details = self.tvApi.details(result.id)
            posterUrl = f"https://image.tmdb.org/t/p/w500{details.poster_path}" if details.poster_path else ""
            genres = ", ".join([g.name for g in details.genres]) if details.genres else "Unknown"
            try:
                epDetails = self.tvApi.episode(result.id, season, episode)
                runtime = epDetails.runtime if epDetails.runtime else None
                epOverview = epDetails.overview if epDetails.overview else details.overview
                airDate = epDetails.air_date if epDetails.air_date else details.first_air_date
            except Exception:
                runtime = None
                epOverview = details.overview
                airDate = details.first_air_date
            return {"length": self.secondsToTime(runtime * 60) if runtime else "Unknown", "release": airDate, "poster": posterUrl, "overview": epOverview, "genre": genres, "season": season, "episode": episode}
        except Exception as e:
            print(e)
            return {"length": "Unknown", "release": "Unknown", "poster": "", "overview": "", "genre": "Unknown", "season": season, "episode": episode}
    
    def getMovies(self, dist: str = "movies.json"):
        with open(os.path.join(os.getcwd(), dist), "r") as f:
            movies = json.load(f)
        return [{"title": m["title"], "poster": m.get("poster", "")} for m in movies]

    def getTVShows(self, dist: str = "tv.json"):
        with open(os.path.join(os.getcwd(), dist), "r") as f:
            tvShows = json.load(f)
        return [{"title": s["title"], "poster": s.get("poster", "")} for s in tvShows]
    
    def loadMovie(self, title: str, dist: str = "movies.json"):
        with open(os.path.join(os.getcwd(), dist), "r") as f:
            movies = json.load(f)
        for movie in movies:
            if movie["title"] == title:
                return movie
        return None
    
    def loadTVShow(self, title: str, dist: str = "tv.json"):
        with open(os.path.join(os.getcwd(), dist), "r") as f:
            tvShows = json.load(f)
        for show in tvShows:
            if show["title"] == title:
                return show
        return None

    def loadTVShowEpisodes(self, title: str, dist: str = "tv.json"):
        with open(os.path.join(os.getcwd(), dist), "r") as f:
            tvShows = json.load(f)
        seasons = {}
        for show in tvShows:
            if show["title"] != title:
                continue
            s = show["season"]
            if s not in seasons:
                seasons[s] = []
            seasons[s].append(show["episode"])
        return {s: sorted(eps) for s, eps in sorted(seasons.items())}
    
    def addMovie(self, filename: str, title: str = "Unknown", date: str = "Unknown"):
        shutil.move(filename, os.path.join(os.getcwd(), "media/movies", filename))
        with open(os.path.join(os.getcwd(), "movies.json"), "r") as f:
            movies = json.load(f)
        info = self.getMovieInformation(title) if self.movie else {"length": "Unknown", "release": date or "Unknown", "poster": "", "overview": "", "genre": "Unknown"}
        movies.append({"title": title, "filename": filename, "release": info.get("release", date), "poster": info.get("poster", ""), "overview": info.get("overview", ""), "genre": info.get("genre", "Unknown"), "length": info.get("length", "Unknown")})
        with open(os.path.join(os.getcwd(), "movies.json"), "w") as f:
            json.dump(movies, f)
        return "Added"

    def addTVShow(self, filename: str, title: str = "Unknown", date: str = "Unknown", season: int = 1, episode: int = 1):
        shutil.move(filename, os.path.join(os.getcwd(), "media/tv", filename))
        with open(os.path.join(os.getcwd(), "tv.json"), "r") as f:
            shows = json.load(f)
        info = self.getTVInformation(title, season, episode) if self.tvApi else {"length": "Unknown", "release": date or "Unknown", "poster": "", "overview": "", "genre": "Unknown"}
        shows.append({"title": title, "filename": filename, "season": season, "episode": episode, "release": date, "poster": info.get("poster", ""), "overview": info.get("overview", ""), "genre": info.get("genre", "Unknown"), "length": info.get("length", "Unknown")})
        with open(os.path.join(os.getcwd(), "tv.json"), "w") as f:
            json.dump(shows, f)
        return "Added"
    
    def run(self, host: str = "127.0.0.1", port: int = 5000, useHTTPS: bool = False):
        app = flask.Flask(__name__, template_folder=os.path.join(os.getcwd(), self.directory), static_folder=os.path.join(os.getcwd(), "static"))
        app.secret_key = os.urandom(128)
        
        def checkAuth():
            if self.password and not flask.session.get("auth"):
                return flask.redirect("/")
            return None

        @app.route("/", methods=["GET", "POST"])
        def index():
            if not self.password or flask.session.get("auth"):
                movies = self.getMovies()
                shows = self.getTVShows()
                return flask.render_template(self.index, movies=movies, shows=shows)
            return flask.render_template(self.login)

        @app.route("/login", methods=["POST"])
        def login():
            if flask.request.form.get("passwd") == self.password:
                flask.session["auth"] = True
                return flask.redirect("/index")
            return flask.render_template(self.login, error="Incorrect password")
        
        @app.route("/index", methods=["GET", "POST"])
        def home():
            if redir := checkAuth(): return redir
            movies = self.getMovies()
            shows = self.getTVShows()
            return flask.render_template(self.index, movies=movies, shows=shows)
        
        @app.route("/search", methods=["GET", "POST"])
        def search():
            if redir := checkAuth(): return redir
            searchTerm = flask.request.args.get("q", "")
            movies = self.getMovies()
            shows = self.getTVShows()
            searchResults = []
            for movie in movies:
                if searchTerm.lower() in movie["title"].lower():
                    searchResults.append({"title": movie["title"], "poster": movie.get("poster", "")})
            for show in shows:
                if searchTerm.lower() in show["title"].lower():
                    searchResults.append({"title": show["title"], "poster": show.get("poster", "")})
            return flask.render_template("search.html", search_results=searchResults)
        
        @app.route("/addMedia", methods=["GET", "POST"])
        def addMedia():
            if redir := checkAuth(): return redir
            return flask.render_template("addMedia.html")
        
        @app.route("/upload", methods=["POST"])
        def upload():
            if redir := checkAuth(): return redir
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
        
        @app.route("/info/<title>", methods=["GET", "POST"])
        def info(title):
            if redir := checkAuth(): return redir
            movieInfo = self.loadMovie(title)
            if not movieInfo:
                tvInfo = self.loadTVShow(title)
                if not tvInfo:
                    return "Not found", 404
                seasons = self.loadTVShowEpisodes(title)
                firstSeason = min(seasons.keys())
                firstEpisode = seasons[firstSeason][0]
                return flask.redirect(f"/info/{title}/{firstSeason}/{firstEpisode}")
            else:
                metadata = self.getMovieInformation(movieInfo["title"])
                return flask.render_template(self.info, title=movieInfo["title"], description=movieInfo.get("overview") or metadata.get("overview", "Unknown"), genre=movieInfo.get("genre", "Unknown"), time=metadata["length"], release=metadata["release"], poster=movieInfo.get("poster", ""))
        
        @app.route("/info/<tvShow>/<int:season>/<int:episode>", methods=["GET", "POST"])
        def infoTV(tvShow, season, episode):
            if redir := checkAuth(): return redir
            tvInfo = self.loadTVShow(tvShow)
            if not tvInfo:
                return "TV show not found", 404
            metadata = self.getTVInformation(tvInfo["title"], season, episode)
            seasons = self.loadTVShowEpisodes(tvInfo["title"])
            return flask.render_template("infoTV.html", title=tvInfo["title"], description=tvInfo.get("overview") or metadata.get("overview", "Unknown"), genre=metadata.get("genre", "Unknown"), time=metadata["length"], release=metadata["release"], season=season, episode=episode, seasons=seasons, poster=tvInfo.get("poster", ""))
        
        @app.route("/player/<title>", methods=["GET", "POST"])
        def player(title):
            if redir := checkAuth(): return redir
            movieInfo = self.loadMovie(title)
            if movieInfo:
                return flask.render_template("player.html", title=movieInfo["title"], filename=os.path.basename(movieInfo["filename"]))
            tvInfo = self.loadTVShow(title)
            if tvInfo:
                return flask.redirect(f"/player/{title}/{tvInfo['season']}/{tvInfo['episode']}")
            return "Not found", 404

        @app.route("/player/<tvShow>/<int:season>/<int:episode>", methods=["GET", "POST"])
        def playerTV(tvShow, season, episode):
            if redir := checkAuth(): return redir
            tvInfo = self.loadTVShow(tvShow)
            if not tvInfo:
                return "TV show not found", 404
            return flask.render_template("player.html", title=tvInfo["title"], filename=os.path.basename(tvInfo["filename"]), season=season, episode=episode)

        @app.route("/media/<path:filename>")
        def media(filename):
            if redir := checkAuth(): return redir
            for jsonFile in ["movies.json", "tv.json"]:
                mediaList = json.load(open(os.path.join(os.getcwd(), jsonFile)))
                for m in mediaList:
                    if os.path.basename(m["filename"]) == filename:
                        return flask.send_from_directory(os.path.dirname(m["filename"]), filename)
            return flask.send_from_directory(os.path.join(os.getcwd(), "media"), filename)
        
        if useHTTPS == True:
            app.run(host=host, port=port, debug=self.debug, ssl_context="adhoc")
        else:
            app.run(host=host, port=port, debug=self.debug)