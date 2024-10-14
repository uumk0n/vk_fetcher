import requests
import json
import argparse
import os
from dotenv import load_dotenv

load_dotenv()

API_VERSION = '5.131'
BASE_URL = 'https://api.vk.com/method/'

def vk_request(method, params):
    url = f'{BASE_URL}{method}'
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    if 'error' in data:
        raise Exception(f"Error {data['error']['error_code']}: {data['error']['error_msg']}")
    return data['response']

def fetch_vk_data(user_id, access_token):
    params = {
        'user_ids': user_id,
        'fields': 'followers_count',
        'access_token': access_token,
        'v': API_VERSION
    }
    user_info = vk_request('users.get', params)[0]

    followers_params = {
        'user_id': user_info['id'],
        'access_token': access_token,
        'v': API_VERSION
    }
    followers = vk_request('users.getFollowers', followers_params)['items']

    subscriptions_params = {
        'user_id': user_info['id'],
        'extended': 1,
        'access_token': access_token,
        'v': API_VERSION
    }
    subscriptions = vk_request('users.getSubscriptions', subscriptions_params)['items']

    groups_params = {
        'user_id': user_info['id'],
        'access_token': access_token,
        'v': API_VERSION
    }
    groups = vk_request('groups.get', groups_params)['items']

    return {
        'user_info': user_info,
        'followers': followers,
        'subscriptions': subscriptions,
        'groups': groups
    }

def save_to_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def main():
    parser = argparse.ArgumentParser(description='Fetch VK user data.')
    parser.add_argument('--user_id', type=str, default=None, help='VK user ID (optional).')
    parser.add_argument('--file_path', type=str, default='vk_data.json', help='Path to save JSON result file (optional).')

    args = parser.parse_args()

    access_token = os.getenv('ACCESS_TOKEN')  # Access token from .env file
    if not access_token:
        print("Access token is missing. Please check your .env file.")
        return

    user_id = args.user_id if args.user_id else 'self'

    try:
        vk_data = fetch_vk_data(user_id, access_token)
        save_to_json(vk_data, args.file_path)
        print(f"Data saved to {args.file_path}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
