# cachesimulator
simple cache simulator made in python for [REDACTED] (one of my classes which i will omit for now to combat plagiarism)

# setup
you can clone the repository using the command:

```git clone https://github.com/josephquismorio/cachesimulator```

# purpose
this project simulates a cache (duh) by utilizing two data structures: a configurable cache memory and a physical memory, or RAM. 

the program takes in RAM data from an input file (input.txt) and allows for memory manipulation through the cache commands. a successful configuration of the RAM is shown by the display: 
```
*** Welcome to the cache simulator ***
initialize the RAM:
init-ram 0x00 0xFF
RAM successfully initialized!
```

you can configure the cache by entering the inputs given by the cache configuration menu, an example of which is given below:
```
configure the cache:
cache size: 32
data block size: 8
associativity: 2
replacement policy: 1
write hit policy: 1
write miss policy: 1
cache successfully configured!
```

- cache size can range from 8 to 256, and represents the aggregate size of all the cache blocks.
- data block size is the number of bytes that a block within the cache can hold. in the case of this project, a block size of 8 is suggested.
- associativity represents the number of lines within a set. the number of sets is calculated by dividing the cache size by the product of the block size and the associativity.
- replacement policy defines how to replace a cache entry following a cache miss. the user can only choose from random replacement (1) or the least recently used (2) policy.
- write hit policy defines where to write the data when an address is a hit. the user can only choose from a write-through or write-back policy, where write-through (1) will write the data in both the block in the cache and the block in RAM, and write-back (2) will write the data only in the block in the cache.
- write miss policy defines where to write the data when an address is a miss. the user can only choose from a write-allocate or no write-allocate policy, where write-allocate (1) will load the block from RAM and write it in the cache, and no write-allocate (2) will write the block in RAM and do not load it in the cache.

# usage
the cache menu dropdown appears thusly:
```
*** Cache simulator menu ***
type one command:
1. cache-read
2. cache-write
3. cache-flush
4. cache-view
5. memory-view
6. cache-dump
7. memory-dump
8. quit
****************************
```

## cache-read
cache-read will take in an address and read in the data located at that address. to access this command, you can type in **cache-read** followed by an 8-bit address in hexadecimal (formatted as 0x--). 

an example of a cache miss with the address **0x18**:
```
cache-read 0x18
set:3
tag:00
hit:no
eviction_line:0
ram_address:0x18
data:0x84
```

## cache-write 
cache-write will take an address and write user-specified data into it. to access this command, you can type in **cache-write** followed by two 8-bit addressed in hexadecimal (formatted as 0x--). the address immediately succeeding the command will represent the address to write data into, while the last address will represent the data to be written into the address.

an example of a cache miss with the address **0x10** with designated data **0xAB**
```
cache-write 0x10 0xAB
set:2
tag:00
write_hit:no
eviction_line:0
ram_address:0x10
data:0xAB
dirty_bit:1
```

## cache-flush
cache-flush flushes the cache - more specifically, it resets the current cache to a cold cache. 

the cache content should look like this after calling the command:
```
0 0 00 00 00 00 00 00 00 00 00
0 0 00 00 00 00 00 00 00 00 00
0 0 00 00 00 00 00 00 00 00 00
0 0 00 00 00 00 00 00 00 00 00
```

## cache-view
cache-view allows you to see the current contents of the cache, as well as the inputs instantiated at the beginning of the program's run. 

an example output would look like:
```
cache-view
cache_size:32
data_block_size:8
associativity:2
replacement_policy:random_replacement
write_hit_policy:write_through
write_miss_policy:write_allocate
number_of_cache_hits:2
number_of_cache_misses:6
cache_content:
1 0 F0 F6 AB 01 22 A5 A6 44 DB
1 0 01 DA FF 23 11 A5 10 29 87
1 0 01 F6 AB CD 97 BB A6 72 DB
1 0 01 F6 AB CD 97 BB A6 72 DB
```

## memory-view
memory-view allows you to see the current contents of the memory. 

an example output would look like:
```
memory-view
memory_size:256
memory_content:
address:data
0x00:F6 AB 01 22 A5 A6 44 DB
0x08:DA FF 23 11 A5 10 29 87
0x10:F6 AB CD 97 BB A6 72 DB
...
```

## cache-dump
cache-dump dumps the current contents of the cache into a file named **cache.txt**.

an example file would look like:
```
F6 AB 01 22 A5 A6 44 DB
DA FF 23 11 A5 10 29 87
F6 AB CD 97 BB A6 72 DB
F6 AB CD 97 BB A6 72 DB
```

## memory-dump
memory-dump dumps the current contents of the memory into a file named **ram.txt**.

an example file would look like:
```
F6
AB
01
22
...
```
