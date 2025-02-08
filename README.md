# Dataxi

Dataxi is a cross-DBMS server tool based on Polars with credential management that can help you centralize the data extraction and transfer from different data sources.

For detailed documentation, please refer to [Dataxi Wiki Page](https://github.com/yyccPhil/dataxi/wiki).

## Highlights

* Supports multiple data sources: ClickHouse, MySQL, PostgreSQL, SQL Server, Splunk
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

#### Command Line

Initialize to manage your credentials. This will create a hidden .dataxi folder in your $HOME directory to securely store credentials.

```sh
cred_mgr
```

<details>

<summary>
Use the <code>add</code> command to store new credential interactively. It requires a unique <code>conn_id</code>, and supports 3 credential types: Database, Secret and Token.
</summary>

You will be prompted to choose among the 3 credential types. For each type, provide the following arguments in order:

**Database**

- **db_type**: one of `mysql`, `mssql` (or `sql_server`), `clickhouse` (or `ch`), `postgresql` (or `postgres`)
- **username**
- **password**
- **host**
- **port**
- **database** (optional)

**Secret**

- **username**
- **password**

**Token**

- **token**

</details>

```sh
cred_mgr add <conn_id>
```

Display all saved conn_ids, similar to how pip list works. This is helpful for quickly identifying available credentials.

```sh
cred_mgr ls
# cred_mgr list
```

Easily remove credentials you no longer need by specifying their conn_id.

```sh
cred_mgr D <conn_id>
# cred_mgr delete <conn_id>
```

Print the details of a stored credential using its conn_id.

```sh
cred_mgr load -id <conn_id>

# Print all stored credentials
cred_mgr load -a
# cred_mgr load --all
```

**(Warning: This action is irreversible!)** Use <code>reset</code> to clear all stored credentials in the .dataxi folder.

```sh
cred_mgr reset
```

**(Warning: This action is irreversible!)** Use <code>clean</code> to completely remove the .dataxi folder.

```sh
cred_mgr clean
```

## License

Copyright 2024-2025 Yuan Yuan.

Distributed under the terms of the  [MIT license](https://github.com/yyccPhil/dataxi/blob/main/LICENSE).