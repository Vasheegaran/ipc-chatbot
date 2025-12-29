import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.chatbot_engine import test_chatbot

def main():
    print("🧪 PHASE 3: CHATBOT ENGINE TEST")
    print("=" * 60)
    
    success = test_chatbot()
    
    if success:
        print("\n📁 Files verified:")
        print("   - utils/chatbot_engine.py")
        print("   - utils/data_manager.py")
        print("   - data/ipc_data.json")
        print("\n✅ PHASE 3 COMPLETED SUCCESSFULLY!")
        print("\n🚀 READY FOR DEPLOYMENT!")
        print("\nTo run the chatbot:")
        print("   streamlit run app.py")
    else:
        print("\n❌ PHASE 3 FAILED")
        print("\nCheck if Phase 1 data is working properly.")

if __name__ == "__main__":
    main()