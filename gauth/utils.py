# Author: Álvaro Parafita (parafita.alvaro@gmail.com)

import json

def raise_json(r, exc=Exception):
    try:
        exc = exc(json.dumps(r.json(), indent=2))
    except:
        exc = exc(r.text) 
        # don't raise it here to avoid "Another Exception occurred"
        
    raise exc