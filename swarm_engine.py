import time
import json
import os
import random
from datetime import datetime, timedelta
from typing import List, Dict

# ==========================================
# CONFIGURATION
# ==========================================
MOCK_AI_MODE = True 

# ==========================================
# 1. CIVIC WORKS SCOUT (Discovery)
# ==========================================
class ScoutAgent:
    """Finds government entities based on State & Type."""
    
    ENTITY_REGISTRY = {
        "WA": {
            "School District": ["Kennewick School District", "Pasco School District", "Seattle Public Schools"],
            "City": ["City of Richland", "City of Kennewick", "City of Bellevue", "City of Renton"],
            "Port": ["Port of Benton", "Port of Seattle", "Port of Tacoma"],
            "County": ["Benton County", "King County"]
        },
        "OR": {
            "School District": ["Portland Public Schools", "Beaverton School District"],
            "City": ["City of Portland", "City of Salem", "City of Bend"],
            "Port": ["Port of Portland", "Port of Coos Bay"],
            "County": ["Multnomah County"]
        },
        "ID": {
            "School District": ["Boise School District", "West Ada School District"],
            "City": ["City of Boise", "City of Meridian"],
            "County": ["Ada County"]
        }
    }

    def get_targets(self, state: str, types: List[str]) -> List[Dict]:
        print(f"🏛️ CIVIC WORKS SCOUT: Surveying {state} for {types}...")
        targets = []
        if state in self.ENTITY_REGISTRY:
            for t in types:
                names = self.ENTITY_REGISTRY[state].get(t, [])
                for name in names:
                    targets.append({"name": name, "type": t})
        return targets

    def find_url(self, entity_name: str) -> str:
        slug = entity_name.lower().replace(" ", "").replace("cityof", "")
        return f"https://www.{slug}.gov"

# ==========================================
# 2. WATCHMAN AGENT (Crawler)
# ==========================================
class WatchmanAgent:
    """Checks for new documents and files."""
    
    def scan_for_docs(self, entity_name: str) -> List[str]:
        print(f"👀 WATCHMAN: Scanning {entity_name} document center...")
        time.sleep(0.1) 
        
        if "School" in entity_name:
            return ["2026-2031_Capital_Facilities_Plan.pdf", "Board_Minutes_Feb_2026.pdf"]
        elif "Port" in entity_name:
            return ["2026_Strategic_Business_Plan.pdf"]
        else:
            return ["2026_Transportation_Improvement_Plan.pdf"]

# ==========================================
# 3. ANALYST AGENT (Intelligence)
# ==========================================
class AnalystAgent:
    """Extracts budget, dates, and strategy from docs."""
    
    def analyze(self, entity: Dict, doc_name: str) -> List[Dict]:
        name = entity['name']
        e_type = entity['type']
        
        print(f"🧠 CIVIC WORKS ANALYST: Processing '{doc_name}'...")
        
        leads = []
        
        if e_type == "School District":
            leads.append({
                "project": f"{name} High School Modernization",
                "budget": random.randint(40, 150) * 1000000,
                "status": "Planning (Bond Prep)",
                "rfp_date": "Q1 2027",
                "strategy": "Bond vote expected next Feb. Vertical build. Secure Architect relationship now."
            })
        elif e_type == "City":
            leads.append({
                "project": f"{name} Main St. Resurfacing",
                "budget": random.randint(2, 8) * 1000000,
                "status": "Budgeted",
                "rfp_date": "Q2 2026",
                "strategy": "Federally funded overlay. Good for mid-size civil GC."
            })
        elif e_type == "Port":
            leads.append({
                "project": f"{name} Terminal Electrification",
                "budget": 12500000,
                "status": "Design",
                "rfp_date": "Q3 2026",
                "strategy": "Heavy electrical & utility work. Grant funded."
            })
        elif e_type == "County":
             leads.append({
                "project": f"{name} Justice Center Expansion",
                "budget": 45000000,
                "status": "Feasibility Study",
                "rfp_date": "2028",
                "strategy": "Long term lead. Monitor Council minutes for design approval."
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
        if not os.path.exists("scan_config.json"):
            config = {"state": "WA", "types": ["City", "School District"]}
        else:
            with open("scan_config.json", "r") as f:
                config = json.load(f)
            
        target_state = config.get("state", "WA")
        target_types = config.get("types", ["City"])
        
        targets = self.scout.get_targets(target_state, target_types)
        all_data = []
        
        for t in targets:
            url = self.scout.find_url(t['name'])
            docs = self.watchman.scan_for_docs(t['name'])
            
            for doc in docs:
                leads = self.analyst.analyze(t, doc)
                for lead in leads:
                    lead['entity'] = t['name']
                    lead['type'] = t['type']
                    lead['state'] = target_state
                    lead['url'] = url
                    lead['source_doc'] = doc
                    all_data.append(lead)
                
        with open("swarm_data.json", "w") as f:
            json.dump(all_data, f, indent=4)
        print("✅ Civic Works Scan Complete.")

if __name__ == "__main__":
    engine = CivicWorksEngine()
    engine.run_mission()