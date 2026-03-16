import os
from Firefly.firefly import Firefly
from dotenv import load_dotenv

load_dotenv()

ff = Firefly(debug=True, tmdbv3api_key=os.getenv("API_KEY"), clientPassword="1234")

ff.homeFile(filename="index.html", directory="templates")
ff.infoPage(filename="info.html", directory="templates")
ff.loginFile(filename="login.html", directory="templates")

ff.run(host="0.0.0.0", port="5000")