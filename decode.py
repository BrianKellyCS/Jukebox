import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
import base64

def decode_base64_url_safe(s: str) -> bytes:
    """Decode URL-safe base64-encoded strings."""
    return base64.urlsafe_b64decode(s + '==')

def rc4_decrypt(key: str, data: bytes) -> bytes:
    """Decrypt data using RC4 algorithm."""
    S = list(range(256))
    j = 0
    out = []

    # Key scheduling algorithm (KSA)
    for i in range(256):
        j = (j + S[i] + ord(key[i % len(key)])) % 256
        S[i], S[j] = S[j], S[i]

    # Pseudo-random generation algorithm (PRGA)
    i = j = 0
    for char in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        out.append(char ^ S[(S[i] + S[j]) % 256])

    return bytes(out)

def decrypt_source_url(encrypted_url: str, key: str = "8z5Ag5wgagfsOuhz") -> str:
    """Decrypt an encoded source URL."""
    data = decode_base64_url_safe(encrypted_url)
    decrypted_data = rc4_decrypt(key, data)
    return unquote(decrypted_data.decode('utf-8'))

def get_streamable_url_from_vidsrc(url: str) -> str:
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to fetch the video page")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    video_id_element = soup.find('a', {'data-id': True})
    if not video_id_element:
        raise Exception("Video ID not found")
    
    video_id = video_id_element['data-id']
    

    
    streamable_url = decrypt_source_url(url)
    
    return streamable_url

# Example use
vidsrc_url = "https://vidsrc.to/embed/movie/10681"
try:
    streamable_url = get_streamable_url_from_vidsrc(vidsrc_url)
    print("Streamable URL:", streamable_url)
except Exception as e:
    print("Error:", str(e))
