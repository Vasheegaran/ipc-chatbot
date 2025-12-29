"""
One-time setup script for IPC Chatbot
Run this first: python setup_environment.py
"""
import os
import subprocess
import sys

def print_step(step_num, description):
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {description}")
    print(f"{'='*60}")

def run_command(command, description):
    print(f"\n▶ {description}")
    print(f"  Command: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ Success")
            if result.stdout.strip():
                print(f"  Output: {result.stdout[:200]}...")
        else:
            print(f"  ❌ Failed")
            print(f"  Error: {result.stderr[:200]}")
        return result.returncode == 0
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return False

def main():
    print("\n" + "⭐" * 30)
    print("   IPC CHATBot - COMPLETE SETUP")
    print("⭐" * 30)
    
    # Step 1: Check Python
    print_step(1, "Checking Python Installation")
    success = run_command("python --version", "Python version")
    if not success:
        print("\n❌ Python not found. Please install Python 3.9+ from python.org")
        return
    
    # Step 2: Create virtual environment
    print_step(2, "Creating Virtual Environment")
    if not os.path.exists("venv"):
        success = run_command("python -m venv venv", "Create venv")
        if not success:
            print("❌ Failed to create virtual environment")
            return
    else:
        print("✅ Virtual environment already exists")
    
    # Step 3: Activate and install packages
    print_step(3, "Installing Dependencies")
    
    # Determine activation command based on OS
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate && "
    else:  # Linux/Mac
        activate_cmd = "source venv/bin/activate && "
    
    commands = [
        f"{activate_cmd}pip install --upgrade pip",
        f"{activate_cmd}pip install -r requirements.txt",
    ]
    
    all_success = True
    for cmd in commands:
        if not run_command(cmd, f"Running: {cmd[:50]}..."):
            all_success = False
    
    if not all_success:
        print("\n❌ Some installations failed")
        return
    
    # Step 4: Check folder structure
    print_step(4, "Checking Folder Structure")
    
    required_folders = ["data", "utils", "tests", ".streamlit"]
    required_files = {
        "data/ipc_data.json": "Your IPC data file (575 sections)",
        "requirements.txt": "Python dependencies",
        ".gitignore": "Git ignore rules",
        ".streamlit/config.toml": "Streamlit configuration"
    }
    
    print("\n📁 Required folders:")
    for folder in required_folders:
        if os.path.exists(folder):
            print(f"  ✅ {folder}/")
        else:
            print(f"  ⚠️  {folder}/ (will be created)")
            os.makedirs(folder, exist_ok=True)
    
    print("\n📄 Required files:")
    for file, description in required_files.items():
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ⚠️  {file} - {description}")
    
    # Step 5: Data verification
    print_step(5, "Data Verification")
    ipc_file = "data/ipc_data.json"
    if os.path.exists(ipc_file):
        import json
        try:
            with open(ipc_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"✅ Found {len(data)} IPC sections in ipc_data.json")
        except Exception as e:
            print(f"❌ Error reading ipc_data.json: {e}")
    else:
        print("⚠️  ipc_data.json not found in data/ folder")
        print("   Please copy your 575-section JSON file to data/ipc_data.json")
    
    # Step 6: Final instructions
    print_step(6, "SETUP COMPLETE!")
    
    print("\n📋 NEXT STEPS:")
    print("1. Activate virtual environment:")
    print("   Windows: venv\\Scripts\\activate")
    print("   Mac/Linux: source venv/bin/activate")
    print("\n2. Test the data system:")
    print("   python tests/test_data.py")
    print("\n3. Run Phase 1 validation:")
    print("   python -c \"from utils.data_manager import test_data_manager; test_data_manager()\"")
    
    print("\n" + "✅" * 30)
    print("   SETUP READY FOR PHASE 2")
    print("✅" * 30)
    
    # Auto-test if data file exists
    if os.path.exists(ipc_file):
        print("\n🎯 Running auto-test...")
        try:
            from utils.data_manager import test_data_manager
            test_result = test_data_manager()
            if test_result:
                print("\n🎉 CONGRATULATIONS! Your IPC Chatbot is ready!")
                print("   Proceed to Phase 2: Search & Question Processing")
            else:
                print("\n⚠️  Tests failed. Please check your ipc_data.json format")
        except ImportError:
            print("⚠️  Could not run auto-test. Please run manually:")
            print("   python tests/test_data.py")

if __name__ == "__main__":
    main()