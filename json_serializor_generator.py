from lepl import *
import sys
import os
from mako.template import Template as tp

def debug(values, enable=False):
    if enable == False:
        pass
    else:
        print(values)

class field_info(object):
    def __init__(self, container, is_type_basic, type_name, field_name):
        self.container = container
        self.is_type_basic = is_type_basic
        self.type_name = type_name
        self.field_name = field_name

    def __str__(self):
        if self.is_type_basic == False:
            type_info = 'user_defined'
        else:
            type_info = 'basic'
        if self.container == 'NULL':
            if self.type_name != 'string':
                return '%s %s' % (self.type_name, self.field_name)
            else:
                return 'std::string %s' % (self.field_name)
                
        return 'std::%s<%s> %s' % (self.container, self.type_name, self.field_name)

class one_struct_parser(object):

    def __init__(self):
        self.struct_name = None
        self.last_type_enable = False
        self.container = None
        self.type_name = None
        self.is_type_basic = None
        self.field_name = None
        self.fields = []
        self.structs = []

    def reinit(self):
        self.struct_name = None
        self.last_type_enable = False
        self.container = None
        self.type_name = None
        self.is_type_basic = None
        self.field_name = None
        self.fields = []

    def parse_struct_name(self, values):
        debug('in parse_struct_name, %s' %(values[1]))
        self.struct_name = values[1]

    def parse_field_info(self, values):
        if not self.last_type_enable:
            self.is_type_basic = False
            self.container = 'NULL'
            self.type_name = values[0]
        self.last_type_enable = False

        self.field_name = values[1]
        
        field_info_obj = field_info(self.container, self.is_type_basic, self.type_name, self.field_name)
        self.fields.append(field_info_obj)
        debug('in parse_field_type, %s:%s' % (str(field_info_obj), self.field_name))

    def parse_basic_type(self, values):
        if len(values):
            self.container = 'NULL'
            self.is_type_basic = True
            self.type_name = values[0]

            self.last_type_enable = True
            debug('in parse_basic_type, %s' % self.type_name)

    def parse_vector_type1(self, values):
        self.container = values[0]
        if self.last_type_enable:
            self.is_type_basic = True
        else:
            self.is_type_basic = False
            self.type_name = values[1]
        self.last_type_enable = True
        debug('in parse_vector_type1, %s~%s' %(values[0], values[1]))

    def parse_vector_type2(self, values):
        self.container = 'vector'
        if self.last_type_enable:
            self.is_type_basic = True
        else:
            self.is_type_basic = False
            self.type_name = values[0]
        self.last_type_enable = True
        debug('in parse_vector_type2, %s~%s' %('vector', values[0]))


    def parse_struct_complete(self, values):
        self.structs.append({"struct_name": self.struct_name, "fields": self.fields})
        self.reinit()

    def __str__(self):
        from mako.template import Template as tp
        info = tp('''
        %for struct in this.structs:
class ${struct["struct_name"]} {
public:
            %for field in struct["fields"]:
    ${str(field)};
            %endfor
public:
    bool decode(const std::string &jsonbuf);
    void decode_from_json_object(const Json::Value &jsonobj);
    Json::Value encode_to_json_object();
    std::string encode(bool readable);
};
        %endfor
''')
        return info.render(this=self)

class structs_parser(object):
    def __init__(self):
        parser = one_struct_parser()
        self.parser = parser

        # drop_space = ~Star(Literal('\t') | Literal(' '))
        drop_space = ~Star(Literal('\n') | Literal('\t') | Literal(' '))
        kw_struct = Literal('struct') | Literal('class')
        left_brace = ~Literal('{')
        right_brace = ~Literal('}')
        semicolon = ~Literal(';')
        identifier = Word(Letter() | '_', Letter() | '_' | Digit())

        with Separator(drop_space):
            typename = Delayed()
            vector_type = ( ~Literal('std') & ~Literal('::') & Literal('vector') ) | Literal('vector')
            string_type = Literal('string') | ( ~Literal('std') & ~Literal('::') & Literal('string') ) | ( Literal('char') & Literal('*') )

            vector1 = vector_type & ~Literal('<') & typename & ~Literal('>') > self.parser.parse_vector_type1
            # comment = ~Literal('//') & (

            base_typename = Literal('int') | string_type [:,...] > self.parser.parse_basic_type
            typename += vector1 | base_typename | identifier

            decl_struct_name = kw_struct & identifier > self.parser.parse_struct_name
            field = typename & identifier & semicolon > self.parser.parse_field_info
            mutil_field = field[:]

            struct_body = left_brace & mutil_field & right_brace & semicolon
            struct_decl =  decl_struct_name &  struct_body > self.parser.parse_struct_complete
            mutil_struct_decl = struct_decl[:]
        mutil_struct_decl = drop_space & mutil_struct_decl & drop_space & Eos()

        self.mutil_struct_decl = mutil_struct_decl

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

        %if field.container == 'NULL':
        <%
            field_name = field.field_name
            type_name = field.type_name
        %>
    if ( root.isObject() && root.isMember("${field_name}") )
    {
        tmp = root["${field_name}"];
        if ( !tmp.isNull() )
        {
            %if field.is_type_basic:
                %if type_name == 'int':
            ${field_name} = tmp.asInt();
                %else:
            ${field_name} = tmp.asString();
                %endif
            %else:
            ${field_name}.decode_from_json_object(tmp);
            %endif
        }
    }
    %endif
    %endfor

    int size = 0;
    int i = 0;
    %for field in struct["fields"]:
    <%
        field_name = None
        type_name = None
        if field.container == 'vector':
            field_name = field.field_name
            type_name = field.type_name
    %>
    %if field_name:
    if ( root.isObject() && root.isMember("${field_name}") )
    {
        Json::Value array_${field_name} = root["${field_name}"];
        if ( !array_${field_name}.isNull() )
        {
            size = array_${field_name}.size();
            for ( i = 0; i < size; i++ ) {
                %if field.is_type_basic:
                    %if type_name == 'int':
                ${field_name}.push_back(array_${field_name}[i].asInt());
                    %else:
                ${field_name}.push_back(array_${field_name}[i].asString());
                    %endif
                %else:
                ${type_name} item;
                item.decode_from_json_object(array_${field_name}[i]);
                ${field_name}.push_back(item);
                %endif
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

    %if field.container == 'NULL':
    <%
        field_name = field.field_name
        type_name = field.type_name
    %>
        %if field.is_type_basic:
    root["${field_name}"] = ${field_name};
        %else:
    root["${field_name}"] = ${field_name}.encode_to_json_object();
        %endif
    %endif
    %endfor


    int size = 0;
    int i = 0;
    %for field in struct["fields"]:
    <%
        field_name = None
        type_name = None
        if field.container == 'vector':
            field_name = field.field_name
            type_name = field.type_name
    %>
    %if field_name:
    size = ${field_name}.size();
    root["${field_name}"] = Json::Value(Json::arrayValue);

    for ( i = 0; i < size; i++ ) {
        %if field.is_type_basic:
        root["${field_name}"].append(${field_name}[i]);
        %else:
        root["${field_name}"].append(${field_name}[i].encode_to_json_object());
        %endif
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
        code = generator.generate_cpp_file_from_code(content, struct_file_name)

        hpp_name = struct_file_name + '.hpp'
        hpp_path = os.path.join(os.path.dirname(struct_file_path), hpp_name)
        hpp_file = open(hpp_path, 'w')
        hpp_file.write(code["hpp"])
        hpp_file.close()

        cpp_name = struct_file_name + '.cpp'
        cpp_path = os.path.join(os.path.dirname(struct_file_path), cpp_name)
        cpp_file = open(cpp_path, 'w')
        cpp_file.write(code["cpp"])
        cpp_file.close()

