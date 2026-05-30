# Part 1

To start, I wanted to run the notebook and see the results because the cells were not excecuted. There was a bug in the seaborn plots but after the fix it ran just fine. I also needed to add xgboost to make it work. The results were right, there is no difference in terms of performance but it is in terms of complexity. The logistinc regression is a much simplier model, and it's fasters in terms of inference.
Finally, since the xgboost model will not be used so I decidied to remove it from the requirements.

6.b.iii. Logistic Regression with Feature Importante and with Balance is the selected model

I needed to change a little the `requirements.txt` file to make it work with the `requirements-test.txt`. And also added a `conftest.py` file because of the relative route of the data file that is read in the `test_model.py`


# Part 2

For part 2 I just added some extra validations for the `POST/predict` endpoint. Mainly validations in the name of the airline (`OPERA`), in the type of flight (`TIPOVUELO`) and in the months (`MES`). For example, if we receive an airline that was not on the training set, the model will fail so we catch it in the endpoint request.

To continue, I added some pydantic models to structure the prediction request.

Finally, the implementation lazy trains the model on the first prediction. Because it's a very simple model and the dataset it's very small as well, this should be no problem for the deployment.