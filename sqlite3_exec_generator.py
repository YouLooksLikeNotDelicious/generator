from lepl import *
import sys
import os

global_structs = []

class struct(object):
    def __init__(self):
        self.fields = []

    def set_name(self, name):
        self.name = name

    def set_field(self, field_type, field_name):
        self.fields.append({"field_type": field_type, "field_name": field_name})

    def __str__(self):
        l = len(self.fields)
        begin = 'struct %s {\n' % self.name
        body = ''
        for each in self.fields:
            body += '\t%s %s;\n' %(each["field_type"], each["field_name"])
        end = '};'
        struct_info = '%s%s%s' %(begin, body, end);
        return struct_info

def set_struct(values):
    struct_name = values[1]
    fields = values[2::]
    fields_type = fields[0::2]
    fields_name = fields[1::2]
    new_struct = struct()
    new_struct.set_name(struct_name)
    count_type = len(fields_type)
    count_name = len(fields_name)
    assert(count_name == count_type)
    for i in xrange(count_type):
        new_struct.set_field(fields_type[i], fields_name[i])
    global_structs.append(new_struct)

class struct_parser(object):
    def __init__(self):
        global global_structs
        if len(global_structs) != 0:
            global_structs = []

        drop_space = ~Star(Literal('\n') | Literal('\t') | Literal(' '))
        kw_struct = Literal('struct')
        left_brace = ~Literal('{')
        right_brace = ~Literal('}')
        semicolon = ~Literal(';')
        identifier = Word(Letter() | '_', Letter() | '_' | Digit())

        with Separator(drop_space):
            typename = Literal('int') | Literal('string') | Literal('std::string') | (Literal('char') & Literal('*'))[:,...]
            decl_struct_name = kw_struct & identifier
            field = typename & identifier & semicolon
            mutil_field = field[:]
            struct_body = left_brace & mutil_field & right_brace & semicolon
            struct_decl =  decl_struct_name &  struct_body > set_struct
            mutil_struct_decl = struct_decl[:]

        mutil_struct_decl = drop_space & mutil_struct_decl & drop_space & Eos()
        self.parser = mutil_struct_decl.parse

    def __call__(self, defination):
        global global_structs
        self.parser(defination)
        self.structs = global_structs
        return global_structs

from mako.template import Template as tp
def add_struct_info(struct_info):
    t = tp('''
class ${struct_info_object.name} : public sqlite3_generator::base_column {
private:
    <%
    struct_info = struct_info_object
    field_counts = len(struct_info.fields)
    %>
    %for i in xrange(field_counts):
    <%
    cur_field_name = struct_info.fields[i]["field_name"]
    cur_field_type = struct_info.fields[i]["field_type"]
    if cur_field_type == "char*" or cur_field_type == "string":
        cur_field_type = "std::string"
    %>
    ${cur_field_type} ${cur_field_name};
    %endfor
public:
    <%
    struct_info = struct_info_object
    field_counts = len(struct_info.fields);
    %>
    %for i in xrange(field_counts):
    <%
    cur_field_name = struct_info.fields[i]["field_name"]
    cur_field_type = struct_info.fields[i]["field_type"]
    if cur_field_type == "char*" or cur_field_type == "string":
        cur_field_type = "std::string"
    %>

    <%
    if cur_field_type == "std::string":
        param_type = 'const std::string &'
    else:
        param_type = 'int'
    %>

    void set_${cur_field_name} (${param_type} ${cur_field_name}_) {
        this->${cur_field_name} = ${cur_field_name}_;
    }

    const ${cur_field_type}& get_${cur_field_name}() {
        return ${cur_field_name};
    }

    const ${cur_field_type}& get_${cur_field_name}() const{
        return ${cur_field_name};
    }
    %endfor

    sqlite3_generator::type_info get_field(const std::string &field_name) {
        sqlite3_generator::type_info ti;
        %for i in xrange(field_counts):
        <%
        cur_field_name = struct_info.fields[i]["field_name"]
        cur_field_type = struct_info.fields[i]["field_type"]
        %>
        if ( field_name == "${cur_field_name}" ) {
        %if cur_field_type == "int":
            ti.type = sqlite3_generator::type_info::integer;
        %elif cur_field_type == "char*" or cur_field_type == "string" or cur_field_type == "std::string":
            ti.type = sqlite3_generator::type_info::string;
        %else:
            assert(false);
        %endif
            ti.data = static_cast<void *>(&this->${cur_field_name});
        }
        %endfor
        return ti;
    }
};''')
    return t.render(struct_info_object=struct_info)

def generate_cpp_file_from_file(cpp_filepath):
    with open(cpp_filepath) as file:
        cpp_code = file.read()

    code = generate_cpp_file_from_code(cpp_code)
    with open(cpp_filepath + '.new.cpp', 'w') as file:
        file.write(code)

def generate_cpp_file_from_code(cpp_code, struct_file_name):
    cpp_parser = struct_parser()
    structs = cpp_parser(cpp_code)

    code = '''#ifndef {0}_INCLUDED
#define {0}_INCLUDED

#include <vector>
#include <string>
#include <map>
#include "../sqlite3.h"

'''.format(struct_file_name.upper())
    for struct_obj in structs:
        code += add_struct_info(struct_obj)
    code += '''

#endif
'''
    return code

if __name__ == '__main__':
    if len(sys.argv) > 1:
        for struct_file_path in sys.argv[1:]:
            struct_file = open(struct_file_path, 'r')
            content = struct_file.read()
            struct_file.close()

            struct_file_name = os.path.basename(struct_file_path)
            struct_file_name = os.path.splitext(struct_file_name)[0];
            cpp_code = generate_cpp_file_from_code(content, struct_file_name)
            cpp_name = struct_file_name + '.hpp'
            cpp_path = os.path.join(os.path.dirname(struct_file_path), cpp_name)
            cpp_file = open(cpp_path, 'w')
            cpp_file.write(cpp_code)
            cpp_file.close()
    else:
        print("please select some struct files")
        exit(0)
