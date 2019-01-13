<?php
namespace AB;

abstract class BaseModel
{
    protected static $connection;
    public static $dbName;
    public $id;

    public function __construct(array $attributes)
    {
        static::$connection = $this->getConnection();
        foreach ($attributes as $key => $value) {
            if (property_exists($this, $key)) {
                if (array_key_exists($key, $this->getAttributes())) {
                    $cls = $this->getAttributes()[$key];
                    $this->$key = new $cls($value);
                }else{
                    $this->$key = $value;
                }

            }
        }
        $this->getConnection();

    }
    abstract public function save();
    abstract public static function getAttributes();
    abstract public function getConnection();
}

// abstract class BaseField
// {
//     private $value;
//     abstract public static function create();
//     public function setValue($value)
//     {
//         $this->value = $value;
//     }
// }
