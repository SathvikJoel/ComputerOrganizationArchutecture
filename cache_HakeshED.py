"""
Authors : 
1. K Sathvik Joel CS19B025
2. Cherrith CS19B037
3. D Hakesh CS19B017

Input File Name : Memory Request are read from input.txt file.

"""


import math
import random

#########################################################################################
#cache Block 
class cache_block: 
    """
    A cache block class

    Attributes:
    -----------

    tag: tag in the block

    valid_bit: validity of the cache block, empty or containing a valid tag

    dirty_bit: If the data is written to the address in the block


    """
    def __init__(self, tag, valid_bit, dirty_bit, next): 
        self.tag = tag  # Assign data 
        self.valid_bit = valid_bit
        self.dirty_bit = dirty_bit
        self.next = next  

############################################################################################ 
# Linked List class contains a Node object 
#Represents Cache Set
class cache_set: 
    # Function to initialize head 
    def __init__(self, ways): 
        self.head = self.create_list(ways)


    def create_list(self, length):
        linked_list_head = cache_block("",0,0,None)
        tail =  linked_list_head
        #Linking
        for _ in  range(1, length):
            tail.next = cache_block("",0,0,None)
            tail = tail.next
        return linked_list_head
#############################################################################################        
#Performance Counters for the cache
class cache_metric:
    """
    A class to keep track of the cache_metrics

    Attributes
    ----------
    The Attributes that need to be measured

    Methods
    -------
    update(str)
        Increments the "str" metric by 1

    """
    def __init__(self,associativity , replacement_policy ):
        self.cache_access = 0
        self.read_access = 0
        self.write_access = 0
        self.cache_miss = 0
        self.compulsory_miss = 0
        self.capacity_miss = 0
        self.conflict_miss = 0
        self.read_miss = 0
        self.write_miss = 0
        self.dirty_evicted = 0

    def update(self, strings):
        if type(strings) == str:
            self.__dict__[strings] += 1
        else:
            for string in strings:
                self.__dict__[string] += 1

    def print_metrics(self):
        for k,v in self.__dict__.items():
            print( k ," = ", v)
################################################# Cache ####################################################
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
        #parameters associated with the cache
        self.num_blocks = cache_size // block_size

        self.enum_blocks = int(math.log2(self.num_blocks))
        self.eblock_size = int(math.log2(block_size))

        self.metrics = cache_metric(associativity, replacement_policy) 
        self.bbox = bbox(self, associativity) 
         
        self.replacer = replacer(self, replacement_policy)

    
    def access(self, string, access):

        addr = self.hex_2_bin(string)
        

        if(access == 'w'):access_type = 1
        else:access_type = 0
        
        self.metrics.update('cache_access')
        if( access_type == 0):
            self.metrics.update('read_access')
        if( access_type == 1):
            self.metrics.update('write_access')
        #core comparator
        self.bbox(addr, access_type)

    @staticmethod
    def hex_2_bin(string):
        return (bin(int(string, 16))[2:]).zfill(32)
    
    def out(self):
        return self.metrics.print_metrics()
###############################################################################################

class bbox:
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
        self.enum_sets = int(math.log2(self.num_sets))
        self.sets = [cache_set(self.ways) for i in range(self.num_sets)]
        self.tagbits = int((32 - self.enum_sets - self.cache.eblock_size))
        
    def __call__(self, addr, access_type):
        cache_set = self.sets[self.set_num(addr)]
        #checking whether Hit or miss ,if miss => what to replace
        self.cache.replacer(addr, access_type, self.tag(addr), cache_set, self.set_num(addr))         
    
    def tag(self, addr):
        return addr[0:(self.tagbits)]
    
    def set_num(self, addr):

        if( self.enum_sets == 0): return 0
        return int(addr[(self.tagbits):(self.tagbits) + (self.enum_sets)], 2)

##########################################################################################################
    
class replacer:
    """
    class for managing the address calling protocol in a set

    Attributes
    ----------
    policy:obj
        Object to deal with replacement policy
    
    Methods
    -------
    _call_(*args, **kwargs)
        Executes the address replacment protocol in a set designated by cache_core
    """
    def __init__(self, cache, replacement_policy):
        self.old_address = dict()
        self.cache = cache
        if( replacement_policy == 0):       self.policy = random_policy(self)
        elif( replacement_policy == 1):     self.policy = lru_policy(self)
        else:                               self.policy = pseudo_policy(self)
            
        
    def __call__(self, addr, access_type, tag,  cache_set ,set_num):


        hit_status = self.policy.tag_check(tag, cache_set, access_type,set_num)
            
        if( hit_status != 1 ):  
            cache_miss_update(self, access_type)
            
            if(addr not in self.old_address): 
                self.cache.metrics.update('compulsory_miss')
                self.old_address[addr] = 1
            else: capacity_conflict_update(self)

            hit_status = self.policy.empty_block(tag, cache_set, hit_status, access_type,set_num)
        
        # capacity miss
        if( hit_status == -1): 
            self.policy.evict(access_type, tag, cache_set , hit_status,set_num)
       
#########################################################################################################
class random_policy:
    '''
    A class to deal with random policy

    '''
    def __init__(self , replacer):
        self.cache = replacer.cache

    def tag_check(self, tag, cache_set, access_type,set_num):
        """
        Traverse through the set and check for the tag
        """
        curr = cache_set.head
        while( curr != None and curr.tag != tag):   curr = curr.next

        if( curr!= None and curr.tag == tag ):
            curr.dirty_bit = access_type
            return 1
        return -1

    def empty_block(self, tag, cache_set, hit_status, access_type,set_num):
        """
        Traverse through the set and replace it if there is a empty block in the set
        """
        curr = cache_set.head
        while( curr != None and curr.valid_bit != False):
            curr   = curr.next
        
        if( curr != None and curr.valid_bit == False ):
            curr.tag = tag
            curr.valid_bit = 1
            curr.dirty_bit = access_type
            
            return 0
        return hit_status

    def evict(self, access_type, tag, cache_set , hit_status,set_num):
        """
        Select a random block and evict the block
        """
        randomizer = random.randint(0, self.cache.bbox.ways-1)
        
        curr = cache_set.head
        randomizer = randomizer - 1
        while( randomizer >= 0):
            curr = curr.next
            randomizer = randomizer -1
        if( curr.dirty_bit == True): self.cache.metrics.update('dirty_evicted')

        curr.tag = tag
        curr.valid_bit = 1
        curr.dirty_bit = access_type

#####################################################################################################
#Pseudo LRU Policy 
class lru_policy:
    def __init__(self, replacer):
        self.cache = replacer.cache

    #Checking Tag in cache
    def tag_check(self,tag, cache_set, access_type ,set_num):
        #Head of current set 
        curr = cache_set.head
        #Invalid case
        if(curr == None):print("Error : No Data !") ; exit(0)

        #If required Block present already as head of set
        if(curr.tag == tag): return 1

        #Iterating over set to find corresponding tag block
        #if found , we move that block to head.
        while(curr.next != None):
            if(curr.next.tag == tag):
                newHead = curr.next
                curr.next = newHead.next

                #moving hit block to head of set
                newHead.next = cache_set.head
                cache_set.head = newHead
                return 1
            curr = curr.next

        #if not found    
        return -1

    def empty_block(self,tag, cache_set, hit_status, access_type,set_num):
        curr = cache_set.head

        #invalid case
        if(curr == None):print("Error : no data "); exit(0)

        #if invalid block is at start itself
        if(curr.valid_bit == 0):
            curr.tag = tag
            curr.valid_bit = 1
            curr.dirty_bit = access_type
            return 0

        #iterating for invalid block
        #if found , we keep current block into that first invalid block in set
        #and we move it to head of set
        while(curr.next != None):
            if(curr.next.valid_bit == 0):
                newHead = curr.next
                curr.next = newHead.next

                #moving first invalid block to head
                newHead.next = cache_set.head
                cache_set.head = newHead

                #keeping current block to first invalid block(the head)
                cache_set.head.tag = tag
                cache_set.head.valid_bit = 1
                cache_set.head.dirty_bit = access_type

                return 0

            curr = curr.next

        #If no invalid block present
        return -1

    def evict(self,access_type, tag, cache_set , hit_status,set_num):
        curr = cache_set.head

        #Invalid case
        if(curr == None):print("data not there");exit(0)

        #if only one block in cache.
        if(curr.next == None):
            if(curr.dirty_bit == 1):
                self.cache.metrics.update('dirty_evicted')

            curr.tag = tag
            curr.valid_bit = 1
            curr.dirty_bit = access_type
            return

        #We need to go to tail of set for eviction .. the least recently accessed block will be there.
        while(curr.next.next != None): curr = curr.next

        #note : tail address is curr.next 
        #if tail is dirty block, update it in metrics.
        if(curr.next.dirty_bit == 1):
            self.cache.metrics.update('dirty_evicted')

        #Moving evictable block to head 
        #and keeping it to head.
        newHead = curr.next
        curr.next = None

        newHead.next = cache_set.head
        cache_set.head = newHead

        newHead.tag = tag
        newHead.valid_bit = 1
        newHead.dirty_bit = access_type



#############################################################################################################
#Class that deals with pseudo lru policy
class pseudo_policy:
    """
    Class to deal with the pseudo_lru policy
    """
    def __init__(self, replacer):
        #Assigning cache 
        self.cache = replacer.cache
        self.tree = Pseudo_LRU(replacer, self.cache)
        
    #Checking the tag in cache.
    #If present we update Pseudo LRU tree
    def tag_check(self, tag, cache_set, access_type,set_num):
        """
        Check if the tag is present
        """
        curr = cache_set.head
        while( curr != None ):
            if( curr.tag == tag ):
                curr.dirty_bit = access_type
                self.tree.update_tree( tag, 1, set_num )
                return 1
            
            curr = curr.next
        return -1

    def empty_block(self, tag, cache_set, hit_status, access_type,set_num):
        """
        Check for the empty block, if it is presnt replace it
        """
        curr = cache_set.head
        while(curr != None ):
            if( curr.valid_bit == 0):
                curr.tag = tag
                curr.valid_bit = 1
                curr.dirty_bit = access_type
                
                self.tree.update_tree( tag, 0, set_num )

                return 0
            curr = curr.next
        return hit_status

    def evict(self,access_type, tag, cache_set , hit_status, set_num):
        """
        Update the tree

        Evict from cache if it is required
        """
        evit_tag = self.tree.update_tree( tag, hit_status, set_num )
        self.evict_tag_from_cache( evit_tag, tag,access_type, cache_set, hit_status)

    def evict_tag_from_cache(self,evit_tag, tag,access_type, cache_set, hit_status):
        curr = cache_set.head
        
        while( curr!= None and curr.tag != evit_tag): curr = curr.next

        if( curr.dirty_bit == True): self.cache.metrics.update('dirty_evicted')
        curr.tag = tag
        curr.valid_bit = 1
        curr.dirty_bit = access_type

#####################################################################################################
 #Pseudo LRU Implementation
class Pseudo_LRU:
    def __init__(self, replacer, cache):
        self.ways = cache.bbox.ways
        (rows, cols) = ( cache.bbox.num_sets, (2*cache.bbox.ways - 1) )

        #Declaring Tree for Pseudo LRU
        self.tree =  [[0 for i in range(cols)] for j in range(rows)]

        self.cache = cache
        self.bbox = cache.bbox

    def update_tree( self, tag, hit_status, set_num  ):
        #if memory request is Miss
        #We traverse Along root to leaf to find evictable block or invalid block. 
        if( hit_status != 1):
            pos= 0

            #travelling along tree from root to leaf 
            #And updating internal nodes (toggling)
            while( pos < self.ways -1 ):
                d = self.tree[set_num][pos]
                self.tree[set_num][pos] ^= 1
                pos = 2*pos + (d+1)

            #Evictable block
            ans = self.tree[set_num][pos]
            #Inserting new tag into tree
            self.tree[set_num][pos] = tag
            
            return ans
        
        #When memory request is Hit.
        #We traversal from leaf, where current tag presents, to root.
        #And toggle bit such a way that , it doesn't point to current sub-tree
        pos = 0

        #Searching for leaf that has current tag
        for i in range( self.ways - 1, 2*self.ways - 1):
            if( self.tree[set_num][i] == tag ):
                pos = i
                break

        #Crawling from leaf to root.
        while( pos != 0 ):
            d = (pos - 1)//2

            #logic to toggle internal nodes for not pointing to same current-sub tree.
            self.tree[set_num][d] ^= ((pos %2) ^ self.tree[set_num][d])

            pos = d


#######################################################################################################

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
    if( replacer.cache.bbox.associativity == 0): replacer.cache.metrics.update('capacity_misses')
    ##Even in non-fully associative caches , if it is capacity miss ,it wont count for conflict misses.
    else:replacer.cache.metrics.update('conflict_miss')


#################################  File Reading and printing Section.  ##################################################

#opening the input file to be read.
f = open( 'input.txt', 'r')
x = f.readlines()

#collecting cache related data.
cache_size, cache_linesize , dm_cache , replacement_policy = x[:4]
#Servicing Memory requests
cache = Cache(int(dm_cache.strip()),int(replacement_policy.strip()),int(cache_size.strip()),int(cache_linesize.strip()) )
for i in x[4:]:
    addr, access = i.split()
    cache.access(addr.strip(), access.strip())

###################################### Printing Section #############################################################    
#Printing cache related stuff
print("Cache Size : ", end = " ")
print(cache_size.strip())
print("Block Size : " , end = " ")
print(cache_linesize.strip())
print("Type of Cache : ",end = " ")

if(int(dm_cache.strip()) == 0):print("Fully Associative Cache")
elif(int(dm_cache.strip()) == 1):print("Direct - Mapped Cache")
else:
    print("Set Associative Cache ",end = " " )
    print(dm_cache.strip(),end = ' ')
    print("Way")

print("Replacement Policy : ",end = " ")
if(int(replacement_policy.strip()) == 0): print("Random Replacement Policy")
elif(int(replacement_policy.strip()) == 1): print("LRU Replacement Policy")
else:print("Pseudo LRU Replacement Policy" )

#finally printing metrics of class.
cache.out()

f.close()
######################################################################################################################
        
