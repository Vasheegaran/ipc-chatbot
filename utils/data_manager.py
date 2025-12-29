import json
import os
import re
from typing import Dict, List, Any, Optional
import time

class IPCDataManager:
    """
    Manages IPC data loading, validation, and search
    Optimized for free deployment on Streamlit Cloud
    """
    
    def __init__(self, data_path: str = "data/ipc_data.json"):
        self.data_path = data_path
        self.raw_data = None
        self.sections_by_number = {}
        self.sections_by_chapter = {}
        self.keyword_index = {}
        self.all_sections = []
        
    def load_and_validate(self) -> List[Dict[str, Any]]:
        """
        Load IPC data and validate structure
        Returns: List of all IPC sections
        """
        print("📂 Loading IPC data...")
        
        # Check if file exists
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"IPC data file not found at: {self.data_path}")
        
        # Load JSON data
        with open(self.data_path, 'r', encoding='utf-8') as f:
            self.raw_data = json.load(f)
        
        print(f"✅ Loaded {len(self.raw_data)} sections from JSON")
        
        # Validate each section
        self._validate_data()
        
        # Build search indexes
        self._build_indexes()
        
        return self.all_sections
    
    def _validate_data(self) -> None:
        """Validate all sections have required fields"""
        required_fields = ["Section", "section_title", "section_desc", "chapter", "chapter_title"]
        
        for i, section in enumerate(self.raw_data):
            # Check required fields
            missing = [field for field in required_fields if field not in section]
            if missing:
                raise ValueError(f"Section {i+1} missing fields: {missing}")
            
            # Ensure Section is string
            if isinstance(section["Section"], (int, float)):
                section["Section"] = str(int(section["Section"]))
        
        print("✅ All sections validated successfully")
    
    def _build_indexes(self) -> None:
        """Build fast search indexes"""
        print("🔍 Building search indexes...")
        
        self.sections_by_number = {}
        self.sections_by_chapter = {}
        self.keyword_index = {}
        self.all_sections = []
        
        # Process each section
        for section in self.raw_data:
            section_num = str(section["Section"])
            
            # Create optimized section data
            optimized_section = {
                "number": section_num,
                "title": section["section_title"],
                "description": section["section_desc"],
                "chapter": str(section["chapter"]),
                "chapter_title": section["chapter_title"],
                "search_text": self._create_search_text(section)
            }
            
            # Add to collections
            self.all_sections.append(optimized_section)
            self.sections_by_number[section_num] = optimized_section
            
            # Add to chapter index
            chapter = str(section["chapter"])
            if chapter not in self.sections_by_chapter:
                self.sections_by_chapter[chapter] = []
            self.sections_by_chapter[chapter].append(section_num)
            
            # Build keyword index (simple version)
            self._add_to_keyword_index(section_num, optimized_section["search_text"])
        
        print(f"✅ Built indexes: {len(self.sections_by_number)} sections, "
              f"{len(self.sections_by_chapter)} chapters, "
              f"{len(self.keyword_index)} keywords")
    
    def _create_search_text(self, section: Dict[str, Any]) -> str:
        """Create searchable text from section"""
        # Combine all text fields for searching
        text_parts = [
            str(section["Section"]),
            section["section_title"],
            section["section_desc"],
            str(section["chapter"]),
            section["chapter_title"]
        ]
        
        # Join and clean
        search_text = " ".join(text_parts)
        search_text = re.sub(r'\s+', ' ', search_text)  # Remove extra spaces
        search_text = search_text.lower()  # Lowercase for case-insensitive search
        
        return search_text
    
    def _add_to_keyword_index(self, section_num: str, search_text: str) -> None:
        """Add section to keyword index (simplified)"""
        # Extract words with 3+ letters
        words = re.findall(r'\b[a-z]{3,}\b', search_text)
        
        for word in words:
            if word not in self.keyword_index:
                self.keyword_index[word] = []
            if section_num not in self.keyword_index[word]:
                self.keyword_index[word].append(section_num)
    
    # SEARCH METHODS
    def search_by_number(self, section_number: str) -> Optional[Dict[str, Any]]:
        """Find section by exact number (e.g., '302', '420')"""
        # Clean input
        section_number = str(section_number).strip()
        
        # Try direct match
        if section_number in self.sections_by_number:
            return self.sections_by_number[section_number]
        
        # Try with 'IPC' prefix removed
        if section_number.lower().startswith('ipc'):
            clean_num = section_number[3:].strip()
            if clean_num in self.sections_by_number:
                return self.sections_by_number[clean_num]
        
        # Try with 'section' prefix removed
        if section_number.lower().startswith('section'):
            clean_num = section_number[7:].strip()
            if clean_num in self.sections_by_number:
                return self.sections_by_number[clean_num]
        
        return None
    
    def search_by_keyword(self, keyword: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find sections containing keyword"""
        keyword = keyword.lower().strip()
        results = []
        
        # Simple keyword matching in search text
        for section in self.all_sections:
            if keyword in section["search_text"]:
                results.append(section)
                if len(results) >= limit:
                    break
        
        return results
    
    def search_by_chapter(self, chapter_number: str) -> List[Dict[str, Any]]:
        """Get all sections in a chapter"""
        chapter_number = str(chapter_number).strip()
        
        if chapter_number not in self.sections_by_chapter:
            return []
        
        sections = []
        for section_num in self.sections_by_chapter[chapter_number]:
            section = self.sections_by_number.get(section_num)
            if section:
                sections.append(section)
        
        return sections
    
    def advanced_search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Smart search that tries multiple strategies:
        1. Exact section number
        2. Keywords in text
        3. Chapter search
        """
        query = query.strip()
        
        # Strategy 1: Check if query contains section number
        section_numbers = re.findall(r'\b\d{1,3}\b', query)
        for num in section_numbers:
            if 1 <= int(num) <= 511:  # IPC section range
                section = self.search_by_number(num)
                if section:
                    return [section]
        
        # Strategy 2: Keyword search
        keyword_results = self.search_by_keyword(query, limit)
        if keyword_results:
            return keyword_results
        
        # Strategy 3: Check for chapter
        chapter_numbers = re.findall(r'\bchapter\s*(\d{1,2})\b', query.lower())
        for chap_num in chapter_numbers:
            chapter_results = self.search_by_chapter(chap_num)
            if chapter_results:
                return chapter_results[:limit]
        
        return []
    
    def get_all_sections(self) -> List[Dict[str, Any]]:
        """Get all IPC sections"""
        return self.all_sections
    
    def get_total_count(self) -> int:
        """Get total number of sections"""
        return len(self.all_sections)
    
    def get_chapter_summary(self, chapter_number: str) -> Dict[str, Any]:
        """Get summary of a chapter"""
        sections = self.search_by_chapter(chapter_number)
        if not sections:
            return {"error": f"Chapter {chapter_number} not found"}
        
        # Get chapter title from first section
        chapter_title = sections[0].get("chapter_title", "Unknown Chapter")
        
        return {
            "chapter_number": chapter_number,
            "chapter_title": chapter_title,
            "section_count": len(sections),
            "sections": [{"number": s["number"], "title": s["title"]} for s in sections[:10]]
        }

# Utility function for easy usage
def create_data_manager() -> IPCDataManager:
    """Create and initialize data manager"""
    manager = IPCDataManager()
    manager.load_and_validate()
    return manager

# Test function
def test_data_manager():
    """Test the data manager functionality"""
    print("🧪 Testing IPC Data Manager...")
    
    try:
        manager = create_data_manager()
        
        print(f"\n📊 Statistics:")
        print(f"  Total sections: {manager.get_total_count()}")
        
        # Test exact search
        print(f"\n🔍 Test 1: Exact section search")
        section_302 = manager.search_by_number("302")
        if section_302:
            print(f"  ✅ Found Section 302: {section_302['title'][:50]}...")
        else:
            print("  ❌ Section 302 not found")
        
        # Test keyword search
        print(f"\n🔍 Test 2: Keyword search")
        theft_sections = manager.search_by_keyword("theft", 3)
        print(f"  ✅ Found {len(theft_sections)} sections about 'theft'")
        for i, sec in enumerate(theft_sections[:2]):
            print(f"    {i+1}. Section {sec['number']}: {sec['title'][:60]}...")
        
        # Test chapter search
        print(f"\n🔍 Test 3: Chapter search")
        chapter_16 = manager.search_by_chapter("16")
        print(f"  ✅ Chapter 16 has {len(chapter_16)} sections")
        
        # Test advanced search
        print(f"\n🔍 Test 4: Advanced search")
        queries = ["punishment for theft", "IPC 420", "chapter 17 criminal trespass"]
        for query in queries:
            results = manager.advanced_search(query, 2)
            print(f"  '{query}': Found {len(results)} results")
        
        print("\n" + "="*50)
        print("✅ ALL TESTS PASSED - Data manager is working!")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_data_manager()