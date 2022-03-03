from rest_framework import serializers
from users.models import User


class UserManagerSerializer(serializers.ModelSerializer):
    """
    用户管理
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email')


class UserAddSerializer(serializers.ModelSerializer):
    """
    添加用户
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'password')
        # username字段增加长度限制，password字段只参与保存，不在返回给前端，增加write_only选项参数
        extra_kwargs = {
            'username': {
                'max_length': 20,
                'min_length': 5
            },
            'password': {
                'max_length': 20,
                'min_length': 8,
                'write_only': True
            }
        }

    # 重写create方法
    def create(self, validated_data):
        # 保存用户数据并对密码加密
        user = User.objects.create_user(**validated_data)
        return user
















