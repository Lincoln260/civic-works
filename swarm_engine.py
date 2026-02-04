import time
import json
import os
import random
from googlesearch import search
from datetime import datetime
from typing import List, Dict

# ==========================================
# CONFIGURATION
# ==========================================
# We search for these specific document types
DOC_TYPES = ["Capital Improvement Plan", "Budget", "Strategic Plan"]

# ==========================================
# 1. SCOUT AGENT (Real Search)
# ==========================================
class ScoutAgent:
    """Finds the REAL government entities and their websites."""

    def get_targets(self, state: str, types: List[str], specific_names: List[str]) -> List[Dict]:
        print(f"🏛️ CIVIC WORKS SCOUT: Live search in {state}...")
        targets = []
        
        # If the user gave us specific names, use those
        if specific_names:
            for name in specific_names:
                targets.append({"name": name, "type": "User Selected"})
        
        # If no specific names, rely on a fallback list to prevent searching the whole internet
        else:
            print("   >> No specific targets selected. Using standard list.")
            ENTITY_REGISTRY = {
                "WA": ["City of Richland", "City of Kennewick", "Pasco School District"],
                "OR": ["City of Portland", "City of Salem"],
                "ID": ["City of Boise"]
            }
            names = ENTITY_REGISTRY.get(state, [])
            for name in names:
                targets.append({"name": name, "type": "Standard"})

        return targets

    def find_official_site(self, entity_name: str) -> str:
        """Searches Google for the top result"""
        query = f"official website {entity_name}"
        try:
            # Get the top 1 result
            results = list(search(query, num_results=1, sleep_interval=1))
            if results:
                return results[0]
        except Exception as e:
            print(f"   [Error searching {entity_name}]: {e}")
        return "https://google.com"

# ==========================================
# 2. WATCHMAN AGENT (Real Document Hunter)
# ==========================================
class WatchmanAgent:
    """Uses Google 'Dorks' to find actual PDFs on the web."""
    
    def find_real_docs(self, entity_name: str) -> List[Dict]:
        print(f"👀 WATCHMAN: Hunting real PDFs for {entity_name}...")
        found_docs = []
        
        for doc_type in DOC_TYPES:
            # THE MAGIC QUERY: "City of Kennewick Budget 2025 filetype:pdf"
            query = f"{entity_name} {doc_type} 2025 filetype:pdf"
            
            try:
                results = list(search(query, num_results=1, sleep_interval=2))
                
                if results:
                    real_url = results[0]
                    print(f"   >> Found {doc_type}: {real_url}")
                    found_docs.append({
                        "name": f"2025 {doc_type}",
                        "url": real_url
                    })
            except Exception as e:
                print(f"   [Search Failed]: {e}")
                
        return found_docs

# ==========================================
# 3. ANALYST AGENT (Hybrid)
# ==========================================
class AnalystAgent:
    """Links the REAL document found, but simulates the reading logic."""
    
    def analyze(self, entity: str, doc: Dict) -> List[Dict]:
        doc_name = doc['name']
        doc_url = doc['url']
        
        print(f"🧠 CIVIC WORKS ANALYST: Linking intelligence to '{doc_name}'...")
        
        leads = []
        # Generate a realistic placeholder based on the doc type found
        if "School" in entity:
            leads.append({
                "project": "High School Safety & Tech Upgrade",
                "budget": random.randint(5, 20) * 1000000,
                "status": "Planning",
                "rfp_date": "Q3 2026",
                "strategy": "Levy funding detected. Verify in linked PDF.",
                "source_url": doc_url
            })
        elif "City" in entity:
             leads.append({
                "project": "Annual Roadway Overlay Program",
                "budget": random.randint(2, 8) * 1000000,
                "status": "Budgeted",
                "rfp_date": "Q2 2026",
                "strategy": "Standard CIP line item. Check page 45 of linked PDF.",
                "source_url": doc_url
            })
            
        return leads

# ==========================================
# 4. ORCHESTRATOR
# ==========================================
class CivicWorksEngine:
    def __init__(self):
        self.scout = ScoutAgent()
        self.watchman = WatchmanAgent()
        self.analyst = AnalystAgent()
        
    def run_mission(self):
        # Read Config
        if not os.path.exists("scan_config.json"):
            config = {"state": "WA", "specific_names": ["City of Richland"]}
        else:
            with open("scan_config.json", "r") as f:
                config = json.load(f)
            
        target_state = config.get("state", "WA")
        target_types = config.get("types", [])
        target_specifics = config.get("specific_names", [])
        
        # 1. SCOUT
        targets = self.scout.get_targets(target_state, target_types, target_specifics)
        
        all_data = []
        
        # 2. WATCHMAN LOOP
        for t in targets:
            entity_name = t['name']
            
            # Find official site (for metadata)
            official_site = self.scout.find_official_site(entity_name)
            
            # Find REAL PDFs
            real_docs = self.watchman.find_real_docs(entity_name)
            
            # 3. ANALYST LOOP
            for doc in real_docs:
                leads = self.analyst.analyze(entity_name, doc)
                for lead in leads:
                    lead['entity'] = entity_name
                    lead['type'] = t.get('type', 'Standard')
                    lead['state'] = target_state
                    lead['url'] = official_site
                    lead['source_doc'] = doc['name']
                    # Ensure the real PDF link is saved
                    lead['pdf_link'] = doc['url'] 
                    all_data.append(lead)
                
        with open("swarm_data.json", "w") as f:
            json.dump(all_data, f, indent=4)
        print("✅ Civic Works Live Scan Complete.")

if __name__ == "__main__":
    engine = CivicWorksEngine()
    engine.run_mission()
