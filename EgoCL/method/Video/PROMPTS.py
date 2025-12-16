def MEMORIZE_PROMPT_SIMPLE(MEMORY_CONTEXT):
    SYSTEM_PROMPT = "You are a video memory assistant that helps users summarize videos based on the provided video and memory context.\
        You will be provided with a video clip and relevant memory context information.\
        Your task is to generate a concise and informative summary of the video using a neutral perspective,\
        incorporating relevant details from the memory context.\
        Do not repeat the memory verbatim; only describe the current situation.\n"
    MEMORY_PROMPT = "Here is the memory context you can refer to while summarizing the video:\n" + MEMORY_CONTEXT
    FINAL_PROMPT = "Referring to the memory mentioned above, please summarize the following video."
    return SYSTEM_PROMPT + "\n" + MEMORY_PROMPT + "\n" + FINAL_PROMPT

RESPOND_PROMPT_SIMPLE = "You are a video memory assistant that helps users recall past events based on their stored memories.\
    You will be provided with retrieved relevant memories and a user query.\
    Your task is to generate a concise and informative response that accurately addresses the user's question using the provided memories.\
    Always ensure your answers are grounded in the retrieved content and written in a neutral perspective."

RESPOND_PROMPT_SIMPLE_OPTIONAL = "You are a video memory assistant that helps users recall past events based on their stored memories.\
    You will be provided with retrieved relevant memories and a user query, which is a multiple choice question.\
    Your task is to choose the closest option that accurately addresses the user's question using the provided memories.\
    Put the option's tag (An UPPER CASE Character) at the beginning of your answer.\
    Always ensure your answers are grounded in the retrieved content and written in a neutral perspective."

def MEMORIZE_PROMPT(MEMORY_CONTEXT):
    SYSTEM_PROMPT = "You are an egocentric video memory assistant that helps users to summarize based on the provided egocentric video and memory context.\
        You will be provided with a video clip and relevant memory context information.\
        Your task is to generate a concise and informative summary of the video by egocentric perspective i.e. use \"I\", \"me\", \"my\", etc., incorporating relevant details from the memory context.\
        But don't repeat the memory anymore, only describe the current situation.\n"
    MEMORY_PROMPT = "Here is the memory context you can refer to while summarizing the video:\n" + MEMORY_CONTEXT
    FINAL_PROMPT = "Refering to the memory mentioned above, please summarize the following video"
    return SYSTEM_PROMPT + "\n" + MEMORY_PROMPT + "\n" + FINAL_PROMPT

RESPOND_PROMPT="You are a egocentric memory assistant that helps users to recall past events based on their stored memories.\
    You will be provided with retrieved relevant memories and a user query.\
    Your task is to generate a concise and informative response that accurately addresses the user's question using the provided memories.\
    Always ensure your answers are grounded in the retrieved content."

RESPOND_PROMPT_OPTIONAL="You are a egocentric memory assistant that helps users to recall past events based on their stored memories.\
    You will be provided with retrieved relevant memories and a user query, which is a multiple choice question.\
    Your task is to choose the closest option that accurately addresses the user's question using the provided memories.\
    Put the option's tag (An UPPER CASE Character) at the beginning of your answer.\
    Always ensure your answers are grounded in the retrieved content."
        
RAG_PROMPT="The following are some of your retrieved memories, each one is provided in a dict format with timestamp, text, images or other useful information:\n"

def SEGMENT_ADJUST_CLIP_PROMPT(_2_CLIP, _1_CLIP):
    OVERALL_PROMPT="Here is two list of descriptions of video clips that continues each other in time order. The second clip comes after the first clip.\
        Your task is to help adjust the clip boundary between these two clips to make the clip division more reasonable and coherent."
    _2_PROMPT="The first clip contains the following description:\n" + "\n".join([f"- clip {i+1}: {clip.data}" for i, clip in enumerate(_2_CLIP.VIDEO_MEM_ATOMS)])
    _1_PROMPT="The second clip contains the following description:\n" + "\n".join([f"- clip {i+1}: {clip.data}" for i, clip in enumerate(_1_CLIP.VIDEO_MEM_ATOMS)])
    INSTRUCTION="Please give the adjustment suggestion as a integer between \"<adjust>\" and \"</adjust>\"tag, indicating how many seconds to shift the boundary between the two clips.\
        A positive integer means shifting the boundary forward in time (i.e., moving some content from the end of the first clip to the start of the second clip),\
        while a negative integer means shifting the boundary backward in time (i.e., moving some content from the start of the second clip to the end of the first clip).\
        For example, if you think the last two clip in the first list should be moved into the second one, you would respond with <adjust>2</adjust>.\
        If no adjustment is needed, please respond with <adjust>0</adjust>."
    return OVERALL_PROMPT + "\n" + _2_PROMPT + "\n" +  _1_PROMPT +  "\n" + INSTRUCTION

def SEGMENT_SEPARATE_CLIP_PROMPT(_1_CLIP):
    OVERALL_PROMPT="Here is a list of descriptions of video clips that form a clip.\
        Your task is to help determine if this clip should be separated into two clips for better organization."
    _1_PROMPT="The clip contains the following descriptions:\n" + "\n".join([f"- clip {i+1}: {clip.data}" for i, clip in enumerate(_1_CLIP.VIDEO_MEM_ATOMS)])
    INSTRUCTION="Please give the separation suggestion as a integer between \"<separate>\" and \"</separate>\"tag, indicating at which clip index (1-based) the clip should be separated into two.\
        For example, if you think the clip should be separated after the third clip, you would respond with <separate>3</separate>.\
        If no separation is needed, please respond with <separate>X</separate>."
    return OVERALL_PROMPT + "\n" + _1_PROMPT +  "\n" + INSTRUCTION

def SUMMARIZE_CLIP_PROMPT_SIMPLE(_1_CLIP):
    OVERALL_PROMPT="Here is a list of descriptions of video clips that form a clip.\
        Your task is to help generate a concise and informative summary of this clip."
    _1_PROMPT="The clip contains the following descriptions:\n" + "\n".join([f"- clip {i+1}: {clip.data}" for i, clip in enumerate(_1_CLIP.VIDEO_MEM_ATOMS)])
    INSTRUCTION="Please provide a summary that captures the key events and details of the clip."
    return OVERALL_PROMPT + "\n" + _1_PROMPT +  "\n" + INSTRUCTION

def SUMMARIZE_CLIP_PROMPT(_1_CLIP):
    OVERALL_PROMPT="Here is a list of descriptions of video clips that form a clip.\
        Your task is to help generate a concise and informative summary of this clip."
    _1_PROMPT="The clip contains the following descriptions:\n" + "\n".join([f"- clip {i+1}: {clip.data}" for i, clip in enumerate(_1_CLIP.VIDEO_MEM_ATOMS)])
    INSTRUCTION="Please provide a summary that captures the key events and details of the clip, written from an egocentric perspective using \"I\", \"me\", \"my\", etc."
    return OVERALL_PROMPT + "\n" + _1_PROMPT +  "\n" + INSTRUCTION

def MEMORY_ADJUST_SEGMENT_PROMPT(_2_SEGMENT, _1_SEGMENT):
    OVERALL_PROMPT="Here is two list of descriptions of video clips that continues each other in time order. The second list comes after the first list.\
        Your task is to help adjust the clip boundaries between these two segments to make the clip division more reasonable and coherent."
    _2_PROMPT="The first segment contains the following clips:\n" + "\n".join([f"- Clip {i+1}: {clip.meta.get('summary', 'No summary available')}" for i, clip in enumerate(_2_SEGMENT.VIDEO_MEM_CLIPS)])
    _1_PROMPT="The second segment contains the following clips:\n" + "\n".join([f"- Clip {i+1}: {clip.meta.get('summary', 'No summary available')}" for i, clip in enumerate(_1_SEGMENT.VIDEO_MEM_CLIPS)])
    INSTRUCTION="Please give the adjustment suggestion as a integer between \"<adjust>\" and \"</adjust>\"tag, indicating how many seconds to shift the boundary between the two segments.\
        A positive integer means shifting the boundary forward in time (i.e., moving some content from the end of the first segment to the start of the second segment),\
        while a negative integer means shifting the boundary backward in time (i.e., moving some content from the start of the second segment to the end of the first segment).\
        For example, if you think the last two clip in the first list should be moved into the second one, you would respond with <adjust>2</adjust>.\
        If no adjustment is needed, please respond with <adjust>0</adjust>."
    return OVERALL_PROMPT + "\n" + _2_PROMPT + "\n" +  _1_PROMPT +  "\n" + INSTRUCTION

def MEMORY_SEPARATE_SEGMENT_PROMPT(_1_SEGMENT):
    OVERALL_PROMPT="Here is a list of descriptions of video clips that form a segment.\
        Your task is to help determine if this segment should be separated into two segments for better organization."
    _1_PROMPT="The segment contains the following clips:\n" + "\n".join([f"- Clip {i+1}: {clip.meta.get('summary', 'No summary available')}" for i, clip in enumerate(_1_SEGMENT.VIDEO_MEM_CLIPS)])
    INSTRUCTION="Please give the separation suggestion as a integer between \"<separate>\" and \"</separate>\"tag, indicating at which clip index (1-based) the segment should be separated into two.\
        For example, if you think the segment should be separated after the third clip, you would respond with <separate>3</separate>.\
        If no separation is needed, please respond with <separate>X</separate>."
    return OVERALL_PROMPT + "\n" + _1_PROMPT +  "\n" + INSTRUCTION

def SUMMARIZE_SEGMENT_PROMPT_SIMPLE(_1_SEGMENT):
    OVERALL_PROMPT="Here is a list of descriptions of video clips that form a segment.\
        Your task is to help generate a concise and informative summary of this segment."
    _1_PROMPT="The segment contains the following clips:\n" + "\n".join([f"- Clip {i+1}: {clip.meta.get('summary', 'No summary available')}" for i, clip in enumerate(_1_SEGMENT.VIDEO_MEM_CLIPS)])
    INSTRUCTION="Please provide a summary that captures the key events and details of the segment."
    return OVERALL_PROMPT + "\n" + _1_PROMPT +  "\n" + INSTRUCTION

def SUMMARIZE_SEGMENT_PROMPT(_1_SEGMENT):
    OVERALL_PROMPT="Here is a list of descriptions of video clips that form a segment.\
        Your task is to help generate a concise and informative summary of this segment."
    _1_PROMPT="The segment contains the following clips:\n" + "\n".join([f"- Clip {i+1}: {clip.meta.get('summary', 'No summary available')}" for i, clip in enumerate(_1_SEGMENT.VIDEO_MEM_CLIPS)])
    INSTRUCTION="Please provide a summary that captures the key events and details of the segment, written from an egocentric perspective using \"I\", \"me\", \"my\", etc."
    return OVERALL_PROMPT + "\n" + _1_PROMPT +  "\n" + INSTRUCTION