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
password = hurrdurr

[app]
ip=localhost
port=hurrdurr
```

# Starting up a database

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

## Testing the database
Then run
```
python test.py
```
and it should work without problems.


# Readme and user manual for AI prediction

This guide aims to guide users and developers on how various aspects of the program functions and goes into more details in how specific functions operate. This guide is aimed at a broad audience while including technical information. 

## How to run the program:

Please follow the appropriate subtitle regarding which steps to follow.

### Docker version:

- Start...

**The following steps need to be done before the program can begin detecting anomalies.** 

## Database:

### Config.ini

Create a config.ini file in the root directory with this content

```

[mysql]

host = [localhost](http://localhost) #exchange this if the database is not localy hosted. 

database = python_mysql #exchange this with your own database

user = root #exchange this with your own username

password = password #exchange this with your own password

[app]

ip=localhost #exchange this with the appropriate ip. 

port=port #exchange this with the appropriate port

```

### Starting up a database

You can test-run the `database.py` file if you start up a mysql docker container and run the file. # No you can't

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

### Upload data to database

Run `wsgy.py`(http://app.py) in terminal by typing:

```
python wsgy.py
```

in the terminal you should see that that the webserver is running.

Open your webbrowser of choice and go to:

```
localhost:1234
```

in order to open app. 

Press the upload button and select a file for upload.

# Technical requirements:

These requirements are included in the docker image.

* **Python**

This program requires python 3.8.3 as of the time or the latest version that is supported by Tensorflow.

* **Coverage - For testing purposes**

To check test coverage. 

* **MySQL**

For database of the MySQL type.

* **MySQL Connector for python**

Interacting with database via Python.

* **Pip Chill** 

Not needed?

* **Seaborn** 

For plotting purposes

* **SKLearn**

For AI part.

* **Cycler**

Part of Matplotlib

* **Flask**

For web app

* **Tensorflow**

For AI model. 

These requirements can be installed by typing in the terminal:

```
pip install -r requirements.txt
```

# Testing:

## Testing the database

Then run

```

python run_tests.py

```

and it should work without problems.


# Database API

## API Functions
* create_sql_connection : `(filename, section)` &#8594; (my_db, db_config)
* create_table : `(cursor, table_name, column_dictionary)` &#8594; None
* show_databases : `()` &#8594; None
* show_tables : `(cursor)` &#8594; `result`
* drop_table : `(cursor, table_name)` &#8594; None
* insert_data : `(cursor, table_name, column_dictionary, limit_offset, limit_row_count)` &#8594; None
* get_data : `(cursor, table_name, column_dictionary, order_by, order_by_asc_desc)` &#8594; `Queried_Data`
* delete_data : `(cursor, table_name, column_dictionary)` &#8594; None
* edit_data : `(cursor, table_name, column_dictionary, column_dictionary)` &#8594; None

## Variables

### filename and section

The `filename` parameter in function `create_sql_connection` shall point to the `config.ini` file used to connect to the database, and the `section` parameter shall point to the section where the MySQL configuration is located.

### cursor

The `cursor` parameter is a MySQLConnection cursor instance that you can get by calling `my_db.cursor()` after having connected to the database using `create_sql_connection()`.

### table_name

A python string representing the name of the table you want to access.

### Queried_Data
A list of tuples where each tuple is representing the MySQL database row queried for. This list can include more than one item.

### column_dictionary

A column_dictionary is a python dictionary that indicates which column should receive which value in the database. An example of a column dictionary would be:
```
{
    'name':'cogitel',
    'age':420
}
```
where the column `name` will receive the value `'cogitel'` and column `age` will receive the value `420`. Note that the user must know beforehand the names of the columns except in the function `create_table` where the table itself is created. create_table also uses a specific `column dictionary` style where it's a `column-name-to-column-type` mapping instead, such as:
```
{
    'id':'INTEGER(6) AUTOINCREMENT',
    'name':'VARCHAR(255)',
    'age':'INTEGER(6)'
}
```

### result

A python list of strings of all table names in the database.

### order_by and order_by_asc_desc

Whether to order the query in any specific manner. 
* order_by: list[str] specifices which columns to order by.
* order_by_asc_desc: 'ASC' for ascending or 'DESC' for descending.

### limit_offset and limit_row_count

Whether or not the SQL query should limit its length.
* limit_offset: int specifies the offset in the starting row.
* limit_row_count: int specifies the maximum number of rows it should return.

## Functions

### create_sql_connection

Creates a MySQLConnection instance connected to the database

### create_table

Creates a table in the database with the name `table_name` built on the data in `column_dictionary`.

### show_databases

Prints all database names in the terminal.

### show_databases

Returns a list of strings containing all available tables in the database.

### drop_table

Removes `table_name` from the database.

### insert_data

Inserts a datapoint in `table_name`. The datapoint needs to be formatted with a columnname-columnvalue mapping.

### get_data

Returns queryied data in the form of a list of tuples where each tuple is a row in the database.  

### delete_data

Deletes a datapoint in `table_name` matching the criteria in `column_dictionary`.

### edit_data

Edits the datapoint with id `id` in the database using the data in `column_dictionary`

# Backend API

## Backend functions
* delete_table `(table_name)` &#8594; None
* import_data_json `(path_to_file, database_table, **kwargs)` &#8594; None
* import_data_csv `(path_to_file, database_table, **kwargs)` &#8594; None
* export_data_json `(path_to_file, database_table, **kwargs)` &#8594; None
* export_data_csv `(path_to_file, database_table, **kwargs)` &#8594; None
* add_dict_to_database `(data_dict, database_table, date_col=None, **kwargs)` &#8594; None
* get_tables: &#8594; `tables`
* get_all_data `(table_name, convert_datetime)` &#8594; None
* edit_classification `(id)` &#8594; None
* train_ai `(table_name, target_column='sensor1')` &#8594; None

## Variables

### table_name and database_table

A python string representing the name of the table you want to access.

### data_dict

A python dictionry containing the data from the import functions

### target_columns

A python list of strings representing the names of the columns you want to train the AI to predict.

### convert_datetime

A python bolean representing if you want to convert dates into DateTime objects;
* `True`: Yes to conversion
* `False`: No to conversion (Default)

### id

A python integer representing the row you want to access in the database.

### tables

A python list of strings containing the names of all tables available in the database

### Constants
#### DATETIME_COLUMN_NAME = 'date'

A python string representing the name of the column considered the column containing the date data. Default: `date`

#### CLASSIFICATION_COLUMN_NAME = 'classification'

A python string representing the name of the column considered the column containing the classification data. Default: `classification`

#### PREDICTION_COLUMN_NAME = 'prediction'

A python string representing the name of the column considered the column containing the prediction data. Default: `prediction`

#### ID_COLUMN_NAME = 'id'

A python string representing the name of the column considered the column containing the id data. Default: `id`

## Functions

### delete_table

Deletes `table_name` from the database.

### import_data_json

Imports a data file of the `.json` format, sending it to be added to the database. 

### import_data_csv

Imports a data file of the `.csv` format, sending it to be added to the database. 

### export_data_json

Exports a data file of the `.json` format, putting it into `path_to_file`. 

### export_data_csv

Exports a data file of the `.csv` format, putting it into `path_to_file`. 

### add_dict_to_database

Adds a python dictionary to `database_table`. If `database_table` does not exist, it is created using the data in `data_dict`. If it does exist, the columns and data types of `data_dict` must match with the data in `database_table`

### get_tables

Returns a list of strings containing the names of all tables in the database.

### get_all_data

Returns all data in `table_name`, with the option to convert the data from the `date` column into `datetime` objects.

### edit_classification

Edits the classification whose row id is `id`.

### train_ai

Trains a new AI model.

# AI

## AI Functions
* load_ai_model `(load_ai_path)`: `model`, `INPUT_WIDTH`, `SHIFT`, `LABEL_WIDTH` &#8594;
* train_ai `(model, train_data, validation_data, patience = 2, max_epochs = 5)`: &#8594; None
* run_ai `(model, input_list, shift = 1, label_width = 1, lower_sensitivity = 1.5, upper_sensitivity = 1.5, verbose = 0)`:  &#8594; `output_array`, `anomaly`
* create_window `(df, input_width=6, label_width=1, shift=1, label_columns=['values'])`: `w2` &#8594;

## Variables

### load_ai_path

A python string representing the file path to where the Ai is loaded from.

### model

A Tensorflow AI model object.

### train_data

Training data connected to the window object.

### validation_data

Validation data connected to the window object.

### patience

A python integer representing how many epochs to allow the training to proceed in spite of val-loss decreasing. Default: `2`

### max_epochs

A python integer representing the maximum amount of epochs the Ai model will be trained with. Default: `5`

### input_list

A list of lists containting the input to be predicted on. Each nestled list is a datapoint. `input_list` needs to be at least `INPUT_WIDTH` * `SHIFT` long, where the last datapoint is the one being predicted upon and tested for anomalies.

### shift

A python integer representing how many datapoints ahead the prediction will be. Default: `1`

### label_width

A python integer representing how many redictions the AI will do at a time. Default: `1`

### lower_sensitivity

A python float representing the lower definition of accepted values. Default: `1.5`

### upper_sensitivity

A python float representing the upper definition of accepted values. Default: `1.5`

### verbose

Debugging variable; 
* If `1`: print debugging info
* If `0`: do not print debugging info

### df

A pandas dataframe that will be turned into training and validation data for the AI model to train on.

### input_width

A python integer representing the amountsd of inputs the AI model will accept when predicting and test for anomalies. Default: `6`

### label_columns

A python list containing the names of the columns that will be predicted upon.

### output_array

A python list containing the values the AI predicted, shifted according to the AI's `shift` value.

### anomaly

A python list containing wether the datapoints are anomalies or not. Each prediction is either a `0` or a `1`;
* `0`: Datapoint is not an anomaly
* `1`: Datapoint is an anomaly

### w2

A `window` object contining a training, a validation and a test dataset for the AI train on.

## Functions

### load_ai_model

Loads a saved AI model.

### train_ai

Trains a new AI model.

### run_ai

Runs the selected AI model and returns a list of predicitons and anomnaly check results.

### create_window

Creates a `window` object containing training, a validation and a test dataset for the AI train on.