import asyncio
import json
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from playwright.async_api import async_playwright
import os
from datetime import datetime
import tempfile
import base64

app = FastAPI(title="Browser MCP Server", version="1.0.0")

class BrowserAPI:
    def __init__(self):
        self.active_browsers = {}

    async def setup_browser_session(self, session_id: str):
        """Setup a new browser session"""
        if session_id in self.active_browsers:
            await self.close_browser_session(session_id)

        # Launch new browser instance
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)  # Set to False for debugging
        context = await browser.new_context()
        page = await context.new_page()

        self.active_browsers[session_id] = {
            'playwright': playwright,
            'browser': browser,
            'context': context,
            'page': page
        }

        return session_id

    async def close_browser_session(self, session_id: str):
        """Close a browser session"""
        if session_id in self.active_browsers:
            browser_data = self.active_browsers[session_id]
            await browser_data['browser'].close()
            await browser_data['playwright'].stop()
            del self.active_browsers[session_id]

    async def navigate_to_url(self, session_id: str, url: str):
        """Navigate to a URL in the browser"""
        if session_id not in self.active_browsers:
            raise Exception(f"Browser session {session_id} not found")

        page = self.active_browsers[session_id]['page']
        await page.goto(url)
        await page.wait_for_load_state('networkidle')

        return {
            "status": "success",
            "url": url,
            "title": await page.title()
        }

    async def fill_form(self, session_id: str, selectors_values: Dict[str, str]):
        """Fill form fields with provided values"""
        if session_id not in self.active_browsers:
            raise Exception(f"Browser session {session_id} not found")

        page = self.active_browsers[session_id]['page']

        for selector, value in selectors_values.items():
            await page.fill(selector, value)
            await page.wait_for_timeout(500)  # Small delay to ensure the value is set

        return {
            "status": "success",
            "fields_filled": len(selectors_values)
        }

    async def click_element(self, session_id: str, selector: str, wait_after_click: int = 1000):
        """Click an element on the page"""
        if session_id not in self.active_browsers:
            raise Exception(f"Browser session {session_id} not found")

        page = self.active_browsers[session_id]['page']

        # Wait for the element to be clickable
        await page.wait_for_selector(selector, state='visible')
        await page.click(selector)

        # Wait after click to allow for page transitions
        await page.wait_for_timeout(wait_after_click)

        return {
            "status": "success",
            "clicked_element": selector
        }

    async def get_page_content(self, session_id: str, selector: str = None):
        """Get content from the current page"""
        if session_id not in self.active_browsers:
            raise Exception(f"Browser session {session_id} not found")

        page = self.active_browsers[session_id]['page']

        if selector:
            # Get content of specific element
            element = await page.query_selector(selector)
            if element:
                content = await element.text_content()
                return {
                    "status": "success",
                    "content": content,
                    "selector": selector
                }
            else:
                raise Exception(f"Element with selector '{selector}' not found")
        else:
            # Get entire page content
            content = await page.content()
            return {
                "status": "success",
                "content": content
            }

    async def take_screenshot(self, session_id: str, path: str = None):
        """Take a screenshot of the current page"""
        if session_id not in self.active_browsers:
            raise Exception(f"Browser session {session_id} not found")

        page = self.active_browsers[session_id]['page']

        if not path:
            # Create a temporary file
            path = tempfile.mktemp(suffix='.png')

        await page.screenshot(path=path)

        # Encode the image to base64 for transmission
        with open(path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        return {
            "status": "success",
            "screenshot_path": path,
            "screenshot_base64": image_data[:100] + "..." if len(image_data) > 100 else image_data  # Truncate for response
        }

    async def login_to_portal(self, session_id: str, portal_type: str, credentials: Dict[str, str]):
        """Perform login to a specific portal type"""
        if session_id not in self.active_browsers:
            raise Exception(f"Browser session {session_id} not found")

        page = self.active_browsers[session_id]['page']
        username = credentials.get('username')
        password = credentials.get('password')

        if not username or not password:
            raise Exception("Username and password are required for login")

        # Different login flows based on portal type
        if portal_type.lower() == "paypal":
            await page.fill('input[name="login_email"]', username)
            await page.click('input[value="Next"]')
            await page.wait_for_timeout(1000)
            await page.fill('input[name="login_password"]', password)
            await page.click('button:has-text("Log In")')
        elif portal_type.lower() == "stripe":
            await page.fill('#email', username)
            await page.fill('#password', password)
            await page.click('button[type="submit"]')
        elif portal_type.lower() == "square":
            await page.fill('input#username', username)
            await page.fill('input#password', password)
            await page.click('button[type="submit"]')
        elif portal_type.lower() == "banking":
            await page.fill('input#user-id', username)
            await page.fill('input#password', password)
            await page.click('button.login-button')
        else:
            # Generic login - assumes common selectors
            await page.fill('input[type="email"], input[type="text"], #username, #email', username)
            await page.fill('input[type="password"], #password', password)
            await page.click('button[type="submit"], .login-button, #login-btn')

        # Wait for login to complete
        await page.wait_for_load_state('networkidle')

        return {
            "status": "success",
            "portal_type": portal_type,
            "logged_in": True
        }

    async def process_payment(self, session_id: str, payment_details: Dict[str, Any]):
        """Process a payment through the browser"""
        if session_id not in self.active_browsers:
            raise Exception(f"Browser session {session_id} not found")

        page = self.active_browsers[session_id]['page']

        # Fill payment form with provided details
        card_number = payment_details.get('card_number')
        expiry_date = payment_details.get('expiry_date')
        cvv = payment_details.get('cvv')
        amount = payment_details.get('amount')
        description = payment_details.get('description')

        if card_number:
            await page.fill('input[name="cardnumber"], #card-number, input[placeholder*="card"], .card-number-input', card_number)
        if expiry_date:
            await page.fill('input[name="exp-date"], #expiry-date, input[placeholder*="MM/YY"], .expiry-input', expiry_date)
        if cvv:
            await page.fill('input[name="cvc"], #cvv, input[placeholder*="CVV"], .cvv-input', cvv)
        if amount:
            await page.fill('input[name="amount"], #amount, .amount-input', str(amount))

        # Click the pay button
        await page.click('button:has-text("Pay"), button:has-text("Submit"), .pay-button, #pay-btn')

        # Wait for payment processing
        await page.wait_for_timeout(3000)

        # Check for success or error messages
        success_indicators = ['success', 'paid', 'completed', 'confirmed']
        error_indicators = ['error', 'failed', 'declined', 'invalid']

        page_text = await page.text_content()
        page_text_lower = page_text.lower()

        if any(indicator in page_text_lower for indicator in success_indicators):
            status = "success"
            message = "Payment processed successfully"
        elif any(indicator in page_text_lower for indicator in error_indicators):
            status = "error"
            message = "Payment failed"
        else:
            status = "unknown"
            message = "Payment status unknown"

        return {
            "status": status,
            "message": message,
            "payment_details": {
                "amount": amount,
                "description": description
            }
        }

browser_api = BrowserAPI()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    active_sessions = len(browser_api.active_browsers)
    return {
        "status": "healthy",
        "active_sessions": active_sessions,
        "capabilities": [
            "navigate_to_url",
            "fill_form",
            "click_element",
            "get_page_content",
            "take_screenshot",
            "login_to_portal",
            "process_payment"
        ]
    }

@app.post("/create_session")
async def create_session(session_data: Dict[str, Any] = None):
    """Create a new browser session"""
    try:
        import uuid
        session_id = str(uuid.uuid4())
        await browser_api.setup_browser_session(session_id)

        return {
            "status": "success",
            "session_id": session_id,
            "message": "Browser session created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@app.post("/close_session/{session_id}")
async def close_session(session_id: str):
    """Close a browser session"""
    try:
        await browser_api.close_browser_session(session_id)
        return {
            "status": "success",
            "session_id": session_id,
            "message": "Browser session closed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to close session: {str(e)}")

@app.post("/navigate/{session_id}")
async def navigate(session_id: str, nav_data: Dict[str, Any]):
    """Navigate to a URL"""
    try:
        url = nav_data.get("url")
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")

        result = await browser_api.navigate_to_url(session_id, url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to navigate: {str(e)}")

@app.post("/fill_form/{session_id}")
async def fill_form(session_id: str, form_data: Dict[str, Any]):
    """Fill form fields"""
    try:
        selectors_values = form_data.get("selectors_values", {})
        if not selectors_values:
            raise HTTPException(status_code=400, detail="Selectors and values are required")

        result = await browser_api.fill_form(session_id, selectors_values)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fill form: {str(e)}")

@app.post("/click/{session_id}")
async def click_element_endpoint(session_id: str, click_data: Dict[str, Any]):
    """Click an element"""
    try:
        selector = click_data.get("selector")
        if not selector:
            raise HTTPException(status_code=400, detail="Selector is required")

        wait_after_click = click_data.get("wait_after_click", 1000)

        result = await browser_api.click_element(session_id, selector, wait_after_click)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to click element: {str(e)}")

@app.post("/get_content/{session_id}")
async def get_content(session_id: str, content_data: Dict[str, Any] = None):
    """Get page content"""
    try:
        selector = content_data.get("selector") if content_data else None
        result = await browser_api.get_page_content(session_id, selector)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get content: {str(e)}")

@app.post("/screenshot/{session_id}")
async def take_screenshot_endpoint(session_id: str, screenshot_data: Dict[str, Any] = None):
    """Take a screenshot"""
    try:
        path = screenshot_data.get("path") if screenshot_data else None
        result = await browser_api.take_screenshot(session_id, path)
        # Don't return the full base64 image in the response to avoid large payloads
        result.pop('screenshot_base64', None)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to take screenshot: {str(e)}")

@app.post("/login/{session_id}")
async def login_to_portal(session_id: str, login_data: Dict[str, Any]):
    """Login to a portal"""
    try:
        portal_type = login_data.get("portal_type")
        credentials = login_data.get("credentials", {})

        if not portal_type:
            raise HTTPException(status_code=400, detail="Portal type is required")
        if not credentials:
            raise HTTPException(status_code=400, detail="Credentials are required")

        result = await browser_api.login_to_portal(session_id, portal_type, credentials)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to login: {str(e)}")

@app.post("/process_payment/{session_id}")
async def process_payment(session_id: str, payment_data: Dict[str, Any]):
    """Process a payment"""
    try:
        result = await browser_api.process_payment(session_id, payment_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process payment: {str(e)}")

@app.get("/sessions")
async def list_sessions():
    """List active browser sessions"""
    try:
        sessions = []
        for session_id in browser_api.active_browsers.keys():
            sessions.append({
                "session_id": session_id,
                "status": "active"
            })

        return {
            "status": "success",
            "sessions": sessions,
            "count": len(sessions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)