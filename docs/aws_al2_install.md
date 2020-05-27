# Very rough notes for installing on an AWS EC2 Amazon Linux 2 instance

__IMPORTANT__: Follow the main project [README.md](../README.md) for a guide of what is being installed/configured and why. The document here is just a short-cut set of steps for those who are already famililar with standing up and running the project.


## EC2 Instance Creation

Via the AWS Console:
* Create an Amazon Linux 2 based EC2 instance (e.g. _m4.2xlarge_ with 8 cores & 32 GB RAM) and for the __Security Group__ open up __inbound__ for __SSH__ + __Custom TCP Port 8080__ + __Custom TCP 5000__
* Add the EC2 instance's public IP address to Atlas project's __whitelist__


## EC2 Instance Setup

SSH to EC2 instance

Run:
```bash
sudo yum update
sudo yum install python3 
sudo amazon-linux-extras install "nginx1.12"
sudo vi /etc/yum.repos.d/mongodb-org-4.2.repo
```

Enter this content & save:
```bash
[mongodb-org-4.2]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/amazon/2/mongodb-org/4.2/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-4.2.asc
```

Run:
```bash
sudo yum install -y mongodb-org-shell
curl -sL https://rpm.nodesource.com/setup_10.x | sudo bash -
sudo yum install nodejs
node --version
npm --version
pip3 install --user pymongo dnspython python-dotenv Flask Flask-Cors gunicorn
sudo npm install -g @vue/cli
wget https://codeload.github.com/pkdone/books-vue-flask-pymongo/zip/master
unzip master
rm master
cd books-vue-flask-pymongo-master
mongo mongodb+srv://main_user:pwd@cluster-abcde.mongodb.net/ rawdata/book-data-to-insert.js
```


## DEVELOPMENT configuration

Run:
```bash
vi app-tier/.env
```

Enter this content & save (changing the MongoDB URL accordingly):
```bash
FLASK_ENV="development"
MONGODB_URL="mongodb+srv://main_user:pwd@cluster-abcde.mongodb.net/"
```

Run:
```bash
cd app-tier
./BooksRestApp.py
```


SSH another session to EC2 instance

Run:
```bash
cd client-tier
vi .env.development.local
```

Enter this content & save (swapping shown IP address for the external IP address of the EC2 instance):
```bash
VUE_APP_REST_API_LOCATION=http://63.32.60.16:5000
```

Run:
```bash
npm install
npm run serve
```

In a browser test the 2 links:
* http://63.32.60.16:5000/books
* http://63.32.60.16:8080/

Stop Flask/Python app

Run:
```bash
gunicorn --reload --workers 4 --bind 0.0.0.0:5000 BooksRestApp:app
```

In the browser test the 2 links again:
* http://63.32.60.16:5000/books
* http://63.32.60.16:8080/

Stop Gunicorn app and Node.js app


## PRODUCTION configuration

Run:
```bash
sudo mkdir /var/www-data
sudo chmod a+wrx /var/www-data
vi app-tier/.env
```

Enter this content & save (changing the MongoDB URL accordingly):
```bash
FLASK_ENV="production"
MONGODB_URL="mongodb+srv://main_user:pwd@cluster-abcde.mongodb.net/"
```

Run:
```bash
cd client-tier
vi .env.production.local
```

Enter this content & save (swapping shown IP address for the external IP address of the EC2 instance):
```bash
VUE_APP_REST_API_LOCATION=http://63.32.60.16:5000
```

Run:
```bash
npm run build
cp -r dist /var/www-data/
sudo vi /etc/systemd/system/gunicorn-flask-books.service
```

Enter this content & save
```bash
[Unit]
Description=Gunicorn instance to serve books Flask Python project
After=network.target

[Service]
User=ec2-user
Group=nginx
WorkingDirectory=/home/ec2-user/books-vue-flask-pymongo-master/app-tier
Environment="PATH=/home/ec2-user/.local/bin"
ExecStart=/home/ec2-user/.local/bin/gunicorn --workers 4 --threads 2 --bind unix:/var/www-data/booksnginxgunicorn.sock -m 007 BooksRestApp:app

[Install]
WantedBy=multi-user.target
```

Run:
```bash
sudo systemctl daemon-reload
sudo systemctl start gunicorn-flask-books
sudo systemctl status -l gunicorn-flask-books
journalctl -u gunicorn-flask-books
sudo systemctl enable gunicorn-flask-books
sudo vi /etc/nginx/conf.d/default.conf
```


Enter this content & save
```bash
server {
    listen      5000;
    server_name localhost;
    charset utf-8;
    root    /var/www-data/dist;
    index   index.html index.htm;
    location /books {
        include proxy_params;
        proxy_pass http://unix:/var/www-data/booksnginxgunicorn.sock;
    }
    location / {
        root /var/www-data/dist;
        try_files $uri /index.html;
    }
}
```

Run:
```bash
sudo vi /etc/nginx/proxy_params
```

Enter this content & save
```bash
proxy_set_header Host $http_host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

Run:
```bash
sudo nginx -t
sudo service nginx restart
sudo service nginx status -l
sudo tail /var/log/nginx/error.log
sudo tail /var/log/nginx/access.log
```

In a browser test the 2 links:
* http://63.32.60.16:5000/books
* http://63.32.60.16:5000/

