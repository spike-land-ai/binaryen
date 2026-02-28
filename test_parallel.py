import asyncio
import subprocess
import time

async def run_gemini(i):
    print(f"Starting {i}")
    proc = await asyncio.create_subprocess_shell(
        'gemini -p "Reply with just the number: " <<< "What is 2+2?"',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    print(f"Finished {i}: {stdout.strip()[-10:]}")

async def main():
    start = time.time()
    await asyncio.gather(*[run_gemini(i) for i in range(4)])
    print(f"Time: {time.time() - start:.2f}s")

asyncio.run(main())
