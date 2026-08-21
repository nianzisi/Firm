from fastapi import APIRouter, Request, Form, Query
from starlette.responses import RedirectResponse

from web.commond import templates

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


@router.get("/search_land_all")
async def search_land_all():
    return action.search_land()


@router.post("/clear_land")
async def clear_land(land_id: int = Form(...)):
    return action.clear_land(land_id)


@router.post("/plan_seed")
async def plan_seed(seed_id: int = Form(...), land_id: int = Form(...)):
    return action.plan_seed(firm_id=land_id, seed_id=seed_id)


@router.post("/get_rewards")
async def get_rewards(land_id: int = Form(...)):
    ok, msg = action.reward(land_id=land_id)
    if ok:
        seed_id = action.land(land_id).get("land.plan_id")
        msg2 = action.get_rewards(seed_id)
        action.clear_land(land_id)
        return msg2[0], msg2[1]
    else:
        return False, msg[1]


@router.get("/back_bag")
async def back_bag():
    return action.search_bag()


@router.post("/throw_away")
async def throw_away(item_id: int = Form(...), amount: int = Form(...)):
    return action.subtract_bag_item(item_id=item_id, amount=amount)
