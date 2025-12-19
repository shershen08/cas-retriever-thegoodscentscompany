from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
import httpx
from bs4 import BeautifulSoup
import re
from typing import Optional

app = FastAPI(title="CAS Lookup API", version="1.0.0")


class CompoundRequest(BaseModel):
    """Request model for compound lookup"""
    compound_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Name of the chemical compound to search for"
    )
    
    @field_validator('compound_name')
    @classmethod
    def validate_compound_name(cls, v: str) -> str:
        """Validate that compound name is not empty after stripping whitespace"""
        v = v.strip()
        if not v:
            raise ValueError("Compound name cannot be empty or only whitespace")
        return v


class CASResponse(BaseModel):
    """Response model for CAS lookup"""
    compound_name: str
    cas_number: Optional[str]
    message: str


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
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch data from The Good Scents Company: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the request: {str(e)}"
        )


@app.post("/lookup-cas", response_model=CASResponse)
async def lookup_cas(request: CompoundRequest) -> CASResponse:
    """
    Lookup CAS number for a given compound name.
    
    Searches The Good Scents Company database for the compound and returns
    its CAS (Chemical Abstracts Service) number if found.
    """
    compound_name = request.compound_name.strip()
    
    cas_number = await fetch_cas_number(compound_name)
    
    if cas_number:
        return CASResponse(
            compound_name=compound_name,
            cas_number=cas_number,
            message="CAS number found successfully"
        )
    else:
        return CASResponse(
            compound_name=compound_name,
            cas_number=None,
            message="CAS number not found for the given compound"
        )


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
