import os
import shutil
import tempfile
from fastapi import UploadFile

from api.base_logger import logger


async def save_upload_file_temporarily(upload_file: UploadFile) -> str:
    """
    Save an upload file temporarily and return the path to the saved file.
    """
    logger.info(f"Saving file temporarily: {upload_file.filename}")
    try:
        # Create a temporary directory
        logger.info(f"Creating temporary directory")
        temp_dir = tempfile.mkdtemp()

        # Create a path to save the file
        file_path = os.path.join(temp_dir, upload_file.filename)
        logger.info(f"File path: {file_path}")

        # Save the file
        logger.info(f"Saving file to {file_path}")
        with open(file_path, "wb") as f:
            contents = await upload_file.read()
            f.write(contents)
        logger.info(f"File saved successfully")
        # Return the path to the saved file
        return file_path
    except Exception as e:
        # Clean up the temporary directory if an error occurs
        logger.error(f"Error saving file: {e}")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        raise e
