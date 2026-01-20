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
    order_ids = event['orderIds']
    
    # Process each order using map
    def process_single_order(ctx: DurableContext, order_id, index, *extra_args):
        # Run validation and payment processing in parallel
        # Using direct step calls without nested function wrappers
        def validate_branch(child_ctx: DurableContext):
            return child_ctx.step(validate_order(order_id), name=f'validate-{index}')
        
        def payment_branch(child_ctx: DurableContext):
            return child_ctx.step(process_payment(order_id), name=f'payment-{index}')
        
        parallel_results = ctx.parallel(
            [validate_branch, payment_branch],
            name=f'parallel-{index}'
        )
        
        # Extract results
        results = parallel_results.get_results()
        validation_result = results[0]
        payment_result = results[1]
        
        # Wait for 2 seconds
        ctx.wait(Duration.from_seconds(2))
        
        # Confirm order
        confirmation_result = ctx.step(confirm_order(order_id), name=f'confirm-{index}')
        
        return {
            "orderId": order_id,
            "status": "completed",
            "steps": [validation_result, payment_result, confirmation_result]
        }
    
    # Map over all order IDs
    results = context.map(
        order_ids,
        process_single_order,
        name='process-all-orders'
    )
    
    return {
        "status": "all-orders-completed",
        "totalOrders": len(order_ids),
        "results": results.get_results()
    }
