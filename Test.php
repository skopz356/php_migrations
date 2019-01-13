<?php
require("php_migrations_files/fields.php");
require("php_migrations_files/models.php");

    class Test extends Model{
		public $title;
		public $some;
		public static $dbName = "test4";
        public static function getAttributes(){
            return ['title' => 'IntField', 'some' => 'StringField'];
        }

        public function getConnection(){
            return new mysqli('localhost', 'root', 'mysql', 'php_migrations');
        }

    }