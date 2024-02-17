import json
import os
import re

class Disk:
    def __init__(self, databus, disk_name = "pyComp-VDISK", size = None):
        self.databus = databus
        self.size = size
        self.disk_name = f"{disk_name}.json"
        # Check if the virtual disk already exists
        if os.path.exists(self.disk_name):
            self.file_system = self.read_from_virtual_disk(self.disk_name)
        else:
            # Create a new virtual disk
            self.file_system = {}
            self.save_to_virtual_disk(self.file_system, self.disk_name)
        
    def save_to_virtual_disk(self, data: dict, filename: str):
        with open(filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)
    
    def read_from_virtual_disk(self, filename: str) -> dict:
        with open(filename, 'r') as json_file:
            data = json.load(json_file)
        return data

    def list_files(self):
        return self.file_system.keys()

    def create_file(self, filename):
        if filename not in self.file_system:
            self.file_system[filename] = []
            self.save_to_virtual_disk(self.filesystem, self.disk_name)
            return 0
        else:
            return 1

    def delete_file(self, filename):
        if filename in self.file_system:
            del self.file_system[filename]
            self.save_to_virtual_disk(self.filesystem, self.disk_name)
            return 0
        else:
            return 1

    def write_to_file(self, filename, data, overwrite_flag = 1):
        if filename in self.file_system:
            if overwrite_flag == 1:
                self.file_system[filename] = file_data
            else:
                file_data = self.file_system[filename]
                file_data.extend(data)
                self.file_system[filename] = file_data
                self.save_to_virtual_disk(self.filesystem, self.disk_name)
            return 0
        else:
            return 1
    
    def read_from_file(self, filename):
        if filename in self.file_system:
            file_data = self.file_system[filename]
            return file_data
        else:
            return 1
        
class Keyboard:
    def __init__(self, databus):
        self.databus = databus
        
    def get_keys(self):
        keys = input()
        return keys

class Terminal:
    def __init__(self, databus):
        self.databus = databus
    
    def render(self, value):
        print(value)

class Register:
    def __init__(self):
        self.current_value = 0
        
    def save(self, value: int, datatype=None):
        self.current_value = value
    
    def load(self, address=None):
        return self.current_value
    
class ROM:
    def __init__(self, program_name):
        self.program_name = f"{program_name}.program"
        
    def read(self):
        with open(self.program_name, 'r') as program_file:
            data = program_file.read()
        return data
        
class RAM:
    def __init__(self, databus, size):
        self.databus = databus
        self.memory = [None for _ in range(size)]
    
    # Returns the memory address of the first empty space in memory
    def find_free_memory(self):
        try:
            return self.memory.index(None)
        except ValueError:
            self.databus.publish("device_event", "terminal", "OUT OF MEMORY")
            return None

    def read(self, address, size=None):
        return self.memory[address]

    def save(self, address, value):
        self.memory[address] = value
        return 0

class ALU:
    def __init__(self):
        pass
        
    def add(self, a, b):
        return a+b
        
    def sub(self, a, b):
        return a-b
        
    def mul(self, a, b):
        return a*b
        
    def div(self, a, b):
        return a/b
    
    def OR(self, a, b):
        return a or b

    def AND(self, a, b):
        return a and b

    def NOT(self, a):
        return not a

class CPU:
        def __init__(self, databus):
            self.databus = databus
            self.alu = ALU()
            self.program_counter = Register()
            self.general_purpose_registers = []
            for i in range(8):
                self.general_purpose_registers.append(Register())
            self.defined_variables = {"TEST": 1023}
            self.defined_functions = {}
            self.debug = False
            
        def debugger(self):
            print("====DEBUG====")
            print("~Defined VARS:~")
            print("VAR - VALUE - MEM ADDRESS")
            for key, value in self.defined_variables.items():
                if value == None:
                    print(f"{key} - None - {value}")
                else:
                    print(f"{key} - {self.databus.publish('device_event', 'memory', value, 'OUT')} - {value}")
            print("~Defined FUNCTIONS:~")
            for key, value in self.defined_functions.items():
                print(f"{key} - {value}")
            print("~Register values:~")
            for i in range(len(self.general_purpose_registers)):
                print(f"{i} - {self.general_purpose_registers[i].load()}")
            print(f"Program counter value: {self.program_counter.load()}")
            print("====DEBUG=END==")
            
        # Execute a program
        def program_reader(self, program):
            program = program.split("\n")
            self.program_counter.save(0)
            while self.program_counter.load() > -1:
                self.pre_scanner(program[self.program_counter.load()])
                self.program_counter.save(self.alu.add(self.program_counter.load(), 1))
            self.program_counter.save(0)
            while self.program_counter.load() > -1:
                # Execute instruction
                self.interpreter(program[self.program_counter.load()])
                # Move to next instruction
                self.program_counter.save(self.alu.add(self.program_counter.load(), 1))

        # Extract the value (string) between opening and closing chars
        def extract_value(self, input_string, char):
            if char == '[':
                closing_char = ']'
            elif char == '(':
                closing_char = ')'
            if char == '{':
                closing_char = "}"
            if char == '<':
                closing_char = ">"
            start_index = input_string.find(char) + 1
            end_index = input_string.find(closing_char)
            if start_index != -1 and end_index != -1:
                return input_string[start_index:end_index]
            else:
                return None

        # Differentiate between different inputs
        def decode_value(self, string):
            if self.debug:
                self.debugger()
            # String
            if string.startswith("{"):
                return self.extract_value(string, string[0])
            # Variable
            elif string.startswith("["):
                variable_name = self.extract_value(string, string[0])
                variable_address = self.defined_variables[variable_name]
                variable_content = self.databus.publish("device_event", "memory", variable_address, "OUT")
                return variable_content
            # Number
            elif string.startswith("("):
                return float(self.extract_value(string, string[0]))
            # Label
            elif string.startswith("<"):
                label_name = self.extract_value(string, string[0])
                label_address = self.defined_functions[label_name]
                return label_address

        # Differentiate between character input or number input
        def txt_or_num(self, string, label=False):
            if self.debug:
                print("string in txt_or_num:", string)
            if string.startswith("TXT"):
                if label == False:
                    # String
                    if "{" in string:
                        return self.extract_value(string, char='{')
                    # Variable
                    else:
                        value =  self.extract_value(string, char='[')
                        variable_address = self.defined_variables[value]
                        variable_content = self.databus.publish("device_event", "memory", variable_address, "OUT")
                        return variable_content
            elif string.startswith("NUM"):
                value = self.extract_value(string, char='(')
                return float(value)
            # Label
            else:
                value = self.extract_value(string, char='{')
                label_address = self.defined_functions[value]
                return label_address
        
        # The pre-scanner checks all the functions in the code and defines them in memory
        # After the pre-scanner the actual program executes
        def pre_scanner(self, instruction):
                if instruction.startswith("LABEL"):
                    self.interpreter(instruction)
                if instruction.startswith("END"):
                    self.program_counter.save(-2)
            
        def interpreter(self, instruction):
            if self.debug:
                print(f"~EXECUTING~: {instruction}")
            # Code comment
            if instruction.startswith("#"):
                pass
            # output to terminal
            if instruction.startswith("OUT"):
                if self.debug == True:
                    self.debugger()
                if "^" in instruction:
                    data = instruction.split("^")[1]
                else:
                    var_adress = self.defined_variables[self.extract_value(instruction, char="(")]
                    data = self.databus.publish("device_event", "memory", var_adress, "OUT")
                self.databus.publish("device_event", "terminal", data)
            # Get user input. Input is stored in last register
            if instruction.startswith("IN"):
                digit_pattern = r'^[0-9].*'
                input_data = self.databus.publish("device_event", "keyboard", None, None)
                # Number
                if re.match(digit_pattern, input_data):
                    input_data = float(input_data)
                self.general_purpose_registers[-1].save(input_data)
            # MOVE a value into a register
            # MOV destination source
            # VALID: MOV REG: REG: _VALID
            # VALID: MOV REG: VAR 
            # VALID: MOV VAR REG: 
            # INVALID: MOV VAR VAR 
            if instruction.startswith("MOV"):
                parameters = instruction.split(" ")
                # Second param is register
                if parameters[2].startswith("REG"):
                    source_register_number = int(parameters[2].split(":")[1])
                    data = self.general_purpose_registers[source_register_number].load()
                # Second param is variable or number or string
                else:
                    data = self.decode_value(parameters[2])
                # First param is register
                if parameters[1].startswith("REG"):
                    destination_register_number = int(parameters[1].split("-"))
                    self.general_purpose_registers[destination_register_number].save(data)
                # First param is variable
                else:
                    var_name = parameters[1]
                    var_adress = self.defined_variables[var_name]
                    if self.debug:
                        print("data", data)
                        print("var_name", var_name)
                        print("var_adress", var_adress)
                    # If variable is not yet assigned
                    if var_adress == None:
                        var_adress = self.databus.publish("device_event", "memory", None, "FREE")
                        self.defined_variables[var_name] = var_adress
                    self.databus.publish("device_event", "memory", [var_adress, data], "IN")
            # Define a variable.
            if instruction.startswith("VAR"):
                parameters = instruction.split(" ")
                if len(parameters) == 2:
                    # Variable is already defined
                    if parameters[1] in self.defined_variables:
                        pass
                    else:
                        self.defined_variables[parameters[1]] = None
                elif len(parameters) == 3:
                    data = self.decode_value(parameters[2])
                    # Variable is already defined, new value will be re-assigned
                    if parameters[1] in self.defined_variables:
                        self.databus.publish("device_event", "memory", [mem_address, data], "IN")
                    else:
                        mem_address = self.databus.publish("device_event", "memory", None, "FREE")
                        self.defined_variables[parameters[1]] = mem_address
                        self.databus.publish("device_event", "memory", [mem_address, data], "IN")
                if self.debug:
                    self.debugger()
            # Define a label(function) in the code
            if instruction.startswith("LABEL"):
                label = instruction.split(" ")[1]
                self.defined_functions[label] = self.program_counter.load()
            # JUMP the code to either a label or a line
            if instruction.startswith("JMP"):
                data = instruction.split(" ")[1]
                address = self.decode_value(data)
                # Save the adress of the next instruction (for return from function)
                self.general_purpose_registers[-2].save(self.alu.add(self.program_counter.load(), 1))
                # Set the address of the label in the PC
                self.program_counter.save(int(address))
            # JUMP to label, if the last register is 0
            if instruction.startswith("JE"):
                if self.general_purpose_registers[-1].load() == 0:
                    data = instruction.split(" ")[1]
                    address = self.decode_value(data)
                    # Save the adress of the next instruction (for return from function)
                    self.general_purpose_registers[-2].save(self.alu.add(self.program_counter.load(), 1))
                    # Set the address of the label in the PC
                    self.program_counter.save(int(address))
                else:
                    pass
            # JUMP to label, if the last register is 1
            if instruction.startswith("JNE"):
                if self.general_purpose_registers[-1].load() == 1:
                    data = instruction.split(" ")[1]
                    address = self.decode_value(data)
                    # Save the adress of the next instruction (for return from function)
                    self.general_purpose_registers[-2].save(self.alu.add(self.program_counter.load(), 1))
                    # Set the address of the label in the PC
                    self.program_counter.save(int(address))
                else:
                    pass
            # return from a function, value is stored in last register
            if instruction.startswith("RET"):
                parameters = instruction.split(" ")
                data = self.decode_value(parameters[1])
                # save result in return 
                self.general_purpose_registers[-1].save(data)
                # Go back to line of code where function was executed
                self.program_counter.save(int(self.general_purpose_registers.load(-2)))
            # Execute a new program
            if instruction.startswith("EXEC"):
                parameters = instruction.split(" ")
                # We load the program from the given variable
                var_name = parameters[1]
                var_address = self.defined_variables[var_name]
                program = self.databus.publish("device_event", "memory", var_address, "OUT") 
                # First we clear memory of the current program
                # fill registers to 0
                for i in range(len(self.general_purpose_registers)):
                    self.general_purpose_registers[i].save(0)
                # Remove variables from memory
                for mem_address in self.defined_variables.values():
                    self.databus.publish("device_event", "memory", [mem_address, None], "IN")
                self.defined_variables = {}
                # Remove functions from memory
                self.defined_functions = {}
                # Start the new program
                self.program_reader(program)
            # END a program and clear program's memory
            if instruction.startswith("END"):
                self.program_counter.save(-2) # -2 is the signal for ending programs
                # fill registers to 0
                for i in range(len(self.general_purpose_registers)):
                    self.general_purpose_registers[i].save(0)
                # Remove variables from memory
                for mem_address in self.defined_variables.values():
                    self.databus.publish("device_event", "memory", [mem_address, None], "IN")
                self.defined_variables = {}
                # Remove functions from memory
                self.defined_functions = {}
            # Add 2 values together, result is stored in last register
            if instruction.startswith("ADD"):
                parameters = instruction.split(" ")
                a = self.decode_value(parameters[1])
                b = self.decode_value(parameters[2])
                self.general_purpose_registers[-1].save(self.alu.add(a, b))
            # Check if A == B. Return 1 if True, return 0 if False Return is saved in the last register
            if instruction.startswith("CMP"):
                parameters = instruction.split(" ")
                a = self.decode_value(parameters[1])
                b = self.decode_value(parameters[2])
                self.general_purpose_registers[-1].save(self.alu.sub(a, b)) 
                if self.general_purpose_registers[-1].load() == 0:
                    self.general_purpose_registers[-1].save(0)
                else:
                    self.general_purpose_registers[-1].save(1)
            # READ from file. Result is stored in last register
            if instruction.startswith("READ"):
                parameters = instruction.split(" ")
                #variable_name = parameters[1]
                filename = parameters[1]
                #var_address = self.defined_variables[variable_name]
                file_content = self.databus.publish("device_event", "disk", filename, "OUT")
                self.general_purpose_registers[-1].save(file_content)
                if self.debug:
                    self.debugger()
                #self.databus.publish("device_event", "memory", [var_address, file_content], "IN")
            # WRITE to file
            if instruction.startswith("WRITE"):
                parameters = instruction.split(" ")
                filename = parameters[1]
                data = parameters[2]
                overwrite_flag = int(parameters[3])
                self.databus.publish("device_event", "disk", [filename, data, overwrite_flag], "IN")
            # CREATE file
            if instruction.startswith("CREATE"):
                parameters = instruction.split(" ")
                filename = parameters[1]
                self.databus.publish("device_event", "disk", filename, "CREATE")
            # DELETE file
            if instruction.startswith("DEL"):
                parameters = instruction.split(" ")
                filename = parameters[1]
                self.databus.publish("device_event", "disk", filename, "DELETE")
            # List files Result is storen in last register
            if instruction.startswith("LS"):
                self.general_purpose_registers[-1].save(self.databus.publish("device_event", "disk", None, "LIST"))
                

# OUT(^5+8=^)
# VAR five (5)
# VAR eight (8)
# VAR result
# ADD [five] [eight]
# MOV result REG:-1
# OUT(result)
# VAR mystring {hello_world}
# OUT(mystring)

# BIOS = str("""out(^welcome to PyComp BIOS^)\n
# out(^Do you want to BOOT from USB or Disk?^)\n
# out(^5+8=^\n
# LABEL my_function\n
# out(^Hello from my_function^)\n
# LABEL another_function\n
# out(^hello from another function^)\n
# VAR myVar 12\n
# VAR anotherVar 99\n
# out(^the variable is: ^)\n
# out(myVar)\n
# out(^the other var is: ^)\n
# out(anotherVar)\n
# VAR textVar hello\n
# out(textVar)\n
# #JMP TXT[my_function]\n
# #JMP NUM[0]\n
# END""")
# LABEL my_function\n
# out(^Hello from my_function^)\n
# LABEL another_function\n
# out(^hello from another function^)\n
# VAR myVar 12\n
# VAR anotherVar 99\n
# out(^the variable is: ^)\n
# out(myVar)\n
# out(^the other var is: ^)\n
# out(anotherVar)\n
# VAR textVar hello\n
# out(textVar)\n
#JMP TXT[my_function]\n
#JMP NUM[0]\n

# The device controller is for moving data between devices.
# It uses a simple Pub Sub system
class DeviceController:
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, event_type, callback):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def unsubscribe(self, event_type, callback):
        if event_type in self.subscribers and callback in self.subscribers[event_type]:
            self.subscribers[event_type].remove(callback)

    def publish(self, event_type, *args, **kwargs):
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                return callback(*args, **kwargs)
    
class Motherboard:
    def __init__(self):
        self.device_controller = DeviceController()
        self.device_controller.subscribe("device_event", self.move_data)
        self.static_rom = ROM("BIOS")
        #self.insertible_rom = ROM("OS_INSTALLER")
        self.terminal = Terminal(self.device_controller)
        self.keyboard = Keyboard(self.device_controller)
        self.memory = RAM(self.device_controller, 1024)
        self.disk = Disk(self.device_controller)
        self.cpu = CPU(self.device_controller)
    
    # Move data between devices
    # "IN" means the data goes into the target device
    # "OUT" means the data goes out of the target device
    # The source device is the one that calls the function
    # The source device receives the return of this function
    # Each device can have its own extra operations
    def move_data(self, device, data, operation=None):
        if device == "memory":
            if operation == "IN":
                return self.memory.save(data[0], data[1])
            if operation == "OUT":
                return self.memory.read(data)    
            if operation == "FREE":
                return self.memory.find_free_memory()
        if device == "terminal":
            self.terminal.render(data)
        if device == "keyboard":
            return self.keyboard.get_keys()
        if device == "disk":
            if operation == "CREATE":
                return self.disk.create_file(data)
            elif operation == "DELETE":
                return self.disk.delete_file(data)
            elif operation == "IN":
                return self.disk.write_to_file(data[0], data[1], data[2])
            elif operation == "OUT":
                return self.disk.read_from_file(data)
            elif operation == "LIST":
                return self.disk.list_files()
        if device == "motherboard":
            if operation == "OFF":
                self.powerOFF()
            if operation == "RESTART":
                self.powerOFF()
                self.powerON()

    def powerON(self):
        # Make the CPU read the BIOS(static ROM)
        self.cpu.program_reader(self.static_rom.read())
        
    def powerOFF(self):
        self.disk.save_to_virtual_disk(self.disk.filesystem, self.disk.disk_name)
        self.memory.memory = {}
                
computer = Motherboard()
computer.powerON()
        
# DOCUMENTATION:

# The last general purpose register is always where the result is stored of the last operation. (Accumulator register)

        



        

    
        
        
