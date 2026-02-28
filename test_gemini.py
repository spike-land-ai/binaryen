import subprocess
import time

start = time.time()
res = subprocess.run(["gemini", "-p", "Categorize the word 'apple' into one of: fruit, vegetable, meat. Output only the category."], capture_output=True, text=True)
end = time.time()
print(f"Time: {end - start:.2f}s")
print(f"Output: {res.stdout.strip()}")
