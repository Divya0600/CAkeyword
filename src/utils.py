import pandas as pd
from pydantic import BaseModel
from typing import Union, Iterable, List
import os
from ranking_features.utils import KeywordDataFrameFields
from ranking_features.keyword_extraction import ids2text


class KeywordName(BaseModel):
    en: str
    fr: str


class KeywordExtractionInput(BaseModel):
    jobContent: str


class Keyword(BaseModel):
    id:  str
    name: KeywordName


class KeywordExtractionOutput(BaseModel):
    keywords: List[Keyword]


def find_pattern(pattern: str, df: pd.DataFrame, df_fields: KeywordDataFrameFields) -> Iterable[int]:
    """Finds element in a Dataframe that match the provided pattern.

    Args:
        pattern (str): Pattern to search for. Search is case independant.
        df (pd.DataFrame): DataFrame containing the data.
        df_fields (KeywordDataFrameFields): Structure to identify columns in the dataframe.

    Returns:
        Iterable[int]: List of keyword IDs that match the pattern
    """
    matching_ids = df[
        df[df_fields.eng_name_field].str.contains(pattern, case=False, regex=False) |
        df[df_fields.fr_name_field].str.contains(pattern, case=False, regex=False)][df_fields.id_field].unique()
    return matching_ids


def build_keyword_output(keywords_df: pd.DataFrame, keyword_prefix: str,
        keyword_ids: Iterable[int], df_fields: KeywordDataFrameFields) -> List[Keyword]:
    """Build a formatted output for a list of keywords with names in both languages.

    Args:
        keywords_df (pd.DataFrame): Keyword dataframe.
        keyword_prefix (str): Prefix to attach to keyword IDs
        keyword_ids (Iterable[int]): List of IDs of the keyword that should be returned.
        df_fields (KeywordDataFrameFields): Structure to identify columns in the dataframe.

    Returns:
        List[Keyword]: List of formatted keywords
    """

    keyword_names_en = ids2text(keyword_ids, keywords_df, df_fields, language='en')
    keyword_names_fr = ids2text(keyword_ids, keywords_df, df_fields, language='fr')

    keyword_list = [
        Keyword(id=f'{keyword_prefix}{id}', name=KeywordName(en=name_en, fr=name_fr))
        for id, name_en, name_fr in zip(keyword_ids, keyword_names_en, keyword_names_fr)
    ]

    return keyword_list
