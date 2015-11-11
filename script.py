# class parser(object):
#     def __init__(self):
#         self.field_types = []
#         self.field_names = []
#         self.field_is_vector = []
#         self.name = None

#     def parse_name(self, values):
#         self.name = values[0]

#     def parse_field(self, values):
#         #print 'parse_field', values
#         self.field_names.append(values[0])
#         if len(self.field_is_vector) == len(self.field_types):
#             return
#         self.field_is_vector.append(False)

#     def parse_vector(self, values):
#         #print 'parse_vector', values
#         self.field_types.append(values[0])
#         self.field_is_vector.append(True)

#     def parse_typename(self, values):
#         #print 'parse_typename', values
#         if not values[0]:
#             return
#         self.field_types.append(values[0])

#     def __str__(self):
#         return str(self.field_types) + str(self.field_names) + str(self.field_is_vector)

# p = parser()

# with Separator(space):
#     name = identifier > p.parse_name
#     t_vec = ~Literal('std') & ~Literal('::') & ~Literal('vector') & ~Literal('<') & identifier & ~Literal('>') > p.parse_vector
#     typename = t_vec | identifier > p.parse_typename
#     field = identifier & ~Literal(':') & typename & semicolon > p.parse_field
#     fields = field[:]
#     body = left_brace & fields & right_brace
#     item = name & body
# item = space & item & space & ~Eos()
# item.parse('hello {id:string; test:int; name:std::vector<int>;}')

# print(p)

# fields = ','.join(p.field_names)
# s = 'insert into tb_%s values(%s)' % (p.name, fields)
# print(s)


# struct = Delayed()

# space = ~Star(Literal('\n') | Literal('\t') | Literal(' '))
# identifier = Word(Letter() | '_', Letter() | '_' | Digit())
# number = Real()
# typename = identifier
# left_brace = ~Literal('{')
# right_brace = ~Literal('}')
# semicolon = ~Literal(';')

# with Separator(space):
#     struct_name = Literal('struct') & identifier
#     struct_field = typename & identifier & semicolon
#     struct_fields = (struct_field | struct)[:]
#     struct_body = left_brace & struct_fields & right_brace & Star(identifier) & semicolon
#     struct += struct_name & struct_body

# struct.parse("struct hello { int c; struct abc {}z; double d; }cde;")
