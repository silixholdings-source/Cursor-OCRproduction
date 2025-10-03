# AI ERP SaaS Web Frontend

A modern, responsive web frontend for the AI ERP SaaS platform built with Next.js 14, TypeScript, and Tailwind CSS.

## Features

- **Modern UI/UX**: Built with shadcn/ui components and Tailwind CSS
- **Real-time Dashboards**: Multiple dashboard views for different aspects of the system
- **Responsive Design**: Mobile-first approach with responsive layouts
- **TypeScript**: Full type safety throughout the application
- **Performance Optimized**: Code splitting, lazy loading, and optimized builds
- **Security Headers**: Comprehensive security headers and CSP policies
- **Accessibility**: WCAG compliant components and interactions

## Dashboard Views

1. **Overview Dashboard**: Quick stats and recent activity
2. **Real-time Dashboard**: Live system monitoring and activity feed
3. **Analytics Dashboard**: Comprehensive business analytics and reporting
4. **Performance Dashboard**: System performance metrics and monitoring
5. **Security Dashboard**: Security events and compliance monitoring
6. **Audit Dashboard**: Complete audit trail and compliance reporting
7. **Integration Dashboard**: ERP and third-party integration management
8. **AI Insights Dashboard**: AI-powered insights and recommendations
9. **Advanced Dashboard**: Comprehensive system overview with multiple tabs

## Technology Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui (Radix UI primitives)
- **Charts**: Recharts
- **Icons**: Lucide React
- **State Management**: React hooks and context
- **HTTP Client**: Fetch API with custom hooks

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

### Building for Production

```bash
npm run build
npm start
```

## Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── dashboard/         # Dashboard page
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Home page
├── components/            # Reusable components
│   ├── dashboard/         # Dashboard-specific components
│   └── ui/               # Base UI components
└── lib/                  # Utility functions
    └── utils.ts          # Common utilities
```

## Key Components

### Dashboard Components
- `RealTimeDashboard`: Live system monitoring
- `AnalyticsDashboard`: Business analytics and reporting
- `PerformanceDashboard`: System performance metrics
- `SecurityDashboard`: Security monitoring and compliance
- `AuditDashboard`: Audit trail and compliance reporting
- `IntegrationDashboard`: ERP integration management
- `AIInsightsDashboard`: AI-powered insights
- `AdvancedDashboard`: Comprehensive system overview

### UI Components
- `AdvancedTable`: Feature-rich data table with sorting, filtering, pagination
- `Card`, `Button`, `Badge`: Base UI components
- `Tabs`, `Select`, `Input`: Form and navigation components
- `Progress`, `Table`: Data display components

## Security Features

- Content Security Policy (CSP) headers
- X-Frame-Options protection
- X-Content-Type-Options protection
- Referrer-Policy configuration
- Permissions-Policy restrictions
- Secure authentication flows
- Input validation and sanitization

## Performance Features

- Code splitting and lazy loading
- Image optimization
- Bundle optimization
- Responsive images
- Efficient re-rendering
- Memoization where appropriate

## Development

### Code Style
- ESLint configuration for Next.js
- TypeScript strict mode
- Consistent component structure
- Proper error handling

### Testing
- Component testing with Jest
- Integration testing
- E2E testing with Playwright
- Performance testing

## Deployment

The application is designed to be deployed on:
- Vercel (recommended)
- AWS Amplify
- Netlify
- Any Node.js hosting platform

## Contributing

1. Follow the established code style
2. Write tests for new components
3. Update documentation
4. Ensure accessibility compliance
5. Test across different devices and browsers

## License

This project is part of the AI ERP SaaS platform and is proprietary software.