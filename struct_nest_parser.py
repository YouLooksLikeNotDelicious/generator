# -*- coding:utf-8 -*-
from lepl import *

# TODO json不是以{}开头

import traceback 
from mako.template import Template as tp

def __function__():
   stack = traceback.extract_stack()
   (filename, line, procname, text) = stack[-2]
   return procname

class field_type(object):
    def __init__(self):
        pass

    def is_random_name(self):
        return self.is_random

    def set_random(self):
        self.is_random = True

    def set_field_name(self, value):
        return self.field_name

    def get_field_name(self):
        return self.field_name

    def get_type(self):
        return self.type

    def get_value(self):
        return self.value

    def set_type(self, type):
        self.type = type

    def set_value(self, value):
        self.value = value

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

class list_item_type(field_type):
    def __init__(self):
        super(list_item_type, self).__init__()
        self.type = 'list_item_type'
        self.item_type = None
        self.item = None
        self.field_name = None
        self.is_random = False

    def __eq__(self, obj):
        obj_type = obj.get_type()
        if obj_type != self.get_type():
            return False
        if self.get_item_type() != obj.get_item_type():
            return False
        return self.get_value() == obj.get_value()

    def get_value(self):
        return self.item

    def set_value(self, value):
        self.item = value

    def set_item_type(self, type):
        self.item_type = type

    def get_item_type(self):
        return self.item_type

    def __str__(self):
        return '{type:list_item_type & item_type:%s}' % self.get_item_type()

class list_type(field_type):
    def __init__(self):
        super(list_type, self).__init__()
        self.type = 'list_type'
        self.items = None
        self.field_name = None
        self.is_random = False
        self.as_class_object = False

    def set_as_class_object(self):
        self.as_class_object = True

    def is_as_class_object(self):
        return self.as_class_object

    def __eq__(self, obj):
        obj_type = obj.get_type()
        if obj_type != self.get_type():
            return False
        if self.get_item_type() != obj.get_item_type():
            return False
        return self.get_one_item_value() == obj.get_one_item_value()

    def get_value(self):
        return self.items

    def get_one_item_value(self):
        return self.items[0]

    def get_item_type(self):
        return self.get_one_item_type()

    def get_one_item_type(self):
        return self.items[0].get_type()

    def set_value(self, values):
        self.items = values

    def __str__(self):
        return '[type:list_type & {%s}]' % ','.join(map(lambda x: str(x), self.items))

class map_item_type(field_type):
    def __init__(self):
        super(map_item_type, self).__init__()
        self.type = 'map_item_type'
        self.key_type = None
        self.value_type = None
        self.value = None
        self.key = None
        self.field_name = None
        self.is_random = False

    def __eq__(self, obj):
        obj_type = obj.get_type()
        if obj_type != self.get_type():
            return False
        if self.get_item_key_type() != obj.get_item_key_type() or self.get_item_value_type() != obj.get_item_value_type():
            return False
        return self.set_value_value() == obj.set_value_value()

    def set_value(self, key, value):
        self.key = key
        self.value = value

    def set_key_value(self, key):
        self.key = key

    def set_value_value(self, value):
        self.value = value

    def get_key_value(self):
        return self.key

    def get_value_value(self):
        return self.value

    def set_item_key_type(self, key):
        self.key_type = key

    def set_item_value_type(self, value):
        self.value_type = value

    def get_item_key_type(self):
        return self.key_type

    def get_item_value_type(self):
        return self.value_type

    def get_value(self):
        return self.key, self.value

    def set_item_type(self, key, value):
        self.key_type = key
        self.value_type = value

    def get_item_type(self):
        return self.key_type, self.value_type

    def __str__(self):
        return '{type:map_item_type & key_type:%s & value_type:%s & key_value:%s}' % (self.key_type, self.value_type, self.key)


class map_type(field_type):
    def __init__(self):
        super(map_type, self).__init__()
        self.type = 'map_type'
        self.items = None
        self.field_name = None
        self.is_random = False

    def __eq__(self, obj):
        obj_type = obj.get_type()
        if obj_type != self.get_type():
            return False

        if len(self.get_value()) != len(obj.get_value()):
            return False
        
        list_self_items = []
        list_obj_items = []
        for item in self.items:
            list_a.append({"item":item, "used":False})
        for item in obj.items:
            list_b.append({"item":item, "used":False})

        list_count = len(list_a)
        compare_ok_count = 0

        for self_item in list_self_items:
            for obj_item in list_obj_items:
                if obj_item["used"]:
                    continue
                if self_item["item"] == obj_item["item"]:
                    self_item["used"] = True
                    obj_item["used"] = True
                    compare_ok_count += 1
                    break

        return compare_ok_count == list_count

    def get_value(self):
        return self.items

    def set_value(self, value):
        self.items = value

    def __str__(self):
        return '{%s}' % ','.join(map(lambda x : str(x), self.items))


class string_type(field_type):
    def __init__(self):
        super(string_type, self).__init__()
        self.type = 'string_type'
        self.value = None
        self.name = 'std::string'
        self.field_name = None
        self.is_random = False

    def __eq__(self, obj):
        return self.get_type() == obj.get_type()

    def get_name(self):
        return self.name

    def __str__(self):
        return '{type:string & value:%s}' % self.value


class number_type(field_type):
    def __init__(self):
        super(number_type, self).__init__()
        self.type = 'number_type'
        self.value = None
        self.name = 'int'
        self.field_name = None
        self.is_random = False

    def __eq__(self, obj):
        return self.get_type() == obj.get_type()

    def get_name(self):
        return self.name

    def __str__(self):
        return '{type:number & value:%s}' % self.value

class json_parser(object):
    def __init__(self):
        self.parsed_fields = []

    def parse_list_item(self, values):
        #print __function__(), values

        token_count = len(values)
        poped_type = None
        parsed_type = list_item_type()
        item = self.parsed_fields.pop()
        parsed_type.set_item_type(item.get_type())
        parsed_type.set_value(item)
        self.parsed_fields.append(parsed_type)

    def parse_map_item(self, values):
        #print __function__(), values

        value = self.parsed_fields.pop()
        key = self.parsed_fields.pop()
        parsed_type = map_item_type()
        parsed_type.set_item_type(key.get_type(), value.get_type())
        parsed_type.set_value(key, value)
        self.parsed_fields.append(parsed_type)

    def parse_number(self, values):
        #print __function__(), values
        parsed_type = number_type()
        parsed_type.set_value(values[0])
        self.parsed_fields.append(parsed_type)

    def parse_string(self, values):
        #print __function__(), values
        parsed_type = string_type()
        parsed_type.set_value(values[0])
        self.parsed_fields.append(parsed_type)

    def parse_list(self, values):
        #print __function__(), values
        item_count = len(values)
        items = []
        for i in range(item_count):
            items.append(self.parsed_fields.pop())
        parsed_type = list_type()
        parsed_type.set_value(items)
        self.parsed_fields.append(parsed_type)

    def parse_map(self, values):
        #print __function__(), values
        item_count = len(values)
        items = []
        for i in range(item_count):
            items.append(self.parsed_fields.pop())
        parsed_type = map_type()
        parsed_type.set_value(items)
        self.parsed_fields.append(parsed_type)

    def fetch_parse_result(self):
        return self.parsed_fields.pop()


class json_grammar(object):
    def __init__(self):
        self.jp = json_parser()

        space = ~Star(Literal('\n') | Literal('\t') | Literal(' '))
        identifier = Word(Letter() | '_' | Digit())

        with Separator(space):
            item = Delayed()
            number = Real() > self.jp.parse_number
            string = ~Literal('"') & identifier & ~Literal('"') > self.jp.parse_string

            json_list_value = item
            json_list_item = json_list_value > self.jp.parse_list_item
            json_list_items = json_list_item[:, Drop(',')]
            json_list = ~Literal('[') & json_list_items & ~Literal(']')  > self.jp.parse_list
            json_map_key_string = ~Literal('"') & identifier & ~Literal('"') > self.jp.parse_string
            json_map_key_number = number
            json_map_key = json_map_key_string | json_map_key_number
            json_map_value = item
            json_map_item = json_map_key & ~Literal(':') & json_map_value > self.jp.parse_map_item
            json_map_items = json_map_item[:, Drop(',')]
            json_map = ~Literal('{') & json_map_items & ~Literal('}') > self.jp.parse_map
            base = string | number
            item += json_list | json_map | base

        self.json = space & item & space & ~Eos()

    def parse(self, string):
        self.json.parse(string)
        return self.jp.fetch_parse_result()

def get_all_class_info(class_info):
    todo = []
    class_infos = []
    class_infos.append({"name":"root_class", "class_info":class_info})
    unknown_idx = 0
    first = True
    while len(class_infos):
        obj = class_infos.pop()
        class_name = obj["name"]
        class_new_info = obj["class_info"]
        class_type = class_new_info.get_type()
        if class_type == 'map_type':
            first = False
            todo.append((class_name, class_new_info))
            for each_item in class_new_info.get_value():
                item_type = each_item.get_type()
                obj = {"name":each_item.get_key_value().get_value(), "class_info":each_item.get_value_value()}
                class_infos.append(obj)
        elif class_type  == 'list_type':
            if first:
                class_new_info.set_name('auto_%d' % unknown_idx)
                todo.append((class_name, class_new_info))
            first = False
            item_type = class_new_info.get_item_type()
            if item_type not in ['string_type', 'number_type']:
                obj = {"name":class_new_info.get_one_item_value().get_value(), "class_info":class_new_info.get_one_item_value()}
                class_infos.append(obj)
        elif class_type == 'list_item_type':
            first = False
            item_type = class_new_info.get_item_type()
            if item_type == 'map_type':
                map_obj = class_new_info.get_value()
                map_obj.set_name('auto_%d' % unknown_idx)
                obj = {"name": map_obj.get_name(), "class_info": map_obj}
                class_infos.append(obj)
            elif item_type == 'list_type':
                list_obj = class_new_info.get_value()
                list_obj.set_name('auto_%d' % unknown_idx)
                obj = {"name": list_obj.get_name(), "class_info": list_obj}
                class_infos.append(obj)
                list_obj.set_as_class_object()
                todo.append((obj["name"], list_obj))
            else:
                pass
        elif class_type == 'map_item_type':
            first = False
            _, item_type = class_new_info.get_item_type()
            key, value = class_new_info.get_value()
            if item_type not in ['string_type', 'number_type']:
                obj = {"name":class_new_info.get_key_value().get_value(), "class_info":class_new_info.get_value_value()}
                class_infos.append(obj)
        else:
            first = False
            pass
    return set(todo)

def define_class(classname, classinfo, filename):
    t = tp('''
struct ${class_name} {
    %if class_info.get_type() == 'map_type':
        %for field in class_info.get_value():
        <%
            item_key_type, item_value_type = field.get_item_type()
            item_key, item_value = field.get_value()
        %>
        %if item_value_type == 'list_type':
    std::vector<${field.get_value_value().get_one_item_value().get_value().get_name()}> ${item_key.get_value()};
        %elif item_value_type == 'map_type':
    ${item_key.get_value()} ${item_key.get_value()};
        %else:
    ${field.value.get_name()} ${item_key.get_value()};
        %endif
        %endfor
    %elif class_info.get_type() == 'list_type':
    <%
        print class_info.items[0]
        item_value = class_info.get_one_item_value()
        item_name = None
        try:
            item_name = item_value.get_value().get_name()
        except:
            item_name = item_value.get_name()
    %>
    std::vector<${item_name}> ${class_info.get_name()};
    %else:

    %endif
};

''')
    return t.render(class_info=classinfo, class_name=classname, fn=filename)

def define_classes(class_infos):
    code = ''
    for class_info in class_infos:
        code += define_class(class_info[0], class_info[1], 'test')
    return code


if __name__ == '__main__':
    json = json_grammar()
    json_obj = json.parse('{"a":{}, "obj":{"id":"20", "name":"my_name", "list":{"a":100}}}')
    all_classes = get_all_class_info(json_obj)
    code = define_classes(all_classes)
    #print(code)

    import json_serializor_generator
    test = json_serializor_generator.code_generator()
    print test.generate_cpp_file_from_code(code)
