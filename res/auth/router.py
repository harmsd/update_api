from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates


router = APIRouter(prefix='', tags=['API'])
templates = Jinja2Templates(directory='./frontend/auth/index.html')


@router.get('/')
async def get_main_page(request: Request):
    return templates.TemplateResponse(name='index.html', context={'request': request})

