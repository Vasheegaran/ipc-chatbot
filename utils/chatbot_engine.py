import re
from typing import List, Dict, Any, Optional
from datetime import datetime

class IPCChatbot:
    """
    IPC Chatbot Engine
    Uses keyword-based search to answer legal questions
    100% free - no APIs required
    """
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.conversation_history = []
        
    def process_question(self, user_question: str) -> Dict[str, Any]:
        """
        Main function: Process user question and generate response
        """
        # Clean and analyze question
        cleaned_question = self._clean_question(user_question)
        question_type = self._classify_question(cleaned_question)
        
        # Find relevant sections
        relevant_sections = self._find_relevant_sections(cleaned_question, question_type)
        
        # Generate response
        response = self._generate_response(cleaned_question, relevant_sections, question_type)
        
        # Store in history
        self._add_to_history(user_question, response, relevant_sections)
        
        return response
    
    def _clean_question(self, question: str) -> str:
        """Clean and normalize the question"""
        question = question.strip()
        question = question.lower()
        
        # Remove common prefixes
        prefixes = ["what is", "tell me about", "explain", "define", "what does", "how is"]
        for prefix in prefixes:
            if question.startswith(prefix):
                question = question[len(prefix):].strip()
        
        return question
    
    def _classify_question(self, question: str) -> str:
        """Classify the type of question"""
        question_lower = question.lower()
        
        # Check for section number
        if re.search(r'\b\d{1,3}\b', question_lower):
            if re.search(r'section\s*\d+|ipc\s*\d+', question_lower):
                return "section_number"
        
        # Check for chapter
        if re.search(r'chapter\s*\d+', question_lower):
            return "chapter"
        
        # Check for definition/what is
        if any(word in question_lower for word in ["what is", "define", "meaning of"]):
            return "definition"
        
        # Check for punishment/penalty
        punishment_words = ["punishment", "punish", "penalty", "sentence", "fine", "imprisonment", "jail", "prison"]
        if any(word in question_lower for word in punishment_words):
            return "punishment"
        
        # Default to keyword search
        return "keyword"
    
    def _get_special_cases(self, question: str) -> List[Dict[str, Any]]:
        """Handle special legal queries with exact answers"""
        question_lower = question.lower()
        sections = []
        
        # SUICIDE RELATED - EXACT MATCH
        if any(word in question_lower for word in ["suicide", "kill himself", "kill herself", "end life"]):
            # Section 306 - Abetment of suicide (10 years)
            sec_306 = self.data_manager.search_by_number("306")
            if sec_306:
                sections.append(sec_306)
            # Section 309 - Attempt to commit suicide (1 year)
            sec_309 = self.data_manager.search_by_number("309")
            if sec_309:
                sections.append(sec_309)
            return sections
        
        # MURDER RELATED
        if "murder" in question_lower and any(word in question_lower for word in ["punish", "sentence", "penalty", "death penalty"]):
            sec_302 = self.data_manager.search_by_number("302")  # Punishment for murder
            if sec_302:
                sections.append(sec_302)
            return sections
        
        # THEFT RELATED
        if "theft" in question_lower and any(word in question_lower for word in ["punish", "sentence", "penalty"]):
            sec_379 = self.data_manager.search_by_number("379")  # Punishment for theft
            if sec_379:
                sections.append(sec_379)
            sec_378 = self.data_manager.search_by_number("378")  # Definition of theft
            if sec_378 and sec_378 not in sections:
                sections.append(sec_378)
            return sections
        
        # CHEATING/SCAM RELATED
        if any(word in question_lower for word in ["cheat", "scam", "420", "fraud"]):
            sec_420 = self.data_manager.search_by_number("420")  # Cheating and dishonestly
            if sec_420:
                sections.append(sec_420)
            sec_415 = self.data_manager.search_by_number("415")  # Definition of cheating
            if sec_415 and sec_415 not in sections:
                sections.append(sec_415)
            return sections
        
        # RAPE RELATED
        if "rape" in question_lower:
            sec_376 = self.data_manager.search_by_number("376")  # Punishment for rape
            if sec_376:
                sections.append(sec_376)
            return sections
        
        # ASSAULT RELATED
        if any(word in question_lower for word in ["assault", "hurt", "grievous hurt"]):
            sec_351 = self.data_manager.search_by_number("351")  # Assault
            if sec_351:
                sections.append(sec_351)
            sec_323 = self.data_manager.search_by_number("323")  # Punishment for voluntarily causing hurt
            if sec_323:
                sections.append(sec_323)
            return sections
        
        # CRIMINAL TRESPASS
        if "criminal trespass" in question_lower:
            sec_441 = self.data_manager.search_by_number("441")  # Criminal trespass
            if sec_441:
                sections.append(sec_441)
            sec_447 = self.data_manager.search_by_number("447")  # Punishment
            if sec_447:
                sections.append(sec_447)
            return sections
        
        # KIDNAPPING
        if "kidnap" in question_lower:
            sec_363 = self.data_manager.search_by_number("363")  # Kidnapping
            if sec_363:
                sections.append(sec_363)
            sec_364 = self.data_manager.search_by_number("364")  # Kidnapping for murder
            if sec_364:
                sections.append(sec_364)
            return sections
        
        # DOWRY RELATED
        if "dowry" in question_lower:
            sec_304b = self.data_manager.search_by_number("304B")  # Dowry death
            if sec_304b:
                sections.append(sec_304b)
            sec_498a = self.data_manager.search_by_number("498A")  # Cruelty by husband
            if sec_498a:
                sections.append(sec_498a)
            return sections
        
        return sections
    
    def _find_relevant_sections(self, question: str, question_type: str) -> List[Dict[str, Any]]:
        """Find relevant IPC sections based on question type"""
        
        # FIRST: Check special cases for accurate legal answers
        special_results = self._get_special_cases(question)
        if special_results:
            return special_results
        
        if question_type == "section_number":
            # Extract section number
            numbers = re.findall(r'\b\d{1,3}\b', question)
            for num in numbers:
                if 1 <= int(num) <= 511:  # Valid IPC section range
                    section = self.data_manager.search_by_number(num)
                    if section:
                        return [section]
        
        elif question_type == "chapter":
            # Extract chapter number
            chapters = re.findall(r'chapter\s*(\d{1,2})', question)
            for chap_num in chapters:
                sections = self.data_manager.search_by_chapter(chap_num)
                if sections:
                    return sections[:5]  # Return first 5 sections
        
        # For all other types, use advanced search
        results = self.data_manager.advanced_search(question, limit=5)
        
        # If no results, try broader keyword search
        if not results:
            # Extract main keywords
            keywords = re.findall(r'\b[a-z]{4,}\b', question)
            for keyword in keywords:
                results = self.data_manager.search_by_keyword(keyword, limit=3)
                if results:
                    break
        
        return results
    
    def _generate_response(self, question: str, sections: List[Dict[str, Any]], question_type: str) -> Dict[str, Any]:
        """Generate chatbot response"""
        
        if not sections:
            return self._generate_no_results_response(question)
        
        # Prepare response based on question type
        if question_type == "section_number" and len(sections) == 1:
            return self._generate_section_detail_response(sections[0])
        
        elif question_type == "chapter":
            return self._generate_chapter_summary_response(sections, question)
        
        elif question_type == "definition":
            return self._generate_definition_response(sections, question)
        
        elif question_type == "punishment":
            return self._generate_punishment_response(sections, question)
        
        else:
            return self._generate_general_response(sections, question)
    
    def _generate_section_detail_response(self, section: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed response for specific section"""
        
        response_text = f"""
**IPC Section {section['number']}: {section['title']}**

**Description:**
{section['description']}

**Chapter {section['chapter']}: {section['chapter_title']}**

---
*Note: This is the legal provision as per Indian Penal Code. For specific legal advice, please consult a lawyer.*
"""
        
        return {
            "text": response_text.strip(),
            "sections": [section],
            "type": "section_detail",
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_chapter_summary_response(self, sections: List[Dict[str, Any]], question: str) -> Dict[str, Any]:
        """Generate summary of a chapter"""
        
        if not sections:
            return self._generate_no_results_response(question)
        
        chapter_num = sections[0]['chapter']
        chapter_title = sections[0]['chapter_title']
        
        # Count sections in chapter
        all_chapter_sections = self.data_manager.search_by_chapter(chapter_num)
        
        response_text = f"""
**Chapter {chapter_num}: {chapter_title}**

This chapter contains **{len(all_chapter_sections)} sections** covering {chapter_title.lower()}.

**Key Sections:**

"""
        
        # Add top 5 sections
        for i, section in enumerate(sections[:5], 1):
            response_text += f"{i}. **Section {section['number']}**: {section['title']}\n"
        
        if len(all_chapter_sections) > 5:
            response_text += f"\n... and {len(all_chapter_sections) - 5} more sections.\n"
        
        response_text += """
---
*To know details of a specific section, ask about the section number.*
"""
        
        return {
            "text": response_text.strip(),
            "sections": sections[:5],
            "type": "chapter_summary",
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_definition_response(self, sections: List[Dict[str, Any]], question: str) -> Dict[str, Any]:
        """Generate definition response"""
        
        response_text = f"""
Based on the Indian Penal Code:

"""
        
        for i, section in enumerate(sections[:3], 1):
            # Extract first sentence for definition
            desc = section['description']
            first_sentence = desc.split('.')[0] + '.' if '.' in desc else desc
            
            response_text += f"{i}. **{section['title']} (Section {section['number']})**: {first_sentence}\n\n"
        
        response_text += """
---
*These are legal definitions from IPC. For complete provisions, refer to specific sections.*
"""
        
        return {
            "text": response_text.strip(),
            "sections": sections[:3],
            "type": "definition",
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_punishment_response(self, sections: List[Dict[str, Any]], question: str) -> Dict[str, Any]:
        """Generate response about punishments - IMPROVED VERSION"""
        
        question_lower = question.lower()
        
        response_text = f"""
**Legal Provisions as per Indian Penal Code:**

"""
        
        # Filter to only punishment-related sections
        punishment_sections = []
        for section in sections:
            desc_lower = section['description'].lower()
            title_lower = section['title'].lower()
            
            # Check if this is actually about punishment
            punishment_keywords = ['punish', 'imprisonment', 'fine', 'death', 'liable', 'sentenced', 'penalty', 'shall be punished']
            
            # Check title for punishment keywords
            title_has_punishment = any(keyword in title_lower for keyword in ['punishment for', 'punishment of'])
            
            # Check description for punishment keywords
            desc_has_punishment = any(keyword in desc_lower for keyword in punishment_keywords)
            
            if title_has_punishment or desc_has_punishment:
                punishment_sections.append(section)
        
        # If no punishment sections found, show the most relevant
        if not punishment_sections:
            punishment_sections = sections[:3]
        
        for i, section in enumerate(punishment_sections[:3], 1):
            # Clean up the description to show punishment part
            desc = section['description']
            
            # Try to extract punishment part
            sentences = desc.split('.')
            punishment_sentences = []
            
            for sentence in sentences:
                sentence_lower = sentence.lower()
                if any(word in sentence_lower for word in ['punish', 'imprisonment', 'fine', 'liable', 'death', 'life imprisonment']):
                    punishment_sentences.append(sentence.strip())
            
            if punishment_sentences:
                # Take first 2 punishment sentences
                punishment_text = '. '.join(punishment_sentences[:2]) + '.'
            else:
                # Show first sentence if no punishment text found
                punishment_text = sentences[0] + '.' if sentences else desc[:200] + '...'
            
            response_text += f"{i}. **Section {section['number']} - {section['title']}**: {punishment_text}\n\n"
        
        # Add legal note based on query
        if "suicide" in question_lower:
            response_text += """
**Important Legal Note:** Attempt to commit suicide (Section 309) was decriminalized in India by the Mental Healthcare Act, 2017. However, abetment of suicide (Section 306) remains punishable.
"""
        elif "murder" in question_lower:
            response_text += """
**Note:** Murder (Section 302) is punishable with death or life imprisonment. The death penalty is awarded in 'rarest of rare' cases.
"""
        
        response_text += """
---
*Penalties vary based on offense severity and circumstances. Always refer to complete section text and consult a lawyer for specific cases.*
"""
        
        return {
            "text": response_text.strip(),
            "sections": punishment_sections[:3],
            "type": "punishment",
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_general_response(self, sections: List[Dict[str, Any]], question: str) -> Dict[str, Any]:
        """Generate general response for keyword searches"""
        
        response_text = f"""
I found these relevant IPC sections for **"{question}"**:

"""
        
        # Sort sections by relevance (section number for legal context)
        sorted_sections = sorted(sections, key=lambda x: int(x['number']))
        
        for i, section in enumerate(sorted_sections[:4], 1):
            # Shorten description for display
            desc = section['description']
            
            # Try to get the essence of the section
            sentences = desc.split('.')
            if len(sentences) > 1:
                short_desc = sentences[0] + '. ' + sentences[1] + '.'
            else:
                short_desc = desc[:250] + "..." if len(desc) > 250 else desc
            
            response_text += f"""
**{i}. Section {section['number']}: {section['title']}**
*Chapter {section['chapter']}: {section['chapter_title']}*
{short_desc}

"""
        
        if len(sections) > 4:
            response_text += f"\n*... and {len(sections) - 4} more relevant sections.*\n"
        
        response_text += """
---
*For detailed information on a specific section, ask about the section number.*
"""
        
        return {
            "text": response_text.strip(),
            "sections": sorted_sections[:4],
            "type": "general",
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_no_results_response(self, question: str) -> Dict[str, Any]:
        """Generate response when no sections found"""
        
        # Check if it might be a legal term we should know
        common_legal_terms = {
            "body shaming": "Try asking about 'Section 509 - Word or gesture intended to insult the modesty of a woman' or 'Section 354 - Assault or criminal force to woman with intent to outrage her modesty'",
            "cyber crime": "Try asking about 'IT Act 2000' or specific computer-related offenses",
            "domestic violence": "Try asking about 'Protection of Women from Domestic Violence Act 2005' or 'Section 498A - Husband or relative cruelty'",
            "sexual harassment": "Try asking about 'Section 354A - Sexual harassment'",
            "hit and run": "Try asking about 'Section 304A - Causing death by negligence' or motor vehicle laws",
        }
        
        suggestion = ""
        for term, advice in common_legal_terms.items():
            if term in question.lower():
                suggestion = f"\n**Note:** {advice}\n"
                break
        
        response_text = f"""
I couldn't find specific IPC sections for **"{question}"**.

**Suggestions:**
1. Try using specific section numbers (e.g., "IPC 302", "Section 420")
2. Use precise legal terminology (e.g., "murder", "theft", "cheating", "criminal trespass")
3. Ask about chapters (e.g., "Chapter 16 offenses")
4. Be more specific in your query
{suggestion}
**Example questions that work well:**
- "What is IPC section 302?"
- "Punishment for theft"
- "Define criminal trespass"
- "Sections in Chapter 17"

The Indian Penal Code has 575 sections across 23 chapters.
"""
        
        return {
            "text": response_text.strip(),
            "sections": [],
            "type": "no_results",
            "timestamp": datetime.now().isoformat()
        }
    
    def _add_to_history(self, question: str, response: Dict[str, Any], sections: List[Dict[str, Any]]):
        """Add interaction to conversation history"""
        
        history_entry = {
            "question": question,
            "response": response["text"][:500] + "..." if len(response["text"]) > 500 else response["text"],
            "sections_found": [s["number"] for s in sections[:3]],
            "type": response["type"],
            "timestamp": response["timestamp"]
        }
        
        self.conversation_history.append(history_entry)
        
        # Keep only last 10 conversations
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

# Helper function to create chatbot
def create_chatbot():
    """Create and initialize chatbot"""
    from utils.data_manager import create_data_manager
    
    data_manager = create_data_manager()
    chatbot = IPCChatbot(data_manager)
    return chatbot

# Test function
def test_chatbot():
    """Test the chatbot functionality"""
    print("🤖 Testing IPC Chatbot Engine...")
    
    try:
        chatbot = create_chatbot()
        
        test_questions = [
            "What is IPC section 302?",
            "Punishment for theft",
            "Chapter 16 offenses",
            "Define cheating",
            "What is criminal trespass?",
            "IPC 420",
            "What is punishment for suicide?",
            "Murder punishment",
            "Rape section"
        ]
        
        print(f"\n{'='*60}")
        print("TESTING CHATBOT WITH SAMPLE QUESTIONS")
        print(f"{'='*60}\n")
        
        for i, question in enumerate(test_questions, 1):
            print(f"Q{i}: {question}")
            print(f"{'-'*40}")
            
            response = chatbot.process_question(question)
            
            # Show summary
            print(f"Response Type: {response['type']}")
            print(f"Sections Found: {len(response['sections'])}")
            
            sections_list = [f"Section {s['number']}" for s in response['sections']]
            if sections_list:
                print(f"Sections: {', '.join(sections_list)}")
            
            # Show first 3 lines of response
            lines = response['text'].split('\n')
            line_count = 0
            for line in lines:
                if line.strip():
                    print(f"  {line}")
                    line_count += 1
                    if line_count >= 3:
                        break
            
            print(f"\n{'-'*60}\n")
        
        print(f"{'='*60}")
        print("✅ CHATBOT ENGINE TEST COMPLETE")
        print(f"{'='*60}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ CHATBOT TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_chatbot()