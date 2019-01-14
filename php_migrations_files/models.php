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
                        $value = [(int) $value, static::$for_keys[$key]];
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
            $return .= $key . ",";
        }
        if (substr($return, -1) == ",") {
            $return = substr($return, 0, strlen($return) - 1);
        }
        $return .= ") VALUES (";

        foreach ($this->get_fields() as $key => $value) {
            $return .= '"' . $value->get_value() . '"' . ",";
        }

        if (substr($return, -1) == ",") {
            $return = substr($return, 0, strlen($return) - 1);
        }
        $return .= ")";

        if (static::$connection->query($return) != true) {
            echo static::$connection->error;
        }
        $this->id = self::count_objects();
    }

    public function set_value(string $var_name, $value)
    {
        $cls = $this->get_attributes()[$var_name];
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

    public function update()
    {
        if ($this->id == null) {
            throw new Exception("The object wasnt saved yet.");
        } else {
            $return = "UPDATE " . static::$dbName . " SET ";
            foreach ($this->get_fields() as $key => $value) {
                $return .= $key . "=" . self::add_quotes($value->value) . ",";
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

    /* STATIC FUNCTIONS */

    public static function select_objects(array $condition)
    {
        $key = "";
        $value = "";
        foreach ($condition as $key => $value) {
            $key = $key;
            $value = self::add_quotes($value);
            break;
        }
        if (!empty($condition)) {
            $sql = "SELECT * FROM " . static::$dbName . " WHERE " . $key . "=" . $value;
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

    private static function add_quotes($attr)
    {
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

    private function evaluate_sql($sql)
    {
        self::set_connection();
        $result = static::$connection->query($sql);
        if (!$result) {
            return null;
        } else {
            return $result;
        }

    }

    public static function set_connection()
    {
        $cls = static::class;
        $s = new $cls([]);
    }

}