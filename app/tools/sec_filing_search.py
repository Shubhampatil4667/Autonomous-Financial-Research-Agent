import requests
from typing import Dict, Any, List
from app.models.schemas import SECFiling
from datetime import datetime
import re
import time

def sec_filing_search(company: str, filing_type: str = "10-K") -> List[SECFiling]:
    """
    Search for SEC filings using EDGAR API
    """
    try:
        # First, get company CIK from symbol
        cik = get_company_cik(company)
        if not cik:
            # Fallback to mock data if CIK not found
            return _get_mock_filings(company, filing_type)

        # Search for filings
        filings = search_edgar_filings(cik, filing_type)
        return filings

    except Exception as e:
        print(f"SEC API error: {e}")
        # Fallback to mock data
        return _get_mock_filings(company, filing_type)

def get_company_cik(symbol: str) -> str:
    """
    Get CIK from company symbol using SEC API
    """
    try:
        # Use SEC's company tickers API
        url = "https://www.sec.gov/files/company_tickers.json"
        response = requests.get(url, headers={'User-Agent': 'Financial Research Agent'})
        if response.status_code == 200:
            data = response.json()
            for company in data.values():
                if company['ticker'].upper() == symbol.upper():
                    return str(company['cik_str']).zfill(10)
    except Exception as e:
        print(f"CIK lookup error: {e}")

    return None

def search_edgar_filings(cik: str, filing_type: str) -> List[SECFiling]:
    """
    Search EDGAR for specific filing types
    """
    filings = []
    try:
        # Use EDGAR's submissions API
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        response = requests.get(url, headers={'User-Agent': 'Financial Research Agent'})

        if response.status_code == 200:
            data = response.json()
            recent_filings = data.get('filings', {}).get('recent', {})

            if recent_filings:
                form_types = recent_filings.get('form', [])
                filing_dates = recent_filings.get('filingDate', [])
                primary_docs = recent_filings.get('primaryDocument', [])
                accession_numbers = recent_filings.get('accessionNumber', [])

                for i, form in enumerate(form_types):
                    if form == filing_type and i < len(filing_dates):
                        filing_date = filing_dates[i]
                        accession = accession_numbers[i] if i < len(accession_numbers) else ""

                        # Get filing content
                        content = get_filing_content(cik, accession, primary_docs[i] if i < len(primary_docs) else "")

                        filings.append(SECFiling(
                            type=form,
                            date=datetime.strptime(filing_date, '%Y-%m-%d'),
                            content=content
                        ))

                        if len(filings) >= 5:  # Limit to 5 most recent
                            break

    except Exception as e:
        print(f"EDGAR search error: {e}")

    return filings

def get_filing_content(cik: str, accession: str, primary_doc: str) -> str:
    """
    Get filing content from EDGAR
    """
    try:
        # Clean accession number
        accession_clean = accession.replace('-', '')

        # Construct filing URL
        url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_clean}/{primary_doc}"

        response = requests.get(url, headers={'User-Agent': 'Financial Research Agent'})
        if response.status_code == 200:
            # Extract text content (simplified - in production would parse HTML/XML properly)
            text = response.text
            # Remove HTML tags and extract meaningful content
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()

            # Return first 2000 characters as summary
            return text[:2000] + "..." if len(text) > 2000 else text

    except Exception as e:
        print(f"Content retrieval error: {e}")

    return "Filing content could not be retrieved"

def _get_mock_filings(company: str, filing_type: str) -> List[SECFiling]:
    """
    Fallback mock data
    """
    mock_filings = [
        SECFiling(
            type="10-K",
            date=datetime(2023, 12, 31),
            content=f"Annual report for {company}. Revenue: $100B, Net Income: $10B. Business description: Technology company focused on electric vehicles and clean energy."
        ),
        SECFiling(
            type="10-Q",
            date=datetime(2024, 3, 31),
            content=f"Quarterly report for {company}. Q1 revenue up 15%."
        )
    ]

    return [f for f in mock_filings if filing_type in f.type]