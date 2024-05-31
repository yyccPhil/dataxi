from setuptools import setup, find_packages

setup(
    name="data-injection",
    version="0.0.1",
    packages=find_packages(),

    # if user doesn't specify any extras_require, will install all of these packages
    install_requires=[
        'pymysql',
        'pymssql',
        'clickhouse_connect',
        'requests',
        'pandas',
    ],
    
    extras_require={
        'mysql': ['pymysql'],
        'mssql': ['pymssql'],
        'clickhouse': ['clickhouse_connect'],
        'splunk': ['requests', 'pandas'],
    },
)
