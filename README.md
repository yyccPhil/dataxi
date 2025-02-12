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

The `creg_mgr` CLI allows secure creation, retrieval, and deletion of credentials through simple and user-friendly commands, while also providing a built-in password generator and a burn-after-reading secret-sending feature via the [Onetime Secret](https://docs.onetimesecret.com/docs/rest-api) API.

> Note: When entering string parameters (like `--conn_id`/`-id` in cred_mgr) in the CLI, it is highly recommended to enclose the value in **quotes** (like `-id 'test@id#1'`), especially if it contains special characters (such as `!`, `@`, `#`, `$`, `%`, `^`, `&`, and `*`).

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

<details>

<summary>
Generate a random password with customizable options.
</summary>

**Options**

- `--length` or `-len`: Password length (default: 12, valid range: 6–50).
- `--uppercase` or `-up`: Exclude uppercase letters.
- `--lowercase` or `-low`: Exclude lowercase letters.
- `--digit` or `-d`: Exclude digits.
- `--symbol` or `-sym`: Exclude symbols.
- `--special` or `-s`: Exclude user-specified special characters.
- `--ambiguous` or `-a`: Exclude ambiguous characters (l, I, 1, O, 0).

> Note: Please enclose the value of `--special`/`-s` in **quotes** (like `-s '!@#$%^&*'`), especially if it contains special characters (such as `!`, `@`, `#`, `$`, `%`, `^`, `&`, and `*`).

</details>

```sh
cred_mgr gen [options]
# e.g. cred_mgr gen -len 10 -s '!@#$%^&*' -a
```

<details>

<summary>
Send credentials or a custom secret securely via Onetime Secret API, and return a shareable, one-time viewable link.
</summary>

**Mutually Exclusive Options (choose one):**

- `--conn_id` or `-id`: Send the credential corresponding to the specified connection ID stored by Dataxi.
- `--secret` or `-s`: Directly send custom secret text.

**Additional Options:**

- `--passphrase` or `-p`: Optionally secure the secret with a passphrase.
- `--ttl` or `-t`: Time-to-live in seconds for the secret (default: 3600).

> Note: Please enclose the values of `--secret`/`-s` and `--passphrase`/`-p` in **quotes** (like `-s '!@#$%^&*'`), especially if they contain special characters (such as `!`, `@`, `#`, `$`, `%`, `^`, `&`, and `*`).

> Special thanks to [Onetime Secret](https://onetimesecret.com/) for their awesome work and excellent API, which powers the secure sharing feature of this tool.

</details>

```sh
cred_mgr send [options]
# e.g. cred_mgr send -s 'test' -p 'p_test'
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
