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

    public   function select_object(array $condition){
        $key = "";
        $value = "";
        foreach($condition as $key => $value){
            $key = $key;
            $value = $value;
            break;
        }
        $sql = "SELECT * FROM ".$this->dbName()." WHERE ".$key."=".$value;
        return $this->connection->query($sql)->fetch_object();
    }

    public static function count_objects(){
        $sql = "SELECT COUNT(*) FROM ";
    }

}
