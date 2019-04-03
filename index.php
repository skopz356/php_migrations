<?php

require_once "Test4.php";
require_once "Test.php";
//$s = new Test4(["title" => 5, "some" => "asd", "test_id" => 1]);
//$s->save();

$s = Test4::get_by_id(1);
echo ($s->test_id->value->some);
//$s->save();
// $s = new Test1([]);
// $s = Test1::get_by_id(1);
// var_dump($s);
// $s->set_value("some", "fungue");
// $s->update();
// var_dump(Test1::get_by_id(1));

//print_r(Test1::all());