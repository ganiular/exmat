from functools import wraps
from flask import request, render_template, redirect

def sense_response(view):
    @wraps(view)
    def wraped_view(*args, **kwargs):
        value = view(*args, **kwargs)
        print("value", value)
        if not isinstance(value, dict):
            raise TypeError(request.endpoint + " must return a dict")
        template = value.pop('template', None)
        if request.is_json:
            return value
        elif template:
            return render_template(template, **value)
        elif value.get('redirect'):
            return redirect(value['redirect'])
        else:
            template = request.endpoint.replace('.', '/') + '.html'
            return render_template(template, **value)
    return wraped_view
