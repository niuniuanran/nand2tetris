from Parser import Parser
from CodeWriter import CodeWriter
import sys


def run_vm_translator():
    file_name = str(sys.argv[1])
    parser = Parser(file_name)
    code_writer = CodeWriter(parser)

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

    parser.finish_parser()
    code_writer.finish_code_writer()


if __name__ == "__main__":
    run_vm_translator()


