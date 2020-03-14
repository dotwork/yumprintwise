import re
import json
from web_crawler.base_web_crawler import BaseWebCrawler


########################################################################################################################
class YumprintPageTypes(object):
    main_cookbook_id = "o0j"
    cookbook_type_api = "https://api.yumprint.com/feeds/cookbook-{}"
    recipe_type_api = "https://api.yumprint.com/feed/object/{}/?user_token=null"


########################################################################################################################
class BaseYumprintCrawler(BaseWebCrawler, YumprintPageTypes):
    def __init__(self):
        super(BaseYumprintCrawler, self).__init__()
        self.data = {}
        self.cookbooks_dict = {}
        self.cookbook_ids = []
        self.yumprint_archive = {}
        self.feeds = {}
        self.yumprint_ids = {
            "main_cookbook": "o0j",
        }
        self.regex = {
            self.recipe_type_api: "http://yumprint.com/app/object/",
        }
        self.page_types = [self.main_cookbook_id, self.cookbook_type_api, self.recipe_type_api]

    ####################################################################################################################
    def build_yumprint_url(self, page_type, yumprint_id):
        if page_type not in self.page_types:
            raise TypeError("Must provide a yumprint page type: '{}'".format(", ".join(self.page_types)))
        return page_type.format(yumprint_id)

    ####################################################################################################################
    def crawl(self, page_type, yumprint_id):
        url = self.build_yumprint_url(page_type, self.yumprint_ids[yumprint_id])
        self.data = json.loads(self.read_page(url))
        assert self.data["success"]
        self.feeds = self.data["result"]["feeds"]

    ####################################################################################################################
    def validate_url_and_get_yumprint_id(self, url, page_type):
        null_user_token = "/?user_token=null"
        if url.endswith(null_user_token):
            regex = re.escape("http://yumprint.com/app/object/") + r"([a-zA-Z\d]{3,6})" + re.escape("/?user_token=null")
        else:
            regex = re.escape("http://yumprint.com/app/object/") + r"([a-zA-Z\d]{3,6})$"
        return re.search(regex, url).group(1)

    ####################################################################################################################
    def get_recipe_data(self, recipe_id):
        url = self.build_yumprint_url(self.recipe_type_api, recipe_id)
        data = json.loads(self.read_page(url))
        if data["success"] is True:
            return data["result"]
        else:
            raise Exception("Failed to get successful response from '{}'".format(url))

    # ####################################################################################################################
    # def archive_all(self):
    #     self.crawl(self.urls["main_cookbook"])
    #     for feed in self.feeds:
    #         for cookbook in feed["items"]:
    #             _id = cookbook["id"]
    #             title = cookbook["title"]
    #             recipe_list = self.getAllCookbookData(_id)
    #             print "recipe list retrieved. writing to file..."
    #             self.yumprint_archive[title] = recipe_list
    #             self.writeResults(self.yumprint_archive)
    #             print "%s cookbook written to file" % title
    #
    # def getAllCookbookData(self, id):
    #     cookbook_dict = {}
    #     cookbook_json = self.getCookbookJson(id)
    #     if cookbook_json:
    #         cookbook_dict = self.getRecipeData(cookbook_json)
    #         return cookbook_dict
    #     else:
    #         cookbook_dict[id] = "Json Error"
    #         print "Json Error"
    #
    # def getCookbookJson(self, cookbook_id):
    #     if cookbook_id == None:
    #         api_url = "https://api.yumprint.com/feeds/trysoon-baF/"
    #     else:
    #         api_url = str(API) + str(cookbook_id) + "/"
    #     webdata = readPage(api_url)
    #     cookbook_json = json.loads(webdata)
    #     if cookbook_json:
    #         return cookbook_json
    #
    # def getRecipeData(self, cookbook_json):
    #     cookbook_dict = {}
    #     result = cookbook_json["result"]
    #     feeds_list = result["feeds"]
    #     for sub_cookbook_dict in feeds_list:
    #         cookbook_title = sub_cookbook_dict["title"]
    #         relevant_recipe_dict = sub_cookbook_dict["items"]
    #
    #         recipe_list = []
    #
    #         for recipe in relevant_recipe_dict:
    #             my_recipe_dict = {}
    #
    #             id = recipe["id"]
    #             image_url = recipe["image"]
    #             source_url = recipe["link"]
    #             title = recipe["title"]
    #
    #             my_recipe_dict[title] = {"image_url":image_url, "source_url":source_url, "recipe_id":id}
    #             my_recipe_dict = self.getRecipeDetails(my_recipe_dict)
    #             recipe_list.append(my_recipe_dict)
    #             print "Recipe %s completed." % len(recipe_list)
    #     return recipe_list
    #
    # def getRecipeDetails(self, my_recipe_dict):
    #     for k,v in my_recipe_dict.iteritems():
    #         recipe_json = readPage("https://api.yumprint.com/feed/object/%s/?user_token=null" % my_recipe_dict[k]["recipe_id"])
    #     recipe_dict = json.loads(recipe_json)
    #     assert recipe_dict["success"]
    #
    #     sections = recipe_dict["result"]["sections"]
    #
    #     for section in sections:
    #
    #         if section["type"] == "ingredient":
    #             ingredients = []
    #             ingredient_list = section["items"]
    #             for i in ingredient_list:
    #                 ingredients.append(i)
    #             my_recipe_dict[k]["ingredients"] = ingredients
    #
    #         if section["type"] == "method":
    #             directions = []
    #             directions_list = section["items"]
    #             for i in directions_list:
    #                 directions.append(i)
    #             my_recipe_dict[k]["directions"] = directions
    #
    #     return my_recipe_dict
    #
    # def writeResults(self, data, path=None):
    #     if path == None:
    #         path = os.getcwd()
    #
    #     json_file = os.path.join(path, JSON_OUTPUT)
    #     cookbookData = json.dumps(data, indent=4, sort_keys=True)
    #
    #     with codecs.open(json_file, "w", encoding="utf8") as out_file:
    #         out_file.write(cookbookData)
    #     out_file.close()
