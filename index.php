<?php

require_once "engine/Test1.php";
$s = new Test1(["title" => 3, "some" => "ahoj"]);
//$s->save();
print_r($s->select_object(["id" => 3]));





// class ahoj{
//     public $name;
//     function __construct($name){
//         $this->name = $name;

//     }
// }

// $d = "ahoj";
// $x = new $d("ahoj");
// print_r($x);