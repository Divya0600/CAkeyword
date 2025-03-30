from fastapi import APIRouter, HTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from dataclasses import fields
from typing import Union
import pandas as pd
import os
from pathlib import Path

from ranking_features.keyword_extraction import extract_keywords, create_skills_job_vectorizers, KeywordDataFrameFields
from ranking_features.utils import detect_language

from src.utils import find_pattern, build_keyword_output, KeywordExtractionInput, KeywordExtractionOutput
from src.logger import logger

router = APIRouter()

# At some point it might be relevant to export this to a database.
keyword_df = None
vectorizers = {}

DATA_FOLDER_PATH = Path.cwd()/'data'
KEYWORDS_FILE = 'global_keywords_df_enhanced.csv'

KEYWORD_FIELDS = KeywordDataFrameFields(
    id_field='KeywordID', eng_name_field='KeywordNamesEN',
    fr_name_field='KeywordNamesFR', idf_field='IDF')

@router.on_event("startup")
async def init():
    logger.info('Launching server')
    
    global keyword_df
    # Skill and job database should be encapsulated in database for easier update.
    # Dataframe creation
    try:
        logger.info(f'Loading keywords from {DATA_FOLDER_PATH}/{KEYWORDS_FILE}')
        df = pd.read_csv(os.path.join(DATA_FOLDER_PATH, KEYWORDS_FILE), 
                        converters={KEYWORD_FIELDS.fr_name_field: eval})
        
        # Select only the columns needed for vectorization (exclude GlobalID)
        columns_needed = [KEYWORD_FIELDS.id_field, KEYWORD_FIELDS.eng_name_field, 
                          KEYWORD_FIELDS.fr_name_field, KEYWORD_FIELDS.idf_field]
        
        keyword_df = df[columns_needed]
        keyword_df = keyword_df.explode(KEYWORD_FIELDS.fr_name_field)
        
        # Optional: Log information about the loaded keywords
        logger.info(f'Loaded {len(keyword_df)} keyword entries')
        logger.info(f'Unique keywords: {keyword_df[KEYWORD_FIELDS.id_field].nunique()}')
        logger.info(f'Columns in dataframe: {keyword_df.columns.tolist()}')
        
        logger.info('Creating vectorizers with the enhanced keyword database.')
        global vectorizers
        vectorizers = create_skills_job_vectorizers(keyword_df, KEYWORD_FIELDS)
        logger.info(f'Created vectorizers for languages: {list(vectorizers.keys())}')
        
    except Exception as e:
        logger.error(f'Error during initialization: {e}', exc_info=True)
        # Continue with empty vectorizers as a fallback
        vectorizers = {}

    logger.info('Initialization completed')

@router.post("/extract-keyword")
async def extract_keyword(extraction_input: KeywordExtractionInput):
    """Extract skill and job title keywords from job description

    Args:
        extraction_input (KeywordExtractionInput): Input data containing job description content

    Returns:
        KeywordExtractionOutput: Output with list of extracted keywords
    """
    logger.info('Extracting keywords')
    job_content = extraction_input.jobContent
    language = detect_language(job_content)
    logger.info(f'Detected language: {language}')
    
    # Handle missing language vectorizer
    if language not in vectorizers:
        logger.warning(f'No vectorizer for {language}, falling back to English')
        language = 'en'
        
        if language not in vectorizers:
            logger.error('No vectorizers available. Cannot extract keywords.')
            return KeywordExtractionOutput(keywords=[])

    try:
        keyword_ids = extract_keywords(docs=job_content, vectorizer=vectorizers[language])
    except Exception as e:
        logger.error('Error while extracting keywords.', exc_info=e)
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while extracting keywords",
        )

    keyword_lst = build_keyword_output(keywords_df=keyword_df, keyword_prefix='', keyword_ids=keyword_ids, df_fields=KEYWORD_FIELDS)

    if not len(keyword_lst):
        logger.warning('No keywords found.')
    else:
        logger.info(f'{len(keyword_lst)} keywords extracted.')

    return KeywordExtractionOutput(keywords=keyword_lst)

@router.get("/search-keywords")
async def suggestion(pattern: Union[str, None]):
    """Search keywords that match specified pattern

    Args:
        pattern (Union[str, None]): Pattern to use for search

    Returns:
        List[Keyword]: list of keywords that match the specified pattern
    """
    logger.info(f'Searching keywords with pattern: {pattern}')
    matching_ids = find_pattern(pattern=pattern, df_fields=KEYWORD_FIELDS, df=keyword_df)

    matching_keywords = build_keyword_output(keywords_df=keyword_df, keyword_prefix='', keyword_ids=matching_ids, df_fields=KEYWORD_FIELDS)

    if not len(matching_keywords):
        logger.warning('No keywords found.')
    else:
        logger.info(f'{len(matching_keywords)} keywords matched.')

    return matching_keywords

@router.get("/health")
async def health_check():
    """Endpoint to check if the application is alive."""
    return {"status": "alive"}

@router.get("/ready")
async def readiness_check():
    """Endpoint to check if the application is ready to receive requests."""

    if vectorizers != {}:
        return {"status": "ready"}
    else:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Application is not ready",
        )