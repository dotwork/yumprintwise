import json
import os

# name = 'carlos_velez'
name = 'deb'


filename = f'/home/carlos/projects/mylibrary/yumprintwise/{name}_yumprint_recipes.json'
with open(filename) as f:
    COOKBOOKS = json.loads(f.read())
with open('/home/carlos/projects/mylibrary/yumprintwise/main_page_template.html') as f:
    main_page_template = f.read()
with open('/home/carlos/projects/mylibrary/yumprintwise/cookbook_template.html') as f:
    cookbook_template = f.read()


dir_path = os.path.join(os.path.dirname(__file__), name)
os.makedirs(dir_path, exist_ok=True)

main_data = []
for cookbook in COOKBOOKS:
    _id = cookbook['id'].split('-')[-1]
    filepath = os.path.join(dir_path, f'cookbook_{_id}.html')
    image = None
    for recipe in cookbook['items']:
        if recipe['image']:
            image = recipe['image']
            break
    main_data.append(dict(
        filepath=f'cookbook_{_id}.html',
        title=cookbook['title'],
        image=image,
    ))
    cookbook_data = dict(
        title=cookbook['title'],
        recipes=[]
    )
    for recipe in cookbook['items']:
        cookbook_data['recipes'].append(dict(
            id=recipe["id"],
            title=recipe['title'],
            image=recipe['image'],
            link=recipe['link'],
            ingredients=recipe['ingredient'],
            directions=recipe['method'],
        ))

    json_filename = f'cookbook_{_id}.json'
    with open(os.path.join(dir_path, json_filename), mode='w') as f:
        f.write(json.dumps(cookbook_data))

    with open(os.path.join(dir_path, f'cookbook_{_id}.html'), mode='w') as f:
        html = cookbook_template.replace("{{ JSON_FILEPATH }}", json_filename).replace(
            "{{ MAIN_PAGE_FILEPATH }}", f'{name}_main_page.html')
        f.write(html)

with open(os.path.join(dir_path, f'{name}_main_page.html'), mode='w') as f:
    f.write(main_page_template.replace('{{ JSON_DATA }}', json.dumps(main_data)))


with open('style.css') as f:
    css = f.read()
with open(os.path.join(dir_path, 'style.css'), mode='w') as f:
    f.write(css)


