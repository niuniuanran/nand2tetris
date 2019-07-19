class CodeWriter(object):
    def __init__(self, compilation_engine):
        self.symbol_table = compilation_engine.symbol_table
        self.vm_stream = open(compilation_engine.file_path[:-5] + '.vm', 'w+')

    def write_code(self, string):
        self.vm_stream.write(string)

    def write_object_memo_alloc(self, memo_needed):
        self.vm_stream.write('push constant ' + str(memo_needed) + '\n')
        self.vm_stream.write('call Memory.alloc 1\n')
        self.vm_stream.write('pop pointer 0\n')

    def write_mid_arithmetic(self, op):
        command_dict = {'+': 'add\n', '-': 'sub\n', '*': 'call Math.multiply 2\n', '/': 'call Math.divide 2\n',
                        '&': 'and\n', '|': 'or\n', '>': 'gt\n', '<': 'lt\n', '=': 'eq\n'}
        self.vm_stream.write(command_dict[op])

    def write_unary_arithmetic(self, op):
        command_dict = {'-': 'neg\n', '~': 'not\n'}
        self.vm_stream.write(command_dict[op])

    def write_keyword_term(self, keyword_term):
        if keyword_term == 'true':
            self.vm_stream.write('push constant 0\nnot\n')
        elif keyword_term in 'false null':
            self.vm_stream.write('push constant 0\n')
        elif keyword_term == 'this':
            self.vm_stream.write('push pointer 0\n')

    def write_string_constant(self, string):
        str_len = len(string)
        self.vm_stream.write('push constant ' + str(str_len) + '\n' + 'call String.new 1\n')
        for c in string:
            self.vm_stream.write('push constant ' + str(ord(c)) + '\n')
            self.vm_stream.write('call String.appendChar 2\n')

    def write_subroutine_call(self, primary_name, subroutine_name, arg_num):
        self.vm_stream.write('call ' + primary_name + '.' + subroutine_name + ' ' + str(arg_num) + '\n')




