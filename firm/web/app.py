"""FastAPI Web 应用"""
from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import pathlib
from seed.firm import Action

app = FastAPI(title="Firm")
templates = Jinja2Templates(
    directory=str(pathlib.Path(__file__).resolve().parent / "templates")
)
action = Action()


@app.get("/seeds")
def seeds_home(request: Request):
    return templates.TemplateResponse("seeds_home",
                                      {"request": request, "title": "首页"})


@app.post("/seeds/create_and_link")
async def create_and_link(plan_name: str = Form(...),
                          plan_grade: int = Form(1),
                          mature_time: int = Form(...),
                          mature_amount: int = Form(1),
                          comment: str = Form("无备注"),
                          reward_name: str = Form(...),
                          rewards_grade: int = Form(1)
                          ):
    seed_id = action.create_plan_seed(plan_name=plan_name,
                                      plan_grade=plan_grade,
                                      mature_time=mature_time,
                                      mature_amount=mature_amount,
                                      comment=comment)
    reward_id = action.create_plan_rewards(reward_name=reward_name,
                                           rewards_grade=rewards_grade)
    action.link_plan_rewards(plan_seed=seed_id, rewards=reward_id)
    return RedirectResponse("/seeds", status_code=303)


@app.post("/seeds/link")
async def link(seed_id: int = Form(...),
               reward_id: int = Form(...)):
    action.link_plan_rewards(plan_seed=seed_id, rewards=reward_id)
    return RedirectResponse("/seeds", status_code=303)


@app.post("/seeds/create")
async def create(plan_name: str = Form(...),
                 plan_grade: int = Form(1),
                 mature_time: int = Form(...),
                 mature_amount: int = Form(1),
                 comment: str = Form("无备注"),
                 ):
    action.create_plan_seed(plan_name=plan_name,
                            plan_grade=plan_grade,
                            mature_time=mature_time,
                            mature_amount=mature_amount,
                            comment=comment)
    return RedirectResponse("/seeds", status_code=303)


@app.post("/seeds/create_rewards")
async def create_rewards(reward_name: str = Form(...),
                         rewards_grade: int = Form(1)):
    action.create_plan_rewards(reward_name=reward_name,
                               rewards_grade=rewards_grade)
    return RedirectResponse("/seeds", status_code=303)
