
import os
import jwt






def decode_jwt(jwt_token):    
    print(f"token: {jwt_token}",flush=True)

    if 'Bearer' in jwt_token:
        token = jwt_token.split()[1]
        res = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])

        print(f"res: {res}",flush=True)

    return {'organization': res.get('organization'),'role': res.get('role'),'user_id': res.get('user_id')}