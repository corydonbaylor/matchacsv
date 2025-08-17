# matchacsv

Here’s a concise, copy‑pasteable **README** section for setting up and running your project with **uv**.



# **Setup (with uv)**

## **1) Install uv**



Choose one:

**Homebrew (macOS)**

```
brew install uv
```

Homebrew formula reference. 

**Official script (macOS/Linux)**

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Official install docs. 

> If ~/.local/bin isn’t on your PATH, add it (the installer suggests this). 



## **2) Install the required Python version**

This repo includes a .python-version file. Have uv install that exact interpreter:

```
uv python install "$(cat .python-version)"
```

uv reads .python-version and installs that version. 

## **3) Create and activate a virtual environment**

```
uv venv --python "$(cat .python-version)" .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -V                   # sanity check
```

Creating & using venvs with uv. 

## **4) Install project dependencies**

```
uv pip install -r requirements.txt
```

uv supports installing from a requirements.txt. 

*(If you later adopt* *pyproject.toml**, you can use* *uv sync* *to install from the lockfile.)* 

## **5) Run the app**

```
python csv_editor.py
```

## **6) Common commands**

```
# Add a new package (and pin it in requirements later if you use one)
uv pip install <package>

# Freeze currently installed versions (optional)
uv pip freeze > requirements.txt

# Update uv itself (Homebrew)
brew upgrade uv
```

General uv feature overview & workflows.  

## **Troubleshooting**

- **Command not found after install:** Ensure ~/.local/bin is on your PATH (if you used the script installer). 
- **Wrong Python version:** Re-run steps 2–3 to recreate the venv with the version in .python-version. 
- **Need to (re)create venv quickly:** uv venv will create .venv and print the activation command. 

