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

def get_fields_response(obj,
                        exclude_instance=[]
                        ):
    """
    :param exclude_instance: list. This for the fields exclude. Bu default is \
    ["password", "is_activated",
    "email",  "send_messages",
    "groups", "user_permissions"]
    return \
     ```json
       {
         "id": 19,
         "last_login": null,
         "is_superuser": false,
         "username": "",
         "first_name": "Денис",
         "last_name": "Королев",
         "is_staff": false,
         "is_active": true,
         "date_joined": "2025-01-03T13:01:53.238635+07:00"
       }
     ```
   """
    if len(exclude_instance) == 0:
        exclude_instance = ["password", "is_activated",
                            "email",  "send_messages",
                            "groups", "user_permissions"]
    new_instance = {}
    # for k, v in obj.data.items():
    for k, v in dict(obj.data).items():
        if k in exclude_instance:
            continue
        new_instance[f"{k}"] = v
    # obj.data = new_instance
    return new_instance

