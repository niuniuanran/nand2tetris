class CodeWriter(object):
    def __init__(self, parser):
        self.code_stream = open(parser.file_path + ".asm", "w")
        self.file_name = parser.file_name
        self.label_num = 0

    def write_arithmetic(self, arg1):
        self.code_stream.write("//                  " + arg1 + '\n')

        # {"add", "sub", " neg", "eq", "gt", "lt", "and", "or", "not"}
        if arg1 == "add":
            self.code_stream.write("@SP\nM=M-1\nA=M\nD=M\n")  # pop the number at top of stack
            self.code_stream.write("@R13\nM=D\n")  # store the fetched number in M[13]
            self.code_stream.write("@SP\nM=M-1\nA=M\nD=M\n")  # pop the number now at the top of stack
            self.code_stream.write("@R13\nD=M+D\n")
            # add up the number stored in D register and the number stored in M[13]
            self.code_stream.write("@SP\nA=M\nM=D\n")
            self.code_stream.write("@SP\nM=M+1\n")  # push the new sum back to the stack, with SP += 1

        elif arg1 == "sub":
            self.code_stream.write("@SP\nM=M-1\nA=M\nD=M\n")
            # pop the number at top of stack. this is the number after the '-'
            self.code_stream.write("@R13\nM=D\n")  # store the fetched number in M[13]
            self.code_stream.write("@SP\nM=M-1\nA=M\nD=M\n")
            # pop the number now at the top of stack and save it at D register
            self.code_stream.write("@R13\nD=D-M\n")  # second popped number - first popped number
            self.code_stream.write("@SP\nA=M\nM=D\n")  # save the result at stack top
            self.code_stream.write("@SP\nM=M+1\n")  # top of stack changed.

        elif arg1 == "neg":
            self.code_stream.write("@SP\nA=M-1\n")  # go to the number at top of stack
            self.code_stream.write("M=-M\n")  # negate it

        elif arg1 == "not":
            self.code_stream.write("@SP\nA=M-1\n")  # go to the number at top of stack
            self.code_stream.write("M=!M\n")  # negate it

        elif arg1 == "eq":
            self.code_stream.write("@SP\nM=M-1\n" # SP will stay here.
                                   "A=M\nD=M\n"
                                   "@R13\nM=D\n"
                                   "@SP\nA=M-1\n"
                                   "D=M\n"
                                   "@R13\nD=D-M\n"
                                   "@EQUAL"+str(self.label_num)+"\nD;JEQ\n"
                                   "@UNEQUAL"+str(self.label_num)+"\nD;JNE\n"
                                   "(EQUAL"+str(self.label_num)+")\nD=-1\n@SAVE_RESULT"+str(self.label_num)+"\n0;JMP\n"
                                   "(UNEQUAL"+str(self.label_num)+")\nD=0\n@SAVE_RESULT"+str(self.label_num)+"\n0;JMP\n"
                                   "(SAVE_RESULT"+str(self.label_num)+")\n@SP\nA=M-1\nM=D\n")
            self.label_num += 1
        elif arg1 == "gt":
            self.code_stream.write("@SP\nM=M-1\n"  # SP will stay here.
                                   "A=M\nD=M\n"
                                   "@R13\nM=D\n"
                                   "@SP\nA=M-1\n"
                                   "D=M\n"
                                   "@R13\nD=D-M\n"  # a-b
                                   "@GREATER"+str(self.label_num)+"\nD;JGT\n"
                                   "@NOT_GREATER"+str(self.label_num)+"\nD;JLE\n"
                                   "(GREATER"+str(self.label_num)+")\nD=-1\n"
                                   "@SAVE_RESULT"+str(self.label_num)+"\n0;JMP\n"
                                   "(NOT_GREATER"+str(self.label_num)+")\nD=0\n"
                                   "@SAVE_RESULT"+str(self.label_num)+"\n0;JMP\n"
                                   "(SAVE_RESULT"+str(self.label_num)+")\n@SP\nA=M-1\nM=D\n")
            self.label_num += 1

        elif arg1 == "lt":
            self.code_stream.write("@SP\nM=M-1\n"  # SP will stay here.
                                   "A=M\nD=M\n"
                                   "@R13\nM=D\n"
                                   "@SP\nA=M-1\n"
                                   "D=M\n"
                                   "@R13\nD=D-M\n"  # a-b
                                   "@LESS"+str(self.label_num)+"\nD;JLT\n"
                                   "@NOT_LESS"+str(self.label_num)+"\nD;JGE\n"
                                   "(LESS"+str(self.label_num)+")\nD=-1\n"
                                   "@SAVE_RESULT"+str(self.label_num)+"\n0;JMP\n"
                                   "(NOT_LESS"+str(self.label_num)+")\nD=0\n"
                                   "@SAVE_RESULT"+str(self.label_num)+"\n0;JMP\n"
                                   "(SAVE_RESULT"+str(self.label_num)+")\n@SP\nA=M-1\nM=D\n")
            self.label_num += 1

        elif arg1 == "and":
            self.code_stream.write("@SP\nM=M-1\nA=M\nD=M\n")  # pop the number at top of stack, b
            self.code_stream.write("@R13\nM=D\n")  # store the fetched number in M[13]
            self.code_stream.write("@SP\nM=M-1\nA=M\nD=M\n")
            # pop the number now at the top of stack and save it at D register, a
            self.code_stream.write("@R13\nD=D&M\n")
            # D= a&b
            self.code_stream.write("@SP\nM=M+1\nA=M-1\nM=D\n")
            # stack top = a&b

        elif arg1 == "or":
            self.code_stream.write("@SP\nM=M-1\nA=M\nD=M\n")  # pop the number at top of stack, b
            self.code_stream.write("@R13\nM=D\n")  # store the fetched number in M[13]
            self.code_stream.write("@SP\nM=M-1\nA=M\nD=M\n")
            # pop the number now at the top of stack and save it at D register, a
            self.code_stream.write("@R13\nD=D|M\n")
            # D= a|b
            self.code_stream.write("@SP\nM=M+1\nA=M-1\nM=D\n")
            # stack top = a|b

        else:
            print("Something going wrong at Arithmetic Command!")
            exit()

    def write_push(self, arg1, arg2):
        self.code_stream.write("//"+"push " + arg1 + " " + arg2 + "\n")

        # arg1 can be: constant, local, argument, this, that, pointer, temp, static
        # arg2 is a string of numbers.
        if arg1 == "constant":
            self.code_stream.write("@"+arg2+"\nD=A\n")
            # now D register stores the constant number.
        elif arg1 == "local":
            self.code_stream.write("@"+arg2+"\nD=A\n")
            # now D register stores how many spaces off the 0 local variable..
            self.code_stream.write("@LCL\nD=M+D\nA=D\nD=M\n")
            # D register stores the value at the local address you want.
        elif arg1 == "argument":
            self.code_stream.write("@" + arg2 + "\nD=A\n")
            # now D register stores how many spaces off the 0 argument variable.
            self.code_stream.write("@ARG\nD=M+D\nA=D\nD=M\n")
            # D register stores the value at the argument address you want.
        elif arg1 == "this":
            self.code_stream.write("@" + arg2 + "\nD=A\n")
            # now D register stores how many spaces off the 0 this variable.
            self.code_stream.write("@THIS\nD=M+D\nA=D\nD=M\n")
            # D register stores the value at the this address you want(THIS[arg2]).
        elif arg1 == "that":
            self.code_stream.write("@" + arg2 + "\nD=A\n")
            # now D register stores how many spaces off the 0 that variable.
            self.code_stream.write("@THAT\nD=M+D\nA=D\nD=M\n")
            # D register stores the value at the that address you want(THAT[arg2]).
        elif arg1 == "pointer":
            if arg2 == "0":
                self.code_stream.write("@THIS\nD=M\n")
                # now D register stores the value of THIS(R3).
            if arg2 == "1":
                self.code_stream.write("@THAT\nD=M\n")
                # now D register stores the value of THAT(R4).
        elif arg1 == "temp":
            tv_name = "R" + str(5+int(arg2))
            self.code_stream.write("@"+tv_name+"\nD=M\n")

        elif arg1 == "static":
            sv_name = self.file_name + "." + arg2
            self.code_stream.write("@" + sv_name + "\nD=M\n")

        else:
            print("Something wrong at push command!")
            exit()

        self.code_stream.write("@SP\nM=M+1\nA=M-1\nM=D\n")
        # store the number in D register into the start of local segment.

    def write_pop(self, arg1, arg2):
        self.code_stream.write("//"+"pop " + arg1 + " " + arg2+"\n")
        if arg1 == "local":
            self.code_stream.write("@" + arg2 + "\nD=A\n")
            self.code_stream.write("@LCL\nD=M+D\n")
            # D now stores the address you want to put the popped value.
            self.code_stream.write("@R13\nM=D\n")
            # M[13] now stores the address you want to put the popped value.
        elif arg1 == "argument":
            self.code_stream.write("@" + arg2 + "\nD=A\n")
            self.code_stream.write("@ARG\nD=M+D\n@R13\nM=D\n")
            # M[13] now stores the address you want to put the popped value.
        elif arg1 == "this":
            self.code_stream.write("@" + arg2 + "\nD=A\n")
            self.code_stream.write("@THIS\nD=M+D\n@R13\nM=D\n")
            # M[13] now stores the address you want to put the popped value.
        elif arg1 == "that":
            self.code_stream.write("@" + arg2 + "\nD=A\n")
            self.code_stream.write("@THAT\nD=M+D\n@R13\nM=D\n")
            # M[13] now stores the address you want to put the popped value.
        elif arg1 == "pointer":
            if arg2 == "0":
                self.code_stream.write("@THIS\nD=A\n@R13\nM=D\n")
                # M[13] now stores the address you want to put the popped value.
            if arg2 == "1":
                self.code_stream.write("@THAT\nD=A\n@R13\nM=D\n")
                # M[13] now stores the address you want to put the popped value.
        elif arg1 == "temp":
            tv_off = 5 + int(arg2)
            self.code_stream.write("@" + str(tv_off) + "\nD=A\n@R13\nM=D\n")
            # M[13] now stores the address you want to put the popped value.

        elif arg1 == "static":
            sv_name = self.file_name + "." + arg2
            self.code_stream.write("@" + sv_name + "\nD=A\n@R13\nM=D\n")
            # M[13] now stores the address you want to put the popped value.
        else:
            print("Something wrong at pop command!")
            exit()

        self.code_stream.write("@SP\nM=M-1\nA=M\nD=M\n")
        # D register now stores the value popped
        self.code_stream.write("@R13\nA=M\nM=D\n")
        # now the popped value is sent to the desired address.

    def finish_code_writer(self):

        self.code_stream.close()



