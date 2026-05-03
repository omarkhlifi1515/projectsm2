import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import rag

try:
    print(rag.generate_rag_response("hello"))
except Exception as e:
    print("ERROR:", repr(e))
