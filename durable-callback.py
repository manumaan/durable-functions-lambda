from aws_durable_execution_sdk_python.context import DurableContext, StepContext, durable_step
from aws_durable_execution_sdk_python.execution import durable_execution
from aws_durable_execution_sdk_python.config import CallbackConfig, Duration
from time import sleep

@durable_step
def _send_approval_request(
    step_context: StepContext,
    documentId: str,
    reviewers: str,
    callbackId: str
) -> str:
    # send API call to third party service
    # notify/validate human interaction here

    return f"_send_approval_request: {documentId} {reviewers} {callbackId}"

@durable_step
def _step(step_context: StepContext, my_arg: int) -> str:
    step_context.logger.info("Hey there from _step")
    sleep(5)
    return f"_step: {my_arg}"

@durable_execution
def lambda_handler(event, context: DurableContext) -> dict:
    document_id = event['documentId']
    reviewers = event['reviewers']

    context.step(lambda _: _step(1)(_), name="prepare-document")

    callback = context.create_callback(
        name="approval_callback",
        config=CallbackConfig(
            timeout=Duration.from_hours(24),  # Maximum wait time
            heartbeat_timeout=Duration.from_hours(2),  # Fail if no heartbeat for 2 hours
        ),
    )

    callback_id = callback.callback_id
    context.step(lambda _: _send_approval_request(document_id, reviewers, callback_id)(_), name="send-document")
    print('callback_id -> ', callback_id)

    # Wait for result - execution suspends here
    result = callback.result()
    print('result -> ', result)

    if result == 'approve':
        return {
            'status': 'approve',
            'documentId': document_id
        }

    return {
        'status': 'rejected',
        'documentId': document_id,
    }
