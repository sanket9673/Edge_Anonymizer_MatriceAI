import time
import numpy as np
import logging
from functools import wraps

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] ComplianceFilter: %(message)s"
)

def fail_closed_compliance(timeout_ms=500):
    """
    Enterprise Compliance Decorator.
    Enforces a strict Fail-Closed architecture. If the wrapped AI function
    fails or exceeds the timeout, it returns a black frame.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, frame, *args, **kwargs):
            start_time = time.time()
            
            # 1. Pre-allocate a black frame of the exact same dimensions
            # This is our "Fail-Closed" safe state
            black_frame = np.zeros_like(frame)
            
            result = {}
            fail_closed_triggered = False
            
            try:
                # 2. Execute the AI inference
                # Expecting the function to return (processed_frame, redacted_count)
                processed_frame, redacted_count = func(self, frame, *args, **kwargs)
                
                # 3. Calculate Latency
                elapsed_ms = (time.time() - start_time) * 1000.0
                
                # 4. Check against strict latency timeout
                if elapsed_ms > timeout_ms:
                    logging.warning(f"SLA Breach: Inference took {elapsed_ms:.2f}ms (Limit: {timeout_ms}ms). FAILING CLOSED.")
                    fail_closed_triggered = True
                else:
                    # Success State
                    result["frame"] = processed_frame
                    result["metadata"] = {
                        "redacted_count": redacted_count,
                        "status": "COMPLIANT",
                        "latency_ms": round(elapsed_ms, 2)
                    }
                    
            except Exception as e:
                # 5. Catch any YOLO/OpenCV crashes
                logging.error(f"Critical AI Crash: {e}. FAILING CLOSED to protect privacy.")
                elapsed_ms = (time.time() - start_time) * 1000.0
                fail_closed_triggered = True
                
            # 6. Apply Fail-Closed State if triggered
            if fail_closed_triggered:
                result["frame"] = black_frame
                result["metadata"] = {
                    "redacted_count": 0,
                    "status": "FAIL_CLOSED",
                    "latency_ms": round(elapsed_ms, 2)
                }
            
            return result
        return wrapper
    return decorator
