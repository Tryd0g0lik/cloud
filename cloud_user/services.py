from cloud_user.models import UserRegister



def find_superuser()-> [object, None]:
    """
    TODO: This is checker. It checks, we have a superuser in db or not/
        'True' if haves a superuser or 'False'
    :return: object or None
    """
    superuser_list = UserRegister.objects.filter(is_superuser=True)
    if len(superuser_list) > 0:
        return superuser_list[0]
    return None

    