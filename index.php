<?php

require_once "engine/Test1.php";
$s = new Test1(["title" => 3, "some" => "ahoj"]);
echo (Test1::get_by_id(2)->title);

// class ahoj{
//     public $name;
//     function __construct($name){
//         $this->name = $name;

//     }
// }

// $d = "ahoj";
// $x = new $d("ahoj");
// print_r($x);