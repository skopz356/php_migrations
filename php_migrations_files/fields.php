<?php

class Field
{
    public $value;
    protected $attribute = array();
    protected $type;

    public function __construct($value)
    {
        $this->set_value($value);
    }

    public function set_value($value)
    {
        $this->value = $value;
    }

    public function get_value()
    {
        return $this->value;
    }

    public function __toString()
    {
        return $this->value;
    }

    public function save($max_length = 255)
    {

        /* Return sql of field
         * >return string: raw sql
         * */

        if (isset(self::$attribute["max-length"])) {
            return sprintf("%s()", self::$type);
        }

    }

}

class CharField extends Field
{

}

class IntField extends Field
{

}

class StringField extends Field
{

}

class ForeginKey extends Field
{
    public function __construct($value)
    {
        $cls = static::class;
        $this->value = $cls::get($value);
    }
    public static function get($value)
    {
        $cls = $value[1];
        if (gettype($value[0]) == "integer") {
            return $cls::get_by_id($value[0]);
        } else {
            return $cls::get_by_id($value[0]->id);
        }
    }

    public function get_value()
    {
        $this->value->update();
        return $this->value->id;
    }
}