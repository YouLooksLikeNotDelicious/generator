from lepl import *
import sys
import os
from mako.template import Template as tp

def debug(values, enable=False):
    if enable == False:
        pass
    else:
        print(values)

class field(object):
    def __init__(self, field_name=None, type_name=None, self_type=None):
        self.field_name = field_name
        self.type_name = type_name
        self.self_type = self_type

    def __str__(self):
        return 'field_name: %s, type_name: %s' % (self.field_name, self.type_name)

class cpp_type(object):
    def __init__(self, selftype, subtype=None, container=None):
        self.subtype = subtype
        self.selftype = selftype
        self.container = container
        self.key_type = None
        self.value_type = None
        self.item_type = None

    def get_type(self):
        return self.selftype

    def is_builtin(self):
        return self.selftype == None

    def is_container(self):
        return self.container == None

    def get_container(self):
        return self.container

    def is_map(self):
        return self.container == 'map'

    def is_vector(self):
        return self.container == 'vector'

    def get_sub_type(self):
        if self.is_builtin():
            return None
        if self.is_vector():
            return self.item_type
        if self.is_map():
            return {"key": self.key_type, "value": self.value_type}
        return None


class parse(object):
    def __init__(self):
        self.token = []
        self.field = []
        self.structs = []

    def parse_struct(self, values):
        self.structs.append({"struct_name": values[1], "fields": self.field})
        self.field = []
        self.token = []
        debug('in parse_struct token: %s' % self.structs[-1])

    def parse_basic_type(self, values):
        typeinfo = 'builtin'
        if values[0] != 'string' and values[0] != 'int':
            typeinfo = 'userdefine'
        if values[0] == 'string':
            values[0] = 'std::string'
        self.token.append({"name": values[0], "type": typeinfo})
        debug('in parse_basic_type token: %s' % self.token[-1])

    def parse_map_type(self, values):
        assert(values[0] == 'map')
        value_type = self.token.pop()
        key_type = self.token.pop()
        key_type_name = key_type["name"]
        value_type_name = value_type["name"]
        if key_type_name == 'string':
            key_type_name = 'std::string'
        if value_type_name == 'string':
            value_type_name = 'std::string'
        self.token.append({"name": 'std::map < %s, %s >' % (key_type_name, value_type_name), "type": 'map', "sub_type": {"key": key_type_name, "value": value_type_name}})
        debug('in parse_map_type token: %s' % self.token[-1])

    def parse_vector_type(self, values):
        assert(values[0] == 'vector')
        item_type = self.token.pop()
        item_type_name = item_type["name"]
        if item_type_name == 'string':
            item_type_name = 'std::string'
        self.token.append({"name": 'std::vector < %s >' % item_type["name"], "type": "vector", "sub_type": item_type_name})
        debug('in parse_vector_type token: %s' % self.token[-1])

    def parse_field(self, values):
        field_type = self.token.pop()
        field_name = values[1]
        self.field.append(field(field_name, field_type))
        debug('in parse_field field: %s' % self.field[-1])

    def __str__(self):
        decl_tp = tp('''
%for struct in all_structs:
class ${struct["struct_name"]} {
public:
    %for field in struct["fields"]:
    ${field.type_name["name"]}  ${field.field_name};
    %endfor
public:
    bool decode(const std::string &jsonbuf);
    void decode_from_json_object(const Json::Value &jsonobj);
    Json::Value encode_to_json_object();
    std::string encode(bool readable);
};
%endfor
''')
        decl = decl_tp.render(all_structs=self.structs)
        return decl

class structs_parser(object):
    def __init__(self):
        parser = parse()
        self.parser = parser

        drop_space = ~Star(Literal('\n') | Literal('\t') | Literal(' '))
        kw_struct = Literal('struct') | Literal('class')
        left_brace = ~Literal('{')
        right_brace = ~Literal('}')
        semicolon = ~Literal(';')
        identifier = Word(Letter() | '_', Letter() | '_' | Digit())

        with Separator(drop_space):

            struct = Delayed()
            typename = Delayed()

            vector_type_special = ( ~Literal('std') & ~Literal('::') & Literal('vector') ) | Literal('vector')
            map_type_special = ( ~Literal('std') & ~Literal('::') & Literal('map') ) | Literal('map')

            basic = Literal('int') | Literal('string') | (~Literal('std') & ~Literal('::') & Literal('string')) | identifier >self.parser.parse_basic_type
            cpp_vector = vector_type_special & ~Literal('<') & typename & ~Literal('>')  > self.parser.parse_vector_type
            cpp_map = map_type_special & ~Literal('<') & typename & ~Literal(',') & typename & ~Literal('>') > self.parser.parse_map_type

            typename += cpp_vector | cpp_map | basic

            struct_name = Literal('struct') & identifier
            struct_field = typename & identifier & semicolon > self.parser.parse_field
            struct_fields = (struct_field[:] | struct[:])
            struct_body = left_brace & struct_fields & right_brace & Star(identifier) & semicolon
            struct_decl = struct_name & struct_body  > self.parser.parse_struct
            struct += struct_decl

            mutil_struct = struct[:]

        mutil_struct = drop_space & mutil_struct & drop_space & Eos()

        self.mutil_struct_decl = mutil_struct

    def parse(self, code):
        self.mutil_struct_decl.parse(code)
        return self.parser

class code_generator(object):

    def __init__(self):
        self.structs = None
        self.parser = structs_parser()
        self.template_init()

    def template_init(self):
        self.template = tp('''
void ${struct["struct_name"]}::decode_from_json_object(const Json::Value &root)
{
    Json::Value tmp;
    %for field in struct["fields"]:

    <%
        field_name = field.field_name
        type_name = field.type_name["type"]
    %>
    %if type_name == 'builtin' or type_name == 'userdefine':
    if ( root.isObject() && root.isMember("${field_name}") ) {
        tmp = root["${field_name}"];
        if ( !tmp.isNull() )
        {
            %if field.type_name["name"] == 'int':
            ${field_name} = tmp.asInt();
            %elif field.type_name["name"] == 'string' or field.type_name["name"] == 'std::string':
            ${field_name} = tmp.asString();
            %elif field.type_name["type"] == 'userdefine':
            ${field_name}.decode_from_json_object(tmp);
            %else:
            <%
                assert(False)
            %>
            %endif
        }
    }
    %endif
    %endfor

    %for field in struct["fields"]:
    <%
        field_name = field.field_name
    %>
    %if field.type_name["type"] == 'vector':
    <%
        type_name = field.type_name["sub_type"]
    %>
    if ( root.isObject() && root.isMember("${field_name}") ) {
        const Json::Value &array_${field_name} = root["${field_name}"];
        if ( !array_${field_name}.isNull() )
        {
            int size = array_${field_name}.size();
            for ( int i = 0; i < size; i++ ) {
                %if type_name == 'int':
                ${field_name}.push_back(array_${field_name}[i].asInt());
                %elif type_name == 'std::string' or type_name == 'string':
                ${field_name}.push_back(array_${field_name}[i].asString());
                %else:
                ${type_name} item;
                item.decode_from_json_object(array_${field_name}[i]);
                ${field_name}.push_back(item);
                %endif
            }
        }
    }
    %elif field.type_name["type"] == 'map':
    if ( root.isObject() && root.isMember("${field_name}") ) {
        const Json::Value map_${field_name} = root["${field_name}"];
        if ( !map_${field_name}.isNull() ) {
            for( Json::ValueIterator it = map_${field_name}.begin(); it != map_${field_name}.end(); ++it ) {
            <%
                key_type_name = field.type_name["sub_type"]["key"]
                value_type_name = field.type_name["sub_type"]["value"]
                if key_type_name == 'std::string' or key_type_name == 'string':
                    key_function = 'asString()'
                elif key_type_name == 'int':
                    key_function = 'asInt()'
                else:
                    assert(False)
                if value_type_name == 'std::string' or value_type_name == 'string':
                    value_function = 'asString()'
                elif value_type_name == 'int':
                    value_function = 'asInt()'
                else:
                    assert(False)
            %>
                std::string key = it.key().${key_function};
                ${field_name}[key] = map_${field_name}[key].${value_function};
            }
        }
    }   
    %endif
    %endfor
}

bool ${struct["struct_name"]}::decode(const std::string &jsonbuf)
{
    Json::Reader reader;
    Json::Value root;
    if ( !reader.parse(jsonbuf, root) ) {
        return false;
    }
    decode_from_json_object(root);
    return true;
}

Json::Value ${struct["struct_name"]}::encode_to_json_object()
{
    Json::Value root(Json::objectValue);

    %for field in struct["fields"]:

    <%
        field_name = field.field_name
        type_name = field.type_name["type"]
    %>
    %if field.type_name["name"] == 'int' or field.type_name["name"] == 'string' or field.type_name["name"] == 'std::string':
    root["${field_name}"] = ${field_name};
    %elif type_name == 'userdefine':
    root["${field_name}"] = ${field_name}.encode_to_json_object();
    %endif
    %endfor


    int size = 0;
    int i = 0;
    %for field in struct["fields"]:
    <%
        field_name = field.field_name
        type_name = field.type_name["type"]
    %>
    %if field.type_name["type"] == 'vector':
    size = ${field_name}.size();
    root["${field_name}"] = Json::Value(Json::arrayValue);
    <%
    type_name = field.type_name["sub_type"]
    %>
    for ( i = 0; i < size; i++ ) {
        %if type_name == 'int' or type_name == 'string' or type_name == 'std::string':
        root["${field_name}"].append(${field_name}[i]);
        %else:
        root["${field_name}"].append(${field_name}[i].encode_to_json_object());
        %endif
    }
    // map in map, how to do ?
    %elif field.type_name["type"] == 'map':
    <%
        key_type_name = field.type_name["sub_type"]["key"]
        value_type_name = field.type_name["sub_type"]["value"]

    %>
    root["${field_name}"] = Json::Value(Json::objectValue);
    for ( std::map< ${key_type_name}, ${value_type_name} >::iterator it = ${field_name}.begin(); it != ${field_name}.end(); ++it) {
        root["${field_name}"][(*it).first] = (*it).second;
    }
    %endif
    %endfor
    return root;
}

std::string ${struct["struct_name"]}::encode(bool readable)
{
    Json::Value root = encode_to_json_object();
    if ( readable )
    {
        Json::StyledWriter writer;
        return writer.write(root);
    }
    else
    {
        Json::FastWriter writer;
        return writer.write(root);
    }
}

''')
   
    def generate_cpp_file_from_code(self, cpp_code, struct_file_name):
        parser = self.parser.parse(cpp_code)
        self.structs = parser.structs

        codes = {}
        code = '''#ifndef {0}_INCLUDED
#define {0}_INCLUDED

#include <string>
#include <vector>
#include <map>

#include <jsoncpp/json/json.h>
'''.format(struct_file_name)
        code += str(parser)
        code += '''\n#endif'''

        codes["hpp"] = code

        code = '#include "%s"\n' % (struct_file_name + '.hpp')
        for each_struct in self.structs:
            code += self.template.render(struct=each_struct)
        
        codes["cpp"] = code
        return codes

if __name__ == '__main__':
    generator = None
    if len(sys.argv) > 1:
        generator = code_generator()
    else:
        print("please select some struct files")
        exit(0)

    for struct_file_path in sys.argv[1:]:
        struct_file = open(struct_file_path, 'r')
        content = struct_file.read()
        struct_file.close()

        struct_file_name = os.path.basename(struct_file_path)
        struct_file_name = os.path.splitext(struct_file_name)[0]

        
        cpp = generator.generate_cpp_file_from_code(content, struct_file_name)

        hpp_name = struct_file_name + '.hpp'
        hpp_path = os.path.join(os.path.dirname(struct_file_path), hpp_name)
        hpp_file = open(hpp_path, 'w')
        hpp_file.write(cpp["hpp"])
        hpp_file.close()

        cpp_name = struct_file_name + '.cpp'
        cpp_path = os.path.join(os.path.dirname(struct_file_path), cpp_name)
        cpp_file = open(cpp_path, 'w')
        cpp_file.write(cpp["cpp"])
        cpp_file.close()
