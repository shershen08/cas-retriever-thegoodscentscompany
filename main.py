from fastapi import FastAPI, HTTPException, Body
import httpx
from bs4 import BeautifulSoup
import re
from typing import Optional, Dict, Any

app = FastAPI(title="CAS Lookup API", version="1.0.0")


def validate_compound_name(compound_name: str) -> str:
    """Validate that compound name is not empty after stripping whitespace"""
    if not isinstance(compound_name, str):
        raise HTTPException(
            status_code=422,
            detail="compound_name must be a string"
        )

    compound_name = compound_name.strip()

    if not compound_name:
        raise HTTPException(
            status_code=422,
            detail="Compound name cannot be empty or only whitespace"
        )

    if len(compound_name) > 200:
        raise HTTPException(
            status_code=422,
            detail="Compound name must be 200 characters or less"
        )

    return compound_name


async def fetch_cas_number(compound_name: str) -> Optional[str]:
    """Fetch CAS number from The Good Scents Company website"""
    url = "https://www.thegoodscentscompany.com/allproc-1.html"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Search for the compound name in the page content
        # The page format is: CAS_NUMBER compound_name EC: ... Use(s): ...
        text_content = soup.get_text()

        # Normalize search term
        search_term = compound_name.lower().strip()

        # Pattern to match CAS number followed by compound name
        # CAS numbers are in format: XXX-XX-X or similar variations
        lines = text_content.split('\n')

        for i, line in enumerate(lines):
            if search_term in line.lower():
                # Try to find CAS number in the same line or nearby lines
                # CAS format: digits-digits-digit
                cas_pattern = r'\b\d{1,7}-\d{2}-\d\b'

                # Check current line and a few lines before
                search_range = lines[max(0, i-2):i+1]
                for search_line in search_range:
                    cas_match = re.search(cas_pattern, search_line)
                    if cas_match:
                        return cas_match.group(0)

        return None

    except httpx.HTTPError as e:
        error_msg = (
            f"Failed to fetch data from The Good Scents Company: {str(e)}"
        )
        raise HTTPException(
            status_code=503,
            detail=error_msg
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the request: {str(e)}"
        )


@app.post("/lookup-cas")
async def lookup_cas(
    request: Dict[str, Any] = Body(
        ...,
        description="Request body containing compound name",
        example={"compound_name": "vanillin"}
    )
) -> Dict[str, Any]:
    """
    Lookup CAS number for a given compound name.

    Searches The Good Scents Company database for the compound and returns
    its CAS (Chemical Abstracts Service) number if found.
    """
    if "compound_name" not in request:
        raise HTTPException(
            status_code=422,
            detail="compound_name field is required"
        )

    compound_name = validate_compound_name(request["compound_name"])

    cas_number = await fetch_cas_number(compound_name)

    if cas_number:
        return {
            "compound_name": compound_name,
            "cas_number": cas_number,
            "message": "CAS number found successfully"
        }
    else:
        return {
            "compound_name": compound_name,
            "cas_number": None,
            "message": "CAS number not found for the given compound"
        }


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "CAS Lookup API",
        "endpoints": {
            "/lookup-cas": "POST - Lookup CAS number for a compound",
            "/docs": "GET - Interactive API documentation"
        }
    }


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
