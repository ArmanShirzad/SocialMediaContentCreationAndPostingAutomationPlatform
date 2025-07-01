import asyncio
import edge_tts
from moviepy import (TextClip, ImageClip, CompositeVideoClip, ColorClip, 
                    concatenate_videoclips, AudioFileClip, VideoFileClip)
from moviepy.video.fx.Resize import Resize
from pathlib import Path
import logging
from gtts import gTTS
import numpy as np
import os
import aiohttp
from config import Config
import textwrap
from llm_processor import LLMVideoAssistant

from moviepy.video.tools.subtitles import SubtitlesClip
import time
from typing import Optional


logger = logging.getLogger(__name__)

class VideoGenerator:
    def __init__(self):
        self.FINAL_HEIGHT = 1920
        self.FINAL_WIDTH = 1080
        self.output_dir = Path("output")
        self.assets_dir = Path("assets")
        self.video_assets_dir = Path("video_assets")
        self.output_dir.mkdir(exist_ok=True)
        self.assets_dir.mkdir(exist_ok=True)
        self.video_assets_dir.mkdir(exist_ok=True)
        self.default_duration = 30
        self.llm_assistant = LLMVideoAssistant(api_key=os.environ.get('GROQ_API_KEY'))  # Requires GROQ_API_KEY in environment

        self.font_path = 'DejaVuSans-Bold'

    async def _create_tts_audio_async(self, text: str, filename="temp_audio.mp3") -> str:
        """Generate TTS audio using Microsoft Edge TTS"""
        try:
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                except PermissionError:
                    base, ext = os.path.splitext(filename)
                    filename = f"{base}_{int(time.time())}{ext}"

            # Create voice instance
            voice = "en-US-AriaNeural"  # Professional female voice
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(filename)
            
            return filename
            
        except Exception as e:
            logger.error(f"Error creating TTS with Edge-TTS: {e}")
            return None

    async def create_video_from_images(self, downloaded_images: list, content: str, 
                                       total_duration: float = None, 
                                       show_text: bool = True) -> str:
        """
        Create video with custom duration and text overlay
        Args:
            downloaded_images: List of image data
            content: Narration text
            total_duration: Total video duration in seconds (overrides TTS duration)
            show_text: Whether to show text overlay
        """
        try:
            # Create audio from content
            audio_file = await self._create_tts_audio_async(content)
            if not audio_file:
                logger.error("Failed to create TTS audio")
                return None

            # Process images with text overlay
            output_path = self._process_images_with_audio(
                images=downloaded_images,
                audio_file=audio_file,
                content=content if show_text else None,
                total_duration=total_duration or self.default_duration
            )

            if os.path.exists(audio_file):
                os.remove(audio_file)

            return output_path

        except Exception as e:
            logger.error(f"Error in video creation: {e}")
            return None

    def create_video_from_stock_footage(self, downloaded_videos: list, content: str) -> str:
        """Create video using downloaded stock footage and generated audio"""
        try:
            # Create audio from content
            audio_file = self.create_tts_audio(content)
            if not audio_file:
                logger.error("Failed to create TTS audio")
                return None

            # Process video
            output_path = self._process_video_with_audio(downloaded_videos, audio_file)

            # Cleanup audio
            if os.path.exists(audio_file):
                os.remove(audio_file)

            return output_path

        except Exception as e:
            logger.error(f"Error in video creation: {e}")
            return None

    def _process_video_with_audio(self, videos: list, audio_file: str) -> str:
        """Internal method to process videos with audio"""
        try:
            if not videos:
                logger.error("No videos to process")
                return None

            audio = AudioFileClip(audio_file)
            duration_per_clip = audio.duration / len(videos)
            clips = []

            for video_data in videos:
                try:
                    video_clip = VideoFileClip(video_data['local_path'])
                    
                    # Handle video duration
                    if video_clip.duration < duration_per_clip:
                        loops_needed = int(np.ceil(duration_per_clip / video_clip.duration))
                        video_clip = concatenate_videoclips([video_clip] * loops_needed)

                    # Resize and set duration
                    video_clip = (video_clip
                        .with_effects([Resize(width=self.FINAL_WIDTH, height=self.FINAL_HEIGHT)])
                        .with_duration(duration_per_clip))

                    # Create background and credits
                    bg = ColorClip(size=(self.FINAL_WIDTH, self.FINAL_HEIGHT), 
                                 color=(0, 0, 0)).with_duration(duration_per_clip)
                    
                    credit = self._create_credit_text(
                        video_data['user']['name'], 
                        video_data['url'],
                        duration_per_clip
                    )

                    # Combine clips
                    combined = CompositeVideoClip(
                        [bg, video_clip.with_position('center'), credit],
                        size=(self.FINAL_WIDTH, self.FINAL_HEIGHT)
                    )
                    clips.append(combined)

                except Exception as e:
                    logger.error(f"Error processing video clip: {e}")
                    continue

            return self._finalize_video(clips, audio)

        except Exception as e:
            logger.error(f"Error in video processing: {e}")
            return None

    def _process_images_with_audio(self, images: list, audio_file: str, 
                                 content: str = None, 
                                 total_duration: float = None) -> str:
        """Internal method to process images with audio and text overlay"""
        try:
            if not images:
                logger.error("No images to process")
                return None

            audio = AudioFileClip(audio_file)
            
            # Use specified duration or audio duration
            video_duration = total_duration or audio.duration
            duration_per_clip = video_duration / len(images)
            
            clips = []
            for idx, img_data in enumerate(images):
                try:
                    # Create image clip without credits
                    img_clip = (ImageClip(img_data['local_path'])
                        .with_effects([Resize(width=self.FINAL_WIDTH, height=self.FINAL_HEIGHT)])
                        .with_duration(duration_per_clip))

                    # Create background
                    bg = ColorClip(
                        size=(self.FINAL_WIDTH, self.FINAL_HEIGHT),
                        color=(0, 0, 0)
                    ).with_duration(duration_per_clip)
                    
                    # Combine without credits
                    combined = CompositeVideoClip(
                        [bg, img_clip.with_position('center')],
                        size=(self.FINAL_WIDTH, self.FINAL_HEIGHT)
                    )
                    clips.append(combined)

                except Exception as e:
                    logger.error(f"Error processing image: {e}")
                    continue

            # Create final video
            final_video = concatenate_videoclips(clips, method="compose")
            
            # Add subtitles if content is provided
            #if content:
             #   subtitles = self._create_subtitles(content, video_duration, len(images))
              #  if subtitles:
               #     final_video = CompositeVideoClip([final_video, subtitles])

            # Add audio
            final_video = final_video.with_audio(audio)
            
            # Write final video
            output_path = str(self.output_dir / "tech_news_video.mp4")
            final_video.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio=True,
                audio_codec='aac',
                threads=4,
                preset='medium'
            )

            return output_path

        except Exception as e:
            logger.error(f"Error in image processing: {e}")
            return None

    def _create_credit_text(self, creator: str, url: str, duration: float) -> TextClip:
        """Create credit text clip"""
        try:
            text = f"Video by {creator} on Pexels"
            return (TextClip(text=text, font_size=30, color='white',
                           font=r"C:\Windows\Fonts\arial.ttf")
                    .with_duration(duration)
                    .with_position(('center', 0.9), relative=True))
        except Exception as e:
            logger.error(f"Error creating credit text: {e}")
            return None

    def _finalize_video(self, clips: list, audio: AudioFileClip) -> str:
        """Finalize video with clips and audio"""
        try:
            if not clips:
                logger.error("No clips to finalize")
                return None

            final_video = concatenate_videoclips(clips, method="compose")
            final_video = final_video.with_audio(audio)
            
            output_path = str(self.output_dir / "tech_news_video.mp4")
            final_video.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio=True,
                audio_codec='aac',
                threads=4,
                preset='medium'
            )

            return output_path

        except Exception as e:
            logger.error(f"Error finalizing video: {e}")
            return None

    async def fetch_pexels_images(self, keywords: list, images_per_keyword: int = 1) -> list:
        """Fetch images from Pexels API"""
        try:
            all_images = []
            
            async with aiohttp.ClientSession() as session:
                for keyword in keywords:
                    headers = {
                        'Authorization': Config.PEXELS_API_KEY
                    }
                    
                    url = "https://api.pexels.com/v1/search"
                    params = {
                        'query': keyword,
                        'per_page': 10,
                        'orientation': 'portrait'
                    }
                    
                    async with session.get(url, headers=headers, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            photos = data.get('photos', [])
                            
                            for photo in photos[:images_per_keyword]:
                                # Download image
                                img_url = photo['src']['large']
                                filename = f"pexels_photo_{photo['id']}_{keyword}.jpg"
                                local_path = self.assets_dir / filename
                                
                                async with session.get(img_url) as img_response:
                                    if img_response.status == 200:
                                        content = await img_response.read()
                                        with open(local_path, 'wb') as f:
                                            f.write(content)
                                            
                                        image_data = {
                                            'local_path': str(local_path),
                                            'photographer': photo['photographer'],
                                            'url': photo['url'],
                                            'user': {'name': photo['photographer']}
                                        }
                                        all_images.append(image_data)
            
            return all_images
            
        except Exception as e:
            logger.error(f"Error fetching Pexels images: {e}")
            return []

    def _create_subtitles(self, content: str, total_duration: float, num_segments: int):
        """Create subtitles from content"""
        try:
            segments = self._split_content(content, num_segments)
            if not segments:
                return None

            duration_per_segment = total_duration / num_segments
            subs = []
            
            # Create individual TextClips for each segment
            for idx, text in enumerate(segments):
                if text.strip():
                    start_time = idx * duration_per_segment
                    
                    # Following exact MoviePy TextClip documentation parameters
                    txt_clip = TextClip(
                        font=r"C:\Windows\Fonts\Arial.ttf",  # Must be path to OpenType font
                        text=text,                           # Text content
                        font_size=70,                        # Size in points
                        color='white',                       # Text color
                        size=(600, None),                    # Width fixed, height auto
                        margin=(None, None),                 # Default margin
                        method='caption',                    # For auto text wrapping
                        text_align='center',                 # Text alignment within box
                        horizontal_align='center',           # Text block alignment in image
                        vertical_align='center',             # Vertical alignment
                        interline=4,                         # Default interline spacing
                        transparent=True,                    # Allow transparency
                        bg_color=None,                       # No background
                        stroke_color=None,                   # No stroke
                        stroke_width=0,                      # No stroke width
                        duration=duration_per_segment        # Clip duration
                    )
                    subs.append(txt_clip)

            if not subs:
                return None

            # Combine all text clips into one
            return CompositeVideoClip(subs)

        except Exception as e:
            logger.error(f"Error creating subtitles: {e}")
            return None

    def _split_content(self, content: str, num_segments: int) -> list:
        """Split content into roughly equal segments"""
        if not content:
            return None
            
        # Split into sentences
        sentences = content.split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Distribute sentences across segments
        segments = []
        sentences_per_segment = max(1, len(sentences) // num_segments)
        
        for i in range(0, len(sentences), sentences_per_segment):
            segment = '. '.join(sentences[i:i + sentences_per_segment])
            if not segment.endswith('.'):
                segment += '.'
            segments.append(segment)
        
        # Pad with empty strings if needed
        while len(segments) < num_segments:
            segments.append("")
            
        return segments[:num_segments]

    def _cleanup_assets(self):
        """Clean up all downloaded assets"""
        try:
            # Clean up image assets
            if self.assets_dir.exists():
                for file_path in self.assets_dir.glob('*'):
                    if file_path.is_file():
                        os.remove(file_path)
                logger.info("Image assets cleaned successfully")

            # Clean up video assets
            if self.video_assets_dir.exists():
                for file_path in self.video_assets_dir.glob('*'):
                    if file_path.is_file():
                        os.remove(file_path)
                logger.info("Video assets cleaned successfully")

        except Exception as e:
            logger.error(f"Error cleaning up assets: {e}")

    async def fetch_pexels_videos(self, keywords: list, videos_per_keyword: int = 1) -> list:
        """Fetch videos from Pexels API"""
        try:
            all_valid_videos = []
            
            async with aiohttp.ClientSession() as session:
                for keyword in keywords:
                    logger.info(f"Fetching videos for keyword: {keyword}")
                    
                    headers = {
                        'Authorization': Config.PEXELS_API_KEY
                    }
                    
                    url = "https://api.pexels.com/videos/search"
                    params = {
                        'query': keyword,
                        'per_page': 10,
                        'orientation': 'portrait',
                        'size': 'medium',
                        'locale': 'en-US'
                    }
                    
                    async with session.get(url, headers=headers, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            videos = data.get('videos', [])
                            
                            # Get valid videos for this keyword
                            keyword_videos = []
                            for video in videos:
                                if self._validate_video(video):
                                    video_file = self._get_best_video_file(video)
                                    if video_file:
                                        filename = f"pexels_video_{video['id']}_{keyword}.mp4"
                                        video_path = self.video_assets_dir / filename
                                        
                                        try:
                                            async with session.get(video_file['link']) as video_response:
                                                if video_response.status == 200:
                                                    video_content = await video_response.read()
                                                    with open(video_path, 'wb') as f:
                                                        f.write(video_content)
                                                    
                                                    video['local_path'] = str(video_path)
                                                    video['search_keyword'] = keyword
                                                    keyword_videos.append(video)
                                                    
                                                    if len(keyword_videos) >= videos_per_keyword:
                                                        break
                                        except Exception as e:
                                            logger.error(f"Error downloading video: {e}")
                                            continue
                            
                            all_valid_videos.extend(keyword_videos)
            
            return all_valid_videos

        except Exception as e:
            logger.error(f"Error fetching Pexels videos: {e}")
            return []

    def _validate_video(self, video: dict) -> bool:
        """Validate video meets requirements"""
        try:
            if not all(key in video for key in ['id', 'duration', 'video_files']):
                return False

            if not (5 <= video['duration'] <= 30):
                return False

            valid_file = False
            for file in video['video_files']:
                if (file.get('quality') in ['hd', 'sd'] and 
                    file.get('file_type') == 'video/mp4' and 
                    file.get('width') and file.get('height')):
                    if file['height'] > file['width']:
                        valid_file = True
                        break

            return valid_file

        except Exception as e:
            logger.error(f"Error validating video: {e}")
            return False

    def _get_best_video_file(self, video: dict) -> Optional[dict]:
        """Get the best quality video file that meets requirements"""
        video_files = [
            f for f in video['video_files']
            if (f['quality'] in ['hd', 'sd'] and 
                f['file_type'] == 'video/mp4' and 
                f['width'] and f['height'] and
                f['height'] > f['width'])
        ]
        
        if not video_files:
            return None
        
        return sorted(
            video_files,
            key=lambda x: (x['quality'] == 'hd', x['height'], x['width']),
            reverse=True
        )[0]

    async def generate_video(self, content: str, use_videos: bool = False, 
                           total_duration: float = None, show_text: bool = True) -> str:
        """Main method to generate video from content"""
        try:
            # Generate keywords from content
      
            
            keywords = self.llm_assistant.generate_keywords(content)
            if not keywords:
                logger.error("Failed to generate keywords")
                return None

            if use_videos:
                # Fetch and process videos
                logger.info(f"Fetching videos for keywords: {keywords}")
                videos = await self.fetch_pexels_videos(keywords, videos_per_keyword=1)
                if not videos:
                    logger.error("Failed to fetch videos")
                    return None

                output_path = await self.create_video_from_stock_footage(videos, content)
            else:
                # Fetch and process images
                logger.info(f"Fetching images for keywords: {keywords}")
                images = await self.fetch_pexels_images(keywords, images_per_keyword=1)
                if not images:
                    logger.error("Failed to fetch images")
                    return None

                output_path = await self.create_video_from_images(
                    downloaded_images=images,
                    content=content,
                    total_duration=total_duration,
                    show_text=show_text
                )

            if output_path:
                logger.info(f"Video generated successfully at: {output_path}")
                self._cleanup_assets()
                return output_path
            
            return None

        except Exception as e:
            logger.error(f"Error in video generation: {e}")
            self._cleanup_assets()  # Clean up on error
            return None