# -*- coding: utf-8 -*-
# Copyright 2017 Dhana Babu
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import random
import string
import tempfile
import shutil

import pypyodbc as odbc

from .access_api import create


_MS_ACCESS_TYPES = {
    'BIT',
    'BYTE',
    'SHORT',
    'LONG',
    'CURRENCY',
    'SINGLE',
    'DOUBLE',
    'DATETIME',
    'TEXT',
    'MEMO',
    'PRIMARY',  # CUSTOM Type for handling AUTOINCREMENT
}

SCHEMA_FILE = 'schema.ini'

_TEXT_SEPARATORS = {
                   r',': 'CSVDelimited',
                   r'\t': 'TabDelimited'
                   }


def _text_formater(sep):
    separator = _TEXT_SEPARATORS.get(sep, 'Delimited({})')
    return separator.format(sep)


def _stringify_path(db_path):
    dtr, path = os.path.split(db_path)
    if dtr == '':
        db_path = os.path.join('.', path)
    return db_path


def _push_access_db(temp_dir, text_file, data_columns,
                    header_columns, dtype, path, table_name, sep,
                    append, overwrite, delete='file'):
    table = Table(temp_dir, text_file,
                  table_name,
                  data_columns,
                  header_columns,
                  dtype, sep, append)
    schema_file = os.path.join(temp_dir, SCHEMA_FILE)
    try:
        with SchemaWriter(temp_dir, text_file, data_columns,
                          header_columns, dtype, sep, schema_file) as schema:
            schema.write()
        with AccessDBConnection(path, overwrite) as con:
            cursor = con.cursor()
            if not append:
                cursor.execute(table.create_query())
            cursor.execute(table.insert_query())
            con.commit()
    finally:
        if delete == 'folder':
            shutil.rmtree(temp_dir)
        else:
            os.unlink(schema_file)


def _get_random_file():
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(10))


class DataTypeNotFound(Exception):
    pass


class SchemaWriter(object):
    def __init__(self, temp_dir, text_file, df_columns,
                 columns, dtype, sep, schema_file):
        self.temp_dir = temp_dir
        self.text_file = text_file
        self.df_columns = df_columns
        self.columns = columns
        self.dtype = dtype
        self.sep = sep
        self.path = schema_file

    def __enter__(self):
        self.fp = open(self.path, 'w')
        return self

    def __exit__(self, *args):
        self.fp.close()

    def formater(self):
        yield '[%s]' % self.text_file
        yield 'ColNameHeader=True'
        yield 'Format=%s' % _text_formater(self.sep)
        self.dcols = {col: ('Col%s' % (i + 1))
                      for i, col in enumerate(self.df_columns)}
        if not isinstance(self.dtype, dict):
            self.dtype = {}
        for col in self.df_columns:
            ctype = self.dtype.get(col, 'text').upper()
            if ctype not in _MS_ACCESS_TYPES:
                raise DataTypeNotFound(
                    'Provided Data Type Not Found %s' % ctype)
            if ctype == 'PRIMARY':
                ctype = 'TEXT'
            yield '{c_col}="{d_col}" {c_type}'.format(
                                                c_col=self.dcols[col],
                                                d_col=col,
                                                c_type=ctype.capitalize())

    def write(self):
        for line in self.formater():
            self.fp.write(line)
            self.fp.write('\n')


class Table(object):
    def __init__(self, temp_dir, text_file,
                 table_name, df_columns, columns,
                 dtype, sep, append):
        self.temp_dir = temp_dir
        self.text_file = text_file
        self.df_columns = df_columns
        self.table_name = table_name
        self.df_columns = df_columns
        self.columns = columns
        self.dtype = dtype
        self.sep = sep
        self.append = append
        if not isinstance(self.dtype, dict):
            self.dtype = {}

    def _get_colunm_type(self, col):
        ctype = self.dtype.get(col, 'TEXT').upper()
        if ctype not in _MS_ACCESS_TYPES:
            raise Exception
        return ctype

    def formater(self):
        for col in self.df_columns:
            c_type = self._get_colunm_type(col)
            if c_type == 'PRIMARY':
                c_type = 'AUTOINCREMENT PRIMARY KEY'
            if self.columns:
                if col not in self.columns:
                    continue
                col = self.columns[col]
            yield '`{c_col}`  {c_type}'.format(c_col=col,
                                               c_type=c_type)

    def insert_formater(self):
        for col in self.df_columns:
            if self._get_colunm_type(col) == 'PRIMARY':
                continue
            if not self.columns:
                self.columns = dict(zip(self.df_columns, self.df_columns))
            if self.columns:
                if col not in self.columns:
                    continue
                cus_col = self.columns[col]
            yield col, cus_col

    def built_columns(self):
        return '(%s)' % ','.join(self.formater())

    def create_query(self):
        return "CREATE TABLE `{table_name}`{columns}".format(
                                            table_name=self.table_name,
                                            columns=self.built_columns())

    @staticmethod
    def required_columns(cols):
        return ','.join('`%s`' % c for c in cols)

    def insert_query(self):
        custom_columns = []
        columns = []
        for col1, col2 in self.insert_formater():
            columns.append(col1)
            custom_columns.append(col2)
        return """
                INSERT INTO `{table_name}`({columns})
                    SELECT {required_cols}  FROM [TEXT;HDR=YES;FMT={separator};
                                    Database={temp_dir}].{text_file}
            """.format(temp_dir=self.temp_dir,
                       text_file=self.text_file,
                       columns=self.required_columns(custom_columns),
                       required_cols=self.required_columns(columns),
                       table_name=self.table_name,
                       separator=_text_formater(self.sep))


class AccessDBConnection(object):
    def __init__(self, db_path, overwrite):
        self.overwrite = overwrite
        self.db_path = _stringify_path(db_path)

    def __enter__(self):
        if not os.path.isfile(self.db_path) or self.overwrite:
            create(self.db_path)
        odbc_conn_str = '''DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};
                           DBQ=%s''' % (self.db_path)
        self.con = odbc.connect(odbc_conn_str)
        return self.con

    def __exit__(self, *args):
        self.con.close()


def to_accessdb(self, path, table_name,
                header_columns=None, dtype='str', engine='text',
                sep=',', append=False, overwrite=False):
    if self.empty:
        return
    temp_dir = tempfile.mkdtemp()
    text_file = '%s.txt' % _get_random_file()
    text_path = os.path.join(temp_dir, text_file)
    self.to_csv(text_path, index=False)
    _push_access_db(temp_dir, text_file,
                    self.columns.tolist(),
                    header_columns, dtype, path, table_name,
                    sep, append, overwrite, 'folder')


def create_accessdb(path, text_path, table_name,
                    header_columns=None, dtype='str',
                    engine='text', sep=',', append=False, overwrite=False):
    temp_dir, text_file = os.path.split(os.path.abspath(text_path))
    with open(text_path) as fp:
        file_columns = fp.readline().strip('\n').split(sep)
    _push_access_db(temp_dir, text_file,
                    file_columns,
                    header_columns, dtype, path, table_name,
                    sep, append, overwrite)
