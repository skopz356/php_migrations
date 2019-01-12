<?php
namespace AB;

abstract class BaseModel
{
    private $connection;
    public function __construct(array $attributes)
    {
        foreach ($attributes as $key => $value) {
            if (property_exists($this, $key)) {
                $cls = $this->getAttributes()[$key];
                $this->$key = new $cls($value);
            }
        }
        $this->getConnection();

    }
    abstract public function save();
    abstract public static function getAttributes();
    abstract public function getConnection();
    abstract public function dbName();
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
