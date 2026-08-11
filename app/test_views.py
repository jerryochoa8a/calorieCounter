# pip install pytest
# pip install pytest-mock
# pip install pytest-django
# created "pytest.ini" at the same level as manage.py
## --> Note: this connects the testing to our django project and its funtionality like talking to models and view functions 
from app.views import calculateTargetCalories, GetfoodInfo, new_user # shorten name ref CTC
import pytest



def test_CTC(mocker): #Note that pytest funtions need to start with "test_"
    # mocker.Mock() makes a fake/temp object that we can test
    profile = mocker.Mock()
    profile.sex = "Female"
    profile.weight = 70
    profile.height = 165
    profile.age = 25
    profile.activityLevels = "Sedentary"
    profile.fitnessGoals = "Lose Weight"

    # this acts like a fake DB for the fake/temp object
    mocker.patch(
        "app.views.Profile.objects.get",
        return_value=profile
    )

    # Normaly takes (request, profile_id)
    result = calculateTargetCalories(None, 1) 
    assert result == pytest.approx(1234.3)



# test foodAPI
def test_foodAPI(mocker, settings):
    settings.calorieninjas_APIKey = "x/emm0VcKlOoc+mRMURCIA==AzrAJ19yrPQ2s7eX" # API Key
    # Fake request
    request = mocker.Mock()
    request.POST = {
        "amount": "1 ",
        "food": "egg"
    }

    # Fake html render
    mock_render = mocker.patch(
        "app.views.render"
    )
    GetfoodInfo(request)

    foodInfo = mock_render.call_args[0][2]
    # the results check
    assert foodInfo["name"] == "egg"
    assert foodInfo["calories"] > 60
    assert foodInfo["protein"] >= 0
    assert foodInfo["carbs"] >= 0
    assert foodInfo["fiber"] >= 0
    assert foodInfo["fat"] >= 0

    