<?php

class Field
{
    public $value;
    protected $attribute = array();
    protected $type;

    public function __construct($value)
    {
        $this->set_value($value);
    }

    public function set_value($value)
    {
        $this->value = $value;
    }

    public function html_code($name)
    {
        return format('<input type="{}" name="{}" placeholder="{}">', array($this->html_type(), $name, $name));
    }

    public function html_code_editable($name)
    {
        return format('<textarea name="{}">{}</textarea>', array($name, $this->value));
    }

    public function html_type()
    {
        return "text";
    }

    public function get_value()
    {
        return $this->value;
    }

    public function __toString()
    {
        return (string) $this->value;
    }

    public function save($max_length = 255)
    {

        /* Return sql of field
         * >return string: raw sql
         * */

        if (isset(self::$attribute["max-length"])) {
            return sprintf("%s()", self::$type);
        }

    }

}

class CharField extends Field
{

}

class IntField extends Field
{
    /*public function html_type()
{
return "number";
}*/

}

class StringField extends Field
{

}

class ImageField extends Field
{
    public function html_code($name)
    {
        return format('<img src=""><input type="text" placeholder="Vyberte obrazek" id="popup-files-opener" name={}>', array($name));
    }

    public function html_code_editable($name)
    {
        $image = image_url($this->value, array(100, 100), true);
        if ($this->value != null) {
            return format('<img src="{}"><input type="text" value="{}" id="popup-files-opener" name={}>', array($image, $this->value, $name));
        }
        return format('<input type="text" placeholder="Vyberte obrazek" id="popup-files-opener" name={}>', array($name));
    }
}

class TextField extends Field
{
    public function html_code($name)
    {
        return format('<textarea class="summernote" type="{}" name="{}">{}</textarea>', array($this->html_type(), $name, $name));
    }

    public function html_code_editable($name)
    {
        return format('<textarea class="summernote" name="{}">{}</textarea>', array($name, $this->value));
    }
}

class PasswordField extends Field
{
    public function set_value($value)
    {
        $this->value = hash('sha256', $value);
    }

}

class ForeginKey extends Field
{
    public $fname;
    public function __construct($value)
    {
        $cls = static::class;
        $this->value = $cls::get($value);
        $this->fname = $value[1];
    }
    public static function get($value)
    {
        $cls = $value[1];
        if ($value[0] == null) {
            return null;
        } else {
            if (is_numeric($value[0])) {
                return $cls::get_by_id((int) $value[0]);
            } else {
                return $cls::get_by_id($value[0]->id);
            }
        }
    }

    public function html_code($name)
    {
        $options = "";
        foreach ($this->fname::all() as $key) {
            $options .= format('<option value="{}">{}</option>', array($key->id, (string) $key));
        }

        return format("<select name={}>{}</select>", array($name, $options));
    }

    public function html_code_editable($name)
    {
        $options = "";
        foreach ($this->fname::all() as $key) {
            $options .= format('<option {} value="{}">{}</option>', array((((int) $key->id == $this->value->id) ? 'selected="selected"' : ""), $key->id, (string) $key));
        }
        return format("<select name={}>{}</select>", array($name, $options));
    }

    public function get_value()
    {
        $this->value->update();
        return $this->value->id;
    }
}

class BooleanField extends Field
{
    public function __construct($value)
    {

        if ($value == 1 or $value == true) {
            $this->value = true;
        } elseif ($value == 0 or $value == false) {
            $this->value = false;
        }
    }

    public function get_value()
    {
        if ($this->value) {
            return 1;
        } else {
            return 0;
        }
    }

    public function html_type()
    {
        return "checkbox";
    }

    public function html_code($name)
    {
        return format('<input type="{}" name="{}" placeholder="{}">', array($this->html_type(), $name, $name));
    }

    public function html_code_editable($name)
    {
        return format('<input type="{}" name="{}" {}>', array($this->html_type(), $name, (($this->value) ? 'checked="checked"' : "")));
    }

}

class Select
{
    private $queryset;
    private $null;

    public function __construct($queryset, $null = true)
    {
        $this->queryset = $queryset;
        $this->null = $null;
    }

    public function html_code($name)
    {
        if ($this->null) {
            $options = '<option value="">------</option> ';
        } else {
            $options = "";
        }

        foreach ($this->queryset as $q) {
            $options .= format('<option value="{}">{}</option>', array(((is_object($q) ? $q->id : $q)), $q));
        }

        return format('<select name="{}">{}</select>', array($name, $options));

    }

    public function html_code_editable($name, $field)
    {
        if ($this->null) {
            $options = '<option value="">------</option> ';
        } else {
            $options = "";
        }
        foreach ($this->queryset as $q) {
            if (is_object($q)) {
                $id = $q->id;
            } else {
                $id = $q;
            }
            $options .= format('<option {} value="{}">{}</option>', array((($id == $field->value) ? 'selected="selected"' : ""), $id, $q));
        }
        return format('<select name="{}">{}</select>', array($name, $options));
    }
}

/*
class CustomField
{
private $html;
private $html_editable;
private $parent;

public function __construct($parent, $html = null, $html_editable = null)
{
$this->parent = $parent;
if ($html != null) {
$this->html = $html;
}
if ($html_editable != null) {
$this->html_editable = $html_editable;
}
}

public function html_code()
{
return $this->html();
}

public function html_code_editable()
{
return $this->html_editable();

}
}

 */