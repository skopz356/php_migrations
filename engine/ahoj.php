<?php
require("php_migrations_files/fields.php");
require("php_migrations_files/models.php");

    class ahoj extends Model{
		public $title;
		public $some;
		public static $dbName = "ahoj";
        public static function getAttributes(){
            return ['title' => 'IntField', 'some' => 'StringField'];
        }

        public function getConnection(){
            return new mysqli('localhost', 'root', 'mysql', 'php_migrations');
        }

    }