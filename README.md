I've created a Python script that downloads YouTube videos and embeds their closed captions directly into the video. Here's how it works:
Key Features

Downloads YouTube videos using the pytube library
Extracts closed captions using the youtube_transcript_api library
Embeds the captions into the video using moviepy
Handles different YouTube URL formats
Supports different caption languages

How to Use It

Install the required dependencies:
pip install pytube youtube_transcript_api moviepy
(You'll also need ffmpeg installed on your system)
Run the script with a YouTube URL:
python youtube_caption_extractor.py https://www.youtube.com/watch?v=VIDEO_ID

Additional options:

-o or --output to specify the output file path
-l or --language to specify the caption language code
-t or --temp-dir to specify a temporary directory for downloaded files



How It Works

The script extracts the video ID from the YouTube URL
Downloads the video using pytube
Uses the YouTube Transcript API to fetch available captions
Creates text clips for each caption with proper timing
Combines the original video with the text clips
Saves the final video with embedded captions
