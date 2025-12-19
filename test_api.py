"""
Simple script to test the CAS Lookup API
Run the server first: uv run uvicorn main:app --reload
Then run this script: uv run python test_api.py
"""
import httpx
import asyncio


async def test_cas_lookup():
    """Test the CAS lookup endpoint with various compounds"""
    base_url = "http://localhost:8000"
    
    # Test cases
    test_compounds = [
        "formaldehyde",
        "lactic acid",
        "vitamin D2",
        "nonexistent compound xyz123"
    ]
    
    async with httpx.AsyncClient() as client:
        print("Testing CAS Lookup API\n" + "="*50)
        
        for compound in test_compounds:
            print(f"\nSearching for: {compound}")
            try:
                response = await client.post(
                    f"{base_url}/lookup-cas",
                    json={"compound_name": compound},
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                
                print(f"  CAS Number: {result['cas_number']}")
                print(f"  Message: {result['message']}")
                
            except httpx.HTTPError as e:
                print(f"  Error: {e}")
            except Exception as e:
                print(f"  Unexpected error: {e}")
        
        print("\n" + "="*50)
        
        # Test invalid input
        print("\nTesting invalid input (empty string):")
        try:
            response = await client.post(
                f"{base_url}/lookup-cas",
                json={"compound_name": "   "},
                timeout=30.0
            )
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.json()}")
        except Exception as e:
            print(f"  Error (expected): {e}")


if __name__ == "__main__":
    print("Make sure the server is running: uv run uvicorn main:app --reload\n")
    asyncio.run(test_cas_lookup())
