from fastapi import FastAPI, status, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import re

from model import (
    AnalysisRequest,
    AnalysisResponse,
    StringAnalysis,
    SessionLocal,
    AnalysisProperties,
)
from utils.analyzer import analyze_string
from database import create_db

app = FastAPI()

# Create the database tables
create_db()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/strings", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
def create_string(request: AnalysisRequest, db: Session = Depends(get_db)):
    if not isinstance(request.value, str):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid data type for 'value', must be a string",
        )

    properties = analyze_string(request.value)
    
    db_string = db.query(StringAnalysis).filter(StringAnalysis.sha256_hash == properties.sha256_hash).first()
    if db_string:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="String already exists in the system")

    new_analysis = StringAnalysis(
        id=properties.sha256_hash,
        value=request.value,
        length=properties.length,
        is_palindrome=properties.is_palindrome,
        unique_characters=properties.unique_characters,
        word_count=properties.word_count,
        sha256_hash=properties.sha256_hash,
        character_frequency_map=properties.character_frequency_map,
    )
    db.add(new_analysis)
    db.commit()
    db.refresh(new_analysis)

    return AnalysisResponse(
        id=new_analysis.id,
        value=new_analysis.value,
        properties=properties,
        created_at=new_analysis.created_at,
    )

@app.get("/strings/{string_value}", response_model=AnalysisResponse)
def get_string(string_value: str, db: Session = Depends(get_db)):
    db_string = db.query(StringAnalysis).filter(StringAnalysis.value == string_value).first()
    if not db_string:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="String does not exist in the system")

    properties = AnalysisProperties(
        length=db_string.length,
        is_palindrome=db_string.is_palindrome,
        unique_characters=db_string.unique_characters,
        word_count=db_string.word_count,
        sha256_hash=db_string.sha256_hash,
        character_frequency_map=db_string.character_frequency_map,
    )
    return AnalysisResponse(
        id=db_string.id,
        value=db_string.value,
        properties=properties,
        created_at=db_string.created_at,
    )

@app.get("/strings")
def get_all_strings(
    is_palindrome: Optional[bool] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    word_count: Optional[int] = None,
    contains_character: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(StringAnalysis)
    filters_applied = {}

    if is_palindrome is not None:
        query = query.filter(StringAnalysis.is_palindrome == is_palindrome)
        filters_applied["is_palindrome"] = is_palindrome
    if min_length is not None:
        query = query.filter(StringAnalysis.length >= min_length)
        filters_applied["min_length"] = min_length
    if max_length is not None:
        query = query.filter(StringAnalysis.length <= max_length)
        filters_applied["max_length"] = max_length
    if word_count is not None:
        query = query.filter(StringAnalysis.word_count == word_count)
        filters_applied["word_count"] = word_count
    if contains_character is not None:
        if len(contains_character) != 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="contains_character must be a single character")
        query = query.filter(StringAnalysis.value.contains(contains_character))
        filters_applied["contains_character"] = contains_character

    results = query.all()
    
    data = [
        {
            "id": res.id,
            "value": res.value,
            "properties": {
                "length": res.length,
                "is_palindrome": res.is_palindrome,
                "unique_characters": res.unique_characters,
                "word_count": res.word_count,
                "sha256_hash": res.sha256_hash,
                "character_frequency_map": res.character_frequency_map,
            },
            "created_at": res.created_at,
        }
        for res in results
    ]

    return {"data": data, "count": len(data), "filters_applied": filters_applied}

@app.get("/strings/filter-by-natural-language")
def filter_by_natural_language(query: str, db: Session = Depends(get_db)):
    parsed_filters = {}
    original_query = query.lower()

    if "single word" in original_query:
        parsed_filters["word_count"] = 1
    if "palindromic" in original_query:
        parsed_filters["is_palindrome"] = True
    
    length_match = re.search(r"longer than (\d+) characters", original_query)
    if length_match:
        parsed_filters["min_length"] = int(length_match.group(1)) + 1

    contains_match = re.search(r"containing the letter (\w)", original_query)
    if contains_match:
        parsed_filters["contains_character"] = contains_match.group(1)

    if not parsed_filters:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to parse natural language query")

    # This is a simplified version, a more robust solution would use a proper NLP library
    api_query = db.query(StringAnalysis)
    if "word_count" in parsed_filters:
        api_query = api_query.filter(StringAnalysis.word_count == parsed_filters["word_count"])
    if "is_palindrome" in parsed_filters:
        api_query = api_query.filter(StringAnalysis.is_palindrome == True)
    if "min_length" in parsed_filters:
        api_query = api_query.filter(StringAnalysis.length >= parsed_filters["min_length"])
    if "contains_character" in parsed_filters:
        api_query = api_query.filter(StringAnalysis.value.contains(parsed_filters["contains_character"]))

    results = api_query.all()
    data = [
        {
            "id": res.id,
            "value": res.value,
            "properties": {
                "length": res.length,
                "is_palindrome": res.is_palindrome,
                "unique_characters": res.unique_characters,
                "word_count": res.word_count,
                "sha256_hash": res.sha256_hash,
                "character_frequency_map": res.character_frequency_map,
            },
            "created_at": res.created_at,
        }
        for res in results
    ]

    return {
        "data": data,
        "count": len(data),
        "interpreted_query": {
            "original": query,
            "parsed_filters": parsed_filters,
        },
    }


@app.delete("/strings/{string_value}", status_code=status.HTTP_204_NO_CONTENT)
def delete_string(string_value: str, db: Session = Depends(get_db)):
    db_string = db.query(StringAnalysis).filter(StringAnalysis.value == string_value).first()
    if not db_string:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="String does not exist in the system")

    db.delete(db_string)
    db.commit()
    return
