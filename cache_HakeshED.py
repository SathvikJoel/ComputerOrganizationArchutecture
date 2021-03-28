import math
import random

#########################################################################################
#cache Block 
class cache_block: 
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
    #initialzing the class
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
    def __init__(self , replacer):
        self.cache = replacer.cache

    def tag_check(self, tag, cache_set, access_type,set_num):
        curr = cache_set.head
        while( curr != None and curr.tag != tag):   curr = curr.next

        if( curr!= None and curr.tag == tag ):
            curr.dirty_bit = access_type
            return 1
        return -1

    def empty_block(self, tag, cache_set, hit_status, access_type,set_num):
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
class lru_policy:
    def __init__(self, replacer):
        self.cache = replacer.cache
    
    def tag_check(self,tag, cache_set, access_type ,set_num):
        curr = cache_set.head
        if(curr == None):print("NO Data !") ; exit(0)

        if(curr.tag == tag):return 1

        while(curr.next != None):
            if(curr.next.tag == tag):
                newHead = curr.next
                curr.next = newHead.next
                newHead.next = cache_set.head
                cache_set.head = newHead
                return 1
            curr = curr.next
        return -1

    def empty_block(self,tag, cache_set, hit_status, access_type,set_num):
        curr = cache_set.head
        if(curr == None):print("no data "); exit(0)

        if(curr.valid_bit == 0):
            curr.tag = tag
            curr.valid_bit = 1
            curr.dirty_bit = access_type
            return 0

        while(curr.next != None):
            if(curr.next.valid_bit == 0):
                newHead = curr.next
                curr.next = newHead.next
                newHead.next = cache_set.head
                cache_set.head = newHead

                cache_set.head.tag = tag
                cache_set.head.valid_bit = 1
                cache_set.head.dirty_bit = access_type

                return 0

            curr = curr.next
        return -1

    def evict(self,access_type, tag, cache_set , hit_status,set_num):
        curr = cache_set.head
        if(curr == None):print("data not there");exit(0)
        if(curr.next == None):
            if(curr.dirty_bit == 1):
                self.cache.metrics.update('dirty_evicted')

            curr.tag = tag
            curr.valid_bit = 1
            curr.dirty_bit = access_type

        while(curr.next.next != None):curr = curr.next

        if(curr.next.dirty_bit == 1):
            self.cache.metrics.update('dirty_evicted')

        newHead = curr.next
        curr.next = None
        newHead.next = cache_set.head
        cache_set.head = newHead
        newHead.tag = tag
        newHead.valid_bit = 1
        newHead.dirty_bit = access_type



#############################################################################################################
class pseudo_policy:
    def __init__(self,replacer):
        self.cache = replacer.cache
        self.tree = Pseudo_LRU(replacer, self.cache)
        

    def tag_check(self, tag, cache_set, access_type,set_num):
        curr = cache_set.head
        while( curr != None ):
            if( curr.tag == tag ):
                curr.dirty_bit = access_type
                self.tree.update_tree( tag, 1, set_num )
                return 1
            
            curr = curr.next
        return -1

    def empty_block(self, tag, cache_set, hit_status, access_type,set_num):
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
 
class Pseudo_LRU:
    def __init__(self, replacer, cache):
        self.ways = cache.bbox.ways
        (rows, cols) = ( cache.bbox.num_sets, (2*cache.bbox.ways - 1) )
        self.tree =  [[0 for i in range(cols)] for j in range(rows)]
        self.cache = cache
        self.bbox = cache.bbox

    def update_tree( self, tag, hit_status, set_num  ): 
        if( hit_status != 1):
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


#######################################################################################################

def cache_miss_update(replacer, access_type):
    replacer.cache.metrics.update('cache_miss')
    if( access_type == 0):
        replacer.cache.metrics.update('read_miss')
    else:
        replacer.cache.metrics.update('write_miss')

def capacity_conflict_update(replacer):
    if( replacer.cache.bbox.associativity == 0): replacer.cache.metrics.update('capacity_misses')
    ##Even in non-fully associative caches , if it is capacity miss ,it wont count for conflict misses.
    else:replacer.cache.metrics.update('conflict_miss')


#################################  File Reading and printing Section.  ##################################################


f = open( 'input.txt', 'r')
x = f.readlines()
cache_size, cache_linesize , dm_cache , replacement_policy = x[:4]

print("Cache Size : ", end = " ")
print(cache_size.strip())
print("Block Size : " , end = " ")
print(cache_linesize.strip())
print("Type of Cache : ",end = " ")
if(dm_cache == 0):print("Fully Associative Cache")
elif(dm_cache == 1):print("Direct - Mapped Cache")
else:
    print("Set Associative Cache ",end = " " )
    print(dm_cache.strip(),end = ' ')
    print("Way")
print("Replacement Policy : ",end = " ")
if(replacement_policy == 0):print("Random Replacement Policy")
elif(replacement_policy == 1):print("LRU Replacement Policy")
else:print("Pseudo LRU Replacement Policy" )

cache = Cache(int(dm_cache.strip()),int(replacement_policy.strip()),int(cache_size.strip()),int(cache_linesize.strip()) )
for i in x[4:]:
    addr, access = i.split()
    cache.access(addr.strip(), access.strip())

print(cache.out())

f.close()
######################################################################################################################
        
