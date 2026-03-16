import asyncio
import json
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
import aiohttp
import os
from datetime import datetime

app = FastAPI(title="X (Twitter) MCP Server", version="1.0.0")

# Configuration for X (Twitter)
X_API_KEY = os.getenv("X_API_KEY", "")
X_API_SECRET = os.getenv("X_API_SECRET", "")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN", "")
X_ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET", "")

class XAPI:
    def __init__(self):
        self.api_key = X_API_KEY
        self.api_secret = X_API_SECRET
        self.access_token = X_ACCESS_TOKEN
        self.access_token_secret = X_ACCESS_TOKEN_SECRET

    async def post_tweet(self, text: str, image_url: str = None) -> Dict[str, Any]:
        """Post a tweet to X (Twitter)"""
        if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            raise Exception("X (Twitter) credentials not configured")

        # In a real implementation, we would use the Twitter API v2
        # For this mock implementation, we'll simulate the API call
        try:
            # Generate a mock tweet ID
            import random
            tweet_id = f"{random.randint(1000000000000000000, 9999999999999999999)}"

            # Simulate posting the tweet
            return {
                "status": "success",
                "platform": "x",
                "tweet_id": tweet_id,
                "text": text,
                "message": "Tweet posted successfully"
            }
        except Exception as e:
            raise Exception(f"Failed to post to X (Twitter): {str(e)}")

    async def get_user_info(self) -> Dict[str, Any]:
        """Get X (Twitter) user information"""
        if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            raise Exception("X (Twitter) credentials not configured")

        # Mock implementation
        try:
            return {
                "status": "success",
                "platform": "x",
                "user_info": {
                    "username": "mock_user",
                    "display_name": "Mock Account",
                    "followers_count": 1250,
                    "following_count": 890,
                    "tweet_count": 342
                }
            }
        except Exception as e:
            raise Exception(f"Failed to get X (Twitter) user info: {str(e)}")

x_api = XAPI()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        user_info = await x_api.get_user_info()
        return {
            "status": "healthy",
            "platform": "x",
            "credentials_configured": all([
                X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET
            ])
        }
    except:
        return {
            "status": "healthy",
            "platform": "x",
            "credentials_configured": False,
            "message": "Credentials not properly configured"
        }

@app.post("/post_tweet")
async def post_tweet(tweet_data: Dict[str, Any]):
    """
    Post a tweet to X (Twitter)
    Expected format:
    {
        "text": "Your tweet content",
        "image_url": "optional image URL"
    }
    """
    try:
        text = tweet_data.get("text", "")
        image_url = tweet_data.get("image_url")

        if not text:
            raise HTTPException(status_code=400, detail="Text content is required")

        if len(text) > 280:
            raise HTTPException(status_code=400, detail="Tweet text exceeds 280 character limit")

        result = await x_api.post_tweet(text, image_url)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to post tweet: {str(e)}")

@app.get("/user_info")
async def get_x_user_info():
    """Get X (Twitter) user information"""
    try:
        result = await x_api.get_user_info()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user info: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)