from re import findall


class CodeWriter(object):
    def __init__(self, file_path):
        if file_path.endswith(".vm"):
            self.asm_name = findall("([^.]+)[.]vm$", file_path)[0]
            self.current_file_name = findall("([^./]+)[.]vm$", file_path)[0]
        else:
            self.asm_name = file_path + "/" + findall("([^/]+)$", file_path)[0]
            self.current_file_name = findall("([^/]+)$", file_path)[0]
        self.code_stream = open(self.asm_name + ".asm", "w+")
        # if you get a directory, the name of the asm should be the directory name.
        # if you get a single file, then the file name.
        self.label_num = 0
        self.curr_func = [["", 1]]

    def write_init(self):
        print("writing init")
        self.code_stream.write("//initialize the asm file\n"
                               "@256\nD=A\n"
                               "@SP\nM=D\n\n")
        # SP = 256
        self.write_call("Sys.init", "0")
        # call Sys.init

    def write_arithmetic(self, arg1):
        self.code_stream.write("//     " + arg1 + '\n')

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
            self.code_stream.write("@SP\nM=M-1\n"  # SP will stay here.
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
        self.code_stream.write("//" + "push " + arg1 + " " + arg2 + "\n")

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
            sv_name = self.current_file_name + "." + arg2
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
            sv_name = self.current_file_name + "." + arg2
            self.code_stream.write("@" + sv_name + "\nD=A\n@R13\nM=D\n")
            # M[13] now stores the address you want to put the popped value.
        else:
            print("Something wrong at pop command!")
            exit()

        self.code_stream.write("@SP\nM=M-1\nA=M\nD=M\n")
        # D register now stores the value popped
        self.code_stream.write("@R13\nA=M\nM=D\n")
        # now the popped value is sent to the desired address.

    def write_label(self, label_name):
        self.code_stream.write("//label " + label_name + '\n')

        label = self.curr_func[-1][0] + "$" + label_name
        self.code_stream.write("(" + label + ")\n")

    def write_goto(self, label_name):
        self.code_stream.write("//goto " + label_name + '\n')

        label = self.curr_func[-1][0] + "$" + label_name
        self.code_stream.write("@"+label+"\n0;JMP\n")

    # pop out the current stack top value, and jump if the value is not 0.
    # negative or positive values all induce goto operation.
    def write_if_goto(self, label_name):

        self.code_stream.write("//if-goto " + label_name + '\n')

        label = self.curr_func[-1][0] + "$" + label_name
        self.code_stream.write("@SP\nM=M-1\nA=M\nD=M\n"
                               "@"+label+"\nD;JNE\n")
        # pop the value at stack top and store it into D register
        # if the value is not 00000000000, jump to the label position.

    def write_call(self, function_name, arg_num):
        self.code_stream.write("//call function " + function_name + '\n')

        return_address_label = self.curr_func[-1][0] + "$ret" + \
            "." + str(self.label_num)
        self.label_num += 1
        # construct a unique return_add_label
        self.code_stream.write("@" + return_address_label + "\nD=A\n@SP\nM=M+1\nA=M-1\nM=D\n")
        # push return-address, as declared below as a label.

        self.code_stream.write("@LCL\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n")
        # push value of LCL (M[1])
        self.code_stream.write("@ARG\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n")
        # push ARG (M[2])
        self.code_stream.write("@THIS\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n")
        # push THIS (M[3])
        self.code_stream.write("@THAT\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n")
        # push THAT (M[4])

        self.code_stream.write("@" + str(arg_num) + "\nD=A\n@SP\nD=M-D\n@ARG\nM=D\n")
        # ARG = SP-n
        self.code_stream.write("@5\nD=A\n@ARG\nM=M-D\n")
        # ARG = ARG - 5 (M[2] = M[0] - arg_num - 5)

        self.code_stream.write("@SP\nD=M\n@LCL\nM=D\n")
        # LCL = SP (M[1] = M[0]), after the local variables are set to 0's at the function declaration, SP will be
        # top of the working stack for the callee.

        self.code_stream.write("@" + function_name + "\n0;JMP\n")
        # transfer control to function body

        self.code_stream.write("("+return_address_label+")\n")
        #  as long as the return address label is unique, and the NUMBER of this label has been stored in the stack
        #  (not the name), and it is available to use when the function is returning.

    def write_func(self, function_name, lcl_num):
        self.code_stream.write("//declare function " + function_name + '\n')

        self.curr_func.pop()
        self.curr_func.append([function_name, 0])

        self.code_stream.write("("+function_name+")\n")
        # declare a label for the function entry for the call command to jump to after its preparation

        for i in range(int(lcl_num)):
            self.write_push("constant", "0")
        # push 0 to hold the place for local variables. notice that after each call command, LCL will be
        #  set to SP, which means after pushing 0 for lcl_num times, the spaces between pointer LCL and SP
        #  will be the current LCL segment.
        # after this preparation, we are ready for the function operations that follows.

    def write_return(self):
        self.curr_func[-1][1] += 1
        self.code_stream.write("@LCL\nD=M\n@frame\nM=D\n"  # frame = LCL, start of the callee setup, and one step 
                               #  after the end of caller's saved status.
                               "@5\nD=A\n@frame\nD=M-D\nA=D\nD=M\n@return\nM=D\n"  # return = *(frame-5)
                               "@SP\nM=M-1\nA=M\nD=M\n@ARG\nA=M\nM=D\n"  # *ARG = pop()  M[ARG] = pop()
                               "@ARG\nD=M\n@SP\nM=D+1\n"  # SP=ARG+1
                               "@frame\nD=M\n@1\nD=D-A\nA=D\nD=M\n@THAT\nM=D\n"  # THAT = *(FRAME-1)  
                               "@frame\nD=M\n@2\nD=D-A\nA=D\nD=M\n@THIS\nM=D\n"  # THis = *(FRAME-2) 
                               "@frame\nD=M\n@3\nD=D-A\nA=D\nD=M\n@ARG\nM=D\n"  # ARG = *(FRAME-3)
                               "@frame\nD=M\n@4\nD=D-A\nA=D\nD=M\n@LCL\nM=D\n"  # LCL = *(FRAME-4)
                               "@return\nA=M\n0;JMP\n")  # jump to the instruction number saved at return.

    def finish_code_writer(self):
        self.code_stream.close()



