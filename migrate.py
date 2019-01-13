#!/var/www/php_migrations/env/bin/python

import json, os, pymysql, sys, re
from text_unidecode import unidecode
from shutil import rmtree

try:
    with open("migrations.json") as file:
        data = json.load(file)
except:
    raise FileNotFoundError("File migrations.json wasnt found.")


# Exceptions
class TypeMissingException(Exception):
    def __init__(self, message):
        super().__init__(message)


# Fields
class Field(object):
    def __init__(self, variety=None, max_length=255, null=False):
        self.variety = variety.upper()
        self.max_length = max_length
        self.null = null

    # def __new__(cls, *args, **kwargs):
    #     if "variety" in kwargs:
    #         if kwargs["variety"] == "foreign-key":
    #             return  ForeignKeyField(*args, **kwargs)
    #         return super().__new__(*args, **kwargs)

    def needed_file(self):
        return 'require("php_migrations_files/fields.php")'  # TODO change this

    def db_value(self):
        if not self.null:
            return "%s(%d) NOT NULL" % (self.variety, self.max_length)
        else:
            return "%s(%d)" % (self.variety, self.max_length)

    def php_value(self, **kwargs):
        if self.variety == "INT":
            field_type = "IntField"
        if self.variety == "VARCHAR":
            field_type = "StringField"

        return field_type

    @classmethod
    def create_from_dict(cls, dictionary: dict):
        for name, data in dictionary.items():
            return cls(variety=data["type"], max_length=int(data["max-length"]))


class ForeignKeyField(Field):
    def __init__(s)
    def db_value(self):
        if not self.null:
            return "%s(%d) NOT NULL" % ("INT", self.max_length)
        else:
            return "%s(%d)" % ("INT", self.max_length)

    def php_value(self):
        return "ForeginKey"


class Model(object):
    def __init__(self, name, d_name=None):
        """
        Model init method
        @param name: name of future model
        @param name(optional): name of future table
        """
        self.name = name
        self.d_name = unidecode(name).lower() if not d_name else d_name
        self.conn = pymysql.connect(
            host=data["connection"]["host"],
            user=data["connection"]["user"],
            password=data["connection"]["password"],
            db=data["connection"]["db_name"],
        )

    def to_php(self):

        code = """<?php
%s
    class %s extends Model{
%s
        public static function get_attributes(){
            return %s;
        }

        public function get_connection(){
            return new mysqli(%s);
        }

    }""" % (
            self._needed_files(),
            self.name,
            "\n".join(
                ["\t\tpublic $" + name + ";" for name in self.get_all_fields()]
                + ['\t\tpublic static $dbName = "%s";' % (self.d_name)]
            ),
            str(
                [
                    "'%s' => '%s'" % (name, field.php_value())
                    for name, field in self.get_all_fields().items()
                ]
            ).replace('"', ""),
            str(
                [
                    data["connection"]["host"],
                    data["connection"]["user"],
                    data["connection"]["password"],
                    data["connection"]["db_name"],
                ]
            )
            .replace("[", "")
            .replace("]", ""),
        )
        return code

    @classmethod
    def create_from_dict(cls, dictionary: dict):
        for name, data in dictionary.items():
            if "d_name" in data:
                m = Model(name=name, d_name=data["d_name"])
            else:
                m = Model(name=name)
            for field, field_properties in data["properties"].items():
                setattr(m, field, Field.create_from_dict({field: field_properties}))
            return m

    def create(self):
        with self.conn.cursor() as cursor:
            cursor.execute(self._get_full_sql())

    def _get_full_sql(self):
        self.check_foreign()
        sql = "CREATE TABLE %s(" % (self.d_name)
        sql += self._get_id_sql()
        for name_field, field in self.get_all_fields().items():
            if isinstance(field, Field):
                sql += "%s %s," % (
                    name_field
                    if not type(field) == ForeignKeyField
                    else name_field + "_id",
                    field.db_value(),
                )
        if sql[len(sql) - 1] == ",":
            sql = sql[: len(sql) - 1]
        if self.foreign:
            return sql + ")" + "".join([f_field.constrait for f_field in self.get_all_fields(foreign=True)])
        return sql + ")"

    def _get_id_sql(self):
        return "id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,"

    def get_all_fields(self, foreign=False):
        if not foreign:
            cls = Field
        else:
            cls=ForeignKeyField
        return {
            name: field
            for name, field in vars(self).items()
            if isinstance(field, cls)
        }

    def check_foreign(self):
        for name, field in vars(self):
            if type(field) == ForeignKeyField:
                self.foreign = True

    def _needed_files(self):
        from collections import OrderedDict

        return "\n".join(
            list(
                OrderedDict.fromkeys(
                    [
                        field.needed_file() + ";"
                        for name, field in self.get_all_fields().items()
                    ]
                )
            )
            + ['require("php_migrations_files/models.php");\n']
        )


class Directory(object):
    def __init__(self, name):
        self.models = list()
        self.name = name

    def php_create(self):
        if os.path.exists(self.name):
            rmtree(self.name)
        os.makedirs(self.name)
        for model in self.models:
            f = open(os.path.join(self.name, model.name + ".php"), "w+")
            f.write(model.to_php())


class IntField(Field):
    def __init(self, variety="INT", max_length=255, null=False):
        super().__init__(variety, max_length, null)


m = Model("ahoj")
setattr(m, "ahoj", Field(variety="int"))
print(m._get_full_sql())

# argument = len(sys.argv) > 1
# for key, value in data.items():
#     if key != "connection":
#         if value["type"] == "directory":
#             d = Directory(key)
#             for model, attributes in value["models"].items():
#                 m = Model.create_from_dict({model: attributes})
#                 if not argument:
#                     m.create()
#                 elif sys.argv[1] == "db":
#                     m.create()
#                 d.models.append(m)
#             if not argument:
#                 d.php_create()
#             elif sys.argv[1] == "php":
#                 d.php_create()

#         if value["type"] == "model":
#             m = Model.create_from_dict({key: value})
#             if not argument:
#                 m.create()
#             elif sys.argv[1] == "php":
#                 with open(key + ".php", "w+") as file:
#                     file.write(m.to_php())

