"""
API Response Validation Utilities
Ensures API responses match expected schemas to prevent silent failures
"""

import logging
from typing import List, Any, Type
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)


class ResponseValidationError(Exception):
    """Raised when API response validation fails"""
    pass


def validate_api_response(data: Any, model_class: Type[BaseModel], operation_name: str) -> Any:
    """
    Validate that API response data matches the expected Pydantic model.
    
    Args:
        data: The data to validate
        model_class: The Pydantic model class to validate against
        operation_name: Name of the operation for logging
        
    Returns:
        The validated data
        
    Raises:
        ResponseValidationError: If validation fails
    """
    try:
        if isinstance(data, list):
            # Validate each item in the list
            validated_items = []
            for i, item in enumerate(data):
                try:
                    if isinstance(item, model_class):
                        validated_items.append(item)
                    else:
                        validated_item = model_class(**item) if isinstance(item, dict) else model_class(item)
                        validated_items.append(validated_item)
                except ValidationError as e:
                    logger.error(f"❌ Validation failed for item {i} in {operation_name}: {e}")
                    logger.error(f"🔍 Item data: {item}")
                    raise ResponseValidationError(f"Validation failed for item {i} in {operation_name}: {str(e)}")
            
            logger.info(f"✅ Successfully validated {len(validated_items)} items for {operation_name}")
            return validated_items
        else:
            # Validate single item
            if isinstance(data, model_class):
                logger.info(f"✅ Data already validated for {operation_name}")
                return data
            else:
                validated_data = model_class(**data) if isinstance(data, dict) else model_class(data)
                logger.info(f"✅ Successfully validated single item for {operation_name}")
                return validated_data
                
    except ValidationError as e:
        logger.error(f"❌ Validation failed for {operation_name}: {e}")
        logger.error(f"🔍 Data: {data}")
        raise ResponseValidationError(f"Validation failed for {operation_name}: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Unexpected error during validation for {operation_name}: {e}")
        raise ResponseValidationError(f"Unexpected validation error for {operation_name}: {str(e)}")


def validate_list_conversion(
    source_data: List[Any], 
    converted_data: List[Any], 
    operation_name: str,
    tolerance: float = 1.0
) -> None:
    """
    Validate that data conversion maintains expected ratios.
    
    Args:
        source_data: Original data before conversion
        converted_data: Data after conversion
        operation_name: Name of the operation for logging
        tolerance: Acceptable conversion ratio (1.0 = 100%, 0.9 = 90%)
        
    Raises:
        ResponseValidationError: If conversion ratio is below tolerance
    """
    source_count = len(source_data)
    converted_count = len(converted_data)
    
    if source_count == 0:
        if converted_count == 0:
            logger.info(f"✅ {operation_name}: Empty source and result - OK")
            return
        else:
            logger.warning(f"⚠️ {operation_name}: Empty source but non-empty result ({converted_count} items)")
            return
    
    conversion_ratio = converted_count / source_count
    
    if conversion_ratio < tolerance:
        error_msg = f"Conversion ratio {conversion_ratio:.2%} below tolerance {tolerance:.2%} for {operation_name}"
        logger.error(f"❌ {error_msg}")
        logger.error(f"🔍 Source: {source_count} items, Converted: {converted_count} items")
        raise ResponseValidationError(error_msg)
    
    logger.info(f"✅ {operation_name}: Conversion ratio {conversion_ratio:.2%} meets tolerance {tolerance:.2%}")


def log_validation_summary(operation_name: str, source_count: int, result_count: int) -> None:
    """Log a summary of validation results"""
    if source_count == 0 and result_count == 0:
        logger.info(f"📊 {operation_name}: No data to process - OK")
    elif source_count > 0 and result_count == 0:
        logger.critical(f"🚨 {operation_name}: CRITICAL - Found {source_count} items but converted 0!")
    elif source_count == result_count:
        logger.info(f"✅ {operation_name}: Perfect conversion - {result_count}/{source_count} items")
    else:
        ratio = result_count / source_count if source_count > 0 else 0
        logger.warning(f"⚠️ {operation_name}: Partial conversion - {result_count}/{source_count} items ({ratio:.2%})") 