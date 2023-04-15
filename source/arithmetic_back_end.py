

from __future__ import print_function
import sys, struct, shlex, operator
import ast

#Old reduntant code, I think it does nothing? Have never used it.
nd_Ident, nd_String, nd_Integer, nd_Sequence, nd_If, nd_Prtc, nd_Prts, nd_Prti,\
nd_While,nd_Assign, nd_Negate, nd_Not, nd_Mul, nd_Div, nd_Mod, nd_Add, nd_Sub,\
nd_Lss, nd_Leq, nd_Gtr, nd_Geq, nd_Eql, nd_Neq, nd_And, nd_Or = range(25)                    
 
LOAD, STORE, PUSH, ADD, SUB, MULT, DIV, MOD, LT, GT, LE, GE, EQ, NE, AND, OR,\
NEG, NOT, JUMP, JIN, PRTC, PRTS, PRTI, STOP, CALLSUB, RET, DC1,DC2, CALLNAT,\
   STORE_IND,LOAD_IND = range(31)
 
operators = {ast.Lt: LT, ast.Gt: GT, ast.LtE: LE, ast.GtE: GE, ast.Eq: EQ, \
             ast.NotEq: NE, ast.And: AND, ast.Or: OR, ast.Sub: SUB,\
             ast.Add: ADD, ast.Div: DIV, ast.Mult: MULT, ast.Mod: MOD}
 
unary_operators = {nd_Negate: NEG, nd_Not: NOT}

comp_ops = {LT:"lt", GT:"gt", LE:"le", GE:"ge", EQ:"eq", NE:"ne"}

###############################################################################
#           CONSIDER PUTTING THE FOLLOWING IN A THYMIO.PY MODULE

event_dict = {"BUTTON.BACKWARD":"_ev.button.backward", \
"BUTTON.LEFT":"_ev.button.left", "BUTTON.CENTER":"_ev.button.center", \
"BUTTON.FORWARD":"_ev.button.forward", "BUTTON.RIGHT":"_ev.button.right", \
"BUTTONS":"_ev.buttons", "PROX":"_ev.prox", "PROX.COMM":"_ev.prox.comm", \
"TAP":"_ev.tap", "ACC":"_ev.acc", "MIC":"_ev.mic", \
"SOUND.FINISHED":"_ev.sound.finished", "TEMPERATURE":"_ev.temperature", \
"RC5":"_ev.rc5", "MOTOR":"_ev.motor", "TIMER0":"_ev.timer0", \
"TIMER1":"_ev.timer1", "restart":"0xffff"}#WITH THYMIO IDETNIFIERS
                         
# event_dict = {"BUTTON.BACKWARD":"0xfffe", "BUTTON.LEFT":"0xfffd", \
# "BUTTON.CENTER":"0xfffc", "BUTTON.FORWARD":"0xfffb", "BUTTON.RIGHT":"0xfffa", \
# "BUTTONS":"0xfff9", "PROX":"0xfff8", "PROX.COMM":"0xfff7", "TAP":"0xfff6", \
# "ACC":"0xfff5", "MIC":"0xfff4", "SOUND.FINISHED":"0xfff3", \
# "TEMPERATURE":"0xfff2", "RC5":"0xfff1", "MOTOR":"0xfff0", "TIMER0":"0xffef", \
# "TIMER1":"0xffee", "restart":"0xffff"}#WITH THYMIO HEX

thymio_vars = {"thymio.motor.left.target":"motor.left.target",\
               "thymio.motor.right.target":"motor.right.target",\
               "thymio.button.center":"button.center",\
               "thymio.timer.period":"timer.period",\
               "thymio.prox.horizontal":"prox.horizontal"}
    
thymio_nf = {"thymio.leds.top":[3,"_nf.leds.top"],\
             "thymio.leds.bottom.left":[3,"_nf.leds.bottom.left"],\
             "thymio.leds.bottom.right":[3,"_nf.leds.bottom.right"],\
             "thymio.leds.circle":[8,"_nf.leds.circle"]}
    

###############################################################################

class HoleCall:
    
    def __init__(self):
        self._dict = {}#stores holes from calls/returns/etc...
        self.flag = 0#usefull conditional flag
    def store_hole(self,address,caller):#self descriptive method
        self._dict[address] = caller
    def eject_holes(self,caller):#one call can come from many holes
        hole_addresses = []
        for address,call in self._dict.items():
            if call == caller:
                hole_addresses.append(address)       
        for address in hole_addresses:
            self._dict.pop(address)
        return hole_addresses
    def eject_call(self,address):#but each hole has only one call
        caller = self._dict[address] 
        self._dict.pop(address)
        return caller
        
 
    
func_calls = HoleCall()
func_rets = HoleCall()
jump_cond = HoleCall()
event_calls = HoleCall()
thymio_var_calls = HoleCall()
thymio_nf_calls = HoleCall()
indirect_sizes = HoleCall()

input_file  = None
code        = bytearray()
globals     = {}
locals      = {}
globals_n   = 0
locals_n    = 0
word_size   = 4

var_offset = 200
stop_flag = 0
scope_flag = globals

#*** show error and exit
def error(msg):
    print("%s" % (msg))
    exit(1)

#***
def int_to_bytes(val):
    return struct.pack("<i", val)

def bytes_to_int(bstr):
    return struct.unpack("<i", bstr)
 
#***
def emit_byte(x):
    code.append(x)
 
def emit_word(x):
    s = int_to_bytes(x)
    for x in s:
        code.append(x)
        
#***     
def emit_word_at(at,n):
    def emit_word_at(at, n):
        code[at:at+word_size] = int_to_bytes(n)
        
    if isinstance(at,int) and isinstance(n,int):
        emit_word_at(at, n)
    elif isinstance(at,list) and isinstance(n,list):
        for i,j in zip(at,n):
            emit_word_at(i, j)
    else:
        error(emit_word_at)
        
 
def hole():
    t = len(code)
    emit_word(0)
    return t
 
#***
def reset_locals():
    global locals
    locals = {}
    for i,j in enumerate(thymio_vars):
        locals[j] = i
    
def fetch_var_offset(name,mode):
    global globals_n
    global locals_n
    n = mode.get(name,None)
    if n == None:
        mode[name] = globals_n + locals_n
        n = globals_n + locals_n
        if mode == globals:
            globals_n += 1
        elif mode == locals:
            locals_n += 1
        else:
            error(fetch_var_offset)
    return n
    

#***
def preprocessor(x,mode = 0):
    main_body = x
#OPTIMIZE
    if(len(main_body) > 1):
        idx = 0
        while(idx < len(main_body)-1):
            idx += 1
            if(type(main_body[idx])!=ast.FunctionDef and\
               type(main_body[idx-1])==ast.FunctionDef):                                
                
                temp_node = main_body[idx]
                main_body[idx] = main_body[idx-1]
                main_body[idx-1] = temp_node
                idx = 0
                
    if(mode):
        global globals_n
        global locals_n
        emit_byte(DC1)
        tab_len_hole = hole()
        emit_byte(DC2)
        start_hole = hole()
        for i in main_body:
            if  type(i)==ast.FunctionDef and i.decorator_list:
                emit_byte(DC2)
                event_hole = hole()
                event_name = i.decorator_list[0].args[0].attr
                event_calls.store_hole(event_hole, event_name)
        emit_word_at(start_hole,len(code)-start_hole)
        event_calls.store_hole(len(code)-start_hole, "restart")
        emit_word_at(tab_len_hole,len(code))#-tab_len_hole)
        
        #loading the thymio variables
        for i,j in enumerate(thymio_vars):
            globals[j] = i
            locals[j] = i
            globals_n += 1
            

#***
def code_finish():
    global stop_flag
    if(stop_flag == 0):
        emit_byte(STOP)
    
def code_gen(x):
    global stop_flag
    global scope_flag
    
    if type(x) == ast.Pass: pass

    elif type(x) == ast.Module:
        preprocessor(x.body,mode = 1)
        code_gen(x.body)
        
    elif type(x) == list:
        preprocessor(x)
        for i in range(len(x)):
            code_gen(x[i])
            
    elif type(x) == ast.Assign:
        
        code_gen(x.value)
        if(type(x.value) == ast.Call):
            emit_byte(LOAD)
            loadadr = hole()
            f = x.value.func.id 
            func_rets.store_hole(loadadr, f)
        code_gen(x.targets[0]) #assume 1 target
    
    elif type(x) == ast.Attribute:
        if type(x.value) == ast.Attribute:
            x.value.attr = x.value.attr+"."+x.attr
        elif type(x.value) == ast.Name:
            x.value.id = x.value.id+"."+x.attr
        else:
            error("Unknown name type")
        if type(x.ctx) == ast.Load:
            x.value.ctx = ast.Load()
        elif type(x.ctx) == ast.Store:
            x.value.ctx = ast.Store()
        else:
            error("Uknown context")
        code_gen(x.value)
    
    elif type(x) == ast.Constant:
        emit_byte(PUSH)
        emit_word(x.n)
            
    elif type(x) == ast.If:                              #ONLY FOR CONDITIONALS
        if type(x.test) != ast.Compare:
            code_gen(x.test)
            emit_byte(PUSH)
            emit_word(0)
            emit_byte(GT)
        else:
            code_gen(x.test)         # expr
        cond_op = code[-1]
        del code[-1]
        emit_byte(JIN)           # if false, jump 
        p1 = hole()              # make room for jump dest
        jump_cond.store_hole(p1, cond_op)
        code_gen(x.body)         # if true statements
        if (len(x.orelse) != 0):
            emit_byte(JUMP)      # jump over else statements
            p2 = hole()
        emit_word_at(p1, len(code) - p1)
        if (len(x.orelse) != 0):
            code_gen(x.orelse)   # else statements
            emit_word_at(p2, len(code) - p2)
            
    elif type(x) == ast.Compare:
        code_gen(x.left)
        code_gen(x.comparators[0])
        emit_byte(operators[type(x.ops[0])])
        
    elif type(x) == ast.While:                           #ONLY FOR CONDITIONALS
        p1 = len(code)
        if type(x.test) != ast.Compare:
            code_gen(x.test)
            emit_byte(PUSH)
            emit_word(0)
            emit_byte(GT)
        else:
            code_gen(x.test)         # expr
        cond_op = code[-1]
        del code[-1]
        emit_byte(JIN)
        p2 = hole()
        jump_cond.store_hole(p2, cond_op)
        code_gen(x.body)
        emit_byte(JUMP)          # jump back to the top
        emit_word(p1 - len(code))
        emit_word_at(p2, len(code) - p2)
        
    elif type(x) == ast.Call:                                     #NO ARGUMENTS
        emit_byte(CALLSUB)
        subcalladr = hole()
        f = x.func.id
        func_calls.store_hole(subcalladr,f)
        
    elif type(x)== ast.FunctionDef:                               #NO ARGUMENTS
        if(stop_flag == 0): # This is called only once,
            emit_byte(STOP) # after the source code(without the functions)
            stop_flag = 1   # has been generated.
            
        call_holes = func_calls.eject_holes(x.name)
        emit_word_at(call_holes,[len(code)-i for i in call_holes])
        
        decorator_flag = 0
        
        if x.decorator_list:
            decorator_flag = 1
            deco_id = x.decorator_list[0].args[0].attr
            event_holes = event_calls.eject_holes(deco_id)
            emit_word_at(event_holes,[len(code)-i for i in event_holes])
            for i in event_holes:
                event_calls.store_hole(len(code)-i, deco_id)
                
        func_rets.flag = x.name
        scope_flag = locals
        code_gen(x.body)
        if decorator_flag:
            emit_byte(STOP)
        else:
            emit_byte(RET)
        reset_locals()
        
    elif type(x) == ast.Return:
        code_gen(x.value)
        scope_flag = globals
        n = fetch_var_offset('0_return_dummy',scope_flag)
                
        ret_holes = func_rets.eject_holes(func_rets.flag)
        emit_word_at(ret_holes,[n for i in ret_holes])
        
        emit_byte(STORE)
        emit_word(n)
        emit_byte(RET)
        reset_locals()
        
    elif type(x) == ast.Expr:
        code_gen(x.value)
        
    elif type(x) == ast.List:
        for i,j in enumerate(reversed(x.elts)):
            code_gen(j)
            if i < len(x.elts)-1:
                n = fetch_var_offset(len(code), scope_flag)
                emit_byte(STORE)
                emit_word(n)
                
    elif type(x) == ast.Name:
        n = 0
        if type(x.ctx) == ast.Load:
            emit_byte(LOAD)
            if x.id in globals and x.id not in locals:
                n = fetch_var_offset(x.id,globals)
            else:
                n = fetch_var_offset(x.id,scope_flag)
        elif type(x.ctx) == ast.Store:
            n = fetch_var_offset(x.id,scope_flag)
            emit_byte(STORE)
        else:
            error("Unknown name type")
        if x.id in thymio_vars:
            var_hole = hole()
            thymio_var_calls.store_hole(var_hole, thymio_vars[x.id])
        else:
            emit_word(n)
        if x.id in thymio_nf:
            global var_offset
            for i in range(thymio_nf[x.id][0]):
                emit_byte(PUSH)
                emit_word(n-i+var_offset)
                
            emit_byte(CALLNAT)
            nf_hole = hole()
            thymio_nf_calls.store_hole(nf_hole, thymio_nf[x.id][1])
                
    elif type(x) == ast.Subscript:
        
        if type(x.value) == ast.Attribute:
            if type(x.ctx) == ast.Load:
                x.value.ctx = ast.Load()
            elif type(x.ctx) == ast.Store:
                x.value.ctx = ast.Store()
            code_gen(x.value)
            thymio_var_calls._dict[len(code)-4] += '+'+str(x.slice.value.n)
            
        else:
            #n = fetch_var_offset(x.value.id, scope_flag)
            if x.value.id in globals and x.value.id not in locals:
                n = fetch_var_offset(x.value.id,globals)
            else:
                n = fetch_var_offset(x.value.id,scope_flag)
            if type(x.slice) == ast.Index:
                n = n - x.slice.value.n
                
            if type(x.ctx) == ast.Load:
                emit_byte(LOAD)
            elif type(x.ctx) == ast.Store:
                emit_byte(STORE)
            else:
                error("Unknown name type")
            emit_word(n)
#BUG?      
    elif type(x) == type(None):
            pass
        
    elif type(x) == ast.Global:
        glob_id=x.names[0]
        n = fetch_var_offset(glob_id, globals)
        locals[glob_id] = n
        
    elif type(x) == ast.NameConstant:    #ONLY FOR SETTING TRUE/FALSE VARIABLES
        emit_byte(PUSH)
        if x.value == True:
            emit_word(1)
        elif x.value == False:
            emit_word(0)
        else:
            error("Unknown logical state")
    
    elif type(x) == ast.UnaryOp:           #WE ASSUME ONLY LOGICAL 'NOT' EXISTS
    
        if type(x.op) == ast.Not:
            code_gen(x.operand)
            emit_byte(PUSH)
            emit_word(0)
            emit_byte(EQ)
        if type(x.op) == ast.USub:
            code_gen(x.operand)
            emit_byte(PUSH)
            emit_word(-1)
            emit_byte(MULT)
        
    elif type(x) == ast.BoolOp:             #ONLY 'AND','OR' LOGICAL STATEMENTS
        code_gen(x.values[0])
        for i in range(len(x.values)-1):
            emit_byte(PUSH)
            emit_word(0)
            emit_byte(JIN)
            h1 = hole()
            if type(x.op) == ast.And:
                jump_cond.store_hole(h1,EQ)
            elif type(x.op) == ast.Or:
                jump_cond.store_hole(h1,NE)
            else:
                error("Unknown binary operation")
            code_gen(x.values[i])
            emit_byte(JUMP)
            h2 = hole()
            emit_word_at(h1, len(code) - h1)
            code_gen(x.values[i+1])
            emit_word_at(h2, len(code) - h2)
    elif type(x) == ast.BinOp:
        code_gen(x.left)
        code_gen(x.right)
        emit_byte(operators[type(x.op)])
#***
        
opcode = []
def list_code():
    global opcode
    global var_offset
    membloat = [LOAD,STORE,PUSH,CALLSUB,JUMP,JIN,DC1,DC2,CALLNAT]
    tpcbloat = [JIN,DC2, PUSH]
    memdict = {}
    pc = 0
    tpc = 0
    while pc < len(code):
        memdict[pc] = tpc
        op = code[pc]
        pc += 1
        tpc +=1
        if(op in membloat):
            pc += word_size 
        if op in tpcbloat:
            tpc +=1

    #print(memdict)    
    print("Datasize: %d" % (len(globals)))
 
    pc = 0
    tpc = 0
    while pc < len(code):
        #print("%4d " % (pc), end='')
        print("%4d " % (tpc), end='')
        op = code[pc]
        pc += 1
        tpc += 1
        if op == LOAD:                                #DONT FORGET _userdata+x
            if pc in thymio_var_calls._dict:          #PLEASE REFACTOR _DICT
                x = thymio_var_calls.eject_call(pc)
            else:
                x = bytes_to_int(code[pc:pc+word_size])[0] + var_offset
            print("load "+str(x));
            opcode.append("load " + str(x))
            pc += word_size
        elif op == STORE:                             #DONT FORGET _userdata+x
            if pc in thymio_var_calls._dict:          #PLEASE REFACTOR _DICT
                x = thymio_var_calls.eject_call(pc)
            else:
                x = bytes_to_int(code[pc:pc+word_size])[0] + var_offset
            print("store "+str(x));
            opcode.append("store " + str(x)) 
            pc += word_size
        elif op == PUSH:
            x = bytes_to_int(code[pc:pc+word_size])[0]
            print("push %d" % (x));
            opcode.append("push " + str(x))
            pc += word_size
            tpc += 1
        elif op == CALLSUB:
            if pc in thymio_nf_calls._dict:
                x = thymio_nf_calls.eject_call(pc)
                print("callsub "+str(x))
                opcode.append("callnat " + str(x))
            else:
                x = bytes_to_int(code[pc:pc+word_size])[0]
                print("callsub %d" %(memdict[pc+x]))
                opcode.append("callsub " + str(memdict[pc+x]))
            pc += word_size
            
        elif op == CALLNAT:
            x = thymio_nf_calls.eject_call(pc)
            print("callnat "+str(x))
            opcode.append("callnat " + str(x))
            pc += word_size
        elif op == ADD:     
            print("add")
            opcode.append("add")
        elif op == SUB:     
            print("sub")
            opcode.append("sub")
        elif op == MULT:    
            print("mult")
            opcode.append("mult")
        elif op == DIV:     
            print("div")
            opcode.append("div")
        elif op == MOD:     
            print("mod")
            opcode.append("mod")
        elif op == LT:      
            print("lt")
            opcode.append("lt")
        elif op == GT:      
            print("gt")
            opcode.append("gt")
        elif op == LE:      
            print("le")
            opcode.append("le")            
        elif op == GE:      
            print("ge")
            opcode.append("ge")            
        elif op == EQ:      
            print("eq")
            opcode.append("eq")            
        elif op == NE:      
            print("ne")
            opcode.append("ne")            
        elif op == AND:     
            print("and")
            opcode.append("and")            
        elif op == OR:      
            print("or")
            opcode.append("or")            
        elif op == NEG:     
            print("neg")
            opcode.append("neg")            
        elif op == NOT:     
            print("not")
            opcode.append("not")            
        elif op == JUMP:
            x = bytes_to_int(code[pc:pc+word_size])[0]
            #print("jump    (%d) %d" % (x, pc + x));
            print("jump %d" % (memdict[pc+x]));
            #print("\n %d %d %d \n" %(pc,vpc,x))
            opcode.append("jump "+str(memdict[pc+x]))
            pc += word_size
        elif op == JIN:
            x = bytes_to_int(code[pc:pc+word_size])[0]
            cond_op = comp_ops[jump_cond.eject_call(pc)]
            print("jump if not "+cond_op+" %d" %(memdict[pc+x]));
            #print("\n %d %d %d \n" %(pc,vpc,x))
            opcode.append("jump.if.not "+cond_op+' '+str(memdict[pc+x]))
            pc += word_size
            tpc += 1
        elif op == STOP:  
            print("stop")
            opcode.append("stop")            
        elif op == RET:   
            print("ret")
            opcode.append("ret")  
        elif op == DC1:
            x = bytes_to_int(code[pc:pc+word_size])[0]
            x = int((x/5-1)*2+1)
            print("dc %d"%(x))#,memdict[pc+x])
            opcode.append("dc "+str(x))
            pc += word_size
        elif op == DC2:
            x = bytes_to_int(code[pc:pc+word_size])[0]
            event_id = event_dict[event_calls.eject_call(x)]
            print("dc "+event_id+", %d"%(memdict[pc+x]))
            opcode.append("dc "+event_id+", %d"%(memdict[pc+x]))
            pc += word_size
            tpc += 1
        else: 
            error("list_code: Unknown opcode %d", (op));
    for bc in opcode:
        print(bc)
 
#*** main driver
#input_file = sys.stdin
#if len(sys.argv) > 1:
from pathlib import Path
p = Path(__file__).with_name('arithmetic_test.py')
test_file = p.absolute()

try:
                    #(sys.argv[1], "r", 4096)
    input_file = open(test_file, "r")
except IOError as e:
                        #sys.argv[1]
    error("Can't open %s" % input_file)

tree_arithmetic = ast.parse(input_file.read())
code_gen(tree_arithmetic)
code_finish()
list_code()