/**
 * Security Configuration for Next.js Application
 * Implements comprehensive security headers and CSP policies
 */

const securityHeaders = [
  {
    key: 'X-DNS-Prefetch-Control',
    value: 'on'
  },
  {
    key: 'Strict-Transport-Security',
    value: 'max-age=63072000; includeSubDomains; preload'
  },
  {
    key: 'X-XSS-Protection',
    value: '1; mode=block'
  },
  {
    key: 'X-Frame-Options',
    value: 'SAMEORIGIN'
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff'
  },
  {
    key: 'Referrer-Policy',
    value: 'origin-when-cross-origin'
  },
  {
    key: 'Permissions-Policy',
    value: 'camera=(), microphone=(), geolocation=(), interest-cohort=()'
  },
  {
    key: 'Content-Security-Policy',
    value: [
      "default-src 'self'",
      "script-src 'self' 'unsafe-eval' 'unsafe-inline' https://js.stripe.com",
      "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
      "img-src 'self' data: https: blob:",
      "font-src 'self' https://fonts.gstatic.com",
      "connect-src 'self' https://api.stripe.com https://*.stripe.com",
      "frame-src 'self' https://js.stripe.com https://hooks.stripe.com",
      "object-src 'none'",
      "base-uri 'self'",
      "form-action 'self'",
      "frame-ancestors 'none'",
      "upgrade-insecure-requests"
    ].join('; ')
  }
];

const securityConfig = {
  headers: securityHeaders,
  
  // Additional security configurations
  poweredByHeader: false,
  
  // Security middleware
  middleware: [
    // Rate limiting
    {
      name: 'rate-limit',
      config: {
        windowMs: 15 * 60 * 1000, // 15 minutes
        max: 100, // limit each IP to 100 requests per windowMs
        message: 'Too many requests from this IP, please try again later.'
      }
    },
    
    // CORS configuration
    {
      name: 'cors',
      config: {
        origin: process.env.NODE_ENV === 'production' 
          ? ['https://ai-erp-saas.com', 'https://www.ai-erp-saas.com']
          : ['http://localhost:3000', 'http://localhost:8000'],
        credentials: true,
        optionsSuccessStatus: 200
      }
    }
  ],
  
  // Content Security Policy for specific pages
  csp: {
    '/api': {
      'script-src': ["'self'", "'unsafe-inline'"],
      'connect-src': ["'self'", "https://api.stripe.com"]
    },
    '/admin': {
      'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
      'style-src': ["'self'", "'unsafe-inline'"]
    }
  },
  
  // Security validation rules
  validation: {
    // Input sanitization rules
    sanitize: {
      html: true,
      sql: true,
      xss: true
    },
    
    // Password requirements
    password: {
      minLength: 12,
      requireUppercase: true,
      requireLowercase: true,
      requireNumbers: true,
      requireSpecialChars: true,
      maxAttempts: 5,
      lockoutDuration: 15 * 60 * 1000 // 15 minutes
    },
    
    // Session security
    session: {
      secure: process.env.NODE_ENV === 'production',
      httpOnly: true,
      sameSite: 'strict',
      maxAge: 24 * 60 * 60 * 1000 // 24 hours
    }
  }
};

module.exports = securityConfig;
