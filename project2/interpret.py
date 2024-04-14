import re
import argparse
import xml.etree.ElementTree as ET
import sys

#xml2inst
class Program:
    def __init__(self):
        self.list_of_instructions = []  # list for instructions
        self.lables = {}  # dict for labels
        self.number_of_lines = 0  # number of useful lines in program
        self.prog_stack = []  # stack for symbols atc
        self.current_pos = 0  # current pos in program
        self.call_stack = []  # call stack for call | return

        # MEMORY MODEL
        self.global_frame = {}  # GF for global variables
        self.temporary_frame: dict = {}
        self.temporary_frame_identif: bool = False
        self.local_frame: dict = {}
        self.local_frame_identif: bool = False
        self.frame_stack: list = []

    def add_variable(self, name, type, value):
        variable = name.split("@")
        frame = variable[0]
        var_name = variable[1]
        frames = {'GF': self.global_frame, 'LF': self.local_frame, 'TF': self.temporary_frame}

        frames[frame][var_name] = {'type': type, 'val': value}

    def set_variable(self, name, type, value):
        variable = name.split("@")
        frame = variable[0]
        var_name = variable[1]

        frames = {'GF': self.global_frame, 'LF': self.local_frame, 'TF': self.temporary_frame}

        frames[frame][var_name] = {'type': type, 'val': value}
    def frame_identif(self, frame):
        if frame == 'GF':
            return True
        elif frame == 'LF':
            return self.local_frame_identif
        elif frame == 'TF':
            return self.temporary_frame_identif

    def get_variable(self, name):
        variable = name.split("@")
        frame = variable[0]
        var_name = variable[1]

        if self.check_var_in_memory(name) == 0:
            if frame == 'GF':
                return self.global_frame[var_name]
            elif frame == 'LF':
                return self.local_frame[var_name]
            elif frame == 'TF':
                return self.temporary_frame[var_name]

    def check_var_in_memory(self, name):
        variable = name.split("@")
        frame = variable[0]
        var_name = variable[1]

        if not self.frame_identif(frame):
            return 2

        if frame == 'GF':
            return 0 if var_name in self.global_frame else 1
        elif frame == 'LF':
            return 0 if var_name in self.local_frame else 1
        elif frame == 'TF':
            return 0 if var_name in self.temporary_frame else 1

    def get_temporary_frame_identif(self):
        return self.temporary_frame_identif

    def get_local_frame_identif(self):
        return self.local_frame_identif

    def create_temporary_frame(self):
        self.temporary_frame_identif = True
        self.temporary_frame = {}

    def pop_local_frame(self):
        if self.get_local_frame_identif():
            self.temporary_frame_identif = True
            self.temporary_frame = self.frame_stack.pop()
            if len(self.frame_stack) > 0:
                self.local_frame_identif = True
                self.local_frame = self.frame_stack[-1]
            else:
                self.local_frame_identif = False
                self.local_frame = {}
            return 0
        else:
            return 1

    def push_temporary_frame(self):
        if self.get_temporary_frame_identif():
            self.frame_stack.append(self.temporary_frame)
            self.local_frame_identif = True
            self.local_frame = self.frame_stack[-1]
            self.temporary_frame_identif = False
            self.temporary_frame = {}
            return 0
        else:
            return 1

    def inc_lines(self):
        self.number_of_lines += 1

    def add_instruction(self, instruction):
        self.list_of_instructions.append(instruction)

    def add_label(self, name: str, index: int):
        self.lables[name] = index

    def get_number_of_lines(self):
        return self.number_of_lines

    def inc_curr_pos(self):
        self.current_pos += 1

    def dec_curr_pos(self):
        self.current_pos -= 1

    def set_curr_pos(self, index):
        self.current_pos = index

    def get_next_instruction(self):
        if self.current_pos < self.number_of_lines:
            return self.list_of_instructions[self.current_pos]
        else:
            return "end"


class Argument:
    def __init__(self, arg_type, value):
        self.type = arg_type
        self.value = value

    def get_argument(self) -> tuple:
        return self.type, self.value

    def get_value(self):
        return self.value

    def get_type(self):
        return self.type


class Instruction:

    def __init__(self, opcode, number):
        self.opcode = opcode
        self.number = number
        self.args = []

    def add_argument(self, arg_type, value):
        self.args.append(Argument(arg_type, value))

    def get_opcode(self):
        return self.opcode

    def get_number(self):
        return self.number

    def get_args(self):
        return self.args


#argparse
sourceFile = ""
inputFile = ""

arg_parse = argparse.ArgumentParser(add_help=False)

arg_parse.add_argument("--source", nargs=1)
arg_parse.add_argument("--input", nargs=1)
arg_parse.add_argument("--help", action="store_true", help="print help")


args = arg_parse.parse_args()
if args.help:
    if args.source or args.input:
        print("Error params")
        exit(10)

    print("HELP TEXT")
    exit(0)

if not args.source and not args.input:
    print("Miss read file")
    exit(10)
else:
    if args.source:
        sourceFile = args.source[0]
    if args.input:
        inputFile = args.input[0]
        sourceFile = sys.stdin
        sys.stdin = open(inputFile, "r")


#xml load

tree = ET.parse(sourceFile)
root = tree.getroot()

#xml check
if root.tag != 'program':
    print("Error xml")
    exit(5)

for child in root:
    if child.tag != 'instruction':
        print("error xml instr")
        exit(5)
    childattr = list(child.attrib.keys())
    if ('order' not in childattr) or ('opcode' not in childattr):
        print("error xml opcode order")
        exit(5)

    for subelem in child:
        if not(re.match(r"arg[123]", subelem.tag)):
            print("error xml args")
            exit(5)


MainProgram = Program()

for element in root:
    opcode = list(element.attrib.values())[1]
    order = list(element.attrib.values())[0]
    new_instruction = Instruction(opcode, order)

    for arg in element:
        if list(arg.attrib.values())[0] == 'int':
            new_instruction.add_argument(list(arg.attrib.values())[0], int(arg.text))
        elif list(arg.attrib.values())[0] == 'bool':
            bool_value = True if arg.text == 'true' else False if arg.text == 'false' else None
            new_instruction.add_argument(list(arg.attrib.values())[0], bool_value)
        elif list(arg.attrib.values())[0] == 'nil':
            new_instruction.add_argument(list(arg.attrib.values())[0], None)
        elif list(arg.attrib.values())[0] == 'string':
            if arg.text == None:
                new_instruction.add_argument(list(arg.attrib.values())[0], "")
            else:
                pattern = r'\\(\d{3})'
                symb = re.sub(pattern, lambda m: chr(int(m.group(1))), arg.text)
                new_instruction.add_argument(list(arg.attrib.values())[0], symb)
        else:
            new_instruction.add_argument(list(arg.attrib.values())[0], arg.text)

    if new_instruction.get_opcode() == 'LABEL':
        MainProgram.add_label(new_instruction.get_args()[0].get_value(), MainProgram.get_number_of_lines())

    MainProgram.add_instruction(new_instruction)
    MainProgram.inc_lines()

while True:

    instruction = MainProgram.get_next_instruction()
    if instruction == 'end':
        break

    iopcode = instruction.get_opcode()

    if iopcode == 'MOVE':
        var = instruction.get_args()[0].get_value()
        err_code = MainProgram.check_var_in_memory(var)

        exit(55) if err_code == 2 else exit(54) if err_code == 1 else None

        symb_type = instruction.get_args()[1].get_type()
        symb = instruction.get_args()[1].get_value()

        if symb_type == 'var':
            err_code = MainProgram.check_var_in_memory(symb)
            exit(55) if err_code == 2 else exit(54) if err_code == 1 else None

            symb_variable = MainProgram.get_variable(symb)
            if symb_variable['type'] is None:
                exit(56)
            MainProgram.set_variable(var, symb_variable['type'], symb_variable['val'])
        else:
            typ = instruction.get_args()[1].get_type()
            if typ == 'nil':
                MainProgram.set_variable(var, None, None)
            elif typ == 'string':
                MainProgram.set_variable(var, typ, symb)
            else:
                MainProgram.set_variable(var, typ, symb)

    elif iopcode == 'DEFVAR':
        var = instruction.get_args()[0].get_value()
        err_code = MainProgram.check_var_in_memory(var)

        exit(55) if err_code == 2 else exit(52) if err_code == 0 else None

        MainProgram.add_variable(var, None, None)

    elif iopcode == 'CALL':
        # if label in labels
        label = instruction.get_args()[0].get_value()
        if label not in MainProgram.lables:
            exit(52)
        MainProgram.call_stack.append(MainProgram.current_pos)
        MainProgram.set_curr_pos(MainProgram.lables[label])
        MainProgram.dec_curr_pos()

    elif iopcode == 'LABEL':
        pass

    elif iopcode == 'RETURN':
        if len(MainProgram.call_stack) != 0:
            MainProgram.set_curr_pos(MainProgram.call_stack.pop())
        else:
            exit(56)

    elif iopcode == 'PUSHS':
        symb_type = instruction.get_args()[0].get_type()
        symb = instruction.get_args()[0].get_value()

        if symb_type == 'var':
            err_code = MainProgram.check_var_in_memory(symb)
            exit(55) if err_code == 2 else exit(54) if err_code == 1 else None
            variable = MainProgram.get_variable(symb)
            if variable['type'] is None:
                exit(56)
            MainProgram.prog_stack.append(MainProgram.get_variable(symb))
        else:
            MainProgram.prog_stack.append({'type': symb_type, 'val': symb})

    elif iopcode == 'POPS':
        var = instruction.get_args()[0].get_value()
        err_code = MainProgram.check_var_in_memory(var)
        exit(55) if err_code == 2 else exit(54) if err_code == 1 else None

        if len(MainProgram.prog_stack) > 0:
            variable = MainProgram.prog_stack.pop()
            MainProgram.set_variable(var, variable['type'], variable['val'])
        else:
            #print("prog stack error")
            exit(56)

    elif iopcode in ['ADD', 'SUB', 'MUL', 'IDIV']:
        var = instruction.get_args()[0].get_value()
        err_code = MainProgram.check_var_in_memory(var)
        exit(55) if err_code == 2 else exit(54) if err_code == 1 else None

        symb1_type = instruction.get_args()[1].get_type()
        symb2_type = instruction.get_args()[2].get_type()
        symb1 = instruction.get_args()[1].get_value()
        symb2 = instruction.get_args()[2].get_value()

        if symb1_type == 'var':
            err_code = MainProgram.check_var_in_memory(symb1)
            exit(55) if err_code == 2 else exit(54) if err_code == 1 else None
            variable = MainProgram.get_variable(symb1)
            if variable['type'] is None:
                exit(56)
            if variable['type'] != 'int':
                exit(53)
            symb1 = variable['val']
        else:
            if symb1_type != 'int':
                exit(53)

        if symb2_type == 'var':
            err_code = MainProgram.check_var_in_memory(symb2)
            exit(55) if err_code == 2 else exit(54) if err_code == 1 else None
            variable = MainProgram.get_variable(symb2)
            if variable['type'] is None:
                exit(56)
            if variable['type'] != 'int':
                exit(53)
            symb2 = variable['val']
        else:
            if symb2_type != 'int':
                exit(53)

        if iopcode == 'ADD':
            MainProgram.set_variable(var, 'int', int(symb1) + int(symb2))
        elif iopcode == 'SUB':
            MainProgram.set_variable(var, 'int', int(symb1) - int(symb2))
        elif iopcode == 'MUL':
            MainProgram.set_variable(var, 'int', int(symb1) * int(symb2))
        else:
            if int(symb2) != 0:
                MainProgram.set_variable(var, 'int', int(int(symb1) / int(symb2)))
            else:
                exit(57)

    elif iopcode in ['LT', 'GT', 'EQ']:
        var = instruction.get_args()[0].get_value()
        err_code = MainProgram.check_var_in_memory(var)
        exit(55) if err_code == 2 else exit(54) if err_code == 1 else None

        symb1_type = instruction.get_args()[1].get_type()
        symb2_type = instruction.get_args()[2].get_type()
        symb1 = instruction.get_args()[1].get_value()
        symb2 = instruction.get_args()[2].get_value()

        if symb1_type == 'var':
            err_code = MainProgram.check_var_in_memory(symb1)
            exit(55) if err_code == 2 else exit(54) if err_code == 1 else None
            variable = MainProgram.get_variable(symb1)
            symb1_type = variable['type']
            symb1 = variable['val']

        if symb2_type == 'var':
            err_code = MainProgram.check_var_in_memory(symb2)
            exit(55) if err_code == 2 else exit(54) if err_code == 1 else None
            variable = MainProgram.get_variable(symb2)
            symb2_type = variable['type']
            symb2 = variable['val']

        if iopcode != 'EQ':
            if symb1_type is None or symb2_type is None:
                exit(56)

            if symb1_type != symb2_type:
                exit(53)

            if symb1 is None or symb2 is None:
                exit(53)
            if iopcode == 'LT':
                MainProgram.set_variable(var, 'bool', symb1 < symb2)
            else:
                MainProgram.set_variable(var, 'bool', symb1 > symb2)
        else:
            if (symb1_type not in (None, 'nil') and symb2_type in (None, 'nil')) or (symb1_type in (None, 'nil') and symb2_type not in (None, 'nil')):
                MainProgram.set_variable(var, 'bool', symb1 == symb2)

            else:
                if symb1_type != symb2_type:
                    exit(53)
                MainProgram.set_variable(var, 'bool', symb1 == symb2)

    elif iopcode in ['AND', 'OR']:
        var = instruction.get_args()[0].get_value()
        err_code = MainProgram.check_var_in_memory(var)
        exit(55) if err_code == 2 else exit(54) if err_code == 1 else None

        symb1_type = instruction.get_args()[1].get_type()
        symb2_type = instruction.get_args()[2].get_type()
        symb1 = instruction.get_args()[1].get_value()
        symb2 = instruction.get_args()[2].get_value()

        if symb1_type == 'var':
            err_code = MainProgram.check_var_in_memory(symb1)
            exit(55) if err_code == 2 else exit(54) if err_code == 1 else None
            variable = MainProgram.get_variable(symb1)
            symb1_type = variable['type']
            symb1 = variable['val']
            if symb1_type is None:
                exit(56)

        if symb2_type == 'var':
            err_code = MainProgram.check_var_in_memory(symb2)
            exit(55) if err_code == 2 else exit(54) if err_code == 1 else None
            variable = MainProgram.get_variable(symb2)
            symb2_type = variable['type']
            symb2 = variable['val']
            if symb2_type is None:
                exit(56)

        if symb1_type != symb2_type and (symb1_type or symb2_type) != 'bool':
            exit(53)


        if iopcode == 'AND':
            MainProgram.set_variable(var, 'bool', symb1 and symb2)
        else:
            MainProgram.set_variable(var, 'bool', symb1 or symb2)

    elif iopcode == 'NOT':
        var = instruction.get_args()[0].get_value()
        err_code = MainProgram.check_var_in_memory(var)
        exit(55) if err_code == 2 else exit(54) if err_code == 1 else None

        symb1_type = instruction.get_args()[1].get_type()
        symb1 = instruction.get_args()[1].get_value()
        if symb1_type == 'var':
            err_code = MainProgram.check_var_in_memory(symb1)
            exit(55) if err_code == 2 else exit(54) if err_code == 1 else None
            variable = MainProgram.get_variable(symb1)
            symb1_type = variable['type']
            symb1 = variable['val']

            if symb1_type is None:
                exit(56)

        if symb1_type != 'bool':
            exit(53)

        if symb1 is None:
            exit(56)


        MainProgram.set_variable(var, 'bool', not symb1)

    elif iopcode == 'INT2CHAR':
        var = instruction.get_args()[0].get_value()
        err_code = MainProgram.check_var_in_memory(var)
        exit(55) if err_code == 2 else exit(54) if err_code == 1 else None

        symb1_type = instruction.get_args()[1].get_type()
        symb1 = instruction.get_args()[1].get_value()

        if symb1_type == 'var':
            err_code = MainProgram.check_var_in_memory(symb1)
            exit(55) if err_code == 2 else exit(54) if err_code == 1 else None
            variable = MainProgram.get_variable(symb1)
            symb1_type = variable['type']
            symb1 = variable['val']
            if symb1_type is None:
                exit(56)

        if symb1_type != 'int':
            exit(53)

        if int(symb1) > 1023 or int(symb1) < 0:
            exit(58)

        symb1 = chr(int(symb1))
        MainProgram.set_variable(var, 'string', symb1)

    elif iopcode == 'STRI2INT':
        var = instruction.get_args()[0].get_value()
        err_code = MainProgram.check_var_in_memory(var)
        exit(55) if err_code == 2 else exit(54) if err_code == 1 else None

        symb1_type = instruction.get_args()[1].get_type()
        symb2_type = instruction.get_args()[2].get_type()
        symb1 = instruction.get_args()[1].get_value()
        symb2 = instruction.get_args()[2].get_value()

        if symb1_type == 'var':
            err_code = MainProgram.check_var_in_memory(symb1)
            exit(55) if err_code == 2 else exit(54) if err_code == 1 else None
            variable = MainProgram.get_variable(symb1)
            symb1_type = variable['type']
            symb1 = variable['val']
            if symb1_type is None:
                exit(56)

        if symb2_type == 'var':
            err_code = MainProgram.check_var_in_memory(symb2)
            exit(55) if err_code == 2 else exit(54) if err_code == 1 else None
            variable = MainProgram.get_variable(symb2)
            symb2_type = variable['type']
            symb2 = variable['val']
            if symb2_type is None:
                exit(56)

        if symb1_type != 'string' or symb2_type != 'int':
            exit(53)

        if symb2 >= len(symb1) or symb2 < 0:
            exit(58)

        MainProgram.set_variable(var, 'int', ord(symb1[symb2]))

    elif iopcode == 'READ':
        var = instruction.get_args()[0].get_value()
        err_code = MainProgram.check_var_in_memory(var)
        exit(55) if err_code == 2 else exit(54) if err_code == 1 else None

        symb1_type = instruction.get_args()[1].get_type()
        symb1 = instruction.get_args()[1].get_value()
        if symb1_type != 'type':
            exit(53)
        try:
            parse_value = input()
        except EOFError:
            exit(56)

        if symb1 == 'int':
            if parse_value.startswith('-'):
                if parse_value[1:].isdigit():
                    MainProgram.set_variable(var, 'int', int(parse_value))
            else:
                if parse_value.isdigit():
                    MainProgram.set_variable(var, 'int', int(parse_value))
                else:
                    MainProgram.set_variable(var, 'nil', None)
        elif symb1 == 'string':
            pattern = r'\\(\d{3})'
            symb = re.sub(pattern, lambda m: chr(int(m.group(1))), str(parse_value))
            MainProgram.set_variable(var, 'str', symb)
        elif symb1 == 'bool':
            if (str(parse_value)).upper() == 'TRUE':
                MainProgram.set_variable(var, 'bool', True)
            else:
                MainProgram.set_variable(var, 'bool', False)

    elif iopcode == 'WRITE':
        symb_type = instruction.get_args()[0].get_type()
        symb = instruction.get_args()[0].get_value()

        if symb_type == 'var':
            err_code = MainProgram.check_var_in_memory(symb)
            exit(55) if err_code == 2 else exit(54) if err_code == 1 else None
            variable = MainProgram.get_variable(symb)
            symb_type = variable['type']
            symb = variable['val']

        if symb_type == 'int':
            print(symb, end="")
        elif symb_type == 'bool':
            if symb == True:
                print("true", end="")
            else:
                print("false", end="")
        elif symb_type == 'string':
            pattern = r'\\(\d{3})'
            if type(symb) == 'str':
                symb = re.sub(pattern, lambda m: chr(int(m.group(1))), symb)
                print(symb, end="")
            else:
                print(symb, end="")
        elif symb_type == 'nil' or symb_type is None:
            print("", end="")

    elif iopcode == 'CONCAT':
        var = instruction.get_args()[0].get_value()
        err_code = MainProgram.check_var_in_memory(var)
        exit(55) if err_code == 2 else exit(54) if err_code == 1 else None

        symb1_type = instruction.get_args()[1].get_type()
        symb2_type = instruction.get_args()[2].get_type()
        symb1 = instruction.get_args()[1].get_value()
        symb2 = instruction.get_args()[2].get_value()

        if symb1_type == 'var':
            err_code = MainProgram.check_var_in_memory(symb1)
            exit(55) if err_code == 2 else exit(54) if err_code == 1 else None
            variable = MainProgram.get_variable(symb1)
            symb1_type = variable['type']
            symb1 = variable['val']
            if symb1_type is None:
                exit(56)

        if symb2_type == 'var':
            err_code = MainProgram.check_var_in_memory(symb2)
            exit(55) if err_code == 2 else exit(54) if err_code == 1 else None
            variable = MainProgram.get_variable(symb2)
            symb2_type = variable['type']
            symb2 = variable['val']
            if symb2_type is None:
                exit(56)

        if symb1_type != 'string' or symb2_type != 'string':
            exit(53)

        MainProgram.set_variable(var, 'string', symb1 + symb2)

    elif iopcode == 'STRLEN':
        var = instruction.get_args()[0].get_value()
        err_code = MainProgram.check_var_in_memory(var)
        exit(55) if err_code == 2 else exit(54) if err_code == 1 else None

        symb1_type = instruction.get_args()[1].get_type()
        symb1 = instruction.get_args()[1].get_value()

        if symb1_type == 'var':
            err_code = MainProgram.check_var_in_memory(symb1)
            exit(55) if err_code == 2 else exit(54) if err_code == 1 else None
            variable = MainProgram.get_variable(symb1)
            symb1_type = variable['type']
            symb1 = variable['val']
            if symb1_type is None:
                exit(56)

        if symb1_type != 'string':
            exit(53)

        MainProgram.set_variable(var, 'int', len(symb1))

    elif iopcode == 'GETCHAR':
        var = instruction.get_args()[0].get_value()
        err_code = MainProgram.check_var_in_memory(var)
        exit(55) if err_code == 2 else exit(54) if err_code == 1 else None

        symb1_type = instruction.get_args()[1].get_type()
        symb2_type = instruction.get_args()[2].get_type()
        symb1 = instruction.get_args()[1].get_value()
        symb2 = instruction.get_args()[2].get_value()

        if symb1_type == 'var':
            err_code = MainProgram.check_var_in_memory(symb1)
            exit(55) if err_code == 2 else exit(54) if err_code == 1 else None
            variable = MainProgram.get_variable(symb1)
            symb1_type = variable['type']
            symb1 = variable['val']
            if symb1_type is None:
                exit(56)

        if symb2_type == 'var':
            err_code = MainProgram.check_var_in_memory(symb2)
            exit(55) if err_code == 2 else exit(54) if err_code == 1 else None
            variable = MainProgram.get_variable(symb2)
            symb2_type = variable['type']
            symb2 = variable['val']
            if symb2_type is None:
                exit(56)

        if symb1_type != 'string' or symb2_type != 'int':
            exit(53)

        if symb2 >= len(symb1) or symb2 < 0:
            exit(58)

        MainProgram.set_variable(var, 'string', symb1[symb2])

    elif iopcode == 'SETCHAR':
        var = instruction.get_args()[0].get_value()
        err_code = MainProgram.check_var_in_memory(var)
        exit(55) if err_code == 2 else exit(54) if err_code == 1 else None

        symb1_type = instruction.get_args()[1].get_type()
        symb2_type = instruction.get_args()[2].get_type()
        symb1 = instruction.get_args()[1].get_value()
        symb2 = instruction.get_args()[2].get_value()

        varr = MainProgram.get_variable(var)
        variable = varr['val']
        variable_type = varr['type']

        if symb1_type == 'var':
            err_code = MainProgram.check_var_in_memory(symb1)
            exit(55) if err_code == 2 else exit(54) if err_code == 1 else None
            variable = MainProgram.get_variable(symb1)
            symb1_type = variable['type']
            symb1 = variable['val']
            if symb1_type is None:
                exit(56)

        if symb2_type == 'var':
            err_code = MainProgram.check_var_in_memory(symb2)
            exit(55) if err_code == 2 else exit(54) if err_code == 1 else None
            variable = MainProgram.get_variable(symb2)
            symb2_type = variable['type']
            symb2 = variable['val']
            if symb2_type is None:
                exit(56)

        variable = varr['val']
        variable_type = varr['type']
        if variable_type != 'string' or symb1_type != 'int' or symb2_type != 'string':
            exit(53)

        if symb1 >= len(variable) or symb1 < 0 or len(symb2) == 0:
            exit(58)

        variable = list(variable)
        variable[symb1] = symb2[0]
        variable = ''.join(variable)
        MainProgram.set_variable(var, 'string', variable)

    elif iopcode == 'TYPE':
        var = instruction.get_args()[0].get_value()
        err_code = MainProgram.check_var_in_memory(var)
        exit(55) if err_code == 2 else exit(54) if err_code == 1 else None

        symb1_type = instruction.get_args()[1].get_type()
        symb1 = instruction.get_args()[1].get_value()

        if symb1_type == 'var':
            err_code = MainProgram.check_var_in_memory(symb1)
            exit(55) if err_code == 2 else None
            if err_code == 0:
                variable = MainProgram.get_variable(symb1)
                symb1_type = variable['type']
                symb1 = variable['val']
            elif err_code == 1:
                symb1_type = ""
                symb1 = ""

        MainProgram.set_variable(var, 'string', symb1_type)

    elif iopcode == 'JUMP':
        label = instruction.get_args()[0].get_value()
        if label not in MainProgram.lables:
            exit(52)
        MainProgram.set_curr_pos(MainProgram.lables[label])
        MainProgram.dec_curr_pos()

    elif iopcode in ['JUMPIFEQ', 'JUMPIFNEQ']:
        label = instruction.get_args()[0].get_value()
        if label not in MainProgram.lables:
            exit(52)

        symb1_type = instruction.get_args()[1].get_type()
        symb2_type = instruction.get_args()[2].get_type()
        symb1 = instruction.get_args()[1].get_value()
        symb2 = instruction.get_args()[2].get_value()

        if symb1_type == 'var':
            err_code = MainProgram.check_var_in_memory(symb1)
            exit(55) if err_code == 2 else exit(54) if err_code == 1 else None
            variable = MainProgram.get_variable(symb1)
            symb1_type = variable['type']
            symb1 = variable['val']
            if symb1_type is None:
                exit(56)

        if symb2_type == 'var':
            err_code = MainProgram.check_var_in_memory(symb2)
            exit(55) if err_code == 2 else exit(54) if err_code == 1 else None
            variable = MainProgram.get_variable(symb2)
            symb2_type = variable['type']
            symb2 = variable['val']
            if symb2_type is None:
                exit(56)

        if symb1_type != symb2_type or symb1_type == None or symb2_type == None:
            exit(53)

        if iopcode == 'JUMPIFEQ':
            if symb1 == symb2:
                MainProgram.set_curr_pos(MainProgram.lables[label])
                MainProgram.dec_curr_pos()
        elif iopcode == 'JUMPIFNEQ':
            if symb1 != symb2:
                MainProgram.set_curr_pos(MainProgram.lables[label])
                MainProgram.dec_curr_pos()

    elif iopcode == 'EXIT':
        symb1_type = instruction.get_args()[0].get_type()
        symb1 = instruction.get_args()[0].get_value()

        if symb1_type == 'var':
            err_code = MainProgram.check_var_in_memory(symb1)
            exit(55) if err_code == 2 else exit(54) if err_code == 1 else None
            variable = MainProgram.get_variable(symb1)
            symb1_type = variable['type']
            symb1 = variable['val']
            if symb1_type is None:
                exit(56)

        if symb1_type != 'int':
            exit(53)

        if symb1 > 49 or symb1 < 0:
            exit(57)

        #print("Exit opcode")
        exit(symb1)

    elif iopcode == 'DPRINT':
        symb1_type = instruction.get_args()[0].get_type()
        symb1 = instruction.get_args()[0].get_value()

        if symb1_type == 'var':
            err_code = MainProgram.check_var_in_memory(symb1)
            exit(55) if err_code == 2 else exit(54) if err_code == 1 else None
            variable = MainProgram.get_variable(symb1)
            symb1_type = variable['type']
            symb1 = variable['val']
            if symb1_type is None:
                exit(56)

        if symb1 == None:
            exit(56)

        sys.stderr.write(str(symb1))

    elif iopcode == 'BREAK': #ADD
        sys.stderr.write("Current pos in program is " + str(MainProgram.current_pos))
        sys.stderr.write("Memory")
        sys.stderr.write("Global frame - " + str(MainProgram.global_frame))
        sys.stderr.write("Local frame - " + str(MainProgram.local_frame))
        sys.stderr.write("Temporary frame - " + str(MainProgram.temporary_frame))

    elif iopcode == 'CREATEFRAME':
        MainProgram.create_temporary_frame()

    elif iopcode == 'POPFRAME':
        if MainProgram.pop_local_frame() == 1:
            exit(56)

    elif iopcode == 'PUSHFRAME':
        if MainProgram.push_temporary_frame() == 1:
            exit(56)
    else:
        print("UNexpected opcode! ")
        exit(100)

    MainProgram.inc_curr_pos()

