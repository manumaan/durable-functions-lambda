# durable-functions-lambda
Demo Repo for Durable Functions Lambda


durable-wait.py 

Simple durable function demo with wait functionality 

paralell-lambda.py

Durable function with paralell steps 

map-lambda.py

Durable function with map functionality 

testing event: 

{
  "orderIds": [
    "ORD-101",
    "ORD-202",
    "ORD-303"
  ]
}

durable-callback.py

Durable function with callback functionality

testing event: 

{
  "documentId": "a1234",
  "reviewers": "awedis"
}

note the callback id printed from send-document step.

callback-return-lambda.py 

Normal lambda function that returns the control to the callback function. 

testing event:

{
  "callback_id": ".... ", //get from previous step 
  "status": "approve"
}
