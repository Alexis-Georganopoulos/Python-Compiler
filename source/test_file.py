
# This script contains python source code used to test/debug the 
# resulting bytecode. Feel free to comment/uncomment certain blocks
# to test the capabilities of the compiler.

#################    BASIC ARITHMETIC AND ASSIGNMENT
a = 1
b = 2
c = ((a*b)/2+4)%2

d = [1,2,3]
d[2] = 5

# ##################    IF/ELSE/WHILE STATEMENTS
# a = 1

# if(a > 0):
#     d = 5
# else:
#     d = 6
    
# while d > 1:
#     d = d - 1
    
# ###################   FUNCTION CALLS AND NESTED FUNCTIONS(NO ARGUMENTS)
# def f():
#     a = 50
#     return a

# def g():
#     a = 5
#     def h():
#         a = 6
#         return a
#     a = h()
#     return a
        
# a =f()
# a = g()

# ###################   WHILE ONLY
# count = 1

# while count < 5:
#     count  = count + 1

# ###################   MEMORY ALLIGNMENT TESTER
# a = 1
# b = 2
# c = 3

# ###################   IF/ELSE ONLY
# if(5>1):
#     a=1
# else:
#     a=2
# def f():
#     pass

# ###################   DECORATOR TESTER
# @thymio.onevent(thymio.BUTTONS)
# def g():
#     a = 10

# a = 50


# ###################   THYMIO VARIABLE TESTER
# @thymio.onevent(thymio.BUTTONS)
# def f():
#   if(thymio.button.center > 0):
#       thymio.motor.left.target = 500
#       thymio.motor.right.target = 0    
        
# ###################   THYMIO NATIVE FUNCTIONS
# thymio.leds.top = [0, 0, 0]

# ###################   DICT STRUCTURE TESTING DO NOT COMPILE WITH BACK END
# class DictStructure:   
#     def __init__(self):
#         self.dict = {}#stores holes from calls/returns/etc...
#         self.flag = 0#usefull conditional flag
#     def store_hole(self,address,caller):
#         self.dict[address] = caller
#     def eject_holes(self,caller):#one call can come from many holes
#         hole_addresses = []
#         for address,call in self.dict.items():
#             if call == caller:
#                 hole_addresses.append(address)       
#         for address in hole_addresses:
#             self.dict.pop(address)
#         return hole_addresses
#     def eject_call(self,address):#but each hole has only one call
#         caller = self.dict[address] 
#         self.dict.pop(address)
#         return caller
      
# a = DictStructure()
# a.store_hole(1,2)
# a.store_hole(2,3)       
# a.store_hole(3,2)
# a.store_hole(4,2)
# b = a.eject_holes(2)  

# ###################   PYTHON SCOPE TESTING
# a = 10
# print(a)
# def f():
#     a =a
#     print(a)
  
# f()
# print(a)

# ###################   PROTOTYPED 1 COMPILABLE THYMIO CODE    
# eventCache = [0]
# todo = [0]

# cond0 = [False]

# reset outputs
# thymio.leds.top = [0, 0, 0]
# thymio.leds.bottom.left = [0, 0, 0]
# thymio.leds.bottom.right = [0, 0, 0]
# thymio.leds.circle = [0, 0, 0, 0, 0, 0, 0, 0]

# thymio.timer.period[1] = 50

# @thymio.onevent(thymio.BUTTONS)
# def onevent_buttons():
# 	cond = thymio.button.center
# 	if cond and not cond0[0]:
# 		eventCache[0] = True
# 	cond0[0] = cond

# @thymio.onevent(thymio.TIMER1)
# def onevent_timer1():
# 	if eventCache[0]:
# 		todo[0] = True
# 	if todo[0]:
# 		thymio.motor.left.target = 500
# 		thymio.motor.right.target = -500
# 	eventCache[0] = False
# 	todo[0] = False

# ###################   PROTOTYPED 2 COMPILABLE THYMIO CODE    

# eventCache = [0, 0]
# todo = [0, 0]

# cond0 = [False, False]

# reset outputs
# thymio.leds.top = [0, 0, 0]
# thymio.leds.bottom.left = [0, 0, 0]
# thymio.leds.bottom.right = [0, 0, 0]
# thymio.leds.circle = [0, 0, 0, 0, 0, 0, 0, 0]

# thymio.timer.period[1] = 50

# @thymio.onevent(thymio.PROX)
# def onevent_prox():
#     a = thymio.prox.horizontal[2] >= 2000
#     b = thymio.prox.horizontal[1] >= 2000
#     c = thymio.prox.horizontal[3] >= 2000
#     cond = a or b or c
#     if cond and not cond0[0]:
#     	eventCache[0] = True
#     cond0[0] = cond
#     d = thymio.prox.horizontal[5] >= 2000
#     e = thymio.prox.horizontal[6] >= 2000
#     cond = d or e
#     if cond and not cond0[1]:
#     	eventCache[1] = True
#     cond0[1] = cond

# @thymio.onevent(thymio.TIMER1)
# def onevent_timer1():
# 	if eventCache[0]:
# 		todo[0] = True
# 	if eventCache[1]:
# 		todo[1] = True
# 	if todo[0]:
# 		thymio.motor.left.target = -500
# 		thymio.motor.right.target = -500
# 	if todo[1]:
# 		thymio.motor.left.target = 500
# 		thymio.motor.right.target = 500
# 	eventCache[0] = False
# 	eventCache[1] = False
# 	todo[0] = False
# 	todo[1] = False
    
# ###################   BOOLEAN STATEMENTS
# a = True
# b = True
# c = False

# d = a and b or not c

# ###################   GLOBAL VARIABLES

# a = 5

# def f():
#     global a
#     a = 25
#     return a

# b = f()

# ###################   MESSY TESTING

# if (1>0):
#     thymio.motor.left.target = -500       
#     thymio.motor.right.target = -500
# a = -1

# b = not True
# test.var.int = 5
# a = 6
# b = 80

# a = thymio.prox.horizontal[2] >= 2000
# b = thymio.prox.horizontal[1] >= 2000
# c = thymio.prox.horizontal[3] >= 2000
# cond = a or b or c



# a = [10]
# print(a)
# def f():
#     a[0] = 1
#     print(a)
  
# f()
# print(a)

# a = [1,2,3]
# a[2] = 5

# for i in [1,2,3]:
#     a = 1
    
# def fact(n):
#     if(n == 1):
#         return 1
#     else:
#         return n*fact(n-1)
    
# def f(a):
#     return a + 1

# def f():
#     return [1,2,3]

# i = 0
# a = [1,2,3]
# a[2*i + 1] = 5


# a = [[1,2,3], [4,5,6], [7,8,9]]
# b = 2.75
        

