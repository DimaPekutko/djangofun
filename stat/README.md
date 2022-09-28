# Statistics microservice

## Allowed commands for AMQP communication:

> `create_page`: request={"id": "str", "user_id": "str", "name": "str"}, response=page 

> `update_page`: request={"id": "str", "user_id": "str", "name": "str"}, response=page 

> `delete_page`: request={"id": "str", "user_id": "str"}, response=status

> `get_stat`: request={"user_id": "str"}, response=pages

> `new_like`: request={"id": "str"}, response=page 

> `new_follower`: request={"id": "str"}, response=page 

> `new_follow_request`: request={"id": "str"}, response=page 

> `undo_like`: request={"id": "str"}, response=page 

> `undo_follower`: request={"id": "str"}, response=page 

> `undo_follow_request`: request={"id": "str"}, response=page 
