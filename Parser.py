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
        self.file_path = findall("(.+)[.]vm$", file_path)[0]
        self.file_name = findall("([a-zA-Z]+)[.]vm$", file_path)[0]
        self.arithmetic_set = {"add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"}
        self.args = []

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
        else:
            print(self.curr_line, "Unknown command type!")
            exit()

    def arg1(self):
        if self.command_type() == "A":
            return self.args[0]

        if self.command_type() in {"POP", "PUSH"}:
            return self.args[1]

    def arg2(self):
        if self.command_type() in {"POP", "PUSH"} and len(self.args) >= 3:
            return self.args[2]
        if self.command_type() == "A":
            return None

    def finish_parser(self):
        self.vm_stream.close()
