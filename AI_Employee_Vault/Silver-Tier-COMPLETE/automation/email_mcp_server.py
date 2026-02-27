#!/usr/bin/env python3
"""
Email MCP Server for Silver Tier AI Employee System
Implements MCP protocol for email operations
"""

import asyncio
import json
from typing import Dict, Any
from aiohttp import web, hdrs
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

routes = web.RouteTableDef()

# Mock email storage (in real implementation, this would connect to actual email service)
emails_sent = []

class EmailMCPServer:
    def __init__(self):
        self.routes = routes

    @routes.get('/health')
    async def health_check(self, request):
        """Health check endpoint"""
        return web.json_response({'status': 'ok', 'service': 'email-mcp'})

    @routes.post('/send-email')
    async def send_email(self, request):
        """Send an email"""
        try:
            data = await request.json()

            required_fields = ['to', 'subject', 'body']
            for field in required_fields:
                if field not in data:
                    return web.json_response(
                        {'error': f'Missing required field: {field}'},
                        status=400
                    )

            # In a real implementation, this would send the actual email
            # For now, we'll just log it as sent

            email_record = {
                'to': data['to'],
                'subject': data['subject'],
                'body': data['body'],
                'timestamp': asyncio.get_event_loop().time(),
                'status': 'sent'
            }

            emails_sent.append(email_record)

            logger.info(f"Email sent to {data['to']}: {data['subject']}")

            return web.json_response({
                'success': True,
                'message': 'Email sent successfully',
                'email_id': len(emails_sent)  # Simple ID for demo
            })

        except json.JSONDecodeError:
            return web.json_response(
                {'error': 'Invalid JSON in request'},
                status=400
            )
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return web.json_response(
                {'error': 'Internal server error'},
                status=500
            )

    @routes.post('/draft-email')
    async def draft_email(self, request):
        """Draft an email (save as draft, don't send)"""
        try:
            data = await request.json()

            required_fields = ['to', 'subject', 'body']
            for field in required_fields:
                if field not in data:
                    return web.json_response(
                        {'error': f'Missing required field: {field}'},
                        status=400
                    )

            # Save as draft (in real implementation, would save to draft folder)
            draft_record = {
                'to': data['to'],
                'subject': data['subject'],
                'body': data['body'],
                'timestamp': asyncio.get_event_loop().time(),
                'status': 'draft'
            }

            logger.info(f"Email drafted for {data['to']}: {data['subject']}")

            return web.json_response({
                'success': True,
                'message': 'Email drafted successfully',
                'draft_id': len(emails_sent) + 1000  # Different ID space for drafts
            })

        except json.JSONDecodeError:
            return web.json_response(
                {'error': 'Invalid JSON in request'},
                status=400
            )
        except Exception as e:
            logger.error(f"Error drafting email: {e}")
            return web.json_response(
                {'error': 'Internal server error'},
                status=500
            )

    @routes.post('/search-emails')
    async def search_emails(self, request):
        """Search through emails"""
        try:
            data = await request.json()

            query = data.get('query', '').lower()
            limit = data.get('limit', 10)

            # Search through sent emails
            results = []
            for email in emails_sent:
                if (query in email['to'].lower() or
                    query in email['subject'].lower() or
                    query in email['body'].lower()):
                    results.append(email)
                    if len(results) >= limit:
                        break

            return web.json_response({
                'success': True,
                'results': results[:limit],
                'total_found': len(results)
            })

        except json.JSONDecodeError:
            return web.json_response(
                {'error': 'Invalid JSON in request'},
                status=400
            )
        except Exception as e:
            logger.error(f"Error searching emails: {e}")
            return web.json_response(
                {'error': 'Internal server error'},
                status=500
            )

    async def start_server(self, host='localhost', port=8000):
        """Start the MCP server"""
        app = web.Application()
        app.add_routes(self.routes)

        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, host, port)
        await site.start()

        logger.info(f"Email MCP Server running on http://{host}:{port}")

        # Keep the server running
        try:
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            logger.info("Shutting down server...")
            await runner.cleanup()

# For standalone execution
async def main():
    server = EmailMCPServer()
    await server.start_server()

if __name__ == "__main__":
    asyncio.run(main())