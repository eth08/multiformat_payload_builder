# Multi-Format Payload Builder

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Version](https://img.shields.io/badge/version-0.0.4-orange)

A multi-format payload builder designed to obfuscate and encode raw payloads. It applies a multi-layered encoding scheme to create a single, data blob for discreet delivery and execution.

## Features

- Accepts local files or remote files (HTTP/HTTPS).  
- Multi-layer encoding pipeline: XOR → substitution table → bit-rotation, then Base64.  
- Output is a JSON object containing the encoded payload and the metadata required for decoding.  
- Simple CLI for quick usage.  
- Minimal dependencies.

## Installation

To set up the application, you'll first need to install the required Python packages. It's recommended to use a virtual environment.

1.  **Clone the repository (or download the script):**
    ```bash
    git clone [https://github.com/eth08/multiformat_payload_builder.git](https://github.com/eth08/multiformat_payload_builder.git)
    cd multiformat_payload_builder
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**
    * On Windows: `venv\Scripts\activate`
    * On macOS/Linux: `source venv/bin/activate`

4.  **Install dependencies from `requirements.txt`:**
    
    Install the packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Basic CLI (summary):

    usage: payload_builder.py [-h] [--version] [--build BUILD] [--output OUTPUT] [--ptype PTYPE]

    Multi-Format Payload Builder
      --build   Build encoded file from path or URL
      --output  Encoded output file
      --ptype   Payload type: python | shellcode | powershell | bat | sh | pe | elf (default: python)

Examples:

Encode a local Python script:

    python payload_builder.py --build ./examples/hello.py --ptype python --output ./out/hello_encoded.dat

Encode a remote binary:

    python payload_builder.py --build "https://example.com/some.bin" --ptype elf --output ./out/remote_encoded.dat

If the script cannot fetch or open the input file, it will print an error and exit without writing output.

## Output format

The output file is JSON with two top-level keys: `p` (payload) and `m` (metadata). Example structure:

    {
      "p": "<base64-encoded-encoded-payload>",
      "m": {
        "key": <int>,           // XOR key used (1..255)
        "rot": <int>,           // bit-rotation amount (1..7)
        "sub": "<base64>",      // base64 of the 256-byte substitution table
        "ptype": "<string>"     // payload type provided by --ptype
      }
    }

- `p` — final payload after XOR → substitution → bit-rotation, then Base64-encoded.  
- `m` — metadata required to reverse the process (needed by a legitimate decoder).

## How it works (high level)

The encoder applies three transformation layers in this order:

1. **XOR** with a single-byte key (random, 1–255).  
2. **Substitution**: a byte-wise substitution using a random permutation of 0–255 (a generated substitution table).  
3. **Bit-rotation**: rotate bits of each byte by a small amount (random, 1–7).

After those transformations, the result is Base64-encoded for safe transport. The substitution table and numeric parameters are stored (substitution table encoded as Base64) in the metadata block so a compatible decoder can reconstruct the original input. See the source for exact details and implementation.

## Security & Ethical Notice (READ THIS)

This tool performs payload obfuscation and can be misused to conceal malicious code. Use and distribution of this project must comply with all applicable laws and policies.

- **Do not** use this tool to create, distribute, or deploy malware, ransomware, or any code intended to harm or access systems without explicit authorization.  
- Use only on files and systems you own or have explicit, written permission to test.  
- For defensive research, penetration testing, or red-team exercises, obtain clear written authorization and follow organizational policies and responsible-disclosure practices.  
- The current implementation stores decoding metadata alongside the encoded payload. Treat files and metadata carefully and consider adding HMAC/signatures or encrypting metadata for added safety.

The project maintainers are not responsible for misuse. If you are unsure whether your intended use is lawful or ethical, consult legal and security professionals before proceeding.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
