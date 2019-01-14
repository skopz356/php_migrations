#!/var/www/php_migrations/env/bin/python

import json, os, pymysql, sys, re
from text_unidecode import unidecode
from shutil import rmtree
import inspect, traceback

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
        if variety:
            self.variety = variety.upper()
        self.max_length = max_length
        self.null = null

    def needed_file(self):
        return 'require_once("php_migrations_files/fields.php")'  # TODO change this

    def db_value(self):
        if not self.null:
            return "%s(%d) NOT NULL" % (self.variety, self.max_length)
        else:
            return "%s(%d)" % (self.variety, self.max_length)

    def php_value(self, **kwargs):
        if self.variety == "INT":
            field_type = "'IntField'"
        if self.variety == "VARCHAR":
            field_type = "'StringField'"

        return field_type

    @classmethod
    def create_from_dict(cls, dictionary: dict):
        for name, data in dictionary.items():
            if data["type"] == "foreign-key":
                return ForeignKeyField(
                    data["model"], max_length=int(data["max-length"])
                )
            else:
                return cls(variety=data["type"], max_length=int(data["max-length"]))


class ForeignKeyField(Field):
    def __init__(self, model_name, max_length=255, null=False):
        self.foreign_model = next(
            filter(lambda x: x.name == model_name, Model.created_models), None
        )
        self.constraint = "CONSTRAINT fk_%s FOREIGN KEY (%s_id) REFERENCES %s (id)" % (
            self.foreign_model.d_name,
            self.foreign_model.d_name,
            self.foreign_model.d_name,
        )
        super().__init__(max_length=max_length, null=null)

    def db_value(self):
        if not self.null:
            return "%s(%d) UNSIGNED NOT NULL" % ("INT", self.max_length)
        else:
            return "%s(%d)" % ("INT", self.max_length)

    def php_value(self):
        return "['ForeginKey', '%s']" % (self.foreign_model.d_name)


class Model(object):
    created_models = []

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

    def register(self):
        """
        register model to the class needed for foreign key
        """
        type(self).created_models.append(self)

    def to_php(self):
        self.check_foreign()

        code = """<?php
%s
    class %s extends Model{
%s
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
            "\t\tpublic static $for_keys = %s;"
            % (
                str(
                    [
                        "'%s' => '%s'" % (name, field.foreign_model.name)
                        for name, field in self.get_all_fields(foreign=True).items()
                    ]
                )
            ).replace('"', "")
            if hasattr(self, "foreign")
            else "",
            str(
                [
                    "'%s' => %s" % (name, field.php_value())
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
                    else field.foreign_model.d_name + "_id",
                    field.db_value(),
                )
        if hasattr(self, "foreign"):
            sql += "".join(
                [
                    f_field.constraint
                    for n, f_field in self.get_all_fields(foreign=True).items()
                ]
            )
        if sql[len(sql) - 1] == ",":
            sql = sql[: len(sql) - 1]
        return sql + ")"

    def _get_id_sql(self):
        return "id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,"

    def get_all_fields(self, foreign=False):
        if not foreign:
            cls = Field
        else:
            cls = ForeignKeyField
        return {
            name if not type(field) == ForeignKeyField else name + "_id": field
            for name, field in vars(self).items()
            if foreign
            and type(field) == cls
            or not foreign
            and isinstance(field, Field)
        }

    def check_foreign(self):
        foreign = None
        for name, field in vars(self).items():
            if type(field) == ForeignKeyField:
                foreign = True
        if foreign:
            self.foreign = foreign

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
            + ['require_once("php_migrations_files/models.php");\n']
        )

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


argument = len(sys.argv) > 1
print(argument)
for key, value in data.items():
    if key != "connection":
        if value["type"] == "directory":
            d = Directory(key)
            for model, attributes in value["models"].items():
                m = Model.create_from_dict({model: attributes})
                m.register()
                if not argument:
                    m.create()
                elif sys.argv[1] == "db":
                    m.create()
                d.models.append(m)
            if not argument:
                d.php_create()
            elif sys.argv[1] == "php":
                d.php_create()

        if value["type"] == "model":
            m = Model.create_from_dict({key: value})
            m.register()
            if not argument:
                m.create()
                with open(key + ".php", "w+") as file:
                    file.write(m.to_php())
            elif sys.argv[1] == "php":
                with open(key + ".php", "w+") as file:
                    file.write(m.to_php())
            elif sys.argv[1] == "db":
                m.create()

