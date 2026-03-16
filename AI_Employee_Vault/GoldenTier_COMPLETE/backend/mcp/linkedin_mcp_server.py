#!/usr/bin/env python3
"""
LinkedIn MCP Server for Silver Tier AI Employee System
Handles posts, drafts, and saves them as .md files in respective folders.
"""

import asyncio
import json
from aiohttp import web
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

routes = web.RouteTableDef()

# In-memory storage
posts_published = []

# Folders
NEEDS_ACTION_DIR = './Needs_Action'
DRAFTS_DIR = './Drafts'
os.makedirs(NEEDS_ACTION_DIR, exist_ok=True)
os.makedirs(DRAFTS_DIR, exist_ok=True)

def save_post_to_md(post_data, folder):
    """Save post data as a markdown file in the given folder"""
    title_safe = post_data.get('title') or 'untitled'
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"{title_safe.replace(' ', '_')}_{timestamp}.md"
    file_path = os.path.join(folder, file_name)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"# {post_data.get('title', '')}\n\n")
        f.write(post_data.get('content', ''))
    return file_path

@routes.get('/health')
async def health_check(request):
    return web.json_response({'status': 'ok', 'service': 'linkedin-mcp'})

@routes.post('/publish-post')
async def publish_post(request):
    try:
        data = await request.json()
        if 'content' not in data:
            return web.json_response({'error': 'Missing content field'}, status=400)

        post_record = {
            'title': data.get('title', ''),
            'content': data['content'],
            'visibility': data.get('visibility', 'PUBLIC'),
            'timestamp': datetime.now().isoformat(),
            'status': 'published',
            'post_url': f"https://linkedin.com/posts/mock-{len(posts_published)+1}"
        }

        # Save in-memory
        posts_published.append(post_record)

        # Save to Needs_Action folder
        file_path = save_post_to_md(post_record, NEEDS_ACTION_DIR)
        logger.info(f"LinkedIn post published: {post_record['title'] or post_record['content'][:50]}...")
        logger.info(f"Saved .md file at: {file_path}")

        return web.json_response({
            'success': True,
            'message': 'LinkedIn post published successfully',
            'post_id': len(posts_published),
            'post_url': post_record['post_url']
        })

    except json.JSONDecodeError:
        return web.json_response({'error': 'Invalid JSON in request'}, status=400)
    except Exception as e:
        logger.error(f"Error publishing post: {e}")
        return web.json_response({'error': 'Internal server error'}, status=500)

@routes.post('/draft-post')
async def draft_post(request):
    try:
        data = await request.json()
        if 'content' not in data:
            return web.json_response({'error': 'Missing content field'}, status=400)

        draft_record = {
            'title': data.get('title', ''),
            'content': data['content'],
            'visibility': data.get('visibility', 'PUBLIC'),
            'timestamp': datetime.now().isoformat(),
            'status': 'draft'
        }

        # Save to Drafts folder
        file_path = save_post_to_md(draft_record, DRAFTS_DIR)
        logger.info(f"Drafted LinkedIn post: {draft_record['title'] or draft_record['content'][:50]}...")
        logger.info(f"Saved draft .md file at: {file_path}")

        return web.json_response({
            'success': True,
            'message': 'Drafted LinkedIn post successfully',
            'draft_id': len(posts_published) + 1000
        })

    except json.JSONDecodeError:
        return web.json_response({'error': 'Invalid JSON in request'}, status=400)
    except Exception as e:
        logger.error(f"Error drafting post: {e}")
        return web.json_response({'error': 'Internal server error'}, status=500)

@routes.get('/published-posts')
async def get_published_posts(request):
    try:
        limit = int(request.query.get('limit', 10))
        offset = int(request.query.get('offset', 0))
        start_idx = offset
        end_idx = offset + limit
        paginated_posts = posts_published[start_idx:end_idx]

        return web.json_response({
            'success': True,
            'posts': paginated_posts,
            'total_count': len(posts_published),
            'returned_count': len(paginated_posts)
        })

    except Exception as e:
        logger.error(f"Error getting published posts: {e}")
        return web.json_response({'error': 'Internal server error'}, status=500)

async def start_server(host='localhost', port=8002):
    app = web.Application()
    app.add_routes(routes)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    logger.info(f"LinkedIn MCP Server running on http://{host}:{port}")
    await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(start_server())