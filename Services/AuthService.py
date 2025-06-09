from functools import wraps
from flask import request, jsonify, g
from Database.UsersRepo import UsersRepo

class AuthService:
    def __init__(self)-> None:
        self.users_repo = UsersRepo()
    
    def authenticate_user(self, api_key:str) -> int:
        return self.users_repo.get_user_id(api_key)
    
    def user_has_quota(self, user_id:int) -> bool:
        return self.users_repo.has_quota(user_id)
    
    def consume_quota(self, user_id:int) -> bool:
        return self.users_repo.decrement_user_quota(user_id)
    def return_qouta(self, user_id:int) -> bool:
        return self.users_repo.incerement_user_quota(user_id)

auth = AuthService()

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('api-key')
        if not api_key:
            return jsonify({"error": "Missing API key"}), 401
        
        user_id = auth.authenticate_user(api_key)
        if not user_id:
            return jsonify({"error": "Invalid API key"}), 401
        
        g.current_user_id = user_id
        return f(*args, **kwargs)
    return decorated_function

def require_quota(consume_on_success=True):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = getattr(g, 'current_user_id', None)
            if not user_id:
                return jsonify({"error": "User not authenticated"}), 401
            
            if not auth.consume_quota(user_id):
                        return jsonify({
                            "error": {
                                "code": "quota_exceeded",
                                "message": "Quota exceeded. Please upgrade your plan or wait until next reset."
                            }
                        }), 429
            
            result = f(*args, **kwargs)
      
            if consume_on_success and result[1] != 200:
                 auth.return_qouta(user_id)

            return result
        return decorated_function
    return decorator