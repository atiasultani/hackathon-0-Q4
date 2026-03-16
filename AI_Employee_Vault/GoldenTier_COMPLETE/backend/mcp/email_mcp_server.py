#!/usr/bin/env python3
"""
Email MCP Server for Gold Tier AI Employee System
Implements MCP protocol for email operations
"""

import asyncio
import json
from aiohttp import web
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

routes = web.RouteTableDef()

# Mock email storage (in real implementation, this would connect to actual email service)
emails_sent = []


@routes.get('/health')
async def health_check(request):
    """Health check endpoint"""
    return web.json_response({'status': 'ok', 'service': 'email-mcp'})


@routes.post('/send-email')
async def send_email(request):
    """Send an email"""
    try:
        data = await request.json()

        # Support both 'to' field and 'recipients' field (from orchestrator)
        if 'recipients' in data and 'to' not in data:
            data['to'] = data['recipients'][0] if isinstance(data['recipients'], list) else data['recipients']

        required_fields = ['to', 'subject', 'body']
        for field in required_fields:
            if field not in data:
                return web.json_response(
                    {'error': f'Missing required field: {field}'},
                    status=400
                )

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
            'status': 'success',
            'success': True,
            'message': 'Email sent successfully',
            'email_id': len(emails_sent)
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
async def draft_email(request):
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
            'draft_id': len(emails_sent) + 1000
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
async def search_emails(request):
    """Search through emails"""
    try:
        data = await request.json()

        query = data.get('query', '').lower()
        limit = data.get('limit', 10)

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


async def start_server(host='localhost', port=8001):
    """Start the MCP server"""
    app = web.Application()
    app.add_routes(routes)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, host, port)
    await site.start()

    logger.info(f"Email MCP Server running on http://{host}:{port}")

    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(start_server())
