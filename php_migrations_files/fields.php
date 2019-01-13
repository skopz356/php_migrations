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

    public static function create()
    {

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