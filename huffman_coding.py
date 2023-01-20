from __future__ import annotations
import os
from typing import List, Dict
import heapq
import json
#-----------------------------------------------------------------------------------------------------------------
class node:
    def __init__(self, symbol: str, freq: int, left: node=None, right: node=None):
        # symbol name
        self.symbol = symbol
        # frequency of symbol
        self.freq = freq
        # node left of current node
        self.left = left
        # node right of current node
        self.right = right
		
    def __lt__(self, nxt: node):
        return self.freq < nxt.freq
#-----------------------------------------------------------------------------------------------------------------
def find_frequency(file_name: str) -> dict[int, int]:
    """finding frequency of eache byte in file

    Args:
        file_name (str): directory of file

    Returns:
        dict[int, str]: dictionary of eache byte with coresponding frequency
    """
    dic = dict()
    with open(file_name, 'rb') as image:
        byte = image.read(1)
        while  byte:
            if ord(byte) in dic:
                dic[ord(byte)] += 1
            else:
                dic[ord(byte)] = 1
            byte = image.read(1)
    return dic
#-----------------------------------------------------------------------------------------------------------------
def huffman_coding(frequencies: dict[int, int]) -> node:
    """creating huffman tree

    Args:
        frequencies (dict[int, int]): dictionary of symbols and their frequency

    Returns:
        node: root of the huffman tree
    """
    # initial the min-heap
    nodes:List[node] = list()
    for symbol in frequencies:
        heapq.heappush(nodes, node(str(symbol), frequencies[symbol]))

    # create the huffman tree
    while (len(nodes) > 1):
        left = heapq.heappop(nodes)
        right = heapq.heappop(nodes)
        # combine the 2 smallest nodes to create new node as their parent
        newNode = node('', left.freq+right.freq, left, right)
        heapq.heappush(nodes, newNode)
    return nodes[0]
#-----------------------------------------------------------------------------------------------------------------
def read_huffman_tree(root: node, code: str='') -> dict[str, str]:
    """reading the huffman tree

    Args:
        root (node): root of huffman tree
        code (str, optional): huffman code for node. Defaults to ''.

    Returns:
        dict[str, str]: dictionary of symbol and cresponding huffman code
    """
    encoded:Dict[str, str] = dict()
    # huffman code for current node
	# if node is not an edge node then traverse inside it
    if(root.left):
        encoded.update(read_huffman_tree(root.left, code + '0'))
    if(root.right):
        encoded.update(read_huffman_tree(root.right, code + '1'))
    # if node is edge node then save its huffman code
    if(not root.left and not root.right):
        encoded[root.symbol] = code
        return encoded
    return encoded
#-----------------------------------------------------------------------------------------------------------------
def create_huffman_tree(huffman_code: dict[str, str]) -> node:
    root = node('', 0)
    for symbol in huffman_code:
        if type(huffman_code[symbol]) == str:
            pointer = root
            for char in huffman_code[symbol]:
                if char == '0':
                    if pointer.left == None:
                        pointer.left = node('', 0)
                    pointer = pointer.left
                else:
                    if pointer.right == None:
                        pointer.right = node('', 0)
                    pointer = pointer.right
            pointer.symbol = symbol
    return root
#-----------------------------------------------------------------------------------------------------------------
def compress(source_file: str, compressed_file: str) -> dict[str, str]:
    # huffman-coding phase
    frequencies = find_frequency(source_file)
    root = huffman_coding(frequencies)
    huffman_code = read_huffman_tree(root)
    
    # encoding
    temp = ''
    with open(source_file, 'rb') as source:
        byte = source.read(1)
        while(byte):
            temp += huffman_code[str(ord(byte))]
            byte = source.read(1)

    # adding '0' at the end of encoded string
    huffman_code['appended'] = (8-len(temp)%8)%8   
    temp += '0' * huffman_code['appended']

    # writing compresed file
    with open(compressed_file, 'wb') as result:
        for i in range(0, len(temp), 8):
            result.write(int(temp[i:i+8], 2).to_bytes(1, 'big'))
    return huffman_code
#-----------------------------------------------------------------------------------------------------------------
def decompress(root: node, compressed_file: str, decompressed_file: str, zero_appended: int) -> None:
    # reading compresed file
    temp = ''
    with open(compressed_file, 'rb') as file:
        byte = file.read(1)
        while(byte):
            append = (8-len(bin(ord(byte))[2:])%8)%8
            temp += append * '0' + bin(ord(byte))[2:]
            byte = file.read(1)
    temp = temp[:-zero_appended]

    # writing decompresed file
    pointer = root
    with open(decompressed_file, 'wb') as file:
        i = 0
        while(i < len(temp)):
            if not pointer.left and not pointer.right:
                file.write(int(pointer.symbol).to_bytes(1, 'big'))
                pointer = root
                continue
            elif temp[i] == '0':
                pointer = pointer.left
            else:
                pointer = pointer.right
            i += 1
        if not pointer.left and not pointer.right:
            file.write(int(pointer.symbol).to_bytes(1, 'big'))
#-----------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':

    # compress and get huffman code
    huffman_code = compress('image_2.jpg', 'compress.jpg')

    # writing huffman code in text file
    with open('huffman_code.txt', 'w') as convert_file:
     convert_file.write(json.dumps(huffman_code))

    # creating huffman tree from huffman code dictionary
    root = create_huffman_tree(huffman_code)

    # decompress
    decompress(root, 'compress.jpg', 'decompress.jpg', huffman_code['appended'])

    # calculate CR
    print(os.stat('image_2.jpg').st_size/os.stat('compress.jpg').st_size)