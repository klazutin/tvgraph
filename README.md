# TV Graph

![Screenshot](http://lazut.in/img/github-tvgraph.png)

A clone of [Graph TV](http://graphtv.kevinformatics.com/) built for educational purposes.
Built with [Hug](http://www.hug.rest/), MongoDB, Beautiful Soup and Highcharts.

A couple of improvements over the original:
- Relies on live scraping of IMDB pages to get the most current ratings.
- Less dependencies (no jQuery, Bootstrap, etc.).

To run:
The easiest way to run locally is to use hug's built-in development server by running `hug -f ./app.py`.
Running in production involves setting up a uWSGI server for which `uwsgi.ini` is included.
Initial configuration of the Mongo database can be achieved by running `mongo < mongo.js`.

TODO:
- Add list of recently viewed shows.
