import asyncio
import json
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
import aiohttp
import os
from datetime import datetime

app = FastAPI(title="Odoo MCP Server", version="1.0.0")

# Configuration for Odoo connection
ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "your_database")
ODOO_USERNAME = os.getenv("ODOO_USERNAME", "your_username")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "your_password")

class OdooAPI:
    def __init__(self):
        self.url = ODOO_URL
        self.db = ODOO_DB
        self.username = ODOO_USERNAME
        self.password = ODOO_PASSWORD
        self.uid = None
        self.common_url = f"{self.url}/xmlrpc/2/common"
        self.object_url = f"{self.url}/xmlrpc/2/object"

    async def authenticate(self):
        """Authenticate with Odoo and get user ID"""
        if self.uid is not None:
            return self.uid

        async with aiohttp.ClientSession() as session:
            try:
                # Authenticate
                payload = {
                    "jsonrpc": "2.0",
                    "method": "call",
                    "params": {
                        "db": self.db,
                        "login": self.username,
                        "password": self.password
                    },
                    "id": 1
                }

                async with session.post(self.common_url, json=payload) as response:
                    result = await response.json()
                    if 'result' in result:
                        self.uid = result['result']
                        return self.uid
                    else:
                        raise Exception(f"Authentication failed: {result.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"Error authenticating with Odoo: {str(e)}")
                return None

    async def call_method(self, model: str, method: str, args: list = None, kwargs: dict = None):
        """Call an Odoo model method"""
        if not self.uid:
            await self.authenticate()

        if not self.uid:
            raise Exception("Not authenticated with Odoo")

        async with aiohttp.ClientSession() as session:
            try:
                payload = {
                    "jsonrpc": "2.0",
                    "method": "call",
                    "params": {
                        "service": "object",
                        "method": "execute_kw",
                        "args": [self.db, self.uid, self.password, model, method] + (args or []) + ([kwargs] if kwargs else [])
                    },
                    "id": 2
                }

                if kwargs is not None:
                    # Special handling for methods that require keyword arguments
                    payload["params"]["args"] = [self.db, self.uid, self.password, model, method] + (args or [])
                    # The kwargs need to be appended separately
                    payload["params"]["args"].append(kwargs or {})

                async with session.post(self.object_url, json=payload) as response:
                    result = await response.json()
                    if 'result' in result:
                        return result['result']
                    else:
                        error_msg = result.get('error', {}).get('data', {}).get('message', 'Unknown error')
                        raise Exception(f"Method call failed: {error_msg}")
            except Exception as e:
                print(f"Error calling Odoo method {model}.{method}: {str(e)}")
                raise

odoo_api = OdooAPI()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        uid = await odoo_api.authenticate()
        if uid:
            return {"status": "healthy", "connected": True, "uid": uid}
        else:
            return {"status": "unhealthy", "connected": False}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.post("/create_invoice")
async def create_invoice(invoice_data: Dict[str, Any]):
    """
    Create an invoice in Odoo
    Required fields: partner_id, invoice_date, move_type='out_invoice'
    Optional fields: invoice_line_ids, currency_id, etc.
    """
    try:
        # Authenticate if needed
        uid = await odoo_api.authenticate()
        if not uid:
            raise HTTPException(status_code=500, detail="Failed to authenticate with Odoo")

        # Prepare invoice values
        vals = {
            'partner_id': invoice_data['partner_id'],
            'invoice_date': invoice_data.get('invoice_date', datetime.now().strftime('%Y-%m-%d')),
            'move_type': 'out_invoice',
            'state': 'draft',  # Start as draft, can be posted after approval
        }

        # Add optional fields if provided
        if 'currency_id' in invoice_data:
            vals['currency_id'] = invoice_data['currency_id']
        if 'invoice_line_ids' in invoice_data:
            vals['invoice_line_ids'] = invoice_data['invoice_line_ids']
        if 'ref' in invoice_data:
            vals['ref'] = invoice_data['ref']
        if 'narration' in invoice_data:
            vals['narration'] = invoice_data['narration']

        # Create the invoice
        invoice_id = await odoo_api.call_method('account.move', 'create', [vals])

        return {
            "status": "success",
            "invoice_id": invoice_id,
            "message": f"Invoice {invoice_id} created successfully as draft"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create invoice: {str(e)}")

@app.post("/post_invoice/{invoice_id}")
async def post_invoice(invoice_id: int):
    """Post a draft invoice to make it official"""
    try:
        uid = await odoo_api.authenticate()
        if not uid:
            raise HTTPException(status_code=500, detail="Failed to authenticate with Odoo")

        # Post the invoice (this confirms it)
        result = await odoo_api.call_method('account.move', 'action_post', [[invoice_id]])

        return {
            "status": "success",
            "invoice_id": invoice_id,
            "message": f"Invoice {invoice_id} posted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to post invoice: {str(e)}")

@app.post("/create_payment")
async def create_payment(payment_data: Dict[str, Any]):
    """Create a payment record in Odoo"""
    try:
        uid = await odoo_api.authenticate()
        if not uid:
            raise HTTPException(status_code=500, detail="Failed to authenticate with Odoo")

        # Prepare payment values
        vals = {
            'partner_id': payment_data['partner_id'],
            'amount': payment_data['amount'],
            'date': payment_data.get('date', datetime.now().strftime('%Y-%m-%d')),
            'payment_type': payment_data.get('payment_type', 'inbound'),  # inbound=outgoing payment, outbound=incoming payment
            'journal_id': payment_data.get('journal_id', 1),  # Default to first journal
            'state': 'draft',
        }

        # Add optional fields
        if 'currency_id' in payment_data:
            vals['currency_id'] = payment_data['currency_id']
        if 'ref' in payment_data:
            vals['ref'] = payment_data['ref']
        if 'communication' in payment_data:
            vals['communication'] = payment_data['communication']

        # Create the payment
        payment_id = await odoo_api.call_method('account.payment', 'create', [vals])

        return {
            "status": "success",
            "payment_id": payment_id,
            "message": f"Payment {payment_id} created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create payment: {str(e)}")

@app.get("/get_invoice/{invoice_id}")
async def get_invoice(invoice_id: int):
    """Retrieve invoice details from Odoo"""
    try:
        uid = await odoo_api.authenticate()
        if not uid:
            raise HTTPException(status_code=500, detail="Failed to authenticate with Odoo")

        # Search for the specific invoice
        invoice = await odoo_api.call_method(
            'account.move',
            'read',
            [[invoice_id]],
            {'fields': ['name', 'partner_id', 'amount_total', 'state', 'invoice_date', 'ref']}
        )

        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        return {
            "status": "success",
            "invoice": invoice[0]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve invoice: {str(e)}")

@app.get("/search_invoices")
async def search_invoices(domain: Optional[str] = None, limit: Optional[int] = 20):
    """Search for invoices with optional domain filter"""
    try:
        uid = await odoo_api.authenticate()
        if not uid:
            raise HTTPException(status_code=500, detail="Failed to authenticate with Odoo")

        # Parse domain if provided, otherwise search for all invoices
        search_domain = []
        if domain:
            try:
                search_domain = json.loads(domain)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid domain format")

        # Search for invoices
        invoice_ids = await odoo_api.call_method(
            'account.move',
            'search',
            [search_domain + [('move_type', '=', 'out_invoice')]]
        )

        # Get limited results
        if limit and len(invoice_ids) > limit:
            invoice_ids = invoice_ids[:limit]

        # Read invoice details
        if invoice_ids:
            invoices = await odoo_api.call_method(
                'account.move',
                'read',
                [invoice_ids],
                {'fields': ['id', 'name', 'partner_id', 'amount_total', 'state', 'invoice_date', 'ref']}
            )
        else:
            invoices = []

        return {
            "status": "success",
            "invoices": invoices,
            "count": len(invoices)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search invoices: {str(e)}")

@app.get("/get_revenue_summary")
async def get_revenue_summary(period: str = "current_month"):
    """Get revenue summary for a specific period"""
    try:
        uid = await odoo_api.authenticate()
        if not uid:
            raise HTTPException(status_code=500, detail="Failed to authenticate with Odoo")

        # Define domain based on period
        if period == "current_month":
            domain = [('move_type', '=', 'out_invoice'), ('state', '=', 'posted'), ('invoice_date', '>=', datetime.now().strftime('%Y-%m-01'))]
        elif period == "current_quarter":
            # Simplified - would need more complex date calculation in practice
            domain = [('move_type', '=', 'out_invoice'), ('state', '=', 'posted')]
        elif period == "current_year":
            domain = [('move_type', '=', 'out_invoice'), ('state', '=', 'posted'), ('invoice_date', '>=', f"{datetime.now().year}-01-01")]
        else:
            domain = [('move_type', '=', 'out_invoice'), ('state', '=', 'posted')]

        # Search for paid invoices
        invoice_ids = await odoo_api.call_method('account.move', 'search', [domain])

        total_revenue = 0
        if invoice_ids:
            invoices = await odoo_api.call_method(
                'account.move',
                'read',
                [invoice_ids],
                {'fields': ['amount_total', 'state']}
            )

            # Calculate total revenue from posted invoices
            for invoice in invoices:
                if invoice.get('state') == 'posted':
                    total_revenue += float(invoice.get('amount_total', 0))

        return {
            "status": "success",
            "period": period,
            "total_revenue": total_revenue,
            "invoice_count": len(invoice_ids)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get revenue summary: {str(e)}")

@app.post("/log_accounting_entry")
async def log_accounting_entry(entry_data: Dict[str, Any]):
    """Log a manual accounting entry/journal entry"""
    try:
        uid = await odoo_api.authenticate()
        if not uid:
            raise HTTPException(status_code=500, detail="Failed to authenticate with Odoo")

        # Prepare journal entry values
        vals = {
            'journal_id': entry_data['journal_id'],  # Required
            'date': entry_data.get('date', datetime.now().strftime('%Y-%m-%d')),
            'ref': entry_data.get('ref', ''),
            'line_ids': entry_data.get('line_ids', []),
        }

        # Create the journal entry
        entry_id = await odoo_api.call_method('account.move', 'create', [vals])

        return {
            "status": "success",
            "entry_id": entry_id,
            "message": f"Accounting entry {entry_id} created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log accounting entry: {str(e)}")

@app.get("/get_ledger_entries")
async def get_ledger_entries(account_id: Optional[int] = None, date_from: Optional[str] = None, date_to: Optional[str] = None):
    """Get ledger entries for accounting reconciliation"""
    try:
        uid = await odoo_api.authenticate()
        if not uid:
            raise HTTPException(status_code=500, detail="Failed to authenticate with Odoo")

        # Build domain for account.move.line search
        domain = []
        if account_id:
            domain.append(('account_id', '=', account_id))
        if date_from:
            domain.append(('date', '>=', date_from))
        if date_to:
            domain.append(('date', '<=', date_to))

        # Search for ledger entries
        entry_ids = await odoo_api.call_method('account.move.line', 'search', [domain])

        # Limit results to prevent huge responses
        if len(entry_ids) > 100:
            entry_ids = entry_ids[:100]

        if entry_ids:
            entries = await odoo_api.call_method(
                'account.move.line',
                'read',
                [entry_ids],
                {
                    'fields': [
                        'id', 'name', 'date', 'account_id', 'partner_id', 'debit',
                        'credit', 'balance', 'move_id', 'ref'
                    ]
                }
            )
        else:
            entries = []

        return {
            "status": "success",
            "entries": entries,
            "count": len(entries)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get ledger entries: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)