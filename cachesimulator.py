#File: cachesimulator.py
#Author: Joseph Quismorio
#Date: 12/07/2021
#Section: 504
#Email: jfquismorio@tamu.edu
#Description: A command-line based cache simulator written in Python. The simulator uses two data structures: a configurable cache memory and a physical memory (RAM). The address width is 8 bits.

import sys
import random 
import math
## Globals
## The memory variable holds all the RAM addresses in an indexed list. 
# Used for accessing addresses at a specific index and exporting to ram.txt.
memory = []
## The memory_list variable holds all the RAM addresses in block form according to user input. 
# Its only significant implementation is to be exported to the memory dictionary.
memory_list = []
## The memory_dict variable is a dictionary that holds all the blocks, tagged by their corresponding address in hexadecimal.
memory_dict = {}
## The cache_list variable holds all the cache data. 
# Modifiable as a global variable.
cache_list = []
## cache_hits and cache_misses track... the cache hits and cache misses.
cache_hits = 0
cache_misses = 0

valid_sum = 0

previous_address = ""

## mem_menu reads in the given input file and initializes memory list to hold all hex addresses.
def mem_menu():
  global memory
  global memory_list
  filename = sys.argv[1]
  
  ## Reads in file data and store in 'memory'.
  with open(filename, 'r') as f:
    for line in f:
      memory.append(line.replace('\n', ''))
  memory_list = [memory[i:i+8] for i in range(0,len(memory),8)]
  
  ## Stores corresponding addresses and block data in a dictionary.
  print("*** Welcome to the cache simulator ***")
  print("initialize the RAM:")
  print("init-ram 0x00 " + "0x{:02X}".format(len(memory) - 1))
  print("RAM successfully initialized!")

## cache_set creates a cold cache given user inputs. 
# Inputs include size of cache, size of each block, associativity, the replacement policy, write hit policy, and write miss policy. 
# Values for number of sets, number of memory addresses, and numbers for tag, set index and block offset bits are calculated using the inputs.
def cache_set():
  global cache_size #C
  global block_size #B
  global associativity #E 
  global rep_policy
  global rep_policy_dict
  global write_hit
  global write_hit_dict
  global write_miss
  global write_miss_dict
  global cache_list
  global S
  global address_bits
  global offset_bits
  global index_bits
  global tag_bits
  global invalid_fill
  global LRU

  memory_addresses = len(memory)

  associativity_choices = [1, 2, 4]
  binary_sys = [1, 2]

  ## User inputs go here. 
  # I/O stuff should be good.
  print("configure the cache: ")
  while True:
    cache_size = input("cache size: ")
    try:
      if (not int(cache_size) >= 8 or not int(cache_size) <= 256):
        continue
      else:
        cache_size = int(cache_size)
        break
    except ValueError:
      continue

  while True:
    block_size = input("data block size: ")
    try:
      if not block_size:
        continue
      else:
        block_size = int(block_size)
        break
    except ValueError:
      continue

  while True:
    associativity = input("associativity: ")
    try:
      if (int(associativity) not in associativity_choices):
        continue
      else:
        associativity = int(associativity)
        break
    except ValueError:
      continue

  while True:
    rep_policy = input("replacement policy: ")
    try:
      if int(rep_policy) not in binary_sys:
        continue
      else:
        rep_policy = int(rep_policy)
        break
    except ValueError:
      continue

  rep_policy_dict = {1 : "random_replacement", 2: "least_recently_used"}

  while True:
    write_hit = input("write hit policy: ")
    try:
      if int(write_hit) not in binary_sys:
        continue
      else:
        write_hit = int(write_hit)
        break
    except ValueError:
      continue

  write_hit_dict = {1 : "write_through", 2 : "write_back"}

  while True:
    write_miss = input("write miss policy: ")
    try:
      if int(write_miss) not in binary_sys:
        continue
      else:
        write_miss = int(write_miss)
        break
    except ValueError:
      continue

  write_miss_dict = {1 : "write_allocate", 2 : "no_write_allocate"}

  S = int(cache_size/block_size/associativity)
  address_bits = int(math.log(memory_addresses, 2))   
  offset_bits = int(math.log(block_size, 2))  
  index_bits = int(math.log(S, 2))
  tag_bits = address_bits - (offset_bits + index_bits)

  invalid_fill = [i for i in range(associativity)]
  LRU = [i for i in range(associativity)]

  for s in range(S):
    sub_list = []
    for j in range(associativity):
      sub_list.append({'valid': 0, 'dirty': 0, 'tag': '00', 'block': ['00']*block_size})
    cache_list.append(sub_list)
    
  print("cache successfully configured!")

## cache_menu allows user to input commands that will modify and read the cache and memory.
def cache_menu():
  global curr_command
  print("*** Cache simulator menu ***")
  print("type one command:")
  print("1. cache-read")
  print("2. cache-write")
  print("3. cache-flush")
  print("4. cache-view")
  print("5. memory-view")
  print("6. cache-dump")
  print("7. memory-dump")
  print("8. quit")
  print("****************************")
  curr_command = str(input()).split(' ')
  if(curr_command[0] == 'cache-read'):
    cache_read()
  elif(curr_command[0] == 'cache-write'):
    cache_write()
  elif(curr_command[0] == 'cache-flush'):
    cache_flush()
  elif(curr_command[0] == 'cache-view'):
    cache_view()
  elif(curr_command[0] == 'memory-view'):
    memory_view()
  elif(curr_command[0] == 'cache-dump'):
    cache_dump()
  elif(curr_command[0] == 'memory-dump'):
    memory_dump()
  elif(curr_command[0] == 'quit'):
    pass
  else:
    cache_menu()

## cache_read reads in data from an address. 
# The user should type the read command followed by an 8-bit address in hexadecimal.
def cache_read():
  global cache_hits
  global cache_misses
  global cache_list
  global invalid_fill
  global LRU
  global valid_sum
  global previous_address
  global memory_list
  #if the length of the command line split is 1 return back to menu
  if len(curr_command) == 1:
    cache_menu()
  address = curr_command[1] #address was split, index at 1 should be the hex address
  address = bin(int(address, 16))[2:].zfill(8) #convert to binary
  address_location = int(int(address, 2)/block_size) #where the address should be located in the memory list
  ## Calculations
  tag_address = int(address[:tag_bits],2)
  # edge case: if number of sets is 1, the set address must be 0
  if(S > 1):
    set_address = int(address[tag_bits:(tag_bits + index_bits)], 2)
  else:
    set_address = 0
  #offset address
  offset_address = int(address[(tag_bits + index_bits):], 2)
  data = '00'
  ram_address = 'foo'
  eviction_line = '-1'
  print(f'set:{set_address}')
  print(f'tag:{"{:02X}".format(tag_address)}')
  hit_str = 'no'

  #initialize hit to false
  hit = False
  
  #check for hits
  for l in cache_list[set_address]:
    if l['tag'] == "{:02X}".format(tag_address):
      hit = True
    if l['valid'] == 0:
      hit = False
    if (hit):
      data = l['block'][offset_address]
      break
  #frankly I forgot why this is here. I'm a terrible coder
  if(data == 0):
    hit = False
  #initialize hit_str to 'no'
  hit_str = 'no'
  #now for hit stuff. if there's a hit, we'll return just the data, and increment the number of hits. the rest is hardcoded
  if(hit):
    hit_str = 'yes'
    cache_hits += 1
    eviction_line = '-1'
    ram_address = '-1'
  #otherwise, we get into the miss policies.
  else:
    if(rep_policy == 1): #random replacement
      vsum = 0 
      for l in cache_list[set_address]:
        vsum += l['valid'] #add all of the valid bits together
      valid_sum = vsum #so we don't have to reset every time
      if valid_sum < associativity: #if the number of valid bits is still under however many lines there are in the set, we fill in all the invalid spaces first before going to random replacement
        eviction_line = invalid_fill[0]
        invalid_fill = invalid_fill[1:] + invalid_fill[:1]
      else:  
        eviction_line = random.randint(0, (associativity - 1))
      #default setting all the output strings and manipulating the cache and whatnot
      if(cache_list[set_address][eviction_line]['dirty'] == 1 and cache_list[set_address][eviction_line]['tag'] != "{:02X}".format(tag_address)):
        for i in range(int(previous_address, 2), (int(previous_address, 2) + block_size)):
          memory[i] = cache_list[set_address][eviction_line]['block'][i - int(previous_address, 2)]
        cache_list[set_address][eviction_line]['dirty'] = 0
        memory_list.clear()
        memory_list = [memory[i:i+block_size] for i in range(0,len(memory),block_size)]
      data = memory[int(address, 2)] 
      ram_address = curr_command[1]
      cache_list[set_address][eviction_line]['valid'] = 1
      cache_list[set_address][eviction_line]['tag'] = "{:02X}".format(tag_address)
      cache_list[set_address][eviction_line]['block'] = memory_list[address_location]
      cache_misses += 1
    elif(rep_policy == 2):
      #basically what i was doing earlier with the filling invalid lines but over and over again.
      eviction_line = LRU[0]
      LRU = LRU[1:] + LRU[:1]
      if(cache_list[set_address][eviction_line]['dirty'] == 1 and cache_list[set_address][eviction_line]['tag'] != "{:02X}".format(tag_address)):
        for i in range(int(previous_address, 2), (int(previous_address, 2) + block_size)):
          memory[i] = cache_list[set_address][eviction_line]['block'][i - int(previous_address, 2)]
        cache_list[set_address][eviction_line]['dirty'] = 0
        memory_list.clear()
        memory_list = [memory[i:i+block_size] for i in range(0,len(memory),block_size)]
      data = memory[int(address, 2)]
      ram_address = curr_command[1]
      cache_list[set_address][eviction_line]['valid'] = 1
      cache_list[set_address][eviction_line]['tag'] = "{:02X}".format(tag_address)
      cache_list[set_address][eviction_line]['block'] = memory_list[address_location]
      cache_misses += 1


  print(f'hit:{hit_str}')
  print(f'eviction_line:{eviction_line}')
  print(f'ram_address:{ram_address}')
  print(f'data:0x{data}')

  cache_menu()

## cache_write writes data to an address in the cache. 
# The user should type the write command followed by an 8-bit address and a byte of data in hexadecimal. 
# In case of a tie following LRU or LFU replacement policies, evict one with the min line number.
def cache_write():
  global cache_hits
  global cache_misses
  global cache_list
  global memory_list
  global invalid_fill
  global LRU
  global valid_sum
  global previous_address
  #global memory

  #if the length of the command line split is less than 3 return back to menu
  if len(curr_command) < 3:
    cache_menu()
  #address to be overwritten
  address = curr_command[1]
  address = bin(int(address, 16))[2:].zfill(8)
  address_location = int(int(address, 2)/block_size) #where the address should be located in the memory list
  #data to write into the address
  data = curr_command[2] 
  data = bin(int(data, 16))[2:].zfill(8)
  #this is for the address - not the data. we just basically keep that
  tag_address = int(address[:tag_bits],2)
  if(S > 1):
    set_address = int(address[tag_bits:(tag_bits + index_bits)], 2)
  else:
    set_address = 0
  offset_address = int(address[(tag_bits + index_bits):], 2)
  grab_data = '00' 
  ram_address = 'foo'
  eviction_line = '-1'
  print(f'set:{set_address}')
  print(f'tag:{"{:02X}".format(tag_address)}')

  #initializers
  hit = False
  hit_str = 'no'
  dirty = 0
  
  #check for a hit
  for l in cache_list[set_address]:
    if l['tag'] == "{:02X}".format(tag_address):
      hit = True
    if l['valid'] == 0:
      hit = False
    if (hit):
      grab_data = l['block'][offset_address]
      break
  if(grab_data == 0):
    hit = False

  #if the hit exists:
  if(hit):
    ram_address = '-1'
    hit_str = 'yes'
    if(write_hit == 1): #write through
      memory[int(address, 2)] = curr_command[2][2:] #change the memory address so that it holds the specified data
      for l in cache_list[set_address]: #then write the new data into the existing block
        if l['tag'] == "{:02X}".format(tag_address) and l['valid'] == 1:
          l['block'][offset_address] = curr_command[2][2:]
    else: #write back
      for l in cache_list[set_address]: #only write the new data into the existing block, leave memory alone
        if l['tag'] == "{:02X}".format(tag_address) and l['valid'] == 1:
          l['block'][offset_address] = curr_command[2][2:]
          l['dirty'] = 1
          dirty = 1
          previous_address = address
  else: #in case of hit
    hit_str = 'no'
    ram_address = curr_command[1]
    eviction_line = int(int(curr_command[1], 16)/8)
    if(write_miss == 1): #write allocate
      #we have to write the block from RAM into cache
      if(rep_policy == 1): #random replacement
        vsum = 0
        for l in cache_list[set_address]:
          vsum += l['valid']
        valid_sum = vsum
        if valid_sum < associativity:
          eviction_line = invalid_fill[0]
          invalid_fill = invalid_fill[1:] + invalid_fill[:1]
        else:  
          eviction_line = random.randint(0, (associativity - 1))
        if(cache_list[set_address][eviction_line]['dirty'] == 1 and cache_list[set_address][eviction_line]['tag'] != "{:02X}".format(tag_address)):
          for i in range(int(previous_address, 2), (int(previous_address, 2) + block_size)):
            memory[i] = cache_list[set_address][eviction_line]['block'][i - int(previous_address, 2)]
          cache_list[set_address][eviction_line]['dirty'] = 0
          memory_list.clear()
          memory_list = [memory[i:i+block_size] for i in range(0,len(memory),block_size)]
        ram_address = curr_command[1]
        cache_list[set_address][eviction_line]['valid'] = 1
        cache_list[set_address][eviction_line]['tag'] = "{:02X}".format(tag_address)
        memory_list[address_location][offset_address] = curr_command[2][2:]
        cache_list[set_address][eviction_line]['block'] = memory_list[address_location]
        cache_misses += 1
      elif(rep_policy == 2): #least recently used
        eviction_line = int(LRU[0])
        LRU = LRU[1:] + LRU[:1]
        data = memory[int(address, 2)]
        ram_address = curr_command[1]
        if(cache_list[set_address][eviction_line]['dirty'] == 1 and cache_list[set_address][eviction_line]['tag'] != "{:02X}".format(tag_address)):
          for i in range(int(previous_address, 2), (int(previous_address, 2) + block_size)):
            memory[i] = cache_list[set_address][eviction_line]['block'][i - int(previous_address, 2)]
          cache_list[set_address][eviction_line]['dirty'] = 0
          memory_list.clear()
          memory_list = [memory[i:i+block_size] for i in range(0,len(memory),block_size)]
        cache_list[set_address][eviction_line]['valid'] = 1
        cache_list[set_address][eviction_line]['tag'] = "{:02X}".format(tag_address)
        memory_list[address_location][offset_address] = curr_command[2][2:]
        cache_list[set_address][eviction_line]['block'] = memory_list[address_location]
        cache_misses += 1
      memory[int(address, 2)] = curr_command[2][2:] #write into memory
    else: #no write allocate
      memory[int(address, 2)] = curr_command[2][2:] #only write into memory
  
  #reset the memory list and load in the amended memory
  memory_list.clear()
  memory_list = [memory[i:i+block_size] for i in range(0,len(memory),block_size)]
  
  print(f'hit:{hit_str}')
  print(f'eviction_line:{eviction_line}')
  print(f'ram_address:{ram_address}')
  print(f'data:0x{curr_command[2][2:]}')
  print(f'dirty_bit:{dirty}')

  cache_menu()

## cache_flush clears the cache, resetting it back to a cold cache.
def cache_flush():
  global memory_list
  global invalid_fill
  global LRU
  global cache_list
  global valid_sum

  for s in range(S):
    for e in range(associativity):
      cache_list[s][e]['valid'] = 0
      cache_list[s][e]['dirty'] = 0
      cache_list[s][e]['tag'] = '00'
      for b in range(block_size):
        cache_list[s][e]['block'][b] = '00'
  ## This function is doing something stupid where it resets the memory list corresponding to the address. 
  # I'm not sure what's causing it exactly, so this will serve as a rough fix. 
  # Not something I'm happy about, but it'll work for now.
  invalid_fill = [i for i in range(associativity)]
  LRU = [i for i in range(associativity)]
  valid_sum = 0
  memory_list = [memory[i:i+8] for i in range(0,len(memory),8)]
  print('cache_cleared')
  cache_menu()

## cache_view displays the cache content and status. 
# The view should print the cache configuration and the cache’s content.
def cache_view():
  print(f'cache_size:{cache_size}')
  print(f'data_block_size:{block_size}')
  print(f'associativity:{associativity}')
  print(f'replacement_policy:{rep_policy_dict[rep_policy]}')
  print(f'write_hit_policy:{write_hit_dict[write_hit]}')
  print(f'write_miss_policy:{write_miss_dict[write_miss]}')
  print(f'number_of_cache_hits:{cache_hits}')
  print(f'number_of_cache_misses:{cache_misses}')
  for s in range(S):
    for e in range(associativity):
      print(cache_list[s][e]['valid'], cache_list[s][e]['dirty'], cache_list[s][e]['tag'], end="")
      for b in range(block_size):
          print(" "+cache_list[s][e]["block"][b], end="")
      print()
  cache_menu()

## memory_view displays the RAM content and status.
def memory_view():
  global memory_list
  print(f'memory_size:{len(memory)}')
  print('memory_content:')
  print('address:data')
  line_address = 0
  ## Reads in file data and store in 'memory'.
  for i in memory_list:
    mem_str = " ".join(i)
    print(f'{"0x{:02X}".format(line_address)}:{mem_str}')
    line_address += block_size
  cache_menu()

## cache_dump dumps the current state of the cache in a file cache.txt. 
# The cache.txt file gets updated only when this command is called.
def cache_dump():
  with open('cache.txt', 'w') as file:
    for s in range(S):
      for e in range(associativity):
        for b in range(block_size):
          file.write(cache_list[s][e]['block'][b] + ' ')
        file.write('\n')
  file.close()
  cache_menu()

## memory_dump dumps the current content of the RAM in a file ram.txt. 
# The ram.txt file gets updated only when this command is called.
def memory_dump():
  with open('ram.txt', 'w') as file:
    for i in memory_list:
      for j in i:
        file.write(j + '\n')
  file.close()
  cache_menu()
      
def run():
  mem_menu()
  cache_set()
  cache_menu()

run()
