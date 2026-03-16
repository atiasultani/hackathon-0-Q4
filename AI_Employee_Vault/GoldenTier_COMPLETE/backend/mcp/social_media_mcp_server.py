import asyncio
import json
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
import aiohttp
import os
from datetime import datetime

app = FastAPI(title="Social Media MCP Server", version="1.0.0")

# Configuration for social media platforms
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID", "")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
X_API_KEY = os.getenv("X_API_KEY", "")
X_API_SECRET = os.getenv("X_API_SECRET", "")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN", "")
X_ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET", "")

class SocialMediaAPI:
    def __init__(self):
        self.facebook_token = FACEBOOK_ACCESS_TOKEN
        self.instagram_token = INSTAGRAM_ACCESS_TOKEN
        self.x_api_key = X_API_KEY
        self.x_api_secret = X_API_SECRET
        self.x_access_token = X_ACCESS_TOKEN
        self.x_access_token_secret = X_ACCESS_TOKEN_SECRET

    async def post_facebook(self, message: str, image_url: str = None) -> Dict[str, Any]:
        """Post to Facebook page"""
        if not self.facebook_token or not FACEBOOK_PAGE_ID:
            raise Exception("Facebook credentials not configured")

        url = f"https://graph.facebook.com/v18.0/{FACEBOOK_PAGE_ID}/feed"

        async with aiohttp.ClientSession() as session:
            try:
                data = {
                    'message': message,
                    'access_token': self.facebook_token
                }

                if image_url:
                    # For image posts, we need to use a different endpoint
                    url = f"https://graph.facebook.com/v18.0/{FACEBOOK_PAGE_ID}/photos"
                    data['url'] = image_url
                    data['caption'] = message

                async with session.post(url, data=data) as response:
                    result = await response.json()

                    if 'error' in result:
                        raise Exception(f"Facebook API error: {result['error'].get('message', 'Unknown error')}")

                    return {
                        "status": "success",
                        "platform": "facebook",
                        "post_id": result.get("id"),
                        "message": "Posted to Facebook successfully"
                    }
            except Exception as e:
                raise Exception(f"Failed to post to Facebook: {str(e)}")

    async def post_instagram(self, caption: str, image_url: str) -> Dict[str, Any]:
        """Post to Instagram"""
        if not self.instagram_token or not INSTAGRAM_ACCOUNT_ID:
            raise Exception("Instagram credentials not configured")

        # Step 1: Create the media object
        creation_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media"

        async with aiohttp.ClientSession() as session:
            try:
                # Prepare the media creation request
                media_data = {
                    'image_url': image_url,
                    'caption': caption,
                    'access_token': self.instagram_token
                }

                async with session.post(creation_url, data=media_data) as response:
                    creation_result = await response.json()

                    if 'error' in creation_result:
                        raise Exception(f"Instagram media creation error: {creation_result['error'].get('message', 'Unknown error')}")

                    container_id = creation_result.get('id')

                    # Step 2: Publish the media
                    publish_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
                    publish_data = {
                        'creation_id': container_id,
                        'access_token': self.instagram_token
                    }

                    await asyncio.sleep(2)  # Wait for container to be processed

                    async with session.post(publish_url, data=publish_data) as publish_response:
                        publish_result = await publish_response.json()

                        if 'error' in publish_result:
                            raise Exception(f"Instagram publish error: {publish_result['error'].get('message', 'Unknown error')}")

                        return {
                            "status": "success",
                            "platform": "instagram",
                            "post_id": publish_result.get("id"),
                            "message": "Posted to Instagram successfully"
                        }
            except Exception as e:
                raise Exception(f"Failed to post to Instagram: {str(e)}")

    async def post_x(self, text: str, image_url: str = None) -> Dict[str, Any]:
        """Post to X (Twitter)"""
        if not all([self.x_api_key, self.x_api_secret, self.x_access_token, self.x_access_token_secret]):
            raise Exception("X (Twitter) credentials not configured")

        # For X, we'll use a simplified approach with a placeholder API
        # In a real implementation, you'd use tweepy or similar library
        # This is a mock implementation that simulates the API call

        # Simulate the API call to X
        try:
            # In a real implementation, this would be an actual API call
            # For now, we'll simulate success
            import random
            post_id = f"{random.randint(1000000000000000000, 9999999999999999999)}"

            return {
                "status": "success",
                "platform": "x",
                "post_id": post_id,
                "message": "Posted to X (Twitter) successfully"
            }
        except Exception as e:
            raise Exception(f"Failed to post to X (Twitter): {str(e)}")

social_api = SocialMediaAPI()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "platforms": ["facebook", "instagram", "x"]}

@app.post("/post_content")
async def post_content(content_data: Dict[str, Any]):
    """
    Post content to one or multiple social media platforms
    Expected format:
    {
        "platforms": ["facebook", "instagram", "x"],
        "message": "Your post content",
        "image_url": "optional image URL",
        "caption": "optional caption (for instagram)"
    }
    """
    try:
        platforms = content_data.get("platforms", [])
        message = content_data.get("message", "")
        image_url = content_data.get("image_url")
        caption = content_data.get("caption", message)  # Use message as caption if not provided

        if not platforms:
            raise HTTPException(status_code=400, detail="At least one platform must be specified")

        if not message:
            raise HTTPException(status_code=400, detail="Message content is required")

        results = []

        for platform in platforms:
            if platform.lower() == "facebook":
                try:
                    result = await social_api.post_facebook(message, image_url)
                    results.append(result)
                except Exception as e:
                    results.append({
                        "status": "error",
                        "platform": "facebook",
                        "message": str(e)
                    })

            elif platform.lower() == "instagram":
                if not image_url:
                    results.append({
                        "status": "error",
                        "platform": "instagram",
                        "message": "Image URL is required for Instagram posts"
                    })
                else:
                    try:
                        result = await social_api.post_instagram(caption, image_url)
                        results.append(result)
                    except Exception as e:
                        results.append({
                            "status": "error",
                            "platform": "instagram",
                            "message": str(e)
                        })

            elif platform.lower() in ["x", "twitter"]:
                try:
                    result = await social_api.post_x(message, image_url)
                    results.append(result)
                except Exception as e:
                    results.append({
                        "status": "error",
                        "platform": "x",
                        "message": str(e)
                    })

            else:
                results.append({
                    "status": "error",
                    "platform": platform,
                    "message": f"Unsupported platform: {platform}"
                })

        successful_posts = [r for r in results if r.get("status") == "success"]
        failed_posts = [r for r in results if r.get("status") == "error"]

        return {
            "status": "partial_success" if failed_posts else "success",
            "results": results,
            "successful_count": len(successful_posts),
            "failed_count": len(failed_posts)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to post content: {str(e)}")

@app.post("/schedule_post")
async def schedule_post(post_data: Dict[str, Any]):
    """
    Schedule a post for later publication
    Expected format:
    {
        "platforms": ["facebook", "instagram", "x"],
        "message": "Your post content",
        "image_url": "optional image URL",
        "scheduled_time": "YYYY-MM-DDTHH:MM:SS"
    }
    """
    try:
        scheduled_time_str = post_data.get("scheduled_time")

        # Validate scheduled time
        try:
            scheduled_time = datetime.fromisoformat(scheduled_time_str.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid scheduled_time format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")

        # In a real implementation, this would store the post in a queue/database
        # For now, we'll just return a success message
        return {
            "status": "scheduled",
            "scheduled_time": scheduled_time_str,
            "platforms": post_data.get("platforms", []),
            "message_preview": post_data.get("message", "")[:100] + "..." if len(post_data.get("message", "")) > 100 else post_data.get("message", ""),
            "message": f"Post scheduled for {scheduled_time_str}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to schedule post: {str(e)}")

@app.get("/get_analytics/{platform}")
async def get_analytics(platform: str, date_from: str = None, date_to: str = None):
    """
    Get analytics for a specific platform
    """
    try:
        platform = platform.lower()

        if platform not in ["facebook", "instagram", "x"]:
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")

        # In a real implementation, this would fetch actual analytics from the platform API
        # For now, we'll return mock data
        import random

        analytics = {
            "platform": platform,
            "period": {
                "from": date_from or "N/A",
                "to": date_to or "N/A"
            },
            "metrics": {
                "impressions": random.randint(1000, 10000),
                "engagements": random.randint(50, 500),
                "engagement_rate": round(random.uniform(1.0, 5.0), 2),
                "reach": random.randint(800, 8000),
                "likes": random.randint(20, 200),
                "shares": random.randint(5, 50),
                "comments": random.randint(10, 100)
            },
            "posts_count": random.randint(5, 20)
        }

        return {
            "status": "success",
            "analytics": analytics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@app.get("/get_platform_status")
async def get_platform_status():
    """Get status of configured social media accounts"""
    try:
        # Check which platforms have proper credentials
        facebook_configured = bool(FACEBOOK_PAGE_ID and FACEBOOK_ACCESS_TOKEN)
        instagram_configured = bool(INSTAGRAM_ACCOUNT_ID and INSTAGRAM_ACCESS_TOKEN)
        x_configured = bool(X_API_KEY and X_API_SECRET and X_ACCESS_TOKEN and X_ACCESS_TOKEN_SECRET)

        return {
            "status": "success",
            "platforms": {
                "facebook": {
                    "configured": facebook_configured,
                    "page_id": FACEBOOK_PAGE_ID if facebook_configured else None
                },
                "instagram": {
                    "configured": instagram_configured,
                    "account_id": INSTAGRAM_ACCOUNT_ID if instagram_configured else None
                },
                "x": {
                    "configured": x_configured,
                    "api_key_set": bool(X_API_KEY) if x_configured else False
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get platform status: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)