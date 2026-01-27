"""
Script to update API_BASE_URL in all frontend pages to use Streamlit secrets
Run this before deploying to production
"""
import os
import re

FRONTEND_DIR = os.path.dirname(__file__)
PAGES_DIR = os.path.join(FRONTEND_DIR, "pages")

# Pattern to match old API_BASE_URL
OLD_PATTERN = r'API_BASE_URL\s*=\s*"http://localhost:8000/api/v1"'
NEW_LINE = 'API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000/api/v1")'

def update_file(filepath):
    """Update API_BASE_URL in a single file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'API_BASE_URL = "http://localhost:8000/api/v1"' in content:
        updated_content = re.sub(OLD_PATTERN, NEW_LINE, content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        return True
    return False

def main():
    """Update all Python files in pages directory"""
    updated_files = []
    
    # Update files in pages directory
    if os.path.exists(PAGES_DIR):
        for filename in os.listdir(PAGES_DIR):
            if filename.endswith('.py'):
                filepath = os.path.join(PAGES_DIR, filename)
                if update_file(filepath):
                    updated_files.append(filename)
    
    # Print results
    if updated_files:
        print(f"✅ Updated {len(updated_files)} files:")
        for filename in updated_files:
            print(f"   - {filename}")
    else:
        print("ℹ️  No files needed updating (already using secrets)")

if __name__ == "__main__":
    main()
