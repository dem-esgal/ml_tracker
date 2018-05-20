Example:

from ml_tracker import Experiment

if __name__ == '__main__':
    expr = Experiment("New one", "1.0.0", True)# Create new Experiment
    expr.log_parameter("first",3)
    expr.log_parameters({
        "first": 3,
        "second": "float"
    })

    expr.log_metric("first", 3)
    expr.log_metrics({
        "first": 4,
        "second": "5"
    })

    expr.log_dataset("new dataset",(0,0))
    expr.commit()
