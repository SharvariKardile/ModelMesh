import time


# --------------------------------------------------
# ModelMesh metrics
# --------------------------------------------------

METRICS = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "total_model_attempts": 0,
    "fallback_attempts": 0,
    "total_response_time": 0.0,

    "model_attempts": {}
}


# --------------------------------------------------
# Start measuring request time
# --------------------------------------------------

def start_timer():

    return time.perf_counter()


# --------------------------------------------------
# Record a model attempt
# --------------------------------------------------

def record_model_attempt(model_name, is_fallback=False):

    METRICS["total_model_attempts"] += 1

    if is_fallback:
        METRICS["fallback_attempts"] += 1

    if model_name not in METRICS["model_attempts"]:

        METRICS["model_attempts"][model_name] = 0

    METRICS["model_attempts"][model_name] += 1


# --------------------------------------------------
# Record a successful request
# --------------------------------------------------

def record_success(start_time):

    METRICS["total_requests"] += 1

    METRICS["successful_requests"] += 1

    elapsed_time = time.perf_counter() - start_time

    METRICS["total_response_time"] += elapsed_time


# --------------------------------------------------
# Record a failed request
# --------------------------------------------------

def record_failure(start_time):

    METRICS["total_requests"] += 1

    METRICS["failed_requests"] += 1

    elapsed_time = time.perf_counter() - start_time

    METRICS["total_response_time"] += elapsed_time


# --------------------------------------------------
# Return metrics
# --------------------------------------------------

def get_metrics():

    total_requests = METRICS["total_requests"]

    if total_requests > 0:

        average_response_time = (
            METRICS["total_response_time"]
            / total_requests
        )

    else:

        average_response_time = 0.0

    return {
        "total_requests": total_requests,
        "successful_requests": METRICS["successful_requests"],
        "failed_requests": METRICS["failed_requests"],
        "total_model_attempts": METRICS["total_model_attempts"],
        "fallback_attempts": METRICS["fallback_attempts"],
        "average_response_time_seconds": round(
            average_response_time,
            4
        ),
        "model_attempts": METRICS["model_attempts"]
    }