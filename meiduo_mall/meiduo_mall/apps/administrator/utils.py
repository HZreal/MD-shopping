

# 自定义JWT认证成功后的返回值
def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'id': user.id or request.user.id,
        'user': user.username or request.user.name,
    }