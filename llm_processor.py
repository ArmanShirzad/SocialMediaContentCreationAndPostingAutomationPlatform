import json
import logging

from groq_client import GroqClient


class LLMVideoAssistant:
    def __init__(self, api_key=None):
        self.logger = logging.getLogger(__name__)
        self.client = GroqClient(api_key)

        logging.basicConfig(level=logging.INFO)

    def generate_keywords(self, caption, max_keywords=5):
        """
        Generate relevant keywords based on the caption.
        Returns a list of clean keywords.
        """
        if not caption:
            self.logger.error("No caption provided for keyword generation")
            return []

        messages = [
            {
                "role": "system",
                "content": (
                    "Extract exactly 5 specific, visual-friendly keywords from the text. "
                    "Return ONLY a comma-separated list of single words or short phrases. "
                    "Example: technology, innovation, computer screen, typing, office"
                )
            },
            {
                "role": "user",
                "content": caption
            }
        ]

        content = self.client.chat(messages, model="llama-3.1-8b-instant",
                                   temperature=0.2)
        self.logger.info(f"Request data: {json.dumps(content)}")
    
        print(content)
        if content:
            # Clean and format keywords
            keywords = [
                keyword.strip().strip("'[]\"")  # Remove quotes, brackets, and whitespace
                for keyword in content.split(',')
                if keyword.strip()
            ]
            self.logger.info(f"Generated keywords: {keywords}")
            return keywords
        return []

    def validate_media(self, caption, video_candidates):
        """
        Validate that the chosen videos align with the post content.
        Uses the vision model to reason about image/video content.
        
        Provide the caption and a summary of each video.
        The LLM returns which are most relevant.
        
        We assume `video_candidates` is a list of dicts, each with keys like:
        {
          "id": ...,
          "url": ...,
          "duration": ...,
          "user": {"id":..., "name":..., "url":...},
          "video_files": [...],
          "tags": ["...","..."]  # If available, else can omit or deduce from context.
        }
        
        The LLM here doesn't have direct vision capabilities to inspect actual frames, 
        but we assume "vision-preview" means it can reason based on provided descriptive metadata.
        
        For best results, provide relevant textual metadata (title, tags) from Pexels.
        """
        if not caption or not video_candidates:
            self.logger.error("Missing caption or video candidates for validation")
            return None

        # Build a representation of the videos
        # We'll provide textual metadata (id, user name, tags if available, and maybe duration)
        video_descriptions = []
        for v in video_candidates:
            desc = (
                f"Video ID: {v.get('id')}\n"
                f"URL: {v.get('url')}\n"
                f"Duration: {v.get('duration', 'N/A')}s\n"
                f"User: {v.get('user', {}).get('name', 'Unknown')}\n"
                f"Possible Tags: {', '.join(v.get('tags', [])) if v.get('tags') else 'No tags'}\n"
            )
            video_descriptions.append(desc)

        combined_description = "\n\n".join(video_descriptions)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a vision-aware assistant that matches textual descriptions of videos to a given caption. "
                    "Given the Instagram caption and several candidate videos with metadata, identify which videos "
                    "are thematically best aligned with the caption. Only return the IDs of the most relevant videos.\n\n"
                    "Instructions:\n"
                    "1- Analyze the caption and the provided video metadata.\n"
                    "2- Choose only the videos that best match the themes/keywords of the caption.\n"
                    "3- Return their IDs in a comma-separated list, with no extra explanation."
                )
            },
            {
                "role": "user",
                "content": f"Caption:\n{caption}\n\nVideos:\n{combined_description}"
            }
        ]

        content = self.client.chat(messages, model="llama-3.2-90b-vision-preview",
                                   temperature=0.1)
        if content:
            # Expecting a comma-separated list of IDs
            chosen_ids = [c.strip() for c in content.split(',') if c.strip().isdigit()]
            # Filter original candidates by chosen IDs
            filtered = [v for v in video_candidates if str(v.get('id')) in chosen_ids]
            return filtered if filtered else []
        return []

    def finalize_caption(self, caption, chosen_videos, keywords):
        """
        Given the chosen videos and keywords, refine the caption to incorporate the keywords naturally 
        and ensure it aligns well with the visuals.
        
        We use the llama-3.1-70b-versatile model since it's good for text refinement.
        """
        if not caption:
            self.logger.error("No initial caption provided for finalization")
            return None

        # Describe chosen videos briefly for context
        video_list_str = ""
        for v in chosen_videos:
            video_list_str += f"Video ID: {v.get('id')}, User: {v.get('user', {}).get('name', 'Unknown')}, Duration: {v.get('duration', 'N/A')}s\n"

        keyword_str = ", ".join(keywords) if keywords else "No specific keywords"

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a creative content editor. You have a draft Instagram caption and some keywords, along "
                    "with a selection of videos chosen for their thematic relevance.\n"
                    "Your task:\n"
                    "1- Integrate the keywords naturally into the caption without breaking coherence.\n"
                    "2- Ensure the caption reflects the theme of the chosen videos.\n"
                    "3- Maintain language quality and formatting.\n"
                    "4- Return only the refined caption."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Original Caption:\n{caption}\n\n"
                    f"Keywords: {keyword_str}\n\n"
                    f"Chosen Videos:\n{video_list_str}"
                )
            }
        ]

        new_caption = self.client.chat(messages, model="llama-3.3-70b-versatile",
                                       temperature=0.3)
        return new_caption

    def generate_video_script(self, instagram_caption: str) -> str:
        """Convert Instagram caption into an engaging 30-second video script"""
        messages = [
            {
                "role": "system",
                "content": (
                    "Convert the given Instagram tech news caption into a 30-second video script. "
                    "The script should be:\n"
                    "1. Engaging and conversational\n"
                    "2. Around 75-85 words (ideal for 30-second narration)\n"
                    "3. Start with a hook\n"
                    "4. Include key points from the original content\n"
                    "5. End with a clear conclusion\n"
                    "Return ONLY the script text, no additional formatting."
                )
            },
            {
                "role": "user",
                "content": instagram_caption
            }
        ]

        content = self.client.chat(messages, model="llama-3.3-70b-versatile",
                                   temperature=0.7)
        if not content:
            self.logger.error("Failed to generate video script")
            return None

        return content
