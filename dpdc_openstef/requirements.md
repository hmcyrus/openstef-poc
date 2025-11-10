Create a simple fastapi project in the directory `dpdc_openstef` that can do following 

- the project will have 4 pages named - Train Model, Forecast, Data Input, Dashboard
- the pages should be implemented with fastapi native jinja2 templates
- pages should use bootstrap's latest version for styling, simple and straightforward css rules should be applied for templating. pages should be responsive for different sizes of desktops
- page should have professional looks
- pages should be able to show plotly graphs

The requirements for the pages will be following 
## Train Model page
- This page will contain a form with following inputs
    - Model -> a select with two values - xgb, lgb
    - Hyper Parameter Section -> This section will contain inputs based on the Model input. while 'xgb' model is selected this section should show input fields for - max_depth, learning_rate, n_estimator, early_stopping_rounds. while 'lgb' is selected this section should show input fields for - n_estimator, learning_rate, num_leaves, max_depth, max_bin  
- the api for form submission should accept a string for model and a dictionary for the hyperparams. For now the api should print the value of the submitted form in console 

## Forecast page
- This page will contain a form that'll send an api request on submit and receive a json response that'll be rendered in table without reloading the page. There will be two more part in this page beside the form - a table showing data from the response of form submission api and another graph showing a plotly-like chart. The chart will use data from another api which will be invoked after the form submission api returns value. 

- The form will have following input fields 
    - Date -> should show a calender on click and when a date is clicked the selected value will be shown. This field is required.
    - Hour -> a searchable select elem with 0 to 23 as value. This field is required.
    - Holiday -> a select elem with two values: 1 and 0. This field is required. default should be 0
    - Holidday Type -> a select with values from 0 to 20. This field is required. default should be 0
    - Nation event -> a select with values from 0 to 5 values. This field is required. default should be 0
- There will be another button within the form which will fetch weather data using api and show a table with following fields within form - temp,rhum,prcp,wdir,wspd,pres,cldc,coco. The table will not be editable. The data in that table have to be submitted with the form

- The response of the form submission will contain a list of object with following fields - model_name, forecasted_value. The response should be shown in a separete block in a tabular form.

- In total there will be two apis associated with this page. One for submitting the form another for fetching the chart.

# Data Input page
- This page should have a date selector and a table. 
- The table should have three columns - Hour, Predicted, Actual. There should be 24 rows of data containing predicted and actual values of 0 to 23 Hr of a particular day.
- When a date is selected an api will be invoked that'll fetch predicted and actual data by hour for that day and the table should be populated. If no data is found for an hour or all hours 0 should be shown in the table
- The table will contain a form underneath that'll contain two fields - date (this'll come from the selection), hourly data - this will be a list of objects with three fields - 'hour', 'predicted', 'actual'
- There should be a button titled 'Update' that'll submit the current state of data.


# Dashboard page
- This page will contain some graphs

# Ideas for better performance
- Due to erratic nature of weather pattern short term patterns demand significant attention. When prediction starts to worsen we should consider training another model with more recent data in training set.
- We provided a Data Quality Indicator(DQI) section in the Dashboard. There we'll highlight useful metrics like missing data points of prediction and actual.