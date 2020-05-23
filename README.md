# Introduction

An example full stack application which displays a sample set of books related to [Post-Apocalyptic fiction](https://en.wikipedia.org/wiki/Apocalyptic_and_post-apocalyptic_fiction) and enables these to be edit.

 ![Books App User Interface](img/appui.png)

### Main Goals

* Provide an example of an easy way to develop a full stack application, without needing to use JavaScript to develop the app-tier logic or needing to leverage Node.js to run it in Production, for developers who prefer using Python. 
* Enable the app-tier to be scalable, with a simple non-invasive way of leveraging multiple host server processes, without being constrained by Python's Global Interpreter Lock (GIL), in a way that enables the developer to just focus on writing normal Python code.
* Host the data-tier on a [MongoDB](https://www.mongodb.com/) database for flexibility, high availability, scale and portability reasons.
* Use JavaScript in the client-tier, in the browser, to avoid server-side rendering of the user interface, to provide a more responsive and smooth user interface, realised as a Single Page Application ([SPA](https://en.wikipedia.org/wiki/Single-page_application)) and loaded into the browser as a set of static resources (bundled as a [Webpack](https://webpack.js.org/)).
 
### Application Architecture

To achieve this goal, the component stack shown in the diagram below is used, with differences between the development and production environments. The development environment allows rapid prototyping with a single instance of a Python application and an auto-checked and auto-generated web application. The production environment provides a more scalable multi-process solution with server-side JavaScript and Node.js completely eliminated from the runtime.

 ![Full Stack Architecture](img/architecture.png)

Further details on some of the components

* __[Vue.js](https://vuejs.org/)__: A JavaScript framework for building user interfaces as Single Page Applications that, in production, is served as a set of static HTML/JavaScript/PNG/CSS resource to run inside the browser requiring no server-side rendering - Node.js is used during the development phase only for to check for issues and to dynamically generate the content for quick prototyping)
* __[Flask](https://flask.palletsprojects.com/en/1.1.x/)__: A lightweight single process Python micro web framework for dynamically generating server-side rendered web applications, or, in this case APIs.
* __[Gunicorn](https://gunicorn.org/)__: A Python Web Server Gateway Interface ([WSGI](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface))  server which is able to fork and manage multiple host processes to each run single-process Python server frameworks like _Flask_. Via WSGI, integrates with common web servers like Apache and Nginx to enable those web services to proxy URL request through to the Python business logic running in each Gunicorn spawned process.
* __[Nginx](https://www.nginx.com/)__: A HTTP web server for serving static websites or, acting as a reverse proxy / load balancer, serving dynamically generated content & exposing  request/response APIs (in this project it is used to serve the static HTML files, JavaScript client-side libraries and other resources, and expose a REST API proxied through Gunicorn & Flask).

&nbsp;

# Installation

### Prerequisites/Assumptions

* A MongoDB database is [installed](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/) or running somewhere (e.g. a local single instance, a remote self-managed cluster, an [Atlas](https://www.mongodb.com/cloud/atlas) cluster in the public cloud)
* These instructions assume the host OS is Ubuntu 20.40 - most of the steps should be easily transferrable to other OSess but some changes may be required


### Software Installation

1. Install Python 3 (including its package manager, {ip), Node.js (including its package manager, npm) and Nginx:
```bash
sudo apt install python3 python3-pip nodejs npm nginx
```

2. Ensure `~/.local/bin` following is on user's path (__change__ _mainuser_ to your local user name) by editing `.bashrc` (retstart the terminal afterwards to pick up this change):
```bash
export PATH=/home/mainuser/.local/bin:$PATH
```

3. Install the system-wide required Python & Node.js libraries/tools:
```bash
pip3 install --user pymongo dnspython python-dotenv Flask Flask-Cors gunicorn
sudo npm install -g @vue/cli
```

3. Install the project-local required Python & Node.js libraries/tools (dependencies specified in the `package.json` file):
```bash
cd client-tier
npm install
```

### Database Records Creation

1. Run the following command which uses the Mongo Shell to insert a sample set of book records into the database (first __change__ the MonogDB URL to match the location of the running MongoDB database):
```bash
mongo mongodb://localhost:27017 ./book-data-to-insert.js
```

### Project Environment Configuration

__NOTE__: The _skeleton_ for this client-tier Vue.js project was originally created by running the command `vue create client-tier`. The resulting Vue.js _skeleton_ files were then modified to enable displaying and navigating books data using the Python REST APIs in the app-tier. When `vue create` was originally run, the following answers where provided to the tool's prompts (__DO NOT__ run this again as this will overwrite modified files - this is just provided for informational purposes)
 - Choose _Babel_ + _Router_ + _Linter/Formatter_
 - Use _history mode_ for router
 - Use _Airbnb_ Linter / formatter
 - Select to _Lint on save_
 - Place config in _package.json_
 - Don't select to _save as preset for future projects_


1. Edit the `.env` file in the root of the project and set the value of the `FLASK_ENV` variable to `development` and the value of the `MONGODB_URL` variable to match the location of the MongoDB database. For example: 
```bash
FLASK_ENV="development"
MONGODB_URL="mongodb://localhost:27017"
```

&nbsp;

# Running the application

Follow the __DEVELOPMENT Phase__ instructions to change and enhance the running application in development mode with easy debugging. Follow the __PRODUCTION Phase__ instructions to deploy this in a production-like way, with auto-regeneration of the client-tier rsource and debugging disabled and with the Python REST API being served from multiple server-side processes, for increased throughput and scale.

&nbsp;

### DEVELOPMENT Phase

1. Start the app-tier application which will run a single process and single threaded Flask server, in debug mode, listening on port 5000 (Flask will automatically re-load the application whenever the underlying Python code is edited and re-saved:
```bash
cd app-tier
./BooksRestApp.py
```

2. In a browser, test the Flask/Python REST API by navigating to the following URL to see if book data results are shown in response to the browser's GET API call to the REST API:
http://localhost:5000/books


3. Execute the _vue-cli-service serve_ utility for the client-tier project to run a Node.js server for dynamically generating, showing errors if any and serving the client side application assets to the browser (his is run in development mode which enables the quick turnaround of changing JavaScript/HTML/CSS code and then being able to test and debug the changes):
```bash
cd client-tier
npm run serve
```

4. In a browser, test the client-tier user interface  by navigating to:
http://localhost:8080/

5. __OPTIONAL__: Wrapping Flask with Gunicorn - this is an optional test you can do in development or alternatively don't bother and just wait to configure Gunicorn during the Production phase later. 

 * Stop the `./BooksRestApp.py` process (stopping the current flask standalone server)
 * Run the following command to start Gunicorn's which in turn will launch 4 processes each running Flask and the Python code (this uses the '--reload' parameter to still support making changes to the Python code and having the changes reloaded on the fly, to speed up development):
    ```bash
    gunicorn --reload --workers 4 --bind 0.0.0.0:5000 BooksRestApp:app
    ```
 * In a browser, check that the Python books REST API still works (now served by Gunicorn wrapping Flask) and that client user interface is still able to invoke the REST API and display the books data::

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;http://localhost:5000/books

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;http://localhost:8080/

&nbsp;

### PRODUCTION Phase

1. Stop the Flask (or Gunicorn) process that was listening on port 5000 and stop the Node.js process that was listening on port 8080.
 
2. Edit the `.env` file in the root of the project and set the value of the `FLASK_ENV` variable to `production` (this will disable CORS support to improve security), which will have the resulting effect of preventing the Node.js served development version of the client-tier app, in the browser, from being able to access the app-tier REST API. For example: 
```bash
FLASK_ENV="production-"
```

3. Generate the Webpack set of static client tier content, ready to be served by a web server in a subsequent step (by default this set of generated static resources is placed in the `dist` sub-folder of the `client-tier` folder):
```bash
npm run build
```

4. Create a configuration file for an OS service for running the Gunicorn with Flask/Python app-tier logic automatically on the host machine, by editing a new file at `/etc/systemd/system/gunicorn-flask-books.service` (__change__ every occurrence of the text _mainuser_ in the service config file to match your local OS user name, e.g. _jdoe_ and change the path field if the project's location differs):
```apache
[Unit]
Description=Gunicorn instance to serve books Flask Python project
After=network.target

[Service]
User=mainuser
Group=www-data
WorkingDirectory=/home/mainuser/books-vue-flask-pymongo/app-tier
Environment="PATH=/home/mainuser/.local/bin"
ExecStart=/home/mainuser/.local/bin/gunicorn --workers 4 --threads 3 --bind unix:booksnginxgunicorn.sock -m 000 BooksRestApp:app

[Install]
WantedBy=multi-user.target
```

5. Enable and start the Gunicorn OS service:
```bash
sudo systemctl start gunicorn-flask-books
sudo systemctl enable gunicorn-flask-books
sudo systemctl status gunicorn-flask-books
```

6. View the output of the running Gunicorn/Flask/Python REST API app-tier code:
```bash
journalctl -u gunicorn-flask-books
```

7. Disable the default site for NGinx (which listens to port 80), by removing the symbolic link:
```bash
sudo rm /etc/nginx/sites-enabled/default
```

8. Create a new Nginx site definition for port 5000 which will do two things: __1)__ Serve the Vue.js static content webpack for the root '/' URL of this site, and __2)__ Proxy HTTP requests for the URL beginning '/books' of this site to the Gunicorn/Flask/Python REST API app-tier code - edit the new file at `/etc/nginx/sites-available/books-vue-flask-pymongo` (__change__ every occurrence of the text _mainuser_ in the web server config file to match your local OS user name, e.g. _jdoe_ and change the 3 path fields if the project's location differs):
```nginx
server {
    listen      5000;
    server_name localhost;
    charset utf-8;
    root    /home/mainuser/books-vue-flask-pymongo/client-tier/dist;
    index   index.html index.htm;
    # Proxy to Books REST API App-Tier
    location /books {
        include proxy_params;
        proxy_pass http://unix:/home/mainuser/books-vue-flask-pymongo/app-tier/booksnginxgunicorn.sock;
    }
    # Server static resources from Vue HTML/CSS/PNG/JAVASCRIPT webpack Client-Tier
    location / {
        root /home/mainuser/books-vue-flask-pymongo/client-tier/dist;
        try_files $uri /index.html;
    }
    error_log  /var/log/nginx/books-vue-flask-pymongo.log;
    access_log /var/log/nginx/books-vue-flask-pymongo.log;
}
```

9. Enable and check the new Nginx site then ensure ensure Nginx is serving it:
```bash
sudo ln -s /etc/nginx/sites-available/books-vue-flask-pymongo /etc/nginx/sites-enabled/books-vue-flask-pymongo
sudo nginx -t
sudo service nginx restart
```

 * In a browser, check that the Python books REST API still works (now served by Nginx proxying to Gunicorn wrapping Flask) and that client user interface is now served as static content from the Nginx web server, now served from port 5000, and this this is able to invoke the REST API and display the books data in the browser:
 
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;http://localhost:5000/books

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;http://localhost:5000/

&nbsp;&nbsp;&nbsp;&nbsp;

# Potential TODOs For The Future

* Secure application with TLS and a Server certificate
* Load test the Gunicorn/Flask/Python REST API to determine what throughput and average response latency is achievable

