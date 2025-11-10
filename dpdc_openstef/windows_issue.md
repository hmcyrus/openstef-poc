Two things that didn't work out of the box

### for the openstef poc script following two lines doesn't work in windows
```
mlflow_dir = "./mlflow_trained_models"
mlflow_tracking_uri = os.path.abspath(mlflow_dir)
```
instead we should use either
```
mlflow_tracking_uri = "file:///" + os.path.abspath(mlflow_dir).replace("\\", "/")
```

or 
```
mlflow_tracking_uri = "mlflow_trained_models"
```


### can't figure what was wrong in the first place 
Initially tried disabling the following main function and run using the command -> `uvicorn main:app --reload --port 8080` and it worked. Now it works either ways. The issue could be with the `run.bat`
```
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8080)

```
