# Part 1

To start, I wanted to run the notebook and see the results because the cells were not excecuted. There was a bug in the seaborn plots but after the fix it ran just fine. I also needed to add xgboost to make it work. The results were right, there is no difference in terms of performance but it is in terms of complexity. The logistinc regression is a much simplier model, and it's fasters in terms of inference.
Finally, since the xgboost model will not be used so I decidied to remove it from the requirements.

6.b.iii. Logistic Regression with Feature Importante and with Balance is the selected model

I needed to change a little the `requirements.txt` file to make it work with the `requirements-test.txt`. And also added a `conftest.py` file because of the relative route of the data file that is read in the `test_model.py`
