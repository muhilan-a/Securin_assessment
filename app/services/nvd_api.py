import time
import requests
from time import sleep
import json
from datetime import datetime 

API_KEY = "5204544b-4363-4bac-b53f-cde286d9b562"  

def fetch_cves(start_index=0, results_per_page=50):
    headers = {}
    if API_KEY:
        headers["apiKey"] = API_KEY

    params = {
        "startIndex": start_index,
        "resultsPerPage": results_per_page
    }

    try:
        response = requests.get(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        
        print("API Response Keys:", data.keys())
        
      
        with open(f"api_response_{start_index}.json", "w") as f:
            json.dump(data, f, indent=2)
            
        return data
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {str(e)}")
        return None
    except Exception as e:
        print(f"General Error: {str(e)}")
        return None

time.sleep(6)  
from datetime import datetime

from datetime import datetime
import json

def parse_cve_data(cve_item):
    try:
        cve_data = cve_item.get('cve', {})
        
        if not cve_data:
            print("Skipping: Missing 'cve' object")
            return None

       
        cve_id = cve_data.get('id')
        if not cve_id:
            print("Skipping: Missing CVE ID")
            return None

        
        published_str = cve_data.get('published')
        last_modified_str = cve_data.get('lastModified')

        try:
            published = datetime.strptime(published_str, "%Y-%m-%dT%H:%M:%S.%f") if published_str else None
            last_modified = datetime.strptime(last_modified_str, "%Y-%m-%dT%H:%M:%S.%f") if last_modified_str else None
        except ValueError as e:
            print(f"Skipping {cve_id}: Invalid date format - {str(e)}")
            return None

        
        if not all([published, last_modified]):
            print(f"Skipping {cve_id}: Missing required date fields")
            return None

        descriptions = cve_data.get('descriptions', [])
        description = next(
            (d['value'] for d in descriptions if d.get('lang') == 'en'),
            'No description available' 
        )

        metrics = cve_data.get('metrics', {})
        cvss_v2 = metrics.get('cvssMetricV2', [{}])[0].get('cvssData', {})
        cvss_v3 = metrics.get('cvssMetricV3', [{}])[0].get('cvssData', {})

        cpe_matches = []
        for config in cve_data.get('configurations', []):
            for node in config.get('nodes', []):
                for cpe_match in node.get('cpeMatch', []):
                    cpe_matches.append({
                        'criteria': cpe_match.get('criteria'),
                        'vulnerable': cpe_match.get('vulnerable')
                    })

        
       
        status = cve_data.get('vulnStatus') or cve_data.get('cveMetadata', {}).get('vulnStatus', 'Unknown')


        return {
            "id": cve_id,
            "published": published,
            "last_modified": last_modified,
            "description": description,
            "source_Identifier": cve_data.get('sourceIdentifier'),
            "base_score_v2": cvss_v2.get('baseScore'),
            "base_score_v3": cvss_v3.get('baseScore'),
            "cvss_v2_vector": cvss_v2.get('vectorString'),
            "cvss_v2_severity": cvss_v2.get('baseSeverity'),
            "cvss_v3_vector": cvss_v3.get('vectorString'),
            "cvss_v3_severity": cvss_v3.get('baseSeverity'),
            "exploitability_score": metrics.get('cvssMetricV2', [{}])[0].get('exploitabilityScore'),
            "impact_score": metrics.get('cvssMetricV2', [{}])[0].get('impactScore'),
            "cpe_list": cpe_matches,
            "status":  status
           
        }
    except Exception as e:
        print(f"Parse error for {cve_id if 'cve_id' in locals() else 'unknown'}: {str(e)}")
        return None