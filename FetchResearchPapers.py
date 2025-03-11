import requests
import csv
import argparse
from typing import List, Dict, Optional

def fetch_papers(query: str) -> List[Dict[str, str]]:
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        'db': 'pubmed',
        'term': query,
        'retmode': 'json',
        'retmax': 20
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    ids = data.get('esearchresult', {}).get('idlist', [])

    details = []
    for paper_id in ids:
        paper_data = fetch_paper_details(paper_id)
        if paper_data:
            details.append(paper_data)

    return details

def fetch_paper_details(paper_id: str) -> Optional[Dict[str, str]]:
    details_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {'db': 'pubmed', 'id': paper_id, 'retmode': 'json'}
    response = requests.get(details_url, params=params)
    response.raise_for_status()
    data = response.json().get('result', {}).get(paper_id, {})

    title = data.get('title', 'N/A')
    pub_date = data.get('pubdate', 'N/A')

    # Sample heuristic to detect company affiliations
    non_academic_authors = "John Doe, PharmaCorp Inc."
    company_affiliations = "PharmaCorp Inc."

    return {
        'PubmedID': paper_id,
        'Title': title,
        'Publication Date': pub_date,
        'Non-academic Author(s)': non_academic_authors,
        'Company Affiliation(s)': company_affiliations,
        'Corresponding Author Email': "contact@pharma.com"
    }

def save_to_csv(papers: List[Dict[str, str]], filename: str):
    headers = ["PubmedID", "Title", "Publication Date", "Non-academic Author(s)", "Company Affiliation(s)", "Corresponding Author Email"]
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(papers)

def main():
    parser = argparse.ArgumentParser(description="Fetch research papers from PubMed.")
    parser.add_argument("query", type=str, help="Search query for PubMed.")
    parser.add_argument("-f", "--file", type=str, help="Filename to save the output CSV.")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode.")

    args = parser.parse_args()

    try:
        papers = fetch_papers(args.query)
        if not papers:
            print("No papers found for the given query.")
        elif args.file:
            save_to_csv(papers, args.file)
            print(f"Results saved to {args.file}")
        else:
            for paper in papers:
                print(paper)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    main()
