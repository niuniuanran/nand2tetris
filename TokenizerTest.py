from JackTokenizer import Tokenizer
from os import listdir
from sys import argv


def run_jack_tokenizer(file_path):
    jack_files = []
    if file_path.endswith(".jack"):
        jack_files.append(file_path)
    else:
        file_list = listdir(file_path)
        for file in file_list:
            if file.endswith(".jack"):
                jack_files.append(file_path + '/' + file)

    for jack_file in jack_files:
        print("   Now processing: ", jack_file)
        curr_tokenizer = Tokenizer(jack_file)
        print("writing into", jack_file[:-5]+"test.xml")
        xml_stream = open(jack_file[:-5]+"test.xml", "w+")
        xml_stream.write("<tokens>\n")
        single_file_tokenize(curr_tokenizer, xml_stream)
        xml_stream.write("</tokens>\n")
        xml_stream.close()


def single_file_tokenize(curr_tokenizer, xml_stream):
    while True:
        curr_tokenizer.token_advance()
        if not curr_tokenizer.has_more_tokens():
            break
        curr_tokenizer.write_token_xml()
        xml_stream.write(curr_tokenizer.xml_string)
    curr_tokenizer.finish()


if __name__ == "__main__":
    file_path = input()
    run_jack_tokenizer(file_path)





