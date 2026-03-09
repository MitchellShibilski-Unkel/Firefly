# 🔥 Firefly (Alpha Version)
**Alpha v1.0**
A self-hosted media server for movies and TV shows, built with Python and Flask.

---

## Features
- Browse and stream movies and TV shows from your local library
- TMDB integration for automatic metadata
- Upload media directly through the web UI
- Search across your entire media library
- Glassmorphism UI

---

## Requirements
- Python 3.8+
- Flask
- tmdbv3api

Install dependencies:
```bash
pip install flask tmdbv3api
```

---

## TMDB API Key
Firefly optionally integrates with [The Movie Database (TMDB)](https://developer.themoviedb.org/docs/getting-started) to fetch movie metadata.

To enable it, generate an API key from the link above and pass it into the `Firefly` constructor.

---

## Usage

```python
from Firefly.firefly import Firefly

ff = Firefly(debug=True, tmdbv3api_key="YOUR_API_KEY")

ff.homeFile(filename="index.html", directory="templates")
ff.infoPage(filename="info.html", directory="templates")

ff.run()
```

By default the server runs at `http://127.0.0.1:5000`.

---

## Project Structure
```
├── Firefly/
│   └── firefly.py        # Core Firefly class
├── templates/
│   ├── index.html        # Home page
│   ├── info.html         # Movie/show info page
│   ├── player.html       # Video player
│   ├── search.html       # Search results
│   └── addMedia.html     # Upload form
├── static/
│   └── style.css         # Glassmorphism styles
├── media/
│   ├── movies/           # Movie files
│   └── tv/               # TV show files
├── movies.json           # Movie library data
├── tv.json               # TV show library data
└── test.py               # Example usage
```

---

## API Reference

### `Firefly(debug, tmdbv3api_key)`
| Param | Type | Default | Description |
|---|---|---|---|
| `debug` | `bool` | `False` | Enables Flask debug mode |
| `tmdbv3api_key` | `str` | `""` | TMDB API key for metadata fetching |

### `ff.run(host, port)`
Starts the Flask server.
| Param | Type | Default |
|---|---|---|
| `host` | `str` | `"127.0.0.1"` |
| `port` | `int` | `5000` |

### `ff.addMovie(filename, title, date)`
Manually add a movie to the library.

### `ff.addTVShow(filename, title, date, season, episode)`
Manually add a TV episode to the library.

---

## Routes
| Route | Description |
|---|---|
| `/` | Home page |
| `/search?q=` | Search results |
| `/info/<title>` | Movie/show detail page |
| `/player/<title>` | Video player |
| `/addMedia` | Upload form |
| `/upload` | Upload handler (POST) |
| `/media/<filename>` | Serves media files |

---

## License
MIT — see [LICENSE](LICENSE)