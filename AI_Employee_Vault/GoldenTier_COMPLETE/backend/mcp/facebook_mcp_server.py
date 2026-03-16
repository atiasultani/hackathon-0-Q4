import asyncio
import json
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
import aiohttp
import os
from datetime import datetime

app = FastAPI(title="Facebook MCP Server", version="1.0.0")

# Configuration for Facebook
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN", "")

class FacebookAPI:
    def __init__(self):
        self.token = FACEBOOK_ACCESS_TOKEN
        self.page_id = FACEBOOK_PAGE_ID

    async def post_message(self, message: str, image_url: str = None) -> Dict[str, Any]:
        """Post a message to Facebook page"""
        if not self.token or not self.page_id:
            raise Exception("Facebook credentials not configured")

        url = f"https://graph.facebook.com/v18.0/{self.page_id}/feed"

        async with aiohttp.ClientSession() as session:
            try:
                data = {
                    'message': message,
                    'access_token': self.token
                }

                if image_url:
                    # For image posts, we use a different approach
                    url = f"https://graph.facebook.com/v18.0/{self.page_id}/photos"
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

    async def get_page_info(self) -> Dict[str, Any]:
        """Get Facebook page information"""
        if not self.token or not self.page_id:
            raise Exception("Facebook credentials not configured")

        url = f"https://graph.facebook.com/v18.0/{self.page_id}"

        async with aiohttp.ClientSession() as session:
            try:
                params = {
                    'access_token': self.token,
                    'fields': 'name,fan_count,category,talking_about_count'
                }

                async with session.get(url, params=params) as response:
                    result = await response.json()

                    if 'error' in result:
                        raise Exception(f"Facebook API error: {result['error'].get('message', 'Unknown error')}")

                    return {
                        "status": "success",
                        "platform": "facebook",
                        "page_info": result
                    }
            except Exception as e:
                raise Exception(f"Failed to get Facebook page info: {str(e)}")

fb_api = FacebookAPI()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        page_info = await fb_api.get_page_info()
        return {
            "status": "healthy",
            "platform": "facebook",
            "page_configured": bool(FACEBOOK_PAGE_ID and FACEBOOK_ACCESS_TOKEN)
        }
    except:
        return {
            "status": "healthy",
            "platform": "facebook",
            "page_configured": False,
            "message": "Credentials not properly configured"
        }

@app.post("/post")
async def post_to_facebook(post_data: Dict[str, Any]):
    """
    Post content to Facebook
    Expected format:
    {
        "message": "Your post content",
        "image_url": "optional image URL"
    }
    """
    try:
        message = post_data.get("message", "")
        image_url = post_data.get("image_url")

        if not message:
            raise HTTPException(status_code=400, detail="Message content is required")

        result = await fb_api.post_message(message, image_url)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to post to Facebook: {str(e)}")

@app.get("/page_info")
async def get_facebook_page_info():
    """Get Facebook page information"""
    try:
        result = await fb_api.get_page_info()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get page info: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)