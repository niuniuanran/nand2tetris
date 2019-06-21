from Parser import Parser
from CodeWriter import CodeWriter
from sys import argv
from os import listdir


def run_vm_translator():
    file_path = str(argv[1])

    vm_files = []
    write_init = 0

    code_writer = CodeWriter(file_path)

    if file_path.endswith(".vm"):
        vm_files.append(file_path)
        if file_path == "Sys.vm":
            write_init = 1
    else:
        file_list = listdir(file_path)
        for file in file_list:
            if file.endswith(".vm"):
                vm_files.append(file_path + "/" + file)
                if file == "Sys.vm":
                    write_init = 1
    if write_init == 1:
        code_writer.write_init()

    for file in vm_files:
        current_parser = Parser(file)
        single_parser(current_parser, code_writer)
    code_writer.finish_code_writer()


def single_parser(parser, code_writer):
    code_writer.current_file_name = parser.file_name
    code_writer.code_stream.write("//entering new file: " + parser.file_name + "\n")
    while True:
        parser.advance()
        if not parser.has_more_commands():
            break
        if parser.command_type() == "A":
            code_writer.write_arithmetic(parser.arg1())
        elif parser.command_type() == "POP":
            code_writer.write_pop(parser.arg1(), parser.arg2())
        elif parser.command_type() == "PUSH":
            code_writer.write_push(parser.arg1(), parser.arg2())
        elif parser.command_type() == "FUNCTION":
            code_writer.write_func(parser.arg1(), parser.arg2())
        elif parser.command_type() == "RETURN":
            code_writer.write_return()
        elif parser.command_type() == "CALL":
            code_writer.write_call(parser.arg1(), parser.arg2())
        elif parser.command_type() == "LABEL":
            code_writer.write_label(parser.arg1())
        elif parser.command_type() == "GOTO":
            code_writer.write_goto(parser.arg1())
        elif parser.command_type() == "IF-GOTO":
            code_writer.write_if_goto(parser.arg1())
        else:
            print("unknown command type")
            print(parser.command_type())
            exit()

    parser.finish_parser()


if __name__ == "__main__":
    run_vm_translator()



