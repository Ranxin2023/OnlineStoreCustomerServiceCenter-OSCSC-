from yanwei_apis.get_all_checkpoints import get_all_checkpoints 

# from yanwei_apis.get_yanwen_tracking_numbers_from_A import get_yanwen_tracking_numbers_from_A   
from yanwei_apis.fetch_all_yanwen_orders import fetch_all_yanwen_orders
if __name__ == "__main__":
    tracking_number = "UK933048204YP"
    auth_token = "10006616"

    # print(f"All data fetched from yanwen by tracking number {tracking_number} is \n{get_all_checkpoints(tracking_number, auth_token)}")
    # print(f"get_yanwen_tracking_numbers_from_A result:{get_yanwen_tracking_numbers_from_A()}")
    print(f"All yanwen orders are{fetch_all_yanwen_orders()}")