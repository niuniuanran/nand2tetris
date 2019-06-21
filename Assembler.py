#r"\2091\sample.txt"
import re
import os


class HackAssembler(object):

    def __init__(self):
        self.symbol_table = {
            "R0": 0, "R1": 1, "R2": 2, "R3": 3, "R4": 4, "R5": 5, "R6": 6, "R7": 7, "R8": 8, "R9": 9, "R10": 10,
            "R11": 11, "R12": 12, "R13": 13, "R14": 14, "R15": 15,
            "SCREEN": 16384, "KBD": 24576, "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4
        }
        self.instructions = []
        self.file_name = ""
        self.curr_add = 16
        self.des_dict = {
            'M': '001', 'D': '010', 'MD': '011', 'A': '100', 'AM': '101', 'AD': '110', 'AMD': '111'
        }
        self.jmp_dict = {
            'JGT': '001', 'JEQ': '010', 'JGE': '011', 'JLT': '100', 'JNE': '101', 'JLE': '110',
            'JMP': '111'
        }
        self.cmp_dict = {
            '0': '0101010',
            '1': '0111111',
            '-1': '0111010',
            'D': '0001100',
            'A': '0110000', 'M': '1110000',
            '!D': '0001101',
            '!A': '0110001', '!M': '1110001',
            'D+1': '0011111',
            'A+1': '0110111', 'M+1': '1110111',
            'D-1': '0001110',
            'A-1': '0110010', 'M-1': '1110010',
            'D+A': '0000010', 'D+M': '1000010', 'M+D': '1000010', 'A+D': '0000010',
            'D-A': '0010011', 'D-M': '1010011',
            'A-D': '0000111', 'M-D': '1000111',
            'D&A': '0000000', 'D&M': '1000000', 'M&D': '1000000', 'A&D': '0000000',
            'D|A': '0010101', 'D|M': '1010101', 'M|D': '1010101', 'A|D': '0010101'
        }

    def get_label(self, curr_line):
        label_p = re.compile('[(](.*?)[)]')

        '''方括号括起来的内容会失去原本在RE中的功能，变成字面的小括号。
        小括号括起来的内容表示我要截取这其中的内容存到findall里面。
        .表示任何字符，*表示前面规定的字符重复0到多次。
        如果没有问号，*是贪婪的，会一直吃到最后一个右括号。*？则是不贪婪的，只会吃到第一个右括号。
        re.compile从字符串生成regular expression的pattern，r''表示生字符串，r是防止字符转义的 如果路径中出现'\t'的话 不加r的话\t就
        会被转义 而加了’r’之后r'\t'就能保留原有的样子
        '''

        label = re.findall(label_p, curr_line)[0]
        # 在当前行中取出label

        self.symbol_table[label] = len(self.instructions)
        # 将label作为索引，label后面一行的instruction行数作为值，存储到symbol table里。

    def read_file(self, path):
        self.file_name = re.findall('(\w+).\w+$', path)[0]
        # 取出路径末尾的文件名，\w即[A-Za-z0-9_],$标记字符串末尾。
        with open(path) as f:
            # with method as f, 同时包含了try.. catch, finalize, enter/exit的操作，可以避免忘记关文件。
            while True:
                curr_line = f.readline()
                if len(curr_line) == 0:
                    break
                    # f.readline操作，对于空行会读入'\n'，到文件末尾则会读入''空字符串，所以line长度为0标记着读取文件结束。
                curr_line = curr_line.strip(" ")
                # str.strip返回一个删掉了开头末尾的空格（或者其他指定的字符）的字符串。

                if curr_line[0:2] == "//" or curr_line == "\n":
                    continue
                if curr_line[0] == "(":
                    self.get_label(curr_line)
                else:
                    self.instructions.append(curr_line)

    def read_instructions(self):
        with open(self.file_name+'.hack', 'w') as new_f:
            # 'w'表示只写，用法是f.write(字符串)，不会自动给加换行符，需要自己指定。
            for instruction in self.instructions:
                a_pattern = re.compile('@([.$\w]+)[/\s]*')
                # 汇编语言的地址symbol可能包含'.''$''_'，其中'$'是系统汇编的时候加进去的。这个RE pattern读取地址，终止的信号是\或空格。
                if re.match(a_pattern, instruction) is not None:
                    ml_instruction = self.a_instruction(instruction)
                    new_f.write(ml_instruction)
                else:
                    ml_instruction = self.c_instruction(instruction)
                    new_f.write(ml_instruction)

    def a_instruction(self, instruction):
        a_pattern = re.compile(r'@([.$\w]+)[\s/]*')
        address = re.findall(a_pattern, instruction)[0]
        if re.fullmatch(r'[0-9]+', address) is None:
            address_val = self.symbol_table.get(address)
            if address_val is None:
                address_val = self.curr_add
                self.symbol_table[address] = address_val
                self.curr_add += 1
                # 因为涉及到curr_add+1的操作，而且python又没有++，所以没办法用setdefault，只能先get再判断。
        else:
            address_val = int(address)
        return '0' + bin(address_val)[2:].zfill(15) + '\n'
        # str.zfill(width)是字符串的一个方法，意思是ZERO FILL,在字符串的前面加0直到凑齐想要的长度。

    def c_instruction(self, instruction):
        jmp_pattern = re.compile(';\s*(J[A-Z][A-Z])')
        # 分号后面的三个大写字母是jump指令，分号和指令之间可能有0-若干个空格。
        jmp = re.findall(jmp_pattern, instruction)
        if len(jmp) == 0:
            jump = '000'
        else:
            jump = self.jmp_dict[jmp[0]]

        des_pattern = re.compile('([AMD]+)=')
        # 等号前面的AMD组合是destination指令，+表示符合前面要求的字符的1到多次重复。

        des = re.findall(des_pattern, instruction)
        if len(des) == 0:
            dest = '000'
            cmp = re.findall(r'([-AMD+!& |01]*[AMD01])[\s;/]*', instruction)[0]
            # - 在方括号里表示范围的意思，若干需要指出'-'本身，则可以把它放在方括号中内容的开头。
        else:
            dest = self.des_dict[des[0]]
            cmp = re.findall(r'=([-AMD+!& |01]*[AMD01])[\s;/]*', instruction)[0]
        comp = self.cmp_dict[cmp]

        return '111' + comp + dest + jump + '\n'


def test():
    h = HackAssembler()
    path = 'Mult.asm'
    h.read_file(path)
    h.read_instructions()


if __name__ == "__main__":
    test()