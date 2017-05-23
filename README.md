Why I created this package ?
----------------------------
1) One by one insertion into Access DB, But it takes too much time to insert 100k
records,
```python
    cursor.execute("INSERT STATEMENT")
    cursor.commit()
```

2) Bulk way insertion into Access DB and it is fast if you compare with above one,
But even it is very slow from https://github.com/mkleehammer/pyodbc/issues/120
```python
    cursor.executemany("Bulk INSERT STATEMENT")
    cursor.commit()
```
But think if you want to insert 1000k records into AccessDB, how much time you have to
wait?

What the package will do ?
---------------------------
  1) Imports the data from text file to Access Database.
  2) Creating Access Database from pandas dataframe very quickly.
  3) Primary Key support.
  4) Can create many tables in Access Database
  5) Data Types support

How to Use:
-----------
1) If you have pandas dataframe you can follow bellow example
```python
    import accessdb
    # your dataframe
    # df.to_accessdb(<DB_PATH>, <TABLE_NAME>)
    df.to_accessdb(r'C:\Users\<user>\Desktop\test.accdb', 'SAMPLE')
```
2) If you have text file you can follow bellow example
```python
    from accessdb import create_accessdb
    # create_accessdb(<DB_PATH>, <TEXT_FILE_PATH>, <TABLE_NAME>)
    create_accessdb(r'C:\Users\<user>\Desktop\test.accdb', r'C:\Users\<user>\Documents\test.text', 'SAMPLE')
```

Installation:
-------------
    pip install accessdb

Note:
-----------
1) It will create text file if you are using pandas dataframe to create Access Database,
   But the file will be deleted after completion of process.
2) It supports only for Windows.
