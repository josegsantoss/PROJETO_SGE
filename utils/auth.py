from functools import wraps
from flask import session, jsonify

def login_required(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        if 'usuario_id' not in session:
            return jsonify({
                'erro': 'Não autenticado'
            }), 401

        return f(*args, **kwargs)

    return decorated
