#!/usr/bin/env python3
# payload_builder.py - A multi-format payload builder
__version__ = "0.0.4"

import os, random, base64, requests, json

def fetch_file(path_or_url: str) -> bytes | None: # Added | None for error cases
    """Fetch file from local path or URL."""
    if path_or_url.startswith("http"):
        try:
            response = requests.get(path_or_url, timeout=10) # Added timeout
            response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"[-] Error fetching URL '{path_or_url}': {e}")
            return None
    else:
        try:
            with open(path_or_url, "rb") as f:
                return f.read()
        except FileNotFoundError:
            print(f"[-] Error: File not found at '{path_or_url}'")
            return None
        except IOError as e:
            print(f"[-] Error reading file '{path_or_url}': {e}")
            return None

def generate_substitution_table():
    """Generate random substitution table and its reverse mapping."""
    table = list(range(256))
    random.shuffle(table)
    return table, {v: i for i, v in enumerate(table)}

def xor_enc(data: bytes, key: int) -> bytes:
    """Apply XOR encoding."""
    return bytes([b ^ key for b in data])

def sub_enc(data: bytes, table: list) -> bytes:
    """Apply substitution table encoding."""
    return bytes([table[b] for b in data])

def bit_rot_enc(data: bytes, r: int) -> bytes:
    """Apply bit rotation encoding."""
    return bytes([((b << r) & 0xFF) | (b >> (8 - r)) for b in data])

def multi_encode(data: bytes):
    """Apply XOR + substitution + bit rotation multi-layer encoding."""
    key = random.randint(1, 255)
    rotation = random.randint(1, 7)
    table, _ = generate_substitution_table()
    step1 = xor_enc(data, key)
    step2 = sub_enc(step1, table)
    step3 = bit_rot_enc(step2, rotation)

    # Encode the substitution table as base64 string
    # The 'meta' dictionary will be directly JSON serializable
    meta = {
        "key": key,
        "rot": rotation,
        "sub": base64.b64encode(bytes(table)).decode('utf-8')
    }
    # The encoded payload itself
    encoded_payload_b64 = base64.b64encode(step3).decode('utf-8')

    return encoded_payload_b64, meta

def build_encoded(input_file: str, output_file: str, payload_type="python"):
    """Encode the given file and save output in encoded format."""
    raw = fetch_file(input_file)
    if raw is None: # Handle case where fetch_file failed
        return

    enc, meta = multi_encode(raw)
    meta["ptype"] = payload_type

    # Prepare the final structure to be JSON encoded
    output_data = {
        "p": enc, # 'p' for payload
        "m": meta # 'm' for metadata
    }

    try:
        with open(output_file, "w", encoding='utf-8') as f: # Specify encoding for text files
            json.dump(output_data, f, indent=4) # Use json.dump for clear, readable output
        print(f"[+] Encoded file saved in {output_file} (type: {payload_type})")
    except IOError as e:
        print(f"[-] Error writing to output file '{output_file}': {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=f"Multi-Format Payload Builder v{__version__}")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--build", help="Build encoded file from path or URL")
    parser.add_argument("--output", help="Encoded output file")
    parser.add_argument("--ptype", help="Payload type: python | shellcode | powershell | bat | sh | pe | elf", default="python")
    args = parser.parse_args()
    if args.build and args.output:
        build_encoded(args.build, args.output, args.ptype)
    else:
        print(f"Example:\n python {parser.prog} --build script.py --ptype python --output encoded.dat") # Use parser.prog for robustness
