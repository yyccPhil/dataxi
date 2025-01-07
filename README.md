# Dataxi

Dataxi is a cross-DBMS server tool based on Polars with credential management that can help you centralize the data extraction and transfer from different data sources.

## Highlights

* Supports multiple data sources: MySQL, SQL Server, ClickHouse, Splunk
* Supports data parsing from multiple formats: pandas, CSV, XLSX, and Parquet
* Offers credential management with easy access using `conn_id`
* Works on Linux/MacOS/Windows

## Install

The preferred way to install Dataxi is via pip

```sh
pip install dataxi
```

## Basic Usage

### Credential Management

Initialize the SaveSecret helper to manage your credentials. This will create a hidden .dataxi folder in your $HOME directory to securely store credentials.

```python
from dataxi import SaveSecret

secret_helper = SaveSecret()
```

Use the save_secret() function to store new credentials. The parameters conn_id, user, and password are mandatory. You can also use this to store non-database credentials if you'd like.

```python
# For db_type, choose one of the following: mysql, mssql/sql_server, clickhouse/ch
secret_helper.save_secret(conn_id='mymysql', user='test_user', password='test_pw', db_type='mysql', host='test.net', port='3306', database='test_db')

# Save non-database credentials
secret_helper.save_secret(conn_id='test',user='yyccPhil',password='test_pw')
```

Display all saved conn_ids, similar to how pip list works. This is helpful for quickly identifying available credentials.

```python
secret_helper.list_conn_id()
```

Easily remove credentials you no longer need by specifying their conn_id.

```python
secret_helper.delete_secret(conn_id='mymysql')
```

Print the details of a stored credential using its conn_id.

```python
secret_helper.load_secret(conn_id='test')

# Print all stored credentials
secret_helper.load_secret(all=1)
```

**(Warning: This action is irreversible!)** Use reset_secret() to clear all stored credentials in the .dataxi folder.

```python
secret_helper.reset_secret()
```

**(Warning: This action is irreversible!)** Use clean_secret_folder() to completely remove the .dataxi folder.

```python
secret_helper.clean_secret_folder()
```

## License

Copyright 2024-2025 Yuan Yuan.

Distributed under the terms of the  [MIT license](https://github.com/yyccPhil/dataxi/blob/main/LICENSE).