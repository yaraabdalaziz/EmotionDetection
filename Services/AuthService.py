from Database.UsersRepo import UsersRepo

class AuthService:
    def __init__(self):
        self.users_repo = UsersRepo()
    
    def authenticate_user(self, api_key):
        """Authenticate user and return user_id, or None if invalid"""
        return self.users_repo.get_user_id(api_key)
    
    def check_user_quota(self, user_id): 
        """Check if user has remaining quota"""
        return self.users_repo.has_quota(user_id)
    
    def consume_quota(self, user_id):
        """Decrement user quota by 1"""
        self.users_repo.decrement_user_quota(user_id)