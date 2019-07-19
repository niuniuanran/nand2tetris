from SymbolTable import SymbolTable
from CodeWriter import CodeWriter


class CompilationEngine(object):
    def __init__(self, tokenizer, file_path):
        self.tokenizer = tokenizer
        self.file_path = file_path
        self.symbol_table = SymbolTable()
        self.class_name = ""
        self.code_writer = CodeWriter(self)
        self.label_ind = 0

    def compile_class(self):
        self.tokenizer.token_advance()
        # print('Compiling class ', end='')
        self.eat_keyword("class")
        # print(self.tokenizer.curr_token)
        self.class_name = self.eat_identifier()
        self.eat_symbol("{")
        while self.tokenizer.curr_token in 'static field':
            self.compile_class_var_dec()

        while self.tokenizer.curr_token in 'constructor function method':
            self.compile_subroutine_dec()
        self.eat_symbol("}")

    def compile_class_var_dec(self):
        # print('compiling class var dec, current line:', self.tokenizer.curr_line)
        curr_kind = self.eat_keyword("static field")
        curr_type = self.eat_type()  # this eats the type
        curr_name = self.eat_identifier()  # this eats varName
        self.symbol_table.load_var(curr_name, curr_type, curr_kind)
        while self.tokenizer.curr_token != ';':
            self.eat_symbol(',')
            curr_name = self.eat_identifier()  # this eats the varName
            self.symbol_table.load_var(curr_name, curr_type, curr_kind)
        self.eat_symbol(';')
        print('class table', self.symbol_table.class_table)

    def compile_subroutine_dec(self):
        # print('compiling subroutine dec, current line:', self.tokenizer.curr_line)
        curr_subroutine_type = self.eat_keyword('constructor function method')
        self.eat_type()
        curr_subroutine_name = self.eat_identifier()  # this eats the subroutine name
        self.code_writer.write_code("function " + self.class_name + '.' + curr_subroutine_name + ' ')

        self.symbol_table.new_subroutine()
        if curr_subroutine_type == 'method':
            self.symbol_table.load_var('this', self.class_name, 'argument')

        self.eat_symbol('(')
        self.compile_parameter_list()
        self.eat_symbol(')')
        self.compile_subroutine_body(curr_subroutine_type)
        print('SUBROUTINE VARIABLE TABLE FOR', curr_subroutine_type, curr_subroutine_name,
              self.symbol_table.subroutine_table)

    def compile_parameter_list(self):
        # print('compiling parameter list, current token:', self.tokenizer.curr_token)
        if self.tokenizer.curr_token != ')':
            curr_type = self.eat_type()
            curr_name = self.eat_identifier()  # varName
            self.symbol_table.load_var(curr_name, curr_type, 'argument')
            while self.tokenizer.curr_token != ')':
                self.eat_symbol(',')
                curr_type = self.eat_type()
                curr_name = self.eat_identifier()
                self.symbol_table.load_var(curr_name, curr_type, 'argument')

    def compile_subroutine_body(self, sub_type):
        # print('compiling subroutine body, current line:', self.tokenizer.curr_line)
        self.eat_symbol('{')
        while self.tokenizer.curr_token == 'var':
            self.compile_var_dec()  # collect all the variable declarations
        # AFTER COMPILING VARIABLE DECLARATION, ALL THE LOCAL VARIABLES HAVE BEEN SAVED IN THE SUBROUTINE SYMBOL TABLE
        # SO NOW YOU KNOW HOW MANY LOCAL VARIABLES YOU NEED FOR DECLARING THE FUNCTION.
        self.code_writer.write_code(str(self.symbol_table.sub_running_index[1])+'\n')
        # write in the number of local variables

        # INITIALIZE CONSTRUCTOR AND METHOD STATUS OF MEMORY AND ARGUMENT
        if sub_type == 'constructor':
            self.code_writer.write_object_memo_alloc(self.symbol_table.class_running_index[1])  # write in memory allocation
        if sub_type == 'method':
            self.code_writer.write_code('push argument 0\npop pointer 0\n')

        self.compile_statements()
        self.eat_symbol('}')

    def compile_var_dec(self):
        # print('compiling var dec, current line:', self.tokenizer.curr_line)
        self.eat_keyword('var')
        curr_type = self.eat_type()
        var_name = self.eat_identifier()  # varName
        self.symbol_table.load_var(var_name, curr_type, 'local')
        while self.tokenizer.curr_token != ';':
            self.eat_symbol(',')
            var_name = self.eat_identifier()  # varName
            self.symbol_table.load_var(var_name, curr_type, 'local')
        self.eat_symbol(';')

    def compile_statements(self):
        # print('compiling statements, current line:', self.tokenizer.curr_line)
        statement_types = 'return let do if while'
        while self.tokenizer.curr_token in statement_types:
            if self.tokenizer.curr_token == 'return':
                self.compile_return_statement()
            elif self.tokenizer.curr_token == 'if':
                self.compile_if_statement()
            elif self.tokenizer.curr_token == 'while':
                self.compile_while_statement()
            elif self.tokenizer.curr_token == 'do':
                self.compile_do_statement()
            elif self.tokenizer.curr_token == 'let':
                self.compile_let_statement()

    def compile_return_statement(self):
        # print('compiling return statement, current line:', self.tokenizer.curr_line)

        self.eat_keyword('return')
        if self.tokenizer.curr_token == ';':
            self.code_writer.write_code('push constant 0\nreturn\n')
        if self.tokenizer.curr_token != ';':
            self.compile_expression()
            self.code_writer.write_code('return\n')
        self.eat_symbol(';')

    def compile_while_statement(self):
        # print('compiling while statement, current line:', self.tokenizer.curr_line)
        self.label_ind = self.label_ind + 1
        curr_label_ind = str(self.label_ind)

        self.eat_keyword('while')
        self.code_writer.write_code('label START_LOOP' + curr_label_ind + '\n')
        self.eat_symbol('(')
        self.compile_expression()
        self.eat_symbol(')')
        self.code_writer.write_code('not\n')
        self.code_writer.write_code('if-goto FINISH_WHILE' + curr_label_ind + '\n')
        self.eat_symbol('{')
        self.compile_statements()
        self.eat_symbol('}')
        self.code_writer.write_code('goto START_LOOP' + curr_label_ind + '\n')
        self.code_writer.write_code('label FINISH_WHILE' + curr_label_ind + '\n')

    def compile_if_statement(self):
        # print('compiling if statement, current line:', self.tokenizer.curr_line)
        self.label_ind += 1
        curr_label_ind = str(self.label_ind)

        self.eat_keyword('if')
        self.eat_symbol('(')
        self.compile_expression()
        self.eat_symbol(')')
        self.code_writer.write_code('not\n')
        self.code_writer.write_code('if-goto IF_FALSE' + curr_label_ind + '\n')
        self.eat_symbol('{')
        self.compile_statements()
        self.eat_symbol('}')
        self.code_writer.write_code('goto FINISH_IF' + curr_label_ind + '\n')
        self.code_writer.write_code('label IF_FALSE' + curr_label_ind + '\n')
        if self.tokenizer.curr_token == 'else':
            self.eat_keyword('else')
            self.eat_symbol('{')
            self.compile_statements()
            self.eat_symbol('}')
        self.code_writer.write_code('label FINISH_IF' + curr_label_ind + '\n')

    def compile_do_statement(self):
        # print('compiling do statement, current line:', self.tokenizer.curr_line)

        self.eat_keyword('do')
        self.compile_subroutine_call()
        self.code_writer.write_code("pop temp 0\n")
        self.eat_symbol(';')

    def compile_let_statement(self):
        # print('compiling let statement, current line:', self.tokenizer.curr_line)

        self.eat_keyword('let')
        primary = self.eat_identifier()  # var name
        target_kind, target_ind = self.symbol_table.locate_var(primary)
        if self.tokenizer.curr_token == '[':
            self.eat_symbol('[')
            self.compile_expression()
            self.eat_symbol(']')
            self.code_writer.write_code('push ' + target_kind + ' ' + target_ind + '\n')
            self.code_writer.write_code('add\n')
            self.eat_symbol('=')
            self.compile_expression()
            self.eat_symbol(';')
            self.code_writer.write_code('pop temp 0\n')
            self.code_writer.write_code('pop pointer 1\n')
            self.code_writer.write_code('push temp 0\n')
            self.code_writer.write_code('pop that 0\n')

        else:
            self.eat_symbol('=')
            self.compile_expression()
            self.eat_symbol(';')
            self.code_writer.write_code('pop ' + target_kind + ' ' + target_ind + '\n')

    # subroutine call: subroutineName+expressionList, or className.subroutineName+expressionList
    def compile_subroutine_call(self, primary_name=""):
        subroutine_name = ""
        is_method = 0

        if len(primary_name) == 0:
            primary_name = self.eat_identifier()

        if self.tokenizer.curr_token == '(':  # calling a method of the current class
            called_class_name, subroutine_name = self.class_name, primary_name
            self.code_writer.write_code('push pointer 0\n')
            is_method = 1
        elif self.tokenizer.curr_token == '.':  # calling a method or function of the given class, primary name can be
                                                    # object name OR class name.
            self.eat_symbol('.')
            called_class_name, subroutine_name = primary_name, self.eat_identifier()

        if is_method == 0 and self.symbol_table.is_a_var(primary_name):
            called_class_name = self.symbol_table.var_type(primary_name)
            var_kind, var_ind = self.symbol_table.locate_var(primary_name)
            self.code_writer.write_code('push ' + var_kind + ' ' + var_ind + '\n')
            is_method = 1
        if is_method == 0:
            called_class_name = primary_name

        self.eat_symbol('(')
        arg_num = self.compile_expression_list()
        self.eat_symbol(')')



        if is_method == 1:
            arg_num += 1

        self.code_writer.write_subroutine_call(called_class_name, subroutine_name, arg_num)

    # expression list: '(expression, expression, ...)', 0 or more expressions
    def compile_expression_list(self):
        # print('compiling expression list, current line:', self.tokenizer.curr_line)
        arg_num = 0
        if self.tokenizer.curr_token != ')':
            self.compile_expression()
            arg_num += 1
        while self.tokenizer.curr_token != ')':
            self.eat_symbol(',')
            self.compile_expression()
            arg_num += 1
        return arg_num

    # expression : term (op term)
    def compile_expression(self):
        mid_op = '+-*/&|<>='
        self.compile_term()
        while self.tokenizer.curr_token in mid_op:
            curr_op = self.eat_symbol()
            self.compile_term()
            self.code_writer.write_mid_arithmetic(curr_op)

    def compile_term(self):

        if self.tokenizer.token_type() == 'integerConstant':
            self.code_writer.write_code('push constant ' + self.tokenizer.curr_token + '\n')
            self.tokenizer.token_advance()

        elif self.tokenizer.token_type() == 'stringConstant':
            self.code_writer.write_string_constant(self.tokenizer.token_content())
            self.tokenizer.token_advance()

        elif self.tokenizer.token_type() == 'keyword':
            curr_keyword_term = self.eat_keyword('false true this null')
            self.code_writer.write_keyword_term(curr_keyword_term)

        elif self.tokenizer.curr_token in '- ~':
            curr_op = self.eat_symbol()
            self.compile_term()
            self.code_writer.write_unary_arithmetic(curr_op)

        elif self.tokenizer.curr_token == '(':
            self.eat_symbol('(')
            self.compile_expression()
            self.eat_symbol(')')

        elif self.tokenizer.token_type() == 'identifier':
            primary = self.eat_identifier()

            if self.tokenizer.curr_token == '.':  # primary is class name, TO DO
                self.compile_subroutine_call(primary)
            elif self.tokenizer.curr_token == '(':
                self.compile_subroutine_call(primary)

            elif self.tokenizer.curr_token == '[':  # primary is array name, TO DO
                array_name = primary
                arr_kind, arr_ind = self.symbol_table.locate_var(array_name)
                self.eat_symbol('[')
                self.compile_expression()
                self.eat_symbol(']')
                self.code_writer.write_code('push ' + arr_kind + ' ' + str(arr_ind) + '\n')
                self.code_writer.write_code('add\n')
                self.code_writer.write_code('pop pointer 1\n')
                self.code_writer.write_code('push that 0\n')

            else:  # primary itself is the name if a variable
                var_seg, var_ind = self.symbol_table.locate_var(primary)
                self.code_writer.write_code('push ' + var_seg + ' ' + str(var_ind) + '\n')

        else:
            print('Something wrong at term compile!')
            exit()

    def eat_type(self):
        # print('compiling type, current token:' + self.tokenizer.curr_token)

        if self.tokenizer.token_type() not in 'identifier keyword':
            print("Mismatch at eat_type!")
            exit()
        curr_type = self.tokenizer.curr_token
        self.tokenizer.token_advance()
        return curr_type

    def eat_symbol(self, symbols=""):
        if self.tokenizer.token_type() != "symbol" or (len(symbols) > 0 and self.tokenizer.curr_token not in symbols):
            print("Mismatch at eat_symbol!")
            print('token:', self.tokenizer.curr_token, 'type:', self.tokenizer.token_type())
            print('expected symbols:', symbols)
            exit()
        curr_symbol = self.tokenizer.curr_token
        self.tokenizer.token_advance()
        return curr_symbol

    def eat_identifier(self):
        if self.tokenizer.token_type() != "identifier":
            print("Mismatch at eat_identifier!")
            print('token:', self.tokenizer.curr_token, 'type:', self.tokenizer.token_type())
            exit()
        curr_name = self.tokenizer.curr_token
        self.tokenizer.token_advance()
        return curr_name

    def eat_keyword(self, keywords=""):
        if self.tokenizer.token_type() != "keyword" or (len(keywords) > 0 and self.tokenizer.curr_token not in keywords):
            print("Mismatch at eat_keyword!")
            exit()
        curr_keyword = self.tokenizer.curr_token
        self.tokenizer.token_advance()
        return curr_keyword



