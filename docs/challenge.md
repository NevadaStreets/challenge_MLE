# Part I
## Model decision
To start, I wanted to run the notebook and see the results because the cells were not executed. There was a bug in the seaborn plots but after the fix it ran just fine. I also needed to add xgboost to make it work. The results were right, there is no difference in terms of performance but there is in terms of complexity. The logistic regression is a much simpler model, and it's faster in terms of inference.
Finally, since the xgboost model will not be used so I decided to remove it from the requirements.

**6.b.iii. Logistic Regression with Feature Importante and with Balance** is the selected model. 

## Note
There were some typos in the notebook like the one above **Feature Importante** instead of **Feature Importance** but I don't know if those are part of the bugs that I need to fix so I left them exactly as I found them.

## Testing
I needed to change a little the `requirements.txt` file to make it work with the `requirements-test.txt`. And also added a `conftest.py` file because of the relative path of the data file that needs to be read in the `test_model.py`.

The `make model-test` passed the 4 tests with a 98% coverage on `model.py`.

## Fixes and extra code
Finally, I added a `.gitignore` to stop tracking the files that are not necessary to have in the remote version.
I corrected the invalid `Union(...)` (parentheses) return annotation to `Union[...]` in the provided `preprocess` signature.

## Changelog
The full changelog is here in this [PR](https://github.com/NevadaStreets/challenge_MLE/pull/1), it was merged into `develop`

# Part II
## Validations
For part 2 I just added some extra validations for the `POST/predict` endpoint. Mainly validations in the name of the airline (`OPERA`), in the type of flight (`TIPOVUELO`) and in the months (`MES`). For example, if we receive an airline that was not on the training set, the model code will fail. Now the validation will catch it in the endpoint request code.

To continue, I added some pydantic models to structure the prediction request.

## Implementation
Finally, the implementation can lazy train the model on the first prediction in case this is necessary. It's a very simple model and the dataset it's very small as well. So, this functionality will not make any problems in the deployment.

## Testing

The `make api-test` passed the 4 tests with a 91% coverage on `api.py`.

## Changelog
The full changelog of this part is in this [PR](https://github.com/NevadaStreets/challenge_MLE/pull/3). These changes were merged into `develop`

# Part III

## Deployment
For the deployment, I made some technical decisions:
1. The app was packaged into a Docker image using the provided Dockerfile. It used only the `requirements.txt` because those are the production environment requirements.
2. The cloud provider selected is GCP as suggested. And the service used is **Cloud Run**. This is a serverless container platform, so it's easy to maintain and update. It provides autoscale as well.
3. In part 2 I said that the model will be lazy trained, so the first prediction call will train the model if this was not done before that. But, I realized that it could be done on the start up event of the API. So, now it trains every time the API is initialized. This will happen every time you make a new deployment and will not use time of the first user that needs a prediction.
4. I used a `.venv` environment for my local development. And there are files that will not be necessary in the deployment as well (Dockerfile, gcloud). So, I added a `.dockerignore` and `.gcloudignore` to not load those files in the deployment.

After completed the deployment, I added the URL to the make file and ran the tests. This is the final `URL` of the app deployed in **Cloud Run**: [https://delay-api-jpe4rb3uia-uc.a.run.app](https://delay-api-jpe4rb3uia-uc.a.run.app)

## Testing
For the test part I needed to fix the `requirements-test.txt`. There was a problem with locust 1.6 dependency on Flask 1.1.x. It is incompatible with modern `Jinja2/Werkzeug/MarkupSafe/itsdangerous`. I pinned the classic compatible stack in the requirements file and then `make stress-test` ran without errors.
After that fix `make stress-test` tested 6,998 requests with 0 failures.

## Changelog
The full changelog of this part is in this [PR](https://github.com/NevadaStreets/challenge_MLE/pull/4). These changes were merged into `develop`

# Part IV
## CI/CD
For this part I added the two files(`ci.yml`,`cd.yml`) into `.github/workflows`. But, to make them work properly I needed to do some things first in the deployment.
- I created a service account key to make the deployments from the github actions.
- I stored this key in the secrets of the repository, so it will be *(allegedly)* safe to be used in the deployments.

After the creation of those resources I added the CI/CD files following this logic:
- `ci.yml`: This github action is in charge of the Continuous Integration. Because this is a simple repository and code, this workflow will only run the tests defined in the `README.md`. It will be activated in `push` commands on the `develop` and in PRs made pointing to the `develop` and `main` branches. To finish, this workflow also triggers on `workflow_dispatch` and `workflow_call` so it can be run manually in Github and be called in another workflow.
- `cd.yml`: This github action is in charge of the Continuous Delivery. This workflow needs to run the tests defined in the `README.md` to assure that everything is working properly. To make this, it reuses the `ci.yml` workflow as a required job. After that, it creates a new deployment every time there is a new `push` on the `main` branch. Here the service account key stored in the secrets is used. And after the deployment, a smoke test runs to check that the deploy was done and it's working fine. This workflow can also be triggered on `workflow_dispatch`, so if you want to manually do a deploy in Github you can. This is something always nice to have in case you want to do a quick deploy. Moreover, I added the `stress-test` in this workflow, but it can only be run manually in the Github UI by selecting the `run_stress_test` checkbox, in case it's necessary to stress test it after the deployment.

## Notes
- I want to clarify that I said "*(allegedly)*" before because of the current situation about the security leaks that *Github* had recently. Moreover, this repository is public. So, I pray for nothing to happen until the review of this challenge hahaha.
- I could have done the authentication with a **Workload Identity Federation** in GCP, but I decided to use a more classical method.

## Changelog
The full changelog of this part is in this [PR](https://github.com/NevadaStreets/challenge_MLE/pull/5).