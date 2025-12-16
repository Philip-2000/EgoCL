
def itemParse(path): #path is the path to the item.yaml file, and all the paths in the file are relative to the location of item.yaml, so we need to convert them to absolute paths
    import yaml, os
    with open(path, 'r') as f:
        item_data = yaml.safe_load(f)
        if "item_file" in item_data and len(item_data["item_file"])>0:
            item_data["item_file"] = os.path.join(os.path.dirname(path), item_data["item_file"])
        for dataset_name in item_data.get("datasets", {}):
            if "item_file" in item_data["datasets"][dataset_name] and len(item_data["datasets"][dataset_name]["item_file"])>0:
                item_data["datasets"][dataset_name]["item_file"] = os.path.join(os.path.dirname(path), item_data["datasets"][dataset_name]["item_file"])
    return item_data