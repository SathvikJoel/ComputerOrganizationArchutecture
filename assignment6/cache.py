import math
import random

class Cache:
    """
    A class used to represent Cache


    Attributes
    ----------
    num_blocks : int
        Number of blocks in the cache
    enum_blocks : int
        Number of bits required to identify a block
    eblock_num : int
        Number of bits required for block offset
    metrics : cache_metrics
        An object to keep track of metrics for cache
    bbox:   bbox
        An object to handle the complexities of associativity
    replacer : replacer
        An object for handling replacement policies

    Methods
    -------
    access(str)
        Takes a hexadecimal string and process the request 
    
    hex_2_bin(str)
        Converts a hexadecimal string to binary
    """

    def __init__(self, associativity, replacement_policy, cache_size, block_size):
        self.num_blocks = cache_size // block_size

        self.enum_blocks = math.log2(self.num_blocks) 
        self.eblock_size = math.log2(block_size)      

        #self.metrics = cache_metric(associativity, replacement_policy) 
        self.bbox = bbox(self, associativity) 
        self.replacer = replacer(self, replacement_policy)  
            

    def access(self, string):
        """
        Parameters
        ----------
        string : str
            Hexadecimal Input string given by the user for request
        """
        addr = self.hex_2_bin(string)
        access_type = addr[0]
        addr = addr[1:]

        self.bbox(addr, access_type)

    @staticmethod
    def hex_2_bin(string):
        """
        Converts the hexadeciaml address into binary and parses it approporiately

        Parameters
        ----------
        string : str
            Hexadecimal string
            
        """
        return (bin(int(string, 16))[2:]).zfill(32)

class cache_metric:
    pass


class bbox:
    def __init__(self, cache, associativity):
        self.associativity = associativity
        self.cache = cache

        if( self.associativity == 1):
            self.blocks = [cache_block('0') for i in range(0, self.cache.num_blocks)]
            self.tagbits = 31 - self.cache.enum_blocks - self.cache.eblock_size

        else:
            self.ways = self.cache.num_blocks if self.associativity == 0 else self.associativity
            self.num_sets = self.cache.num_blocks // self.ways
            self.enum_sets = math.log2(self.num_sets)
            self.sets = [cache_set(self.ways) for i in range(0, self.num_sets)]
            self.tagbits = (int)(31 - self.enum_sets - self.cache.eblock_size)
        
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
            head = self.sets[self.set_num(addr)].head
            self.cache.replacer(addr, access_type, self.tag(addr), self.set_num(addr), head)         


    def block_num(self, addr):
        return int(addr[int(self.tagbits):int(self.tagbits) + int(self.cache.enum_blocks)],2)
    
    def tag(self, addr):
        return addr[0:int(self.tagbits)]
    
    def set_num(self, addr):
        if( self.enum_sets == 0): return 1
        return int(addr[int(self.tagbits):int(self.tagbits) + int(self.enum_sets)], 2)


    
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
            self.tree = Pseudo_LRU(self, cache)
            
        
    def __call__(self, addr, access_type, tag, set_num, head ):
            if( self.policy == 0):
                randomizer = random.randint(0, self.cache.bbox.ways)
                curr = head
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
                while( curr != None and curr.valid_bit != False):
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
                curr = head
                hit_status = -1
                while( curr != None ):
                    if( curr.tag == tag ):
                        hit_status = 1
                        curr.dirty_bit = 1 if access_type == 1 else 0
                        curr.valid_bit = True
                        break

                curr = head
                while(curr != None ):
                    if( curr.valid_bit == False):
                        hit_status = 0
                        curr.tag = tag
                        curr.dirty_bit = access_type
                        curr.valid_bit = True
                        break
                
                evit_tag = self.tree.update_tree( tag, hit_status, set_num )

                curr = head
                if( hit_status == -1 ):
                    while( curr.tag != evit_tag):
                        curr = curr.next
                
                    curr.tag = tag
                    curr.dirty_bit = access_type
                    curr.valid_bit = True

                 




class cache_block: 
  
    # Function to initialise the node object 
    def __init__(self, tag): 
        self.tag = tag  # Assign data 
        self.valid_bit = False
        self.dirty_bit = False
        self.next = None  # Initialize next as null 
  
  
class Pseudo_LRU:
    def __init__(self, replacer, cache):
        self.ways = cache.bbox.ways
        (rows, cols) = ( cache.bbox.num_sets, (2*cache.bbox.ways - 1) )
        self.tree =  [[0 for i in range(cols)] for j in range(rows)]
        self.cache = cache
        self.bbox = cache.bbox

    def update_tree( self, tag, hit_status, set_num  ): 
        if( hit_status == -1):
            pos= 0
            while( pos < self.ways -1 ):
                d = self.tree[set_num][pos]
                self.tree[set_num][pos] ^= 1
                pos = 2*pos + (d+1)
            ans = self.tree[set_num][pos]
            self.tree[set_num][pos] = tag
            return ans
        
        pos = 0
        for i in range( self.ways - 1, 2*self.ways - 1):
            if( self.tree[set_num][i] == tag ):
                pos = i
                break
        
        while( pos != 0 ):
            d = (pos - 1)//2
            self.tree[set_num][d] ^= ((pos %2) ^ self.tree[set_num][d])
            pos = d


# Linked List class contains a Node object 
class cache_set: 
  
    # Function to initialize head 
    def __init__(self, ways): 
        self.head = self.create_list(ways)


    def create_list(self, length):
        linked_list = cache_block('0')
        head =  linked_list
        for _ in  range(1, length):
            head.next = cache_block('0')
            head = head.next
        return head




        
cache = Cache(4,1, 2**16, 2**3)
cache.access('0000555F')

'''
Updates:
-------

Directmapped cache : KO ( passed test ) -- Ex1


TODO:
----

Test parameters for fully associative
Test LRU for set associative / fully associative
Test Pseudo LRU for set associative
'''

'''
Please write your examples here for me to test

Ex 1:
cache(1, 1, 2**16, 2**3)
cachce.access('7FFFFFFF')

sol:
Number of Read Accesses = 1
Number of Write Accesses = 0
Number of Cache Misses = 1
Number of Compulsory Misses = 1 
Number of Capacity Misses = N/A
Number of Conflict Misses = 0
Number of Read Misses = 1
Number of Write Misses = 0
Number of Dirty Blocks Evicted = 0

Ex 2:
cache(4, 1, 2**16, 2**3)
cachce.access('0000555F')
set number = 683( 01010101011 )
use this as a running example

'''