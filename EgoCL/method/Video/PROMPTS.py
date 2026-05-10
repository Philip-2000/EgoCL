def MEMORIZE_PROMPT(MEMORY_CONTEXT, EGO=True, SCREEN_SHOT=False, REFER_CONTEXT=True):
    SYSTEM_PROMPT = ""

    #(1) EGO
    if not EGO:
        if REFER_CONTEXT:
            SYSTEM_PROMPT += "You are a video memory assistant that helps users summarize videos based on the provided video and memory context.\n\
                You will be provided with a video clip and relevant memory context information."
        
            SYSTEM_PROMPT += "Your task is to generate a concise and informative summary of the video using a neutral perspective, incorporating relevant details from the memory context."
        else:
            SYSTEM_PROMPT += "You are a video memory assistant that helps users summarize videos based on the provided video.\
                You will be provided with a video clip."
            
            SYSTEM_PROMPT += "Your task is to generate a concise and informative summary of the video using a neutral perspective, describing the key events and details in the video."
        
    else:
        if REFER_CONTEXT:
            SYSTEM_PROMPT += "You are an egocentric video memory assistant that helps users to summarize based on the provided egocentric video and memory context.\n\
                You will be provided with a video clip and relevant memory context information."
        
            SYSTEM_PROMPT += "Your task is to generate a concise and informative summary of the video by egocentric perspective i.e. use \"I\", \"me\", \"my\", etc., incorporating relevant details from the memory context."
        else:
            SYSTEM_PROMPT += "You are an egocentric video memory assistant that helps users to summarize based on the provided egocentric video.\n\
                You will be provided with a video clip."
            SYSTEM_PROMPT += "Your task is to generate a concise and informative summary of the video by egocentric perspective i.e. use \"I\", \"me\", \"my\", etc., describing the key events and details in the video."


    #(2) TASK
    if SCREEN_SHOT:
        SYSTEM_PROMPT += "Additionally, if you think that there is any key frames that can help illustrate the summary better, please describe the location of the key frames in the video and provide a brief explanation of what is shown in the frame.\n\
        Describe in the format like <frame>25%<description>A person is entering the room</description></frame>. The percentage indicates the position of the frame in the video compared to the total length of the video.\n"        
    else:
        pass
        
        
    SYSTEM_PROMPT += "Do not repeat the memory verbatim; only describe the current situation.\n"


    #(3) MEMORY CONTEXT

    if REFER_CONTEXT:
        MEMORY_PROMPT = "Here is the memory context you can refer to while summarizing the video:\n" + MEMORY_CONTEXT
    else:
        MEMORY_PROMPT = ""
        
    return SYSTEM_PROMPT, MEMORY_PROMPT


def SCREEN_SHOOTING(clip, summary, TIMESPAN, START_NATURAL):
    import re, moviepy#, imageio
    images, descriptions, times = [], [], []
    duration = clip.duration #TIMESPAN.ENDSTAMP.seconds_experience - TIMESPAN.STARTSTAMP.seconds_experience
    
    #START_NATURAL="Day1_11:30:00"  #YYYY_MM_DD_hh:mm:ss
    #shift Day1_00:00:00 to 0 seconds
    STARTSTAMP_seconds_natural = (int(START_NATURAL.split("_")[0].replace("Day",""))-1) * 86400
    STARTSTAMP_seconds_natural += int(START_NATURAL.split("_")[1].split(":")[0]) * 3600 + int(START_NATURAL.split("_")[1].split(":")[1]) * 60 + int(START_NATURAL.split("_")[1].split(":")[2])
    
    for match in re.finditer(r"<frame>(\d+)%<description>(.*?)</description></frame>", summary):
        percentage = min(int(match.group(1)), 95)
        description = match.group(2)

        STAMP_seconds_natural = STARTSTAMP_seconds_natural + duration * (percentage / 100.0)
        timestring = f"Day{1+int(STAMP_seconds_natural // 86400)}_{int((STAMP_seconds_natural % 86400) // 3600):02d}:{int((STAMP_seconds_natural % 3600) // 60):02d}:{int(STAMP_seconds_natural % 60):02d}"
        # Extract frame using moviepy
        # video = moviepy.editor.VideoFileClip(clip.video_path)
        
        frame = clip.get_frame(duration * (percentage / 100.0))
        # Save or process the frame as needed
        # For example, save the frame as an image file
        #imageio.imwrite(f"frame_{percentage}.jpg", frame)
        
        # YOG.debug((f"Extracted frame at {percentage}% ({timestamp}s): {description}"), tag="ScreenShooting")
        images.append(frame)
        descriptions.append(description)
        times.append(timestring)
    summary_cleaned = re.sub(r"<frame>\d+%<description>.*?</description></frame>", "", summary)
    return images, descriptions, times, summary_cleaned

def RESPOND_PROMPT(hits, query, EGO=True, OPTIONAL=False, SCREEN_SHOT=False):
    SYSTEM_PROMPT = ""
    #SYSTEM_PROMPT += "You are a video memory assistant. You should help users recall past events based on their stored memories."
    
    #"Always ensure your answers are grounded in the retrieved content and written in a neutral perspective."

    if not EGO:
        SYSTEM_PROMPT += "You are a video memory assistant. You should help users recall past events based on their stored memories.\n\
        You will be provided with retrieved relevant memories and a user query.\n"
    else:
        SYSTEM_PROMPT += "You are an egocentric video memory assistant. You should help users recall past events based on their stored memories.\n\
        You will be provided with retrieved relevant memories and a user query.\n"
    
    if not OPTIONAL:
        SYSTEM_PROMPT += "You will be provided with retrieved relevant memories and a user query.\n\
        Your task is to generate a concise and informative response that accurately addresses the user's question using the provided memories."
    else:
        SYSTEM_PROMPT += "You will be provided with retrieved relevant memories and a user query, which is a multiple choice question.\n\
        Your task is to choose the closest option that accurately addresses the user's question using the provided memories.\
        Put the option's tag (An UPPER CASE Character) at the beginning of your answer."

    if SCREEN_SHOT:
        SYSTEM_PROMPT += ""
    else:
        SYSTEM_PROMPT += ""

    RAG_PROMPT = "The following are some of your retrieved memories, each one is provided in a dict format with timestamp, text, images or other useful information:\n" + "\n".join([f"{i}. {hit}" for i,hit in enumerate(hits)])
    QUERY_PROMPT = "User Query:\n" + query + "\n"
    
    return SYSTEM_PROMPT, RAG_PROMPT + "\n" + QUERY_PROMPT
    
    #（3）就是截屏的关键字设定，还有截屏的解读，
    #然后还有检测程序，还有存储程序，还有存储的数据结构，还有RAG时的加载程序等等，
    
    #（4）还有就是文本的联合编码问题了。但是这个周日开始再做，对。

# RAG_PROMPT="The following are some of your retrieved memories, each one is provided in a dict format with timestamp, text, images or other useful information:\n"

def SEGMENT_ADJUST_CLIP_PROMPT(_2_CLIP, _1_CLIP):
    raise NotImplementedError("deprecated function")
    OVERALL_PROMPT="Here is two list of descriptions of video clips that continues each other in time order. The second clip comes after the first clip.\
        Your task is to help adjust the clip boundary between these two clips to make the clip division more reasonable and coherent."
    _2_PROMPT="The first clip contains the following description:\n" + "\n".join([f"- clip {i+1}: {clip.data}" for i, clip in enumerate(_2_CLIP.VIDEO_MEM_ATOMS)])
    _1_PROMPT="The second clip contains the following description:\n" + "\n".join([f"- clip {i+1}: {clip.data}" for i, clip in enumerate(_1_CLIP.VIDEO_MEM_ATOMS)])
    INSTRUCTION="Please give the adjustment suggestion as a integer between \"<adjust>\" and \"</adjust>\"tag, indicating how many seconds to shift the boundary between the two clips.\
        A positive integer means shifting the boundary forward in time (i.e., moving some content from the end of the first clip to the start of the second clip),\
        while a negative integer means shifting the boundary backward in time (i.e., moving some content from the start of the second clip to the end of the first clip).\
        For example, if you think the last two clip in the first list should be moved into the second one, you would respond with <adjust>2</adjust>.\
        If no adjustment is needed, please respond with <adjust>0</adjust>."
    return OVERALL_PROMPT + "\n" + INSTRUCTION, _2_PROMPT + "\n" +  _1_PROMPT

def SEGMENT_SEPARATE_CLIP_PROMPT(_1_CLIP):
    raise NotImplementedError("deprecated function")
    OVERALL_PROMPT="Here is a list of descriptions of video clips that form a clip.\
        Your task is to help determine if this clip should be separated into two clips for better organization."
    _1_PROMPT="The clip contains the following descriptions:\n" + "\n".join([f"- clip {i+1}: {clip.data}" for i, clip in enumerate(_1_CLIP.VIDEO_MEM_ATOMS)])
    INSTRUCTION="Please give the separation suggestion as a integer between \"<separate>\" and \"</separate>\"tag, indicating at which clip index (1-based) the clip should be separated into two.\
        For example, if you think the clip should be separated after the third clip, you would respond with <separate>3</separate>.\
        If no separation is needed, please respond with <separate>X</separate>."
    return OVERALL_PROMPT + "\n" + INSTRUCTION, _1_PROMPT 

def SUMMARIZE_CLIP_PROMPT_SIMPLE(_1_CLIP):
    raise NotImplementedError("deprecated function")
    OVERALL_PROMPT="Here is a list of descriptions of video clips that form a clip.\
        Your task is to help generate a concise and informative summary of this clip."
    _1_PROMPT="The clip contains the following descriptions:\n" + "\n".join([f"- clip {i+1}: {clip.data}" for i, clip in enumerate(_1_CLIP.VIDEO_MEM_ATOMS)])
    INSTRUCTION="Please provide a summary that captures the key events and details of the clip."
    return OVERALL_PROMPT + "\n" + INSTRUCTION, _1_PROMPT

def SUMMARIZE_CLIP_PROMPT(_1_CLIP):
    raise NotImplementedError("deprecated function")
    OVERALL_PROMPT="Here is a list of descriptions of video clips that form a clip.\
        Your task is to help generate a concise and informative summary of this clip."
    _1_PROMPT="The clip contains the following descriptions:\n" + "\n".join([f"- clip {i+1}: {clip.data}" for i, clip in enumerate(_1_CLIP.VIDEO_MEM_ATOMS)])
    INSTRUCTION="Please provide a summary that captures the key events and details of the clip, written from an egocentric perspective using \"I\", \"me\", \"my\", etc."
    return OVERALL_PROMPT + "\n" + INSTRUCTION, _1_PROMPT

def MEMORY_ADJUST_SEGMENT_PROMPT(_2_SEGMENT, _1_SEGMENT):
    raise NotImplementedError("deprecated function")
    OVERALL_PROMPT="Here is two list of descriptions of video clips that continues each other in time order. The second list comes after the first list.\
        Your task is to help adjust the clip boundaries between these two segments to make the clip division more reasonable and coherent."
    _2_PROMPT="The first segment contains the following clips:\n" + "\n".join([f"- Clip {i+1}: {clip.meta.get('summary', 'No summary available')}" for i, clip in enumerate(_2_SEGMENT.VIDEO_MEM_CLIPS)])
    _1_PROMPT="The second segment contains the following clips:\n" + "\n".join([f"- Clip {i+1}: {clip.meta.get('summary', 'No summary available')}" for i, clip in enumerate(_1_SEGMENT.VIDEO_MEM_CLIPS)])
    INSTRUCTION="Please give the adjustment suggestion as a integer between \"<adjust>\" and \"</adjust>\"tag, indicating how many seconds to shift the boundary between the two segments.\
        A positive integer means shifting the boundary forward in time (i.e., moving some content from the end of the first segment to the start of the second segment),\
        while a negative integer means shifting the boundary backward in time (i.e., moving some content from the start of the second segment to the end of the first segment).\
        For example, if you think the last two clip in the first list should be moved into the second one, you would respond with <adjust>2</adjust>.\
        If no adjustment is needed, please respond with <adjust>0</adjust>."
    return OVERALL_PROMPT + "\n" + INSTRUCTION, _2_PROMPT + "\n" +  _1_PROMPT

def MEMORY_SEPARATE_SEGMENT_PROMPT(_1_SEGMENT):
    raise NotImplementedError("deprecated function")
    OVERALL_PROMPT="Here is a list of descriptions of video clips that form a segment.\
        Your task is to help determine if this segment should be separated into two segments for better organization."
    _1_PROMPT="The segment contains the following clips:\n" + "\n".join([f"- Clip {i+1}: {clip.meta.get('summary', 'No summary available')}" for i, clip in enumerate(_1_SEGMENT.VIDEO_MEM_CLIPS)])
    INSTRUCTION="Please give the separation suggestion as a integer between \"<separate>\" and \"</separate>\"tag, indicating at which clip index (1-based) the segment should be separated into two.\
        For example, if you think the segment should be separated after the third clip, you would respond with <separate>3</separate>.\
        If no separation is needed, please respond with <separate>X</separate>."
    return OVERALL_PROMPT + "\n" + INSTRUCTION, _1_PROMPT

def SUMMARIZE_SEGMENT_PROMPT_SIMPLE(_1_SEGMENT):
    raise NotImplementedError("deprecated function")
    OVERALL_PROMPT="Here is a list of descriptions of video clips that form a segment.\
        Your task is to help generate a concise and informative summary of this segment."
    _1_PROMPT="The segment contains the following clips:\n" + "\n".join([f"- Clip {i+1}: {clip.meta.get('summary', 'No summary available')}" for i, clip in enumerate(_1_SEGMENT.VIDEO_MEM_CLIPS)])
    INSTRUCTION="Please provide a summary that captures the key events and details of the segment."
    return OVERALL_PROMPT + "\n" + INSTRUCTION, _1_PROMPT

def SUMMARIZE_SEGMENT_PROMPT(_1_SEGMENT):
    raise NotImplementedError("deprecated function")
    OVERALL_PROMPT="Here is a list of descriptions of video clips that form a segment.\
        Your task is to help generate a concise and informative summary of this segment."
    _1_PROMPT="The segment contains the following clips:\n" + "\n".join([f"- Clip {i+1}: {clip.meta.get('summary', 'No summary available')}" for i, clip in enumerate(_1_SEGMENT.VIDEO_MEM_CLIPS)])
    INSTRUCTION="Please provide a summary that captures the key events and details of the segment, written from an egocentric perspective using \"I\", \"me\", \"my\", etc."
    return OVERALL_PROMPT + "\n" + INSTRUCTION, _1_PROMPT
