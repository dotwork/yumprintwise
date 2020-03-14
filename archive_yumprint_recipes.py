from datetime import datetime
import json
import random
import time

import requests

CARLOS_COOKBOOK_ID = "oje"
CARLOS_AND_STEPH_COOKBOOK_ID = "o0j"
DEB_COOKBOOK_ID = 'cvjh'
# API = "https://api.yumprint.com/feeds/cookbook-"
# http://yumprint.com/app/object/o0j  #api feed for our main page


class Archiver:

    def __init__(self, user_id):
        response = requests.get(f'https://api.yumprint.com/feeds/cookbook-{user_id}')
        self.account_dict = json.loads(response.content)
        assert self.account_dict["success"]
        self.creator_id = self.account_dict['result']['person']['id']
        self.creator_name = self.account_dict['result']['person']['name']
        self.cookbooks = []
        self.current_cookbooks = []
        with open('/home/carlos/projects/mylibrary/yumprintwise/deb_yumprint_recipes.json') as f:
            data = json.loads(f.read())
        for cookbook in data:
            self.current_cookbooks.append(cookbook['id'].split('-')[-1])

    def fetch_user_cookbooks(self):
        found_try_soon = False
        for cookbook in self.account_dict["result"]["feeds"][0]["items"]:
            cookbook_id = cookbook["id"]
            title = cookbook["title"]
            # cookbook_data = self.get_all_cookbook_data(cookbook_id)
            if cookbook_id in self.current_cookbooks:
                print(f'Skipping cookbook {cookbook_id}. Already have it...')
                continue
            elif cookbook_id is None:
                if found_try_soon:
                    print(cookbook)
                    raise Exception('Already found try soon!')
                found_try_soon = True
                continue
            cookbook_json = self.get_cookbook_json(cookbook_id)
            cookbook_data = self.get_recipe_data(cookbook_json)
            print("recipe list retrieved. writing to file...")
            self.cookbooks.append(cookbook_data)
            print("%s cookbook written to file" % title)
            time.sleep(random.randint(10, 20))
        return self.cookbooks

    def get_cookbook_json(self, cookbook_id):
        if cookbook_id is None:
            url = f"https://api.yumprint.com/feeds/trysoon-{self.creator_id}/"
        else:
            url = f"https://api.yumprint.com/feed/object/{cookbook_id}/"
        response = requests.get(url)
        try:
            cookbook_json = json.loads(response.content)
        except Exception:
            print('*' * 50)
            print(response.content)
            print(response.status_code)
            print('*' * 50)
            raise
        assert cookbook_json["success"], f"failure cookbook_id: {cookbook_id}. URL: {url}"
        return cookbook_json

    def get_recipe_data(self, cookbook_json):
        cookbook = cookbook_json["result"]["feeds"][0]
        for i, recipe in enumerate(cookbook["items"]):
            recipe.update(self.get_recipe_details(recipe["id"]))
            print(f'Recipe {i + 1} of {len(cookbook["items"])} completed.')
        print(f"returning cookbook {cookbook['title']}")
        return cookbook

    @staticmethod
    def get_recipe_details(recipe_id):
        url = f"https://api.yumprint.com/feed/object/{recipe_id}/?user_token=null"
        response = requests.get(url)
        time.sleep(random.randint(10, 20))
        recipe_dict = json.loads(response.content)
        assert recipe_dict["success"]

        details = {}
        for section in recipe_dict["result"]["sections"]:
            details[section["type"]] = section["items"]
        return details

    # def get_all_cookbook_data(self, cookbook_id):
    #     cookbook_json = self.get_cookbook_json(cookbook_id)
    #     if cookbook_json:
    #         return self.getRecipeData(cookbook_json)
    #     else:
    #         raise Exception(f'Failed to get cookbook_json: {cookbook_json}')


####################################################################################
if __name__ == "__main__":
    c = Archiver(DEB_COOKBOOK_ID)
    try:
        c.fetch_user_cookbooks()
    except Exception:
        print('FAILED!')
        pass
    name = c.creator_name.lower().replace(' ', '_')
    if c.cookbooks:
        try:
            with open(f'{name}_yumprint_recipes_{datetime.now().timestamp()}.json', mode='w') as f:
                f.write(json.dumps(c.cookbooks))
        except Exception:
            print('FAILED!')
            print(c.cookbooks)
    else:
        print('No cookbooks to write')
