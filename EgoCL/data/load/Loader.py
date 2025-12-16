def loader(args, use_tqdm: bool = True):
    import yaml, os
    from .. import UNI_PATHS_GLOBAL
    from ..elements.Activity import Activity, Activities
    from .. import itemParse
    from tqdm import tqdm
    activities = []
    item_config = itemParse(args.item_config)
    
    for dataset_name in item_config['datasets']:
        lst = []
        if len(item_config['datasets'][dataset_name].get('items', [])) > 0:
            lst = item_config['datasets'][dataset_name]['items'].copy()
        elif len(item_config['datasets'][dataset_name].get('item_file', '')) > 0 and os.path.exists(item_config['datasets'][dataset_name]['item_file']):
            lst = open(item_config['datasets'][dataset_name]['item_file'], 'r').read().splitlines()
        else:
            lst = os.listdir(UNI_PATHS_GLOBAL[dataset_name])
        
        
        num = item_config['datasets'][dataset_name]['num'] if "num" in item_config['datasets'][dataset_name] else item_config['base'].get('num', -1)
        if num > 0: lst = lst[:num]
        
        activities = [Activity() for _ in range(len(lst))]
        if not use_tqdm:
            for i, item in enumerate(lst): activities[i].load(os.path.join(UNI_PATHS_GLOBAL[dataset_name], f"{item}_activity.json"))
            continue
        t = tqdm(lst)
        for i, item in enumerate(t):
            t.set_description("loading: " + item[:8])
            activities[i].load(os.path.join(UNI_PATHS_GLOBAL[dataset_name], f"{item}_activity.json"))
    return Activities(activities)
