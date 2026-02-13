import os
import zipfile
import subprocess
import sys
import shutil
import urllib.request

GH_URL = "https://github.com/cli/cli/releases/download/v2.42.1/gh_2.42.1_windows_amd64.zip"
GH_ZIP = "gh.zip"
GH_EXE = "gh.exe"
REPO_NAME = "chendai"

def run_command(cmd, input_text=None):
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(
            cmd,
            input=input_text.encode() if input_text else None,
            capture_output=True,
            shell=True,
            check=True
        )
        print(result.stdout.decode())
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(e.stderr.decode())
        return False

def main():
    # 1. Download and Install GH CLI
    if not os.path.exists(GH_EXE):
        print("Downloading GitHub CLI...")
        try:
            urllib.request.urlretrieve(GH_URL, GH_ZIP)
            print("Extracting...")
            with zipfile.ZipFile(GH_ZIP, 'r') as zip_ref:
                # Find the gh.exe path inside zip
                gh_path = next(name for name in zip_ref.namelist() if name.endswith("bin/gh.exe"))
                # Extract only that file to current dir
                with zip_ref.open(gh_path) as source, open(GH_EXE, "wb") as target:
                    shutil.copyfileobj(source, target)
            print("GitHub CLI installed.")
        except Exception as e:
            print(f"Failed to install gh: {e}")
            return
        finally:
            if os.path.exists(GH_ZIP):
                os.remove(GH_ZIP)

    # 2. Git Init
    if not os.path.exists(".git"):
        run_command("git init")
    
    # 3. Commit
    run_command("git add .")
    run_command('git commit -m "Initial commit of ChendAI Research Project"')

    # 4. Auth
    # Load token
    token = None
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("GITHUB_TOKEN="):
                    token = line.strip().split("=")[1]
                    break
    
    if not token:
        print("Error: GITHUB_TOKEN not found in .env")
        return

    print("Authenticating with GitHub...")
    # Use full path to gh.exe to be safe
    gh_cmd = f".\\{GH_EXE}"
    if not run_command(f"{gh_cmd} auth login --with-token", input_text=token):
        return

    # 5. Create Repo
    print("Creating repository...")
    # check if remote already exists
    if run_command("git remote get-url origin"):
        print("Remote origin already exists.")
    else:
        # Create public repo
        run_command(f"{gh_cmd} repo create {REPO_NAME} --public --source=. --remote=origin")

    # 6. Push
    print("Pushing to GitHub...")
    run_command("git push -u origin master")

if __name__ == "__main__":
    main()
