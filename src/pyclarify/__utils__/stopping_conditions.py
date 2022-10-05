from pyclarify.views.generics import Response


def select_stopping_condition(response: Response):
    if hasattr(response.result, "data"):
        if len(response.result.data) < 1000:
            return True
    else:
        return True
    return False
