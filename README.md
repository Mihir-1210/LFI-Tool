# LFI Matrix Scanner (v4.0 #Stable)

A high-concurrency, dynamic Local File Inclusion (LFI) reconnaissance and validation engine written in Python. This tool maps an application's attack surface dynamically, bypasses client-side URL normalization limitations using custom socket transport adapters, and multi-threads payload delivery across targeted structural matrices.

<img width="1185" height="493" alt="LFI-2" src="https://github.com/user-attachments/assets/34358506-2417-4a10-8d97-aac12c9de489" />

---

## Key Features

* **Raw Socket Override:** Implements a custom `HTTPAdapter` transport layer to bypass Python's default client-side URL normalization (RFC 3986), forcing raw, unparsed directory traversal vectors (`../`) onto the wire.
* **Three-Pronged Recon Surface Mapping:**
    * **Crawler:** Parses active DOM attributes (`src`, `href`, `action`) via regex to map parameters expecting real asset tracks.
    * **Native Query Parser:** Strips and targets parameters explicitly provided in the initial URL query string.
    * **Endpoint Matrix Fuzzer:** Generates cross-product arrays of common hidden endpoint pathways and input flags.
* **Deterministic Signature Validation:** Eliminates false positives by verifying exact operating system and wrapper markers (`root:x:`, `[boot loader]`, `PD9waH`) rather than relying on fickle HTTP status codes or response lengths.
* **High Performance:** Optimized for I/O-bound scaling using a thread-pool architecture (defaulting to 45 concurrent workers).

---

## Installation

Clone the repository and ensure you have the required dependencies installed:

```bash
git clone [https://github.com/yourusername/lfi-matrix-scanner.git](https://github.com/yourusername/lfi-matrix-scanner.git)
cd lfi-matrix-scanner
pip install -r requirements.txt
