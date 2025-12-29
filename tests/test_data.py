import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_manager import test_data_manager

def main():
    print("🧪 PHASE 1: IPC DATA VALIDATION TESTS")
    print("=" * 60)
    
    success = test_data_manager()
    
    if success:
        print("\n📁 Files verified:")
        print("   - data/ipc_data.json (your 575 sections)")
        print("   - utils/data_manager.py")
        print("   - tests/test_data.py")
        print("\n✅ PHASE 1 COMPLETED SUCCESSFULLY!")
        print("\n📋 Ready to move to Phase 2: Search & Question Processing")
    else:
        print("\n❌ PHASE 1 FAILED")
        print("\nCommon issues:")
        print("1. ipc_data.json not in data/ folder")
        print("2. JSON format incorrect")
        print("3. Missing required fields in sections")

if __name__ == "__main__":
    main()