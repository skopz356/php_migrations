<?php
// require_once "abstract.php";
// use AB\BaseField;

abstract class BaseField
{
    public $value;
    abstract public static function create();
    public function setValue($value)
    {
        $this->value = $value;
    }
}

class Field extends BaseField
{
    protected $attribute = array();
    protected $type;

    public function __construct($value)
    {
        $this->setValue($value);
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
