from Firefly.firefly import Firefly

ff = Firefly(debug=True, tmdbv3api_key="")

ff.homeFile(filename="index.html", directory="templates")
ff.infoPage(filename="info.html", directory="templates")

ff.run()