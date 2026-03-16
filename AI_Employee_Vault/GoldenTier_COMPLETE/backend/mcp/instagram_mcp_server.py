import asyncio
import json
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
import aiohttp
import os
from datetime import datetime

app = FastAPI(title="Instagram MCP Server", version="1.0.0")

# Configuration for Instagram
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID", "")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")

class InstagramAPI:
    def __init__(self):
        self.token = INSTAGRAM_ACCESS_TOKEN
        self.account_id = INSTAGRAM_ACCOUNT_ID

    async def post_image(self, caption: str, image_url: str) -> Dict[str, Any]:
        """Post an image to Instagram"""
        if not self.token or not self.account_id:
            raise Exception("Instagram credentials not configured")

        async with aiohttp.ClientSession() as session:
            try:
                # Step 1: Create the media object
                creation_url = f"https://graph.facebook.com/v18.0/{self.account_id}/media"

                media_data = {
                    'image_url': image_url,
                    'caption': caption,
                    'access_token': self.token
                }

                async with session.post(creation_url, data=media_data) as response:
                    creation_result = await response.json()

                    if 'error' in creation_result:
                        raise Exception(f"Instagram media creation error: {creation_result['error'].get('message', 'Unknown error')}")

                    container_id = creation_result.get('id')

                    # Step 2: Wait briefly for the container to be processed
                    await asyncio.sleep(2)

                    # Step 3: Publish the media
                    publish_url = f"https://graph.facebook.com/v18.0/{self.account_id}/media_publish"
                    publish_data = {
                        'creation_id': container_id,
                        'access_token': self.token
                    }

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

    async def get_account_info(self) -> Dict[str, Any]:
        """Get Instagram account information"""
        if not self.token or not self.account_id:
            raise Exception("Instagram credentials not configured")

        url = f"https://graph.facebook.com/v18.0/{self.account_id}"

        async with aiohttp.ClientSession() as session:
            try:
                params = {
                    'access_token': self.token,
                    'fields': 'username,account_type,media_count,followers_count,follows_count'
                }

                async with session.get(url, params=params) as response:
                    result = await response.json()

                    if 'error' in result:
                        raise Exception(f"Instagram API error: {result['error'].get('message', 'Unknown error')}")

                    return {
                        "status": "success",
                        "platform": "instagram",
                        "account_info": result
                    }
            except Exception as e:
                raise Exception(f"Failed to get Instagram account info: {str(e)}")

ig_api = InstagramAPI()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        account_info = await ig_api.get_account_info()
        return {
            "status": "healthy",
            "platform": "instagram",
            "account_configured": bool(INSTAGRAM_ACCOUNT_ID and INSTAGRAM_ACCESS_TOKEN)
        }
    except:
        return {
            "status": "healthy",
            "platform": "instagram",
            "account_configured": False,
            "message": "Credentials not properly configured"
        }

@app.post("/post_image")
async def post_to_instagram(post_data: Dict[str, Any]):
    """
    Post an image to Instagram
    Expected format:
    {
        "caption": "Your caption",
        "image_url": "URL of the image to post"
    }
    """
    try:
        caption = post_data.get("caption", "")
        image_url = post_data.get("image_url")

        if not caption:
            raise HTTPException(status_code=400, detail="Caption is required")

        if not image_url:
            raise HTTPException(status_code=400, detail="Image URL is required")

        result = await ig_api.post_image(caption, image_url)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to post to Instagram: {str(e)}")

@app.get("/account_info")
async def get_instagram_account_info():
    """Get Instagram account information"""
    try:
        result = await ig_api.get_account_info()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get account info: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)