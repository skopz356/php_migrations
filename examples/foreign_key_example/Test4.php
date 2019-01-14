<?php
require_once("php_migrations_files/fields.php");
require_once("php_migrations_files/models.php");

    class Test4 extends Model{
		public $title;
		public $some;
		public $test_id;
		public static $dbName = "test4";
		public static $for_keys = ['test_id' => 'Test'];
        public static function get_attributes(){
            return ['title' => 'IntField', 'some' => 'StringField', 'test_id' => ['ForeginKey', 'test']];
        }

        public function get_connection(){
            return new mysqli('localhost', 'root', 'mysql', 'php_migrations');
        }

    }