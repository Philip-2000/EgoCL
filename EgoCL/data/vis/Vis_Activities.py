
import os

def tiny_change(item):
    return { "category": item.category, "start": item.start_s, "end": item.end_s, "label": item.info }


class VisActivities:
    def __init__(self, ACTIVITIES):
        self.ACTIVITIES = ACTIVITIES
    

    def list_videos(self):
        return [ {"id": activity.name, "title": activity.name} for activity in self.ACTIVITIES ]
    
    def get_annotations(self, video_id):
        activity = self.ACTIVITIES[video_id]
        return [tiny_change(item) for anno in activity.ANNOS.ANNOS for item in activity.ANNOS[anno]]
        #print("Getting video path for video_id:", video_id)
        #print("Available activities:", [activity.name for activity in self.ACTIVITIES])
        #print(list(activity.ANNOS.keys()))
        print("narr", len(activity.ANNOS['narration']))
        print("summ", len(activity.ANNOS['summary']))
        ret = [tiny_change(item) for anno in activity.ANNOS.ANNOS for item in activity.ANNOS[anno]]
        print("ret", len(ret))
        return ret
    
    def get_video_path(self, video_id):
        #print("Getting video path for video_id:", video_id)
        #print("Available activities:", [activity.name for activity in self.ACTIVITIES])
        return self.ACTIVITIES[video_id].VIDEO.path
    
    def get_mime_type(self, video_id):
        return "video/mp4"  # Assuming all videos are mp4 for simplicity