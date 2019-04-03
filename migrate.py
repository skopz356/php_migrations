#!/var/www/base/env/bin/python

import json, os, pymysql, sys, glob
from shutil import rmtree
import inspect, traceback
from datetime import datetime

import dictdiffer
from text_unidecode import unidecode


# Exceptions
class TypeMissingException(Exception):
    def __init__(self, message):
        super().__init__(message)


# Fields
class Field(object):
    def __init__(self, variety=None, max_length=255, null=True, default=None):
        if variety:
            self.variety = variety.upper()
        self.default = default
        self.max_length = max_length
        self.null = null

    def needed_file(self):
        return 'require_once("php_migrations_files/fields.php")'  # TODO change this

    def db_value(self):
        if self.null and not self.default:
            return "%s(%d) NOT NULL" % (self.variety, self.max_length)
        else:
            return "%s(%d) %s" % (
                self.variety,
                self.max_length,
                "DEFAULT " + str(self.default) if self.default else "",
            )

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
                if "max-length" in data:
                    return ForeignKeyField(
                        data["model"], max_length=int(data["max-length"])
                    )
                elif "verbose_name" in data:
                    return ForeignKeyField(
                        data["model"], verbose_name=data["verbose_name"]
                    )
                else:
                    return ForeignKeyField(data["model"])
            elif data["type"] == "text":
                if "null" in data:
                    if data["null"] == "true":
                        return TextField(null=True)
                    elif data["null"] == "false":
                        return TextField()
                else:
                    return TextField()
            elif data["type"] == "boolean":
                if "default" in data:
                    return BooleanField(default=data["default"])
                else:
                    return BooleanField()
            else:
                if "null" in data:
                    if data["null"] == "true":
                        return cls(
                            variety=data["type"],
                            max_length=int(data["max-length"]),
                            null=True,
                        )
                    elif data["null"] == "false":
                        return cls(
                            variety=data["type"], max_length=int(data["max-length"])
                        )
                elif "default" in data:
                    return cls(
                        variety=data["type"],
                        max_length=int(data["max-length"]),
                        default=data["default"],
                    )
                else:
                    return cls(variety=data["type"], max_length=int(data["max-length"]))


class Cache(object):
    extension = ".json"
    directory = ".cache/"

    def __init__(self, *args, **kwargs):
        if os.path.exists(".cache/"):
            self.caches = list(
                filter(
                    lambda x: "all" not in x,
                    sorted(glob.glob(Cache.directory + "*.json")),
                )
            )
            self._set_caches()
        else:
            os.mkdir(Cache.directory)
            self.caches = []

    def _set_caches(self):
        for i, file in enumerate(self.caches):
            self.caches[i] = Cache.CacheFile(file)

    def _set_models(self):
        all_file = os.path.join(Cache.directory, "all_migrations.json")
        with open(all_file, "r") as file:
            for name, value in json.load(file).items():
                m = Model.create_from_dict({name: value})
                m.register()

    def get_last(self):
        if self.caches:
            return self.caches[len(self.caches) - 1]
        return None

    def is_new(self):
        return len(self.caches) == 1

    def cache(self, value):
        self.store_in_all(value)
        self._set_models()
        value = json.dumps(value)
        if self.caches:
            file_name = "%s_%s" % (self.get_last().get_order() + 1, Cache.get_date())
        else:
            file_name = "0_" + Cache.get_date()
        c = Cache.CacheFile.create(Cache.directory + file_name + Cache.extension, value)

    def has_changed(self, value):
        if self.caches:
            return not self.get_last() == value
        return True

    def store_in_all(self, value: dict):
        all_file = os.path.join(Cache.directory, "all_migrations.json")
        if os.path.exists(all_file):
            with open(all_file, "r") as file:
                # merge loaded value and the current
                value = {**value, **json.load(file)}
        with open(all_file, "w+") as file:
            json.dump(value, file)

    @staticmethod
    def get_date():
        return str(datetime.now().date()).replace("-", "_")

    class CacheFile(object):
        def __init__(self, path, content=None, *args, **kwargs):
            self.path = path
            if not content:
                with open(self.path, "r") as f:
                    self.content = json.load(f)
            else:
                self.content = content

        def save(self):
            with open(self.path, "w") as file:
                json.dump(self.content, file)

        def get_order(self):
            return int(self.path.replace(Cache.directory, "")[0])

        @classmethod
        def create(cls, path, value, create=True):
            if create:
                with open(path, "w+") as f:
                    f.write(value)
            return cls(path, content=json.loads(value))

        def __eq__(self, value):
            if hasattr(value, "content"):
                return self.content == value.content
            elif type(value) == dict:
                return self.content == value
            return super().__eq__(value)


class MigrationControl(object):
    def _get_part_code(self, diff_part):
        x = diff_part
        if diff_part[0] == "add":
            if not diff_part[1]:
                m = Model.create_from_dict({diff_part[2][0][0]: diff_part[2][0][1]})
            else:
                Model.created_models
        if diff_part[0] == "remove":
            pass
        if diff_part[0] == "change":
            pass

    def _get_migration_code(self, value, last_object, initial=False):
        result = ""
        if not initial:
            differ = dictdiffer.diff(last_object.content, value)
            for df in differ:
                result += self._get_part_code(df)
        else:
            pass

        return list(differ)

    def check_migration(self, value):
        c = Cache()
        if c.has_changed(value):
            c.cache(value)
            c = Cache()
            x = self._get_migration_code(value, c.get_last(), c.is_new())

        else:
            print("No changes were detected")
            sys.exit()


class ForeignKeyField(Field):
    variety = "foreign-key"

    def __init__(self, model_name, max_length=6, null=False, verbose_name=None):
        self.foreign_model = next(
            filter(lambda x: x.model_name == model_name, Model.created_models), None
        )
        self.constraint = "CONSTRAINT fk_%s FOREIGN KEY (%s_id) REFERENCES %s (id)" % (
            self.foreign_model.d_name if not verbose_name else verbose_name,
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


class TextField(Field):
    variety = "text"

    def __init__(self, null=False):
        self.null = null

    def db_value(self):
        if self.null:
            return "TEXT NOT NULL"
        else:
            return "TEXT"

    def php_value(self):
        return "'TextField'"


class BooleanField(Field):
    variety = "boolean"

    def __init__(self, default=None):
        self.default = default

    def db_value(self):
        if self.default:
            return "TINYINT(1) DEFAULT %s" % (self.default)
        else:
            return "TINYINT(1) NOT NULL"

    def php_value(self):
        return "'BooleanField'"


class Model(object):
    created_models = []

    def __init__(self, name, d_name=None):
        """
        Model init method
        @param name: name of future model
        @param name(optional): name of future table
        """

        self.model_name = name
        self.altered_fields = dict()
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
            self.model_name,
            "\n".join(
                ["\t\tpublic $" + name + ";" for name in self.get_all_fields()]
                + ['\t\tpublic static $dbName = "%s";' % (self.d_name)]
            ),
            "\t\tpublic static $for_keys = %s;"
            % (
                str(
                    [
                        "'%s' => '%s'" % (name, field.foreign_model.model_name)
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
            cursor.execute(self.get_full_sql())

    def get_alter_sql(self):
        sql = "ALTER TABLE %s"
        for value, field in self.altered_fields:
            sql += "%s COLUMN %s" % (value.upper(), field.db_value())
        return sql

    def get_full_sql(self):
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

    def _get_id_sql(self):
        return "id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,"

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
        if not os.path.exists(self.name):
            os.makedirs(self.name)
        for model in self.models:
            f = open(os.path.join(self.name, model.model_name + ".php"), "w+")
            f.write(model.to_php())


if __name__ == "__main__":
    import argparse

    try:
        with open("migrations.json") as file:
            data = json.load(file)
    except:
        raise FileNotFoundError("File migrations.json wasnt found.")

    parser = argparse.ArgumentParser(description="Generator for php_migrations")
    parser.add_argument("type", default="all", choices=["php", "db", "sql", "all"], action="store_const", const=True)
    args = parser.parse_args()
    print(args.all)
    argument = len(sys.argv) > 1
    if argument:
        if sys.argv[1] == "sql":
            sql = ""

    # for key, value in data.items():
    #     if key != "connection":
    #         if value["type"] == "directory":
    #             d = Directory(key)
    #             for model, attributes in value["models"].items():
    #                 m = Model.create_from_dict({model: attributes})
    #                 m.register()
    #                 if not argument:
    #                     m.create()
    #                 elif sys.argv[1] == "db":
    #                     m.create()
    #                 elif sys.argv[1] == "sql":
    #                     sql += m.get_full_sql() + ";"
    #                 d.models.append(m)
    #             if not argument:
    #                 d.php_create()
    #             elif sys.argv[1] == "php":
    #                 d.php_create()

    #         if value["type"] == "model":
    #             m = Model.create_from_dict({key: value})
    #             m.register()
    #             if not argument:
    #                 m.create()
    #                 with open(key + ".php", "w+") as file:
    #                     file.write(m.to_php())
    #             elif sys.argv[1] == "php":
    #                 with open(key + ".php", "w+") as file:
    #                     file.write(m.to_php())
    #             elif sys.argv[1] == "db":
    #                 m.create()

    # if sql:
    #     if len(sys.argv) != 3:
    #         sys.argv.append("migrations.sql")
    #         sql = sql[: len(sql) - 1]
    #     with open(sys.argv[2], "w+") as file:
    #         file.write(sql)

