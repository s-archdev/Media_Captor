#!/usr/bin/env python3
"""
YouTube Caption Extractor and Embedder

This script downloads a YouTube video, extracts its closed captions,
and creates a new video with the captions embedded directly in the video.

Requirements:
- pytube
- youtube_transcript_api
- moviepy
- ffmpeg (system dependency)

Install dependencies with:
pip install pytube youtube_transcript_api moviepy
"""

import os
import argparse
import tempfile
from typing import List, Dict, Any

# YouTube video download
from pytube import YouTube

# Caption extraction
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

# Video processing
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.config import change_settings

# Configure MoviePy to use the correct ffmpeg binary if needed
# Uncomment and modify if ffmpeg is not in your PATH
# change_settings({"FFMPEG_BINARY": "/path/to/ffmpeg"})

def download_youtube_video(url: str, output_path: str = None) -> str:
    """
    Download a YouTube video.
    
    Args:
        url: YouTube video URL
        output_path: Directory to save the video (default is current directory)
    
    Returns:
        Path to the downloaded video file
    """
    print(f"Downloading video from {url}...")
    yt = YouTube(url)
    video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    
    if output_path is None:
        output_path = os.getcwd()
    
    video_path = video.download(output_path)
    print(f"Video downloaded to {video_path}")
    return video_path

def get_video_captions(video_id: str, language: str = 'en') -> List[Dict[str, Any]]:
    """
    Extract captions from a YouTube video.
    
    Args:
        video_id: YouTube video ID
        language: Preferred caption language (default is English)
    
    Returns:
        List of caption dictionaries with 'text', 'start', and 'duration' keys
    """
    try:
        print(f"Extracting captions for video {video_id}...")
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        try:
            # Try to get the specified language
            transcript = transcript_list.find_transcript([language])
        except NoTranscriptFound:
            # If specified language not found, get any available transcript
            transcript = transcript_list.find_transcript([])
        
        captions = transcript.fetch()
        print(f"Found {len(captions)} caption entries")
        return captions
    
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        print(f"Error: {str(e)}")
        return []

def add_captions_to_video(video_path: str, captions: List[Dict[str, Any]], output_path: str) -> str:
    """
    Add captions to a video file.
    
    Args:
        video_path: Path to video file
        captions: List of caption dictionaries
        output_path: Path to save the output video
    
    Returns:
        Path to the output video file
    """
    print("Adding captions to video...")
    video = VideoFileClip(video_path)
    
    # Create TextClips for each caption and set their duration and start times
    text_clips = []
    for caption in captions:
        start_time = caption['start']
        duration = caption.get('duration', 5)  # Default to 5 seconds if duration not specified
        text = caption['text']
        
        # Create text clip for this caption
        text_clip = (TextClip(text, fontsize=24, color='white', bg_color='black',
                             stroke_color='black', stroke_width=1.5)
                    .set_position(('center', 'bottom'))
                    .set_start(start_time)
                    .set_duration(duration))
        
        text_clips.append(text_clip)
    
    # Combine the original video with all text clips
    final_video = CompositeVideoClip([video] + text_clips)
    
    # Write the result to a file
    final_video.write_videofile(output_path, codec='libx264')
    
    # Close the clips to free up resources
    video.close()
    final_video.close()
    
    return output_path

def extract_video_id(url: str) -> str:
    """
    Extract the video ID from a YouTube URL.
    
    Args:
        url: YouTube video URL
    
    Returns:
        YouTube video ID
    """
    # Handle URLs in different formats
    if 'youtu.be/' in url:
        # Format: https://youtu.be/VIDEO_ID
        return url.split('youtu.be/')[1].split('?')[0]
    elif 'youtube.com/watch' in url:
        # Format: https://www.youtube.com/watch?v=VIDEO_ID
        from urllib.parse import parse_qs, urlparse
        query = urlparse(url).query
        return parse_qs(query)['v'][0]
    else:
        raise ValueError("Invalid YouTube URL format")

def main():
    parser = argparse.ArgumentParser(description='Download YouTube video and embed its captions.')
    parser.add_argument('url', help='YouTube video URL')
    parser.add_argument('-o', '--output', help='Output file path', default='output_with_captions.mp4')
    parser.add_argument('-l', '--language', help='Caption language code (default: en)', default='en')
    parser.add_argument('-t', '--temp-dir', help='Temporary directory for downloaded files', default=None)
    
    args = parser.parse_args()
    
    try:
        # Use temporary directory if not specified
        temp_dir = args.temp_dir if args.temp_dir else tempfile.mkdtemp()
        os.makedirs(temp_dir, exist_ok=True)
        
        # Extract video ID
        video_id = extract_video_id(args.url)
        
        # Download video
        video_path = download_youtube_video(args.url, temp_dir)
        
        # Get captions
        captions = get_video_captions(video_id, args.language)
        
        if not captions:
            print("No captions found for this video. The output will be the original video without captions.")
            # Just copy the original video to the output path
            import shutil
            shutil.copy(video_path, args.output)
        else:
            # Add captions to video
            output_path = add_captions_to_video(video_path, captions, args.output)
            print(f"Video with embedded captions saved to {output_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
