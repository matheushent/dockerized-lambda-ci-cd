"""Core module for HTTP response operations"""
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from pydantic import BaseModel
import fastapi


def error(detail):

    raise HTTPException(
        status_code=400,
        detail=detail,
        headers={
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        }
    )


def success(body):

    return JSONResponse(
        content=body,
        status_code=200,
        headers={
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        }
    )


def unauthorized(body):

    return JSONResponse(
        content=body,
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        headers={
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        }
    )


class OK(BaseModel):
    """
    A response that there was no error, when no other data is required
    """

    status: str = "ok"
    message: str = ""