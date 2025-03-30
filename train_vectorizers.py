"""
Training script for keyword extraction vectorizers.
This updates the vectorizers based on the enhanced keywords database.
"""
import os
import pickle
import pandas as pd
from pathlib import Path
import logging
import traceback

# Import the same fields used in the microservice
from ranking_features.utils import KeywordDataFrameFields
from ranking_features.keyword_extraction import extract_keywords, create_skills_job_vectorizers
from ranking_features.utils import detect_language

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('training')

# Define paths exactly as they are in routes.py
DATA_FOLDER_PATH = Path.cwd()/'data'
MODELS_FOLDER_PATH = Path.cwd()/'data'/'models'
KEYWORDS_FILE = 'global_keywords_df_enhanced.csv'

# Define keyword fields exactly as in routes.py
KEYWORD_FIELDS = KeywordDataFrameFields(
    id_field='KeywordID', 
    eng_name_field='KeywordNamesEN',
    fr_name_field='KeywordNamesFR', 
    idf_field='IDF')

def main():
    """Main training function"""
    # Create models directory if it doesn't exist
    os.makedirs(MODELS_FOLDER_PATH, exist_ok=True)
    
    # Create backup of any existing vectorizers
    existing_vectorizer_path = os.path.join(MODELS_FOLDER_PATH, 'vectorizers.pkl')
    if os.path.exists(existing_vectorizer_path):
        backup_path = os.path.join(MODELS_FOLDER_PATH, 'vectorizers.backup.pkl')
        logger.info(f"Creating backup of existing vectorizers at {backup_path}")
        import shutil
        shutil.copy(existing_vectorizer_path, backup_path)
    
    # Load the updated keywords dataframe
    logger.info(f"Loading keywords from {DATA_FOLDER_PATH}/{KEYWORDS_FILE}")
    try:
        # Load CSV and select only the columns we need - exclude GlobalID
        df = pd.read_csv(os.path.join(DATA_FOLDER_PATH, KEYWORDS_FILE))
        
        # Print the columns to verify
        logger.info(f"Original columns: {df.columns.tolist()}")
        
        # Keep only the columns needed for vectorization
        keyword_columns = [KEYWORD_FIELDS.id_field, KEYWORD_FIELDS.eng_name_field, 
                          KEYWORD_FIELDS.fr_name_field, KEYWORD_FIELDS.idf_field]
        
        # Verify all required columns exist
        for col in keyword_columns:
            if col not in df.columns:
                logger.error(f"Required column {col} not found in CSV!")
                return
        
        # Select only needed columns
        keyword_df = df[keyword_columns]
        
        # Handle the French names which are stored as stringified lists
        keyword_df[KEYWORD_FIELDS.fr_name_field] = keyword_df[KEYWORD_FIELDS.fr_name_field].apply(eval)
        
        # Explode the dataframe to handle multiple French names
        keyword_df = keyword_df.explode(KEYWORD_FIELDS.fr_name_field)
        
        # Print some stats about the keywords
        logger.info(f"Loaded {len(keyword_df)} keyword entries")
        logger.info(f"Unique keywords: {keyword_df[KEYWORD_FIELDS.id_field].nunique()}")
        logger.info(f"Final columns: {keyword_df.columns.tolist()}")
        
    except Exception as e:
        logger.error(f"Error loading keywords: {e}")
        logger.error(traceback.format_exc())
        return
    
    # Create vectorizers - this is the actual training step
    logger.info("Creating new vectorizers with updated keywords...")
    try:
        vectorizers = create_skills_job_vectorizers(keyword_df, KEYWORD_FIELDS)
        logger.info(f"Created vectorizers: {list(vectorizers.keys())}")
        
        # Save the updated vectorizers
        vectorizer_path = os.path.join(MODELS_FOLDER_PATH, 'vectorizers.pkl')
        logger.info(f"Saving vectorizers to {vectorizer_path}")
        with open(vectorizer_path, 'wb') as f:
            pickle.dump(vectorizers, f)
            
        logger.info("Vectorizers successfully trained and saved!")
        
    except Exception as e:
        logger.error(f"Error creating vectorizers: {e}")
        logger.error(traceback.format_exc())
        return
    
    # Test the new vectorizers with a sample job description
    try:
        logger.info("Testing new vectorizers with sample job description...")
        sample_job = "We are looking for a Machine Learning Engineer with experience in Generative AI and Large Language Models."
        
        # Detect language
        language = detect_language(sample_job)
        logger.info(f"Detected language: {language}")
        
        # Check if the vectorizer for this language exists
        if language in vectorizers:
            logger.info(f"Vectorizer for {language} exists!")
        else:
            logger.warning(f"No vectorizer found for language: {language}")
            
        logger.info("Vectorizer test complete!")
        
    except Exception as e:
        logger.error(f"Error testing vectorizers: {e}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    logger.info("Starting vectorizer training...")
    main()
    logger.info("Training process completed!")