<?php
require "abstract.php";
use AB\BaseModel;

abstract class Model extends BaseModel
{

    public function save()
    {
        $return = "INSERT INTO " . $this->dbName() . " (";
        foreach ($this->get_fields() as $key => $value) {
            $return .= $key . ",";
        }
        if (substr($return, -1) == ",") {
            $return = substr($return, 0, strlen($return) - 1);
        }
        $return .= ") VALUES (";

        foreach ($this->get_fields() as $key => $value) {
            $return .= '"' . $value->value . '"' . ",";
        }

        if (substr($return, -1) == ",") {
            $return = substr($return, 0, strlen($return) - 1);
        }
        $return .= ")";

        if ($this->connection->query($return) != true) {
            echo $this->connection->error;
        }
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
                array_push($return, self::return_self($value, false));
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
        return self::return_self(self::evaluate_sql($sql)->fetch_object());

    }

    private static function add_quotes($attr)
    {
        if (gettype($attr) == "string") {
            return '"' . $attr . '"';
        } else {
            return $attr;
        }

    }

    private static function return_self($obj, $is_object = true)
    {
        $parametrs = [];
        $cls = static::class;
        if ($is_object) {
            $f_object = new $cls([]);
            foreach (get_object_vars($obj) as $key => $value) {
                if (property_exists($f_object, $key)) {
                    $parametrs[$key] = $value;
                }
            }
        } else {
            $parametrs = $obj;
        }
        return new $cls($parametrs);

    }

    private function evaluate_sql($sql)
    {
        $result = static::$connection->query($sql);
        if (!$result) {
            return null;
        } else {
            return $result;
        }

    }

}