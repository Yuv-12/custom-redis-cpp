import socket
import struct
import sys

# Serialization Tags
TAG_NIL = 0
TAG_ERR = 1
TAG_STR = 2
TAG_INT = 3
TAG_DBL = 4
TAG_ARR = 5

def encode_request(args):
    """
    Encode request: 
    [4 bytes length] [4 bytes num_strings] [4 bytes len1][str1] [4 bytes len2][str2] ...
    """
    body = struct.pack("<I", len(args))
    for arg in args:
        arg_bytes = arg.encode('utf-8') if isinstance(arg, str) else arg
        body += struct.pack("<I", len(arg_bytes)) + arg_bytes
    
    header = struct.pack("<I", len(body))
    return header + body

def read_exact(sock, n):
    data = b""
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            raise ConnectionError("Connection closed by server")
        data += packet
    return data

def parse_response(data, offset=0):
    """
    Parse the custom serialized data type returned by the server.
    """
    if offset >= len(data):
        return None, offset
        
    tag = data[offset]
    offset += 1
    
    if tag == TAG_NIL:
        return "(nil)", offset
    elif tag == TAG_ERR:
        code = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        msg_len = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        msg = data[offset:offset+msg_len].decode('utf-8')
        offset += msg_len
        return f"(error: code={code}) {msg}", offset
    elif tag == TAG_STR:
        msg_len = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        msg = data[offset:offset+msg_len].decode('utf-8')
        offset += msg_len
        return f"(str) \"{msg}\"", offset
    elif tag == TAG_INT:
        val = struct.unpack_from("<q", data, offset)[0]
        offset += 8
        return f"(int) {val}", offset
    elif tag == TAG_DBL:
        val = struct.unpack_from("<d", data, offset)[0]
        offset += 8
        return f"(dbl) {val}", offset
    elif tag == TAG_ARR:
        arr_len = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        arr = []
        for _ in range(arr_len):
            val, offset = parse_response(data, offset)
            arr.append(val)
        return arr, offset
    else:
        raise ValueError(f"Unknown serialization tag: {tag}")

def send_command(host, port, args):
    try:
        # Create socket and connect
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        
        # Send encoded command
        req = encode_request(args)
        sock.sendall(req)
        
        # Read response length (4-byte header)
        header = read_exact(sock, 4)
        res_len = struct.unpack("<I", header)[0]
        
        # Read response body
        res_body = read_exact(sock, res_len)
        
        # Parse and print response
        res, _ = parse_response(res_body)
        print(res)
        
        sock.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python client.py <host> <port> <command> [args...]")
        print("Example: python client.py custom-redis-cpp.onrender.com 10000 set key1 value1")
        sys.exit(1)
        
    host = sys.argv[1]
    port = int(sys.argv[2])
    cmd_args = sys.argv[3:]
    
    send_command(host, port, cmd_args)
