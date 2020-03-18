
from tortoises.scholar.wos import AppWebKnowledge

apk = AppWebKnowledge()
argument = 'climate change'
apk.fetch_home()
apk.search(argument=argument, mode='topic')
apk.search_init()

for _ in range(apk.num_pages):
    for idx in range(apk.num_items_current_page):
        apk.fetch_current_page(index=idx)
        if apk.parse_doi() and apk.parse_abstract():
            apk.expand_all_fields()
            print(apk.parse_article())
        apk.switch_handle()
    apk.next_page()


# import sys
# sys.path.append('/home/wchen/project/tortoises')


# from tortoises.scholar.wos import AppWebKnowledge, AppWebKnowledgeParser
# import json
#
# apk = AppWebKnowledge(headless=False, verbose=True, mode='slow')
#
# topic = 'global warming'
# apk.fetch_home()
# apk.search(argument=topic, mode='topic')
# apk.search_init()
#
# infos = []
#
# for _ in range(apk.num_pages):
#     try:
#         for idx in range(apk.num_items_current_page):
#             apk.fetch_current_page(index=idx)
#             parser = AppWebKnowledgeParser(verbose=False).parse_article(apk.driver)
#             infos.append(parser.parsed_info)
#             apk.switch_handle()
#         apk.next_page()
#     except Exception as e:
#         print(e)
#         continue
#
#
# with open('download/infos.json', 'w') as f:
#     json.dump(infos, f)
