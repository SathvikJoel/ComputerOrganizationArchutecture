"""
Authors : 
1. K Sathvik Joel CS19B025
2. P Cherrith CS19B035
3. D Hakesh CS19B017

Note : Require Python 2.7 or more version to run.

"""


import math

############# metric-variables ################################

instructions = 0
arthmetic_instructions = 0
logical_instructions = 0
data_instructions = 0
control_instructions = 0
halt_instructions = 0

cpi = 0

stalls = 0
data_stalls = 0
control_stalls = 0

################ global variables #############################
#store 8 bit information as strings (256 entries)
lcache = [] 
dcache = []

RF = [0,] #16 entries,8-bit each

PC = 0
IR = 0

#############################################################
def InstructionFetch():

    #return nothing

def InstructionDecode():

    return opcode, R1, R2, R3, L1

def Execute(opcode, A, B):

    return ALUOutput, cond

def Memory(opcode, B):

    return data #in load instruction
    #return nothing if store

def WriteBack(R1, result):

    #return nothing

###############################################################
A = 0
B = 0

LMD = 0
ALUOutput = 0

cond = True

stall = False
num_stalls = 0

clockCycles = 1
while(clockCycles++):

    #Write back handling
    if(number == 1):



        number++

    #memory handling
    if(number == 2):

        if(stall):number --

    #execute handling
    if(number == 3):

        if(normal) number++
        else number--

    #decoding handing
    if(number == 4):

    #instruction fetching handling
    if(number == 5):
        //data hazard logic..
        if(data hazard):
            stall = True
            num_stalls = 3

#add r1, r2, r3
#add r4, r1, r8 : current

#############################################################
#Read from lcache.txt to lcache[]


#Read from dcache.txt to dcache[]


#Read from RF.txt to RF[]


#writing dcache back into dcache.txt


#writing metrics - variables to output.txt 



###################  END of file ##################################
