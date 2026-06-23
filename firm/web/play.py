from fastapi import APIRouter, Request, Form, Query
from starlette.responses import RedirectResponse

from web.app import templates

from seed.firm import Action

router = APIRouter(prefix="/firm", tags=["游玩"])

action = Action()


@router.get("")
def farm_page(request: Request):
    return templates.TemplateResponse(request, "firm.html", {})


@router.post("/creat_land")
async def creat_land():
    action.create_land()
    return RedirectResponse("/", status_code=303)


@router.get("/search_land")
async def search_land(land_id: int = Query(...)):
    msg = action.land(land_id)
    return msg


@router.post("/plan_seed")
async def plan_seed(seed_id: int = Form(...),
                    land_id: int = Form(...)):
    return action.plan_seed(firm_id=land_id, seed_id=seed_id)


@router.post("/clear_land")
async def clear_land(land_id: int = Form(...)):
    return action.clear_land(land_id)


@router.post("/get_rewards")
async def get_rewards(land_id: int = Form(...)):
    return action.get_rewards(land_id)
