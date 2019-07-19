from JackTokenizer import Tokenizer
from CompilationEngine import CompilationEngine
from sys import argv
from os import listdir


def run_jack_compiler(file_path):
    jack_files = []
    if file_path.endswith(".jack"):
        jack_files.append(file_path)
    else:
        file_list = listdir(file_path)
        for file in file_list:
            if file.endswith(".jack"):
                jack_files.append(file_path + '/' + file)

    for jack_file in jack_files:
        # print("   Now processing: ", jack_file)
        curr_tokenizer = Tokenizer(jack_file)
        curr_compilation_engine = CompilationEngine(curr_tokenizer, jack_file)
        curr_compilation_engine.compile_class()


if __name__ == "__main__":
    path = str(argv[1])
    # path = input('Enter your path:')
    run_jack_compiler(path)
