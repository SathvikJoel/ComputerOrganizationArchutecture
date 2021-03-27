import math
import random

class Cache:
    """
    A class used to represent Cache


    Attributes
    ----------
    num_blocks : int
        Number of blocks in the cache
    eblock_num : int
        Number of bits required for block offset
    metrics : cache_metrics
        An object to keep track of metrics for cache
    cache_core:   cache_core
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

        #self.enum_blocks = math.log2(self.num_blocks) 
        self.eblock_size = math.log2(block_size)      

        self.metrics = cache_metric(associativity, replacement_policy) 
        self.cache_core = cache_core(self, associativity) 
        #if( associativity != 1 ) : self.replacer = replacer(self, replacement_policy)  
        self.replacer = replacer(self, replacement_policy)

    def access(self, string, access):
        """
        Parameters
        ----------
        string : str
            Hexadecimal Input string given by the user for request
        """
        addr = self.hex_2_bin(string)
        print(access)
        print(addr)
        print("-----")
        access_type = 1 if access == 'w' else 0
        self.metrics.update('cache_access')
        if( access_type == 0):
            self.metrics.update('read_access')
        if( access_type == 1):
            self.metrics.update('write_access')
        self.cache_core(addr, access_type)

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
    
    def out(self):
        return self.metrics.print_metrics()

class cache_metric:
    """
    A class to keep track of the cache_metrics

    Attributes
    ----------
    associativity: int 
        Associativity of the cache
    
    replacement_policy: int
        Replacement policy of the cache

    Methods
    -------
    update(str)
        Increments the "str" metric by 1

    """
    def __init__(self,associativity , replacement_policy ):
        self.associativity = associativity
        self.replacement_policy = replacement_policy

    def update(self, string):
            self.__dict__[string] = self.__dict__.get(string, 0) + 1

    def print_metrics(self):
        output =""
        for k,v in self.__dict__.items():
            output += ( str(k)  + " = " +  str(v) + "\n")
        return output

class cache_core:
    """
    A class for dealing with the sets and tags of an address

    Attributes
    ----------
    ways:int
        The number of ways in cache

    num_sets:int
        Number of sets in cache

    enum_sets:int
        log of number of sets
    
    sets:List
        List of cache_set objects each representing a set

    tag_bits:int
        Number of binary digits in tag 

    Methods
    -------
    block_num(addr)
        The block number corresponding to the address
    
    tag(addr)
        returns the tag bits in addr
    
    set_num(addr)
        returns the set_num of the addr
    


    """
    def __init__(self, cache, associativity):
        self.associativity = associativity
        self.cache = cache

        self.ways = self.cache.num_blocks if self.associativity == 0 else self.associativity
        self.num_sets = self.cache.num_blocks // self.ways
        self.enum_sets = math.log2(self.num_sets)
        self.sets = [cache_set(self.ways) for i in range(0, self.num_sets)]
        self.tagbits = (int)(32 - self.enum_sets - self.cache.eblock_size)
        
    def __call__(self, addr, access_type):
       
        cache_set = self.sets[self.set_num(addr)]
        self.cache.replacer(addr, access_type, self.tag(addr), self.set_num(addr), cache_set)         


    def block_num(self, addr):
        return int(addr[int(self.tagbits):int(self.tagbits) + int(math.log2(self.cache.num_blocks))],2)
    
    def tag(self, addr):
        return addr[0:int(self.tagbits)]
    
    def set_num(self, addr):
        if( self.enum_sets == 0): return 0
        return int(addr[int(self.tagbits):int(self.tagbits) + int(self.enum_sets)], 2)


    
class replacer:
    """
    class for managing the address calling protocol in a set

    Attributes
    ----------
    policy:obj
        Object to deal with replacement policy
    
    Methods
    -------
    __call__(*args, **kwargs)
        Executes the address replacment protocol in a set designated by cache_core
    """
    def __init__(self, cache, replacement_policy):
        self.cache = cache
      
        if( replacement_policy == 0):       self.policy = random_policy(self)
        elif( replacement_policy == 1):     self.policy = lru_policy(self)
        else:                               self.policy = pseudo_policy(self)
            
        
    def __call__(self, addr, access_type, tag, set_num, cache_set ):
           
        # check if the tag is present in the cache
        hit_status = self.policy.tag_check(tag, cache_set, access_type)
            
        # update if the tag is not presnt in the set
        if( hit_status != 1 ):  cache_miss_update(self, access_type)

        # Check and replace if there is a empty block in the set
        hit_status = self.policy.empty_block(tag, cache_set, hit_status, access_type)
        
        # If the set is full, evict a block and update nessary metrics
        if( hit_status == -1): 
            capacity_conflict_update(self)
            self.policy.evict(access_type, tag, cache_set, set_num , hit_status)

     
  
class random_policy:
    '''
    A class to deal with random policy

    '''
    def __init__(self , replacer):
        self.cache = replacer.cache

    def tag_check(self, tag, cache_set, access_type):
        """
        Traverse through the set and check for the tag
        """
        curr = cache_set.head
        while( curr != None and curr.tag != tag):   curr = curr.next

        if( curr!= None and curr.tag == tag ):  
            curr(tag, True, access_type)
            return 1
        return -1

    def empty_block(self, tag, cache_set, access_type, hit_status):
        """
        Traverse through the set and replace it if there is a empty block in the set
        """
        curr = cache_set.head
        while( curr != None and curr.valid_bit != False):
            curr   = curr.next
        
        if( curr != None and curr.valid_bit == False ):
            curr(tag, True, access_type)
            self.cache.metrics.update('compulsory_miss')
            return 0
        return hit_status

    def evict(self, access_type, tag, cache_set, set_num , hit_status):
        """
        Select a random block and evict the block
        """
        randomizer = random.randint(0, self.cache.cache_core.ways)
        curr = cache_set.head
        randomizer = randomizer - 1
        while( randomizer >= 0):
            curr = curr.next
            randomizer = randomizer -1
        if( curr.dirty_bit == True): self.cache.metrics.update('dirty_evicted')

        curr(tag, True, access_type)

class lru_policy:
    """
    A class for LRU replacemnt policy
    """
    def __init__(self, replacer):
        self.cache = replacer.cache
    
    def tag_check(self,tag, cache_set, access_type ):
        """
        Traverse through the set and check for the tag

        If it is present bring it to the front of the linked list
        """
        curr = cache_set.head
        prev = None

        while( curr != None and curr.tag != tag):
            prev = curr
            curr = curr.next
        if( curr != None and curr.tag == tag):
            #print("{tag = ", tag, "} already prensent ")
            curr(tag, True, access_type)
            if( prev != None ): prev.next = curr.next
            temp = cache_set.head
            cache_set.head = curr
            if( prev != None ):cache_set.head.next = temp
            return  1

        return -1

    def empty_block(self,tag, cache_set, access_type, hit_status):
        """
        Traverse through the linked list to find a empty block

        If there is a empty block, keep the tag in that position and bring the node to the head of the linked list

        """
        curr = cache_set.head
        prev = None
        while( curr != None and curr.valid_bit != False):
            prev = curr
            curr = curr.next

        if( curr != None and curr.valid_bit == False ):
            #print("{tag = ", tag, "} invlaid found ")
            #update
            self.cache.metrics.update('compulsory_miss')
            curr(tag, True, access_type)
            # bring the block to the front
            if( prev != None ): prev.next = curr.next
            temp = cache_set.head
            cache_set.head = curr
            if( prev != None ):cache_set.head.next = temp
            return 0
        return hit_status

    def evict(self,access_type, tag, cache_set, set_num , hit_status):
        """
        Evict a block in the set

        The block to be evicted is the last block in the linked list

        Evict it and bring the new block to the head of the linked list

        """
        curr = cache_set.head
        prev = None
        pprev = None
        while( curr != None and curr.valid_bit != False):
            pprev = prev
            prev = curr
            curr = curr.next
        if( curr == None ):
            #print("{tag = ", tag, "} cache full, evicting {prev.tag" , prev.tag , "}")
            if( prev.dirty_bit == True): self.cache.metrics.update('dirty_evicted')
            capacity_conflict_update(self)
            #update? remove the last block in linked list

            prev.tag = tag
            prev(tag, True, access_type)
            temp = cache_set.head
            cache_set.head = prev
            if( pprev != None ): pprev.next = None
            cache_set.head.next = temp

class pseudo_policy:
    """
    Class to deal with the pseudo_lru policy
    """
    def __init__(self,replacer):
        self.cache = replacer.cache
        self.tree = Pseudo_LRU(replacer, self.cache)
        

    def tag_check(self, tag, cache_set, access_type):
        """
        Check if the tag is present
        """
        curr = cache_set.head
        while( curr != None ):
            if( curr.tag == tag ):
                curr.dirty_bit = access_type
                return 1
            
            curr = curr.next
        return -1

    def empty_block(self, tag, cache_set, hit_status, access_type):
        """
        Check for the empty block, if it is presnt replace it
        """
        curr = cache_set.head
        while(curr != None ):
            if( curr.valid_bit == False):
                self.cache.metrics.update('compulsory_miss')
                curr(tag, True, access_type)
                return 0
            curr = curr.next
        return hit_status

    def evict(self,access_type, tag, cache_set, set_num , hit_status ):
        
        evit_tag = self.tree.update_tree( tag, hit_status, set_num )
        self.evict_tag_from_cache( evit_tag, tag,access_type, cache_set, hit_status)

    def evict_tag_from_cache(self,evit_tag, tag,access_type, cache_set, hit_status):
        curr = cache_set.head
        if( hit_status == -1 ):
            while( curr!= None and curr.tag != evit_tag): curr = curr.next

            if( curr.dirty_bit == True): self.cache.metrics.update('dirty_evicted')

            curr(tag, True , access_type)


class cache_block: 
    """
    A cache block class

    Attributes:
    -----------

    tag: tag in the blocl

    valid_bit: validity of the cache block, empty or containing a valid tag

    dirty_bit: If the data is written to the address in the block

    Methods:
    --------

    __call__(*args, **kwargs)
        updates the block to a particuar tag

    """
  
    # Function to initialise the node object 
    def __init__(self, tag): 
        self.tag = tag  # Assign data 
        self.valid_bit = False
        self.dirty_bit = False
        self.next = None  # Initialize next as null 
    
    def __call__(self, tag, valid_bit , access_type):
        self.tag = tag
        self.valid_bit = True
        self.dirty_bit = access_type

  
class Pseudo_LRU:
    def __init__(self, replacer, cache):
        self.ways = cache.cache_core.ways
        (rows, cols) = ( cache.cache_core.num_sets, (2*cache.cache_core.ways - 1) )
        self.tree =  [[0 for i in range(cols)] for j in range(rows)]
        self.cache = cache
        self.cache_core = cache.cache_core

    def update_tree( self, tag, hit_status, set_num  ): 
        if( hit_status != 1):
            pos= 0
            while( pos < self.ways -1 ):
                d = self.tree[set_num][pos]
                self.tree[set_num][pos] ^= 1
                pos = 2*pos + (d+1)
            ans = self.tree[set_num][pos]
            self.tree[set_num][pos] = tag
            for i in range( 2*self.ways - 1):
                print(self.tree[set_num][i] , end = " -- ")
            print( " tree completed")
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
        
        for i in range( 2*self.ways - 1):
                print(self.tree[set_num][i] , end = " -- ")
        print( " tree completed")


# Linked List class contains a Node object 
class cache_set: 
    """
    A class for cache_set

    Attributes:
    ----------

    head : The head of the linked list of the set, since a set is represented as linked list
  
    Methods:
    -------

    create_list(length)
        Creates a linked list of specified length

    """
    # Function to initialize head   
    def __init__(self, ways): 
        self.head = self.create_list(ways)


    def create_list(self, length):
        linked_list = cache_block('0')
        head =  linked_list
        for _ in  range(1, length):
            head.next = cache_block('0')
            head = head.next
        return linked_list

def cache_miss_update(replacer, access_type):
    """
    update the metrics if there is a cache miss
    """
    replacer.cache.metrics.update('cache_miss')
    if( access_type == 0):
        replacer.cache.metrics.update('read_miss')
    else:
        replacer.cache.metrics.update('write_miss')

def capacity_conflict_update(replacer):
    """
    update the metrics if there is a conflict or capacity miss
    """
    if( replacer.cache.cache_core.associativity == 0): replacer.cache.metrics.update('capacity_misses')
    replacer.cache.metrics.update('conflict_miss')



# main

f = open( '/home/joel/Dropbox/Sem4/CS2610/ComputerOrganizationArchutecture/TestCase/sathvik/test_case_1/input.txt', 'r')

x = f.readlines()
cache_size, cache_linesize , dm_cache , replacement_policy = x[:4]
cache = Cache(int(dm_cache.strip()),int(replacement_policy.strip()),int(cache_size.strip()),int(cache_linesize.strip()) )
#print(cache_size.strip(), '----',cache_linesize.strip(), '----', dm_cache.strip())
for i in x[4:]:
    addr, access = i.split()
    cache.access(addr.strip(), access.strip())
    #print(addr, '----', access)

print(cache.out())

f.close()
'''
Updates:
-------

Directmapped cache : KO ( passed test ) -- Ex1
Test parameters for fully associative -- Ex3
tested LRU for set associative --Ex4 ( cherrith I will kil you!!, u easted my time)

TODO:
----

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


Ex 3:
cache(0,0,2**16, 2**3)
cache.access('0000555F')


Ex 4:
cache = Cache(4,1, 2**16, 2**3)
cache.access('0000555F')
cache.access('0000955F')
cache.access('0000D55F')
cache.access('0001D55F')
cache.access('0A00555F')
cache.access('0001D55F')
cache.access('0A00555F')
cache.access('0B00555F')
cache.access('0C00555F')

'''