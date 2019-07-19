import re


class Tokenizer(object):
    def __init__(self, file_path):
        try:
            self.jack_stream = open(file_path, 'r')
        except FileNotFoundError:
            print('File not found!')
            exit()

        self.curr_line = "\n"
        self.curr_token = "\n"
        self.in_comment = 0
        self.curr_line_quotes = []

        self.key_words = {"class", "method", "function", "constructor", "int", "boolean", "char",
                          "void", "var", "static", "field", "let", "do", "if", "else",
                          "while", "return", "true", "false", "null", "this"}
        self.symbols = {"{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/",
                        "&", "|", "<", ">", "=", "~"}
        self.symbol_pattern = re.compile(r'[-{}()\[\].,;+*/&|<>=~]')
        self.curr_line_tokens = []
        self.token_at_line = 0
        self.xml_string = ""

    def has_more_tokens(self):
        if len(self.curr_line) == 0:
            return False
        if len(self.curr_token) == 0:
            return False
        return True

    def _line_advance(self):
        self.token_at_line = 0
        while True:
            self.curr_line = self.jack_stream.readline()
            if len(self.curr_line) == 0:
                break
            self.curr_line = self.curr_line.strip()
            if len(self.curr_line) < 1 or self.curr_line.startswith("//"):
                continue
            if self.curr_line.endswith("*/"):
                self.in_comment = 0
                continue
            if self.curr_line.startswith("/*"):
                self.in_comment = 1
                if self.curr_line.endswith("*/"):
                    self.in_comment = 0
                continue
            if self.in_comment == 1:
                continue
            # print("cooked line:", self.curr_line)
            break

    @staticmethod
    def _repl_add_space(match_object):
        symbol = match_object.group(0)

        return " " + symbol + " "

    @staticmethod
    def _repl_swap_quote():
        i = -1

        def produce_string(_):
            nonlocal i
            i += 1
            return " #quoted_string"+str(i) + " "
        return produce_string

    def _recover_quote(self, match_object):
        digit = match_object.group(1)
        return self.curr_line_quotes[int(digit)]

    def _line_parse(self):
        self.curr_line_quotes = re.findall(re.compile(r'".*?"'), self.curr_line)
        self.curr_line = re.sub(re.compile(r'".*?"'), self._repl_swap_quote(), self.curr_line)
        self.curr_line = self.curr_line.split('//')[0]
        spaced_line = re.sub(self.symbol_pattern, self._repl_add_space, self.curr_line)
        self.curr_line_tokens = spaced_line.split()
        for i in range(len(self.curr_line_tokens)):
            if self.curr_line_tokens[i].startswith("#"):
                self.curr_line_tokens[i] = re.sub('#quoted_string([0-9]+)', self._recover_quote, self.curr_line_tokens[i])

    def token_advance(self):
        while self.has_more_tokens() and self.token_at_line > len(self.curr_line_tokens)-1:
            self._line_advance()
            self._line_parse()
        if self.has_more_tokens():
            self.curr_token = self.curr_line_tokens[self.token_at_line]
            self.token_at_line += 1

    def write_token_xml(self):
        token_type = self.token_type()

        escape_dict = {"&": "&amp;", ">": "&gt;", "<": "&lt;", '"': "&quot;"}
        if token_type == "symbol" and self.curr_token in escape_dict:
            written_token = escape_dict[self.curr_token]
        else:
            written_token = self.curr_token

        self.xml_string = "<" + token_type + "> "
        self.xml_string += str(written_token)
        self.xml_string += " </" + token_type + ">\n"

    def token_type(self):
        if self.curr_token in self.key_words:
            return "keyword"
        if self.curr_token in self.symbols:
            return "symbol"
        if self.curr_token.startswith('"') and self.curr_token.endswith('"'):
            return "stringConstant"
        if ord("0") <= ord(self.curr_token[0]) <= ord("9"):
            return "integerConstant"
        else:
            return "identifier"

    def token_content(self):
        if self.token_type() == 'stringConstant':
            return self.curr_token[1:-1]
        else:
            return self.curr_token

    def symbol(self):
        return self.curr_token

    def keyword(self):
        return self.curr_token

    def identifier(self):
        return self.curr_token

    def int_val(self):
        return int(self.curr_token)

    def string_val(self):
        return self.curr_token[1:-1]

    def finish(self):
        self.jack_stream.close()



















