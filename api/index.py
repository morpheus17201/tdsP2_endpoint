from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import Optional, List
import httpx
import json

# from openai_client import get_openai_response
from file_handler import save_upload_file_temporarily

from base_logger import logger

# Import the functions you want to test directly
# from functions import *

app = FastAPI(title="IITM TDS Project 2")

# Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


endpoint_URL = r"http://4.186.56.117:8000"


@app.get("/")
@app.get("/api/")
async def health_check():
    return {"answer": "Get request working succesfully"}


@app.post("/")
@app.post("/api/")
async def process_question(
    # question: str = Form(...), file: Optional[UploadFile] = File(None)
    question: str = Form(...),
    file: List[UploadFile] = File([]),
):
    print(" " * 80)
    print("=" * 80)
    print(" " * 80)

    logger.info(f"Received question: {question}")
    logger.info(f"Number of files received: {len(file)}")
    try:
        # Save file temporarily if provided
        logger.info(f"Attempting to save the file")
        file_path_list = []
        temp_file_path = None
        files_dict = {}
        if file:
            logger.info(f"Detected that file has been received")
            if len(file) == 1:
                logger.info(f"Only single file received")
                logger.info(f"Attempting to save the file")
                temp_file_path = await save_upload_file_temporarily(file[0])
                logger.info(f"Successfully saved the file to {temp_file_path}")
                files_dict = {"file": open(temp_file_path, "rb")}

            elif len(file) > 1:
                file_path_list = []
                logger.info(f"Multiple files received")
                logger.info(f"Attempting to save multiple files")
                for counter, f in enumerate(file):
                    logger.info(f"Saving file {counter} of {len(file)}")
                    temp_file_path = await save_upload_file_temporarily(f)
                    logger.info(f"Saved succesfully to {temp_file_path}")
                    file_path_list.append(temp_file_path)
                    files_dict[f.filename] = open(temp_file_path, "rb")

        # Get answer from OpenAI
        with httpx.Client() as client:
            logger.info(f"Sending question & files to endpoint {endpoint_URL}")
            answer = client.post(
                url=endpoint_URL,
                files=files_dict,
                data={"question": question},
                timeout=60,
            )
            logger.info(f"Response status from endpoint:{answer.status_code}")
            answer.raise_for_status()
            logger.info(f"Answer received from endpoint:{answer.text}")

        # answer = await get_openai_response(question, temp_file_path)
        # if answer.text[0]== '"' or answer.text[0] == "'":
        #     final_answer= answer[1:-1]
        # return {"answer": answer}
        return answer.text

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # finally:
    #     for f in files_dict.values():
    #         f[1].close()


# if __name__ == "__main__":
#     import uvicorn

#     logger.info("Starting FastAPI server...")
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
#     # uvicorn.run("app", host="0.0.0.0", port=8000, reload=True)
