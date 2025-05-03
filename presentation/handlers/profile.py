from infrastructure.bus import bus_client as bus
from application.services import profile_service

@bus.register_handler("SEARCH_PROFILE")
def search(payload, ch):
    try:
        display_name = payload.get("display_name")
        user_ids = payload.get("user_ids")

        if not display_name and not user_ids:
            return {"message": "Either 'display_name' or 'user_ids' must be provided"}

        data = profile_service.search(display_name, user_ids)

        if not data:
            return []
        
        return [{**user['human']['profile'], 'userId': user['userId']} for user in data.get('result')]
    except Exception as e:
        return {"message": str(e)}
    
@bus.register_handler("MOST_FOLLOWED")
def hottest(payload, ch):
    try:
        return profile_service.most_followed()
    except Exception as e:
        return { 'message': str(e) }

@bus.register_handler("PROFILE_INFO")
def info(payload, ch):
    try:
        return profile_service.info(payload['user_id'])
    except Exception as e:
        return { 'message': str(e) }

@bus.register_handler('FOLLOW_COUNT')
def follow_counting(payload, ch):
    try:
        profile_service.edit_count_followers(payload['user_id'], payload['operation'])
        return { 'message': f"Operation {payload['operation']} was done" }
    except Exception as e:
        return { 'message': str(e) }