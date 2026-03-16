# Golden UI - Gold Tier AI Employee Dashboard

Professional dashboard frontend for the Gold Tier AI Employee System. Provides real-time monitoring, task management, and approval workflows for the autonomous AI employee.

## Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **State Management:** Zustand
- **HTTP Client:** Axios
- **Charts:** Recharts
- **Icons:** Lucide React, Heroicons
- **Animation:** Framer Motion

## Project Structure

```
golden-ui/
├── app/                    # Next.js 14 App Router
│   ├── (dashboard)/        # Dashboard route group
│   │   ├── layout.tsx      # Dashboard layout with sidebar
│   │   ├── page.tsx        # Home redirect to /dashboard
│   │   ├── dashboard/      # Executive overview page
│   │   ├── tasks/          # Task management page
│   │   └── approvals/      # Human-in-the-loop approvals page
│   ├── layout.tsx          # Root layout with providers
│   └── globals.css         # Global styles and Tailwind
├── components/
│   ├── layout/
│   │   ├── Header.tsx      # Top navigation bar
│   │   └── Sidebar.tsx     # Side navigation menu
│   └── ui/
│       ├── Button.tsx      # Button with variants
│       ├── Card.tsx        # Content container
│       └── Toast.tsx       # Notification system
├── lib/
│   └── api.ts              # API client (Axios)
└── types/                  # TypeScript type definitions
```

## Pages

| Page | Route | Description |
|------|-------|-------------|
| Dashboard | `/dashboard` | Executive overview with stats, system status, charts |
| Tasks | `/tasks` | View and filter tasks across all workflow stages |
| Approvals | `/approvals` | Review and approve/reject pending requests |

## Installation

```bash
cd golden-ui
npm install
```

## Configuration

Create `.env.local` (optional):

```env
BACKEND_URL=http://localhost:8000
```

Default backend URL is `http://localhost:8000` if not set.

## Running

### Standalone (Frontend Only)

```bash
npm run dev       # Development server on port 3000
npm run build     # Production build
npm run start     # Production server on port 3000
npm run lint      # ESLint
npm run type-check # TypeScript type checking
```

### With Backend (Full System)

From the project root:

```bash
python run_all.py
```

This starts both:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## API Integration

The frontend connects to the backend API server. Key endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/dashboard/stats` | GET | Dashboard statistics |
| `/api/system/status` | GET | System component status |
| `/api/tasks` | GET | All tasks (paginated) |
| `/api/tasks/{id}` | GET | Single task details |
| `/api/approvals` | GET | Pending approvals |
| `/api/approvals/{id}/approve` | POST | Approve request |
| `/api/approvals/{id}/reject` | POST | Reject request |
| `/api/finance/summary` | GET | Financial summary |
| `/api/logs` | GET | Audit logs |
| `/api/social/posts` | GET | Social media posts |
| `/api/system/start` | POST | Start backend system |
| `/api/system/stop` | POST | Stop backend system |

## Ports

| Service | Port |
|---------|------|
| Frontend | 3000 |
| Backend API | 8000 |
