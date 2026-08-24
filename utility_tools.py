from datetime import datetime

def get_current_datetime():
    try:
        now = datetime.now()

        return {
            "success" : True,
            "date" : now.strftime("%Y-%m-%d"),
            "time" : now.strftime("%H:%M:%S")
        }

    except Exception as e:
        return {
            "success" : False,
            "error_type" : "datetime_error",
            "message" : str(e)
        }