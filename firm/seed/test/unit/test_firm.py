"""仅仅测试Action类，其余类的多是参数拼接与简单查询，基本都是IDE的识别错误(非业务逻辑错误)。不予单元测试"""
from pytest_mock import MockerFixture

from seed.firm import Action

action = Action()


def test_plan_plan(mocker):
    mocker.patch.object(action, "plan_seed")

    mocker.patch.object(action, "land_free", return_value=False)
    success, mes = action.plan_plan(plan_id=1, firm_id=2)
    assert success is False
    assert "土地不存在|土地已种植" in mes

    mocker.patch.object(action, "land_free", return_value=True)
    mocker.patch.object(action, "seed_empty", return_value=False)
    success, mes = action.plan_plan(plan_id=1, firm_id=2)
    assert success is False
    assert "种子不存在" in mes

    mocker.patch.object(action, "seed_empty", return_value=True)
    success, mes = action.plan_plan(plan_id=1, firm_id=2)
    assert success is True
    assert "种植" in mes
    assert "成功" in mes


def test_reward(mocker):
    mocker.patch.object(action, "land_free", return_value=True)
    success, mes = action.reward(land_id=1)
    assert success is False
    assert "土地空闲" in mes

    mocker.patch.object(action, "land_free", return_value=False)
    test_dic = {"land.plan_time": None}
    mocker.patch.object(action, "land", return_value=test_dic)
    success, mes = action.reward(land_id=1)
    assert success is False
    assert "时间错误" in mes

    test_dic = {"land.plan_time": 3}
    mocker.patch.object(action, "land", return_value=test_dic)
    mocker.patch("time.time", return_value=2)
    success, mes = action.reward(land_id=1)
    assert success is False
    assert "未成熟" in mes

    test_dic = {"land.plan_time": 1}
    mocker.patch.object(action, "land", return_value=test_dic)
    mocker.patch("time.time", return_value=2)
    success, mes = action.reward(land_id=1)
    assert success is True
    assert "可收获" in mes


def test_get_rewards(mocker):
    test_list = []
    mocker.patch.object(action, "search_rewards", return_value=test_list)
    success, mes = action.get_rewards(seed_id=1)

    assert success is False
    assert "该物品不存在" in mes

    test_list = [[1, 2, 0.5], [2, 4, 0.1], [3, 6, 0.9]]
    mocker.patch.object(action, "search_rewards", return_value=test_list)
    mocker.patch.object(action, "add_bag_item", return_value=False)
    mocker.patch("random.random", return_value=0.6)

    success, mes = action.get_rewards(seed_id=1)

    assert success is False
    assert "添加失败" in mes

    mock_func = mocker.patch.object(action, "add_bag_item", return_value=True)
    mocker.patch("random.random", return_value=0.6)

    success, mes = action.get_rewards(seed_id=1)

    assert success is True
    assert "添加成功" in mes
    assert mock_func.call_count == 1
