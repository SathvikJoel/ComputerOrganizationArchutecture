import math
import random

class Cache:
    def __init__(self, associativity, replacement_policy, cache_size, block_size):
        self.num_blocks = cache_size // block_size

        self.enum_blocks = math.log2(self.num_blocks)
        self.eblock_size = math.log2(block_size)

        self.metrics = cache_metric(associativity, replacement_policy)
        self.bbox = bbox(self, associativity)
        self.replacer = replacer(self, replacement_policy)
            

    def access(self, string):
        addr = self.hex_2_bin(string)
        access_type = addr[0]
        addr = addr[1:]

        self.bbox(addr, access_type)

    @staticmethod
    def hex_2_bin(string):
        return (bin(int(string, 16))[2:]).zfill(32)

class cache_metric:
    pass


class bbox:
    def __init__(self, cache, associativity):
        self.associativity = associativity
        
        self.cache = cache
        if( self.associativity == 1):
            self.blocks = [cache_block('0') for i in cache.num_blocks]
            self.tagbits = 31 - self.cache.enum_blocks - self.cache.eblock_size

        else:
            self.ways = self.cache.num_blocks if self.associativity == 0 else self.associativity
            self.num_sets = self.cache.num_blocks // self.ways
            self.enum_sets = math.log2(nums_sets)
            self.sets = [cache_set(self.ways) for i in range(0, self.num_sets)]
            self.tagbits = 31 - self.enum_sets - self.cache.eblock_size
        
    def __call__(self, addr, access_type):
        if( self.associativity == 1):
            # Directly mapped is completely dealt here, replacer is not used
            #check if the line has appropriate tag
            line = self.blocks[self.block_num(addr)]
            
            if( line.tag == self.tag(addr)):
                pass
                #update?

            if( line.tag != self.tag(addr)):
                #update?
                line.tag = self.tag(addr)
                line.dirty_bit = True if access_type == 1 else False
                line.valid_bit = True
        
        if( self.associativity != 1):
            #go to the set
            head = self.sets[self.set_num(addr)]
            self.cache.replacer(addr, access_type, self.tag(addr), self.set_num(addr), head)         


    def block_num(self, addr):
        return int(addr[self.tagbits:self.tagbits + self.cache.enum_blocks],2)
    
    def tag(self, addr):
        return addr[0:self.tagbits]
    
    def set_num(self, addr):
        if( self.enum_sets == 0): return 1
        return int(addr[self.tagbits:self.tagbits + self.enum_sets], 2)


    
class replacer:
    def __init__(self, cache, replacement_policy):
        self.cache = cache
        self.policy = replacement_policy
        if( self.policy == 0):
            pass
        elif( self.policy == 1):
            pass
        else:
            # Pseudo LRU
            #create a list of trees of appropriate size
            self.trees = []
        
    def __call__(self, addr, access_type, tag, set, head ):
            if( self.policy == 0):
                randomizer = random.randint(0, self.cache.bbox.ways)
                head = curr
                while( randomizer > 0):
                    curr = curr.next
                #update ?
                curr.tag = tag
                curr.valid_bit = True
                if( access_type == 1): curr.dirty_bit = True

            if( self.policy == 1):
                curr = head
                prev = None
                pprev = None 
                while( curr.valid_bit != False and curr != None ):
                    pprev = prev
                    prev = curr
                    curr = curr.next
                if( curr == None ):
                    #update? remove the last block in linked list 
                    prev.tag = tag
                    temp = head.next
                    head = prev
                    pprev.next = None
                    head.next = temp
                if( curr.valid_bit == False ):
                    #update
                    curr.tag = tag
                    if( access_type == 1): curr.dirty_bit = True
                    curr.valid_bit = True
            
            if( self.policy == 2):




class cache_block: 
  
    # Function to initialise the node object 
    def __init__(self, tag): 
        self.tag = tag  # Assign data 
        self.valid_bit = False
        self.dirty_bit = False
        self.next = None  # Initialize next as null 
  
  
# Linked List class contains a Node object 
class cache_set: 
  
    # Function to initialize head 
    def __init__(self, ways): 
        self.head = self.create(ways)


    def create_list(self, length):
        linked_list = cache_block('0')
        head =  linked_list
        for _ in  range(1, length):
            head.next = cache_block('0')
            head = head.next
        return head




        

