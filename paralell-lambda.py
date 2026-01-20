from aws_durable_execution_sdk_python import (
    DurableContext,
    durable_execution,
    durable_step,
)
from aws_durable_execution_sdk_python.config import Duration

@durable_step
def validate_order(step_context, order_id):
    step_context.logger.info(f"Validating order {order_id}")
    return {"orderId": order_id, "status": "validated"}

@durable_step
def process_payment(step_context, order_id):
    step_context.logger.info(f"Processing payment for order {order_id}")
    return {"orderId": order_id, "status": "paid", "amount": 99.99}

@durable_step
def confirm_order(step_context, order_id):
    step_context.logger.info(f"Confirming order {order_id}")
    return {"orderId": order_id, "status": "confirmed"}

@durable_execution
def lambda_handler(event, context: DurableContext):
    order_id = event['orderId']
    
    # Define parallel step functions
    def validate_order_step(ctx: DurableContext):
        return ctx.step(validate_order(order_id), name='validate-order')
    
    def process_payment_step(ctx: DurableContext):
        return ctx.step(process_payment(order_id), name='process-payment')
    
    # Run validation and payment processing in parallel
    parallel_results = context.parallel(
        [validate_order_step, process_payment_step],
        name='order-processing'
    )
    
    # Extract results from BatchResult object using results() method
    results = parallel_results.get_results()
    validation_result = results[0]
    payment_result = results[1]
    
    # Wait for 2 seconds to simulate external confirmation
    context.wait(Duration.from_seconds(2))
    
    # Step 3: Confirm order
    confirmation_result = context.step(confirm_order(order_id))
    
    return {
        "orderId": order_id,
        "status": "completed",
        "steps": [validation_result, payment_result, confirmation_result]
    }
