<?php

abstract class Model
{
    protected static $connection;
    public static $dbName;
    public $id;

    abstract public static function get_attributes();
    abstract public function get_connection();

    public function __construct(array $attributes)
    {
        static::$connection = $this->get_connection();
        foreach ($attributes as $key => $value) {
            if (property_exists($this, $key)) {
                if (array_key_exists($key, $this->get_attributes())) {
                    if (is_array($this->get_attributes()[$key])) {
                        $cls = $this->get_attributes()[$key][0];
                        $value = [$value, static::$for_keys[$key]];
                    } else {
                        $cls = $this->get_attributes()[$key];
                    }
                    $this->$key = new $cls($value);
                } else {
                    $this->$key = $value;
                }

            }
        }

    }

    public function save()
    {
        $return = "INSERT INTO " . static::$dbName . " (";
        foreach ($this->get_fields() as $key => $value) {
            if ($value->value != null) {
                $return .= $key . ",";
            }
        }

        if (substr($return, -1) == ",") {
            $return = substr($return, 0, strlen($return) - 1);
        }
        $return .= ") VALUES (";

        foreach ($this->get_fields() as $key => $value) {
            if ($value->value != null) {
                $return .= format('"{}",', array(static::escape($value->get_value())));
            }
        }

        if (substr($return, -1) == ",") {
            $return = substr($return, 0, strlen($return) - 1);
        }
        $return .= ")";

        if (static::$connection->query($return) != true) {
            echo static::$connection->error;
            return static::$connection->error;

        }
        $this->id = self::count_objects();
    }

    public function set_value(string $var_name, $value)
    {
        /**
         * set value of object
         * @param string var_name: name of variable
         * @param string value: the future value
         */

        $cls = $this->get_attributes()[$var_name];
        if (is_array($cls)) {
            $cls = $this->get_attributes()[$var_name][0];
            $value = [$value, static::$for_keys[$var_name]];
        }
        $this->$var_name = new $cls($value);
    }

    public function get_fields()
    {
        $fields = [];
        foreach (get_object_vars($this) as $key => $value) {
            if (is_a($value, "Field")) {
                $fields[$key] = $value;
            }
        }

        return $fields;
    }

    public function get_url()
    {
        return format("/{}/{}", array(static::$dbName, $this->id));
    }

    public function insert_nulls()
    {
        foreach ($this as $key => $value) {
            if (array_key_exists($key, $this->get_attributes())) {
                $this->set_value($key, null);
            }
        }
    }

    public function update()
    {
        if ($this->id == null) {
            throw new Exception("The object wasnt saved yet.");
        } else {
            $return = "UPDATE " . static::$dbName . " SET ";
            foreach ($this->get_fields() as $key => $value) {
                if ($value->value != null) {

                    $v = $value->get_value();

                    $return .= $key . "=" . (($v == "null") ? "null" : self::add_quotes($v)) . ",";
                }
            }
            if (substr($return, -1) == ",") {
                $return = substr($return, 0, strlen($return) - 1);
            }
            $return .= " WHERE id=" . $this->id;
        }
        if (static::$connection->query($return) != true) {
            echo static::$connection->error;
        }
    }

    public function delete()
    {
        $sql = format("DELETE FROM {} WHERE id={}", array(static::$dbName, $this->id));
        if (static::$connection->query($sql) != true) {
            echo static::$connection->error;
            return false;
        } else {
            return true;
        }
    }

    /* STATIC FUNCTIONS */

    public static function select_objects(array $condition)
    {
        $key = "";
        $value = "";
        $another = "";
        foreach ($condition as $key => $value) {
            $key = $key;
            $value = self::add_quotes($value);
            break;
        }
        $i = 0;
        foreach ($condition as $_key => $_value) {
            if ($i != 0) {
                $another .= format(" AND ({}={})", array($_key, self::add_quotes($_value)));
            }
            $i += 1;
        }

        if (!empty($condition)) {
            if ($another != "") {
                $sql = format("SELECT * FROM {} WHERE ({}={}){}", array(static::$dbName, $key, $value, $another));
            } else {
                $sql = "SELECT * FROM " . static::$dbName . " WHERE " . $key . "=" . $value;
            }
        } else {
            $sql = "SELECT * FROM " . static::$dbName;
        }

        if (self::evaluate_sql($sql) != null) {
            $return = [];
            foreach (self::evaluate_sql($sql)->fetch_all(MYSQLI_ASSOC) as $value) {
                array_push($return, self::return_self($value));
            }
            return $return;
        } else {
            return self::evaluate_sql($sql);
        }

    }

    public static function all()
    {
        /**
         * >Return array all objects
         */

        return self::select_objects([]);
    }

    public static function count_objects()
    {
        $sql = "SELECT COUNT(*) AS total FROM " . static::$dbName;

        return static::$connection->query($sql)->fetch_object()->total;
    }

    public static function get_by_id($id)
    {
        $sql = "SELECT * FROM " . static::$dbName . " WHERE id=" . $id;

        return self::return_self(self::evaluate_sql($sql)->fetch_assoc());
    }

    public static function set_connection()
    {
        $cls = static::class;
        $s = new $cls([]);
    }

    public static function order($objects, string $by)
    {
        if ($objects != null) {
            $how = true;
            //check if first char is -
            if (substr($by, 0, 1) == "-") {
                $how = false;
                $by = substr($by, 1, strlen($by));
            }
            usort($objects, function ($a, $b) use ($by, $how) {
                if ($a->{$by}->value == $b->{$by}->value) {
                    return 0;

                } elseif ($a->{$by}->value > $b->{$by}->value) {
                    if ($how) {
                        return 1;
                    } else {
                        return -1;
                    }
                } elseif ($a->{$by}->value < $b->{$by}->value) {
                    if ($how) {
                        return -1;
                    } else {
                        return 1;
                    }
                }

            });
        }
        return $objects;
    }

    private static function add_quotes($attr)
    {
        $attr = static::escape($attr);
        if (gettype($attr) == "string") {
            return '"' . $attr . '"';
        } else {
            return $attr;
        }
    }

    private static function return_self($parametrs)
    {
        $cls = static::class;
        if ($parametrs != null) {
            return new $cls($parametrs);
        } else {
            return $parametrs;
        }
    }

    private static function escape($value)
    {
        return static::$connection->real_escape_string($value);
    }

    private static function evaluate_sql($sql)
    {
        self::set_connection();
        $result = static::$connection->query($sql);
        if (!$result) {
            return null;
        } else {
            return $result;
        }
    }

}