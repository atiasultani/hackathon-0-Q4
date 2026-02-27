#!/usr/bin/env python3
"""
LinkedIn MCP Server for Silver Tier AI Employee System
Implements MCP protocol for LinkedIn operations
"""

import asyncio
import json
from typing import Dict, Any
from aiohttp import web
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

routes = web.RouteTableDef()

# Mock LinkedIn post storage (in real implementation, this would connect to LinkedIn API)
posts_published = []

class LinkedInMCPServer:
    def __init__(self):
        self.routes = routes

    @routes.get('/health')
    async def health_check(self, request):
        """Health check endpoint"""
        return web.json_response({'status': 'ok', 'service': 'linkedin-mcp'})

    @routes.post('/publish-post')
    async def publish_post(self, request):
        """Publish a LinkedIn post"""
        try:
            data = await request.json()

            required_fields = ['content']
            for field in required_fields:
                if field not in data:
                    return web.json_response(
                        {'error': f'Missing required field: {field}'},
                        status=400
                    )

            # Additional optional fields
            post_title = data.get('title', '')
            post_content = data['content']
            visibility = data.get('visibility', 'PUBLIC')  # PUBLIC, CONNECTIONS_ONLY, etc.

            # In a real implementation, this would publish to LinkedIn
            # For now, we'll just log it as published

            post_record = {
                'title': post_title,
                'content': post_content,
                'visibility': visibility,
                'timestamp': datetime.now().isoformat(),
                'status': 'published',
                'post_url': f'https://linkedin.com/posts/mock-{len(posts_published)+1}'
            }

            posts_published.append(post_record)

            logger.info(f"LinkedIn post published: {post_title or post_content[:50]}...")

            return web.json_response({
                'success': True,
                'message': 'LinkedIn post published successfully',
                'post_id': len(posts_published),
                'post_url': post_record['post_url']
            })

        except json.JSONDecodeError:
            return web.json_response(
                {'error': 'Invalid JSON in request'},
                status=400
            )
        except Exception as e:
            logger.error(f"Error publishing LinkedIn post: {e}")
            return web.json_response(
                {'error': 'Internal server error'},
                status=500
            )

    @routes.post('/draft-post')
    async def draft_post(self, request):
        """Draft a LinkedIn post (save as draft, don't publish)"""
        try:
            data = await request.json()

            required_fields = ['content']
            for field in required_fields:
                if field not in data:
                    return web.json_response(
                        {'error': f'Missing required field: {field}'},
                        status=400
                    )

            # Save as draft
            draft_record = {
                'title': data.get('title', ''),
                'content': data['content'],
                'visibility': data.get('visibility', 'PUBLIC'),
                'timestamp': datetime.now().isoformat(),
                'status': 'draft'
            }

            logger.info(f"LinkedIn post drafted: {draft_record['title'] or draft_record['content'][:50]}...")

            return web.json_response({
                'success': True,
                'message': 'LinkedIn post drafted successfully',
                'draft_id': len(posts_published) + 1000  # Different ID space for drafts
            })

        except json.JSONDecodeError:
            return web.json_response(
                {'error': 'Invalid JSON in request'},
                status=400
            )
        except Exception as e:
            logger.error(f"Error drafting LinkedIn post: {e}")
            return web.json_response(
                {'error': 'Internal server error'},
                status=500
            )

    @routes.get('/published-posts')
    async def get_published_posts(self, request):
        """Get list of published posts"""
        try:
            limit = int(request.query.get('limit', 10))
            offset = int(request.query.get('offset', 0))

            # Return paginated results
            start_idx = offset
            end_idx = offset + limit
            paginated_posts = posts_published[start_idx:end_idx]

            return web.json_response({
                'success': True,
                'posts': paginated_posts,
                'total_count': len(posts_published),
                'returned_count': len(paginated_posts)
            })

        except ValueError:
            return web.json_response(
                {'error': 'Invalid limit or offset parameter'},
                status=400
            )
        except Exception as e:
            logger.error(f"Error getting published posts: {e}")
            return web.json_response(
                {'error': 'Internal server error'},
                status=500
            )

    async def start_server(self, host='localhost', port=8001):
        """Start the MCP server"""
        app = web.Application()
        app.add_routes(self.routes)

        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, host, port)
        await site.start()

        logger.info(f"LinkedIn MCP Server running on http://{host}:{port}")

        # Keep the server running
        try:
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            logger.info("Shutting down server...")
            await runner.cleanup()

# For standalone execution
async def main():
    server = LinkedInMCPServer()
    await server.start_server()

if __name__ == "__main__":
    asyncio.run(main())