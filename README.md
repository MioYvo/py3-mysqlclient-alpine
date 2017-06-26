# py3-mysqlclient-alpine

Install python3 mysql driver [mysqlclient](https://github.com/PyMySQL/mysqlclient-python) on alpine linux.


* Total Size: **101 MB**
  * Based image: `python:3.6.1-alpine`(**88.7 MB**)
* Why mysqlclient ? [Answers on stackoverflow](https://stackoverflow.com/questions/4960048/python-3-and-mysql)


## Usage

First, a mariadb container named **my-mariadb** is running.

```bash
>> docker ps 
d627912ec946        mariadb             "docker-entrypoint..."   6 days ago          Up 6 days           0.0.0.0:3306->3306/tcp                                                          my-mariadb
```

Run this mysqlclient driver linked with **my-mariadb**

```bash
docker run -it --link my-mariadb:mysql py3-mysqlclient-alpine python

Python 3.6.1 (default, Jun 19 2017, 23:58:41)
[GCC 5.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import MySQLdb
>>> MySQLdb.connect(host="mysql", user="YOUR USER", passwd="YOUR PASSWORD", db="YOUR DATABASE NAME")
<_mysql.connection open to 'mysql' at 55f032a2bbb8>

```

* For more info about `--link`, click https://docs.docker.com/engine/userguide/networking/default_network/dockerlinks/#communication-across-links
* Some examples about MySQLdb https://github.com/PyMySQL/mysqlclient-python/blob/master/doc/user_guide.rst#some-examples

In most cases, you will build your own image based on this.
