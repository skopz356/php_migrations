<?php
require_once("php_migrations_files/fields.php");
require_once("php_migrations_files/models.php");

    class Test extends Model{
		public $title;
		public $some;
		public static $dbName = "test4";

        public static function get_attributes(){
            return ['title' => 'IntField', 'some' => 'StringField'];
        }

        public function get_connection(){
            return new mysqli('localhost', 'root', 'mysql', 'php_migrations');
        }

    }