<?php

require_once "engine/Test1.php";
$s = new Test1([]);
$s = Test1::get_by_id(1);
var_dump($s);
$s->set_value("some", "fungue");
$s->update();
var_dump(Test1::get_by_id(1));

//print_r(Test1::all());