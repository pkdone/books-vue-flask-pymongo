FROM nginx

RUN set -x \
    && apt-get update -y \
    && apt-get install -y \
        python3  \
        python3-pip \
    && apt-get autoremove \
    && apt-get autoclean \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install --user \
        pymongo \
        dnspython \
        python-dotenv \
        Flask \
        Flask-Cors \
        gunicorn \
    && rm -rf /root/.cache/pip

RUN echo "proxy_set_header Host \$http_host;\n\
proxy_set_header X-Real-IP \$remote_addr;\n\
proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;\n\
proxy_set_header X-Forwarded-Proto \$scheme;" > /etc/nginx/proxy_params

RUN echo "server {\n\
    listen      5000;\n\
    server_name localhost;\n\
    charset utf-8;\n\
    root    /usr/share/nginx/html;\n\
    index   index.html index.htm;\n\    
    location /books {\n\
        include proxy_params;\n\
        proxy_pass http://unix:/booksnginxgunicorn.sock;\n\
    }\n\        
    location / {\n\
        root /usr/share/nginx/html;\n\
        try_files \$uri /index.html;\n\
    }\n\
}" > /etc/nginx/conf.d/default.conf

RUN echo "FLASK_ENV=\"production\"\n\
MONGODB_URL=\"mongodb://172.17.0.1:27017\"" > /.env

RUN echo "#!/bin/bash\n\
set -e\n\
\n\
if [ -z \"\$MONGODB_URL\" ]; then\n\
  echo \"WARNING - environment variable MONGODB_URL not specified - using a default MongoDB URL of mongodb://172.17.0.1:27017 which may not exist or may not be accessible\"\n\
else\n\
  echo \"Using the MongoDB URL of: \$MONGODB_URL\"\n\
fi\n\
\n\
if [ -z \"\$WORKER_PROCESSES\" ]; then\n\
  WORKER_PROCESSES=4\n\
fi\n\
\n\
  echo \"Starting Gunicorn with \$WORKER_PROCESSES worker processes\"\n\
\n\
/root/.local/bin/gunicorn --workers \$WORKER_PROCESSES --threads 2 --bind unix:booksnginxgunicorn.sock -m 000 BooksRestApp:app &\n\
/usr/sbin/nginx -g \"daemon off;\"" > /docker-entrypoint.sh \
    && chmod u+x /docker-entrypoint.sh

COPY client-tier/dist /usr/share/nginx/html

COPY app-tier/BooksRestApp.py /BooksRestApp.py

COPY app-tier/BooksMgr.py /BooksMgr.py

ENTRYPOINT ["/docker-entrypoint.sh"]

EXPOSE 5000

