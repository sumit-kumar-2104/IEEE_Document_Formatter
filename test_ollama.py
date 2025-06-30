import subprocess

prompt = "Suggest 3 research paper titles on energy-efficient AI."

try:
    result = subprocess.run(
        ["ollama", "run", "phi3:mini"],
        input=prompt,
        text=True,
        capture_output=True,
        timeout=60
    )
    print("STDOUT:")
    print(result.stdout)
    print("STDERR:")
    print(result.stderr)
except Exception as e:
    print("Error:", e)
