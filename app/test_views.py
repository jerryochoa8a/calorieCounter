# pip install pytest
# pip install pytest-mock
# pip install pytest-django
# created "pytest.ini" at the same level as manage.py
## --> Note: this connects the testing to our django project and its funtionality like talking to models and view functions 
from app.views import calculateTargetCalories # shorten name ref CTC
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

    result = calculateTargetCalories(None, 1) # Normaly takes (request, profile_id)
    assert result == pytest.approx(1234.3)





# test fitnessSurvey