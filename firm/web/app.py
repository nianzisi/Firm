"""FastAPI Web 应用"""

from typing import Optional

import uvicorn
from fastapi import FastAPI, Form, Query, Request
from fastapi.responses import RedirectResponse


from seed.firm import Action
from web.play import router
from web.commond import templates

app = FastAPI(title="Firm")


app.include_router(router)

action = Action()


@app.get("/seeds")
def seeds_home(request: Request):
    return templates.TemplateResponse(
        request, "seeds_home.html", {"request": request, "title": "首页"}
    )


@app.post("/seeds/create_and_link")
async def create_and_link(
    plan_name: str = Form(...),
    plan_grade: int = Form(1),
    plan_price: Optional[int] = Form(None),
    mature_time: int = Form(...),
    mature_amount: int = Form(1),
    reward_name: str = Form(...),
    rewards_grade: int = Form(1),
    rewards_price: Optional[int] = Form(None),
):
    """
    创建种子与物品及其之间的联系
    :param plan_name: 种子名称
    :param plan_grade: 种子等级
    :param plan_price: 种子价值
    :param mature_time: 成长时间
    :param mature_amount: 成熟数量
    :param reward_name: 收获物名称
    :param rewards_grade: 收获物等级
    :param rewards_price: 收获物价值
    :return: 重定向
    """
    item_id = action.create_item(
        name=plan_name, grade=plan_grade, shopping_price=plan_price
    )
    seed_id = action.create_plan_seed(
        item_id=item_id, mature_amount=mature_amount, mature_time=mature_time
    )
    reward_id = action.create_item(
        name=reward_name, grade=rewards_grade, shopping_price=rewards_price
    )
    action.link_plan_rewards(plan_seed=seed_id, item_id=reward_id)
    return RedirectResponse("/seeds", status_code=303)


@app.post("/seeds/link")
async def link(seed_id: int = Form(...), reward_id: int = Form(...)):
    """
    关联种子和收获物
    :param seed_id: 种子id
    :param reward_id: 收获物id
    :return: 重定向
    """
    action.link_plan_rewards(plan_seed=seed_id, item_id=reward_id)
    return RedirectResponse("/seeds", status_code=303)


@app.post("/seeds/create")
async def create(
    item_id: int = Form(...), mature_time: int = Form(...), mature_amount: int = Form(1)
):
    """
    给物品赋予种子属性
    :param item_id: id
    :param mature_time: 时间
    :param mature_amount: 数量
    :return: 重定向
    """
    action.create_plan_seed(
        item_id=item_id, mature_time=mature_time, mature_amount=mature_amount
    )
    return RedirectResponse("/seeds", status_code=303)


@app.post("/seeds/create_items")
async def create_item(
    name: str = Form(...),
    grade: int = Form(1),
    shopping_price: Optional[int] = Form(None),
):
    """
    创建新物品
    :param name: 名称
    :param grade: 等级
    :param shopping_price: 价值
    :return: 重定向
    """
    action.create_item(name=name, grade=grade, shopping_price=shopping_price)
    return RedirectResponse("/seeds", status_code=303)


@app.get("/api/items/search")
def search_items(
    name: str = Query(""), grade: int = Query(None), shopping_price: int = Query(None)
):
    """
    搜说物品
    :param name: 名称
    :param grade: 等级
    :param shopping_price: 价值
    :return: 数据
    """
    return action.search_item(
        name=name or None,
        grade=grade,
        shopping_price=shopping_price,
    )


if __name__ == "__main__":
    uvicorn.run("app:app", host="localhost", port=8000, reload=True)
