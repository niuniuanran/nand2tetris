from re import findall


class Parser(object):
    def __init__(self, file_path):
        try:
            self.vm_stream = open(file_path, 'r')
        except FileNotFoundError:
            print('File not found!')
            exit()
        except OSError:
            print('Some OSError!')
            exit()

        self.curr_line = "\n"
        self.file_name = findall("([^/]+)[.]vm$", file_path)[0]
        self.arithmetic_set = {"add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"}
        self.args = []
        self.curr_func = []

    def has_more_commands(self):
        if len(self.curr_line) == 0:
            return False
        else:
            return True

    def advance(self):
        while True:
            curr_line = self.vm_stream.readline().strip(" ")
            if curr_line.startswith("//") or curr_line == "\n":
                continue
            else:
                break

        self.curr_line = curr_line

    def command_type(self):
        args = self.curr_line.split('//')
        if len(args) > 1:
            self.curr_line = args[0].strip()
        # get rid of comments
        self.args = []

        args = self.curr_line.split(' ')
        for arg in args:
            self.args.append(arg.strip())

        if self.args[0] in self.arithmetic_set:
            return "A"
        elif self.args[0] == "pop":
            return "POP"
        elif self.args[0] == "push":
            return "PUSH"
        elif self.args[0] == "label":
            return "LABEL"
        # label bar within function foo in a file xxx.vm will
        # generate (xxx.foo$bar) label in assembly language
        elif self.args[0] == "if-goto":
            return "IF-GOTO"
        # pop out the current stack top value, and jump if the value is not 0.
        # negative or positive values all induce goto operation.
        elif self.args[0] == "goto":
            return "GOTO"
        elif self.args[0] == "function":
            return "FUNCTION"
        # function foo in xxx.vm will be named xxx.foo in assembly.
        elif self.args[0] == "return":
            return "RETURN"
        elif self.args[0] == "call":
            return "CALL"
        # to save the return address of a function of foo in the xxx.vm file,
        # use xxx.foo$ret.i, where i is a running number recording the number of times
        # function foo has been called within the xxx.vm file.
        else:
            print(self.curr_line, "Unknown command type!")
            exit()

    def arg1(self):
        if self.command_type() == "A":
            return self.args[0]

        elif self.command_type() in {"POP", "PUSH", "GOTO", "IF-GOTO", "FUNCTION", "CALL", "LABEL"}:
            return self.args[1]
        else:
            print(self.curr_line)
            print("Nothing to give for arg1")
            exit()

    def arg2(self):
        if self.command_type() in {"POP", "PUSH", "FUNCTION", "CALL"} and len(self.args) >= 3:
            return self.args[2]
        else:
            print(self.curr_line)
            print("Nothing to give for arg2")
            exit()

    def finish_parser(self):
        self.vm_stream.close()
