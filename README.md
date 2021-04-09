# Python
This program requires python 3.8.3 as of the time or the latest version that is supported by Tensorflow.

# Demo

## Start the web
* To start the web make sure to run `demo_ai.py` with python as a normal python file instead of using Flask as a module. So `python demo/demo_ai.py` and not `python -m flask run`. 
* `Upload Data` is yet not implemented.
* The AI is now integrated with the website, however it re-trains itself every time the webserver is restarted.
* The AI has loadable and saveable weights. You'll find those weights under `demo/ai_data` named `weights.h5` and/or `weights_prel.h5`. If `weights.h5` exists it will attempt to use those weights, otherwise it will retrain itself and save the weights as `weights_prel.h5`. It is your job as a user to change the name to `weights.h5` in order to make sure they're used the next time the server restarts.

## Config.ini

Create a config.ini file in the root directory with this content
```
[mysql]
host = localhost
database = python_mysql
user = root
password =
```

## Test with a docker container

You can test-run the `database.py` file if you start up a mysql docker container and run the file. 

Pull the mysql docker image with 

```
docker pull mysql
```

Run the docker image with 

```
docker run --name mysql -e MYSQL_ROOT_PASSWORD=123 -d -p 3306:3306 mysql:latest
```

Let this be your config.ini file
```
[mysql]
host = localhost
database = mysql
user = root
password = 123
```

Then run
```
python ./database/database_test.py
```
and it should work without problems.