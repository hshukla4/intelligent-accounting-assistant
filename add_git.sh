# 1. From your project root
cd ~/Downloads/intelligent-accounting-assistant

# 2. Create a .gitignore
cat > .gitignore <<EOF
# Python
*.pyc
__pycache__/
.venv/
env/
*.egg-info/

# Environment files
.env

# Data folders
data/output/
data/raw_documents/

# IDE/editor
.vscode/
.idea/
.DS_Store
EOF

# 3. Initialize Git
git init

# 4. Stage and commit
git add .
git commit -m "chore: initial commit of Intelligent Accounting Assistant pipeline"

# 5. (Optional) Add a remote and push
# Replace URL with your repo’s remote
git remote add origin git@github.com:hshukla4/accounting-ai.git
git branch -M main
git push -u origin main