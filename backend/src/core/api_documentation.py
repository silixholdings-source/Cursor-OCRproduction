"""
Enhanced API Documentation and OpenAPI Configuration
Provides comprehensive API documentation with examples, schemas, and interactive features
"""
from typing import Dict, Any, List, Optional
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.responses import HTMLResponse
import json

from .config import settings

def create_openapi_schema(app: FastAPI) -> Dict[str, Any]:
    """Create enhanced OpenAPI schema with comprehensive documentation"""
    
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=f"""
        # {settings.APP_NAME} API Documentation
        
        A comprehensive AI-powered ERP SaaS application with advanced invoice processing, 
        OCR capabilities, and multi-tenant architecture.
        
        ## Features
        
        - **Multi-tenant Architecture**: Complete tenant isolation with company-based data segregation
        - **Advanced OCR Processing**: AI-powered invoice data extraction with machine learning
        - **ERP Integration**: Support for major ERP systems (Dynamics GP, D365 BC, Xero, QuickBooks)
        - **Real-time Processing**: Asynchronous invoice processing with real-time status updates
        - **Comprehensive Audit**: Complete audit trail for all operations
        - **Advanced Security**: JWT authentication, role-based access control, rate limiting
        - **Email Processing**: Automated invoice processing from email attachments
        - **Machine Learning**: AI model training and continuous improvement
        
        ## Authentication
        
        All API endpoints require authentication using JWT tokens. Include the token in the 
        Authorization header: `Authorization: Bearer <your-token>`
        
        ## Rate Limiting
        
        API requests are rate limited per IP address and user. Rate limits are returned in 
        response headers:
        - `X-RateLimit-Limit`: Maximum requests per window
        - `X-RateLimit-Remaining`: Remaining requests in current window
        - `X-RateLimit-Reset`: Time when the rate limit resets
        
        ## Error Handling
        
        All errors follow a consistent format:
        ```json
        {{
            "error": {{
                "id": "unique-error-id",
                "code": "ERROR_CODE",
                "message": "Human-readable error message",
                "details": {{}},
                "timestamp": "2024-01-01T00:00:00Z",
                "path": "/api/v1/endpoint",
                "method": "POST"
            }}
        }}
        ```
        
        ## Pagination
        
        List endpoints support pagination with the following parameters:
        - `page`: Page number (default: 1)
        - `size`: Items per page (default: 20, max: 100)
        - `sort`: Sort field (default: created_at)
        - `order`: Sort order (asc/desc, default: desc)
        
        ## Multi-tenancy
        
        All data is automatically scoped to the authenticated user's company. Users can only 
        access data belonging to their company.
        
        ## Webhooks
        
        The API supports webhooks for real-time notifications. Configure webhook endpoints 
        in your company settings to receive notifications for:
        - Invoice processing completion
        - ERP synchronization events
        - System alerts and notifications
        
        ## Support
        
        For API support and questions:
        - Documentation: https://docs.ai-erp-saas.com
        - Support Email: support@ai-erp-saas.com
        - Status Page: https://status.ai-erp-saas.com
        """,
        routes=app.routes,
        servers=[
            {
                "url": "https://api.ai-erp-saas.com",
                "description": "Production server"
            },
            {
                "url": "https://staging-api.ai-erp-saas.com", 
                "description": "Staging server"
            },
            {
                "url": "http://localhost:8000",
                "description": "Development server"
            }
        ]
    )
    
    # Add custom OpenAPI extensions
    openapi_schema["x-logo"] = {
        "url": "https://ai-erp-saas.com/logo.png",
        "altText": "AI ERP SaaS Logo"
    }
    
    openapi_schema["x-tagGroups"] = [
        {
            "name": "Authentication",
            "tags": ["authentication"]
        },
        {
            "name": "Company Management", 
            "tags": ["companies"]
        },
        {
            "name": "User Management",
            "tags": ["users"]
        },
        {
            "name": "Invoice Processing",
            "tags": ["invoices", "invoice-processing"]
        },
        {
            "name": "OCR & AI/ML",
            "tags": ["ocr-ai-ml"]
        },
        {
            "name": "ERP Integration",
            "tags": ["erp-integration"]
        },
        {
            "name": "System Health",
            "tags": ["health"]
        }
    ]
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token obtained from /api/v1/auth/login endpoint"
        },
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API key for programmatic access"
        }
    }
    
    # Add global security
    openapi_schema["security"] = [{"BearerAuth": []}]
    
    # Add examples for common responses
    openapi_schema["components"]["examples"] = {
        "SuccessResponse": {
            "summary": "Successful API Response",
            "value": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {},
                "timestamp": "2024-01-01T00:00:00Z"
            }
        },
        "ErrorResponse": {
            "summary": "Error Response",
            "value": {
                "error": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": {
                        "field": "email",
                        "message": "Invalid email format"
                    },
                    "timestamp": "2024-01-01T00:00:00Z",
                    "path": "/api/v1/users",
                    "method": "POST"
                }
            }
        },
        "PaginatedResponse": {
            "summary": "Paginated List Response",
            "value": {
                "success": True,
                "message": "Data retrieved successfully",
                "data": [],
                "meta": {
                    "pagination": {
                        "page": 1,
                        "size": 20,
                        "total": 100,
                        "pages": 5,
                        "has_next": True,
                        "has_prev": False
                    },
                    "sort": {
                        "field": "created_at",
                        "order": "desc"
                    }
                },
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }
    }
    
    # Add external documentation
    openapi_schema["externalDocs"] = {
        "description": "API Documentation",
        "url": "https://docs.ai-erp-saas.com"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

def create_enhanced_docs_routes(app: FastAPI):
    """Create enhanced documentation routes with custom styling and features"""
    
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui():
        """Custom Swagger UI with enhanced features"""
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=f"{settings.APP_NAME} API Documentation",
            swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
            swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
            swagger_ui_parameters={
                "deepLinking": True,
                "displayOperationId": True,
                "filter": True,
                "showExtensions": True,
                "showCommonExtensions": True,
                "tryItOutEnabled": True,
                "requestSnippetsEnabled": True,
                "syntaxHighlight": {
                    "activate": True,
                    "theme": "agate"
                },
                "layout": "StandaloneLayout",
                "plugins": [
                    "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/plugins/try-it-out/try-it-out.js"
                ]
            }
        )
    
    @app.get("/redoc", include_in_schema=False)
    async def custom_redoc():
        """Custom ReDoc with enhanced features"""
        return get_redoc_html(
            openapi_url=app.openapi_url,
            title=f"{settings.APP_NAME} API Documentation",
            redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.1.3/bundles/redoc.standalone.js",
            redoc_js_url_2="https://cdn.jsdelivr.net/npm/redoc@2.1.3/bundles/redoc.standalone.js",
            redoc_favicon_url="https://redoc.ly/img/favicon.png",
            redoc_options={
                "theme": {
                    "colors": {
                        "primary": {
                            "main": "#1976d2"
                        }
                    },
                    "typography": {
                        "fontSize": "14px",
                        "lineHeight": "1.5em",
                        "code": {
                            "fontSize": "13px"
                        }
                    }
                },
                "scrollYOffset": 0,
                "hideDownloadButton": False,
                "hideHostname": False,
                "hideLoading": False,
                "nativeScrollbars": False,
                "pathInMiddlePanel": True,
                "requiredPropsFirst": True,
                "sortPropsAlphabetically": False,
                "showObjectSchemaExamples": True,
                "jsonSampleExpandLevel": 2,
                "hideSchemaPattern": False,
                "expandDefaultServerVariables": True,
                "maxDisplayedEnumValues": 10,
                "hideSingleRequestSampleTab": False,
                "menuToggle": True,
                "search": True,
                "searchMaxDepth": 10,
                "searchHotKey": "ctrl+k",
                "searchHotKey": "cmd+k"
            }
        )
    
    @app.get("/openapi.json", include_in_schema=False)
    async def get_openapi_json():
        """Get OpenAPI schema as JSON"""
        return create_openapi_schema(app)
    
    @app.get("/api-docs", include_in_schema=False)
    async def api_docs_landing():
        """API documentation landing page"""
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>AI ERP SaaS API Documentation</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .card { border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin: 20px 0; }
                .button { display: inline-block; padding: 10px 20px; background: #1976d2; color: white; text-decoration: none; border-radius: 4px; margin: 5px; }
                .button:hover { background: #1565c0; }
                .feature { margin: 10px 0; }
                .code { background: #f5f5f5; padding: 10px; border-radius: 4px; font-family: monospace; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>AI ERP SaaS API Documentation</h1>
                <p>Welcome to the AI ERP SaaS API documentation. Choose your preferred documentation format:</p>
                
                <div class="card">
                    <h2>Interactive Documentation</h2>
                    <p>Try out the API endpoints directly in your browser:</p>
                    <a href="/docs" class="button">Swagger UI</a>
                    <a href="/redoc" class="button">ReDoc</a>
                </div>
                
                <div class="card">
                    <h2>API Schema</h2>
                    <p>Download the complete OpenAPI specification:</p>
                    <a href="/openapi.json" class="button">OpenAPI JSON</a>
                </div>
                
                <div class="card">
                    <h2>Quick Start</h2>
                    <div class="feature">
                        <h3>1. Authentication</h3>
                        <p>Get your JWT token by logging in:</p>
                        <div class="code">POST /api/v1/auth/login</div>
                    </div>
                    <div class="feature">
                        <h3>2. Process Invoice</h3>
                        <p>Upload and process an invoice:</p>
                        <div class="code">POST /api/v1/processing/upload</div>
                    </div>
                    <div class="feature">
                        <h3>3. View Results</h3>
                        <p>Check processing status and results:</p>
                        <div class="code">GET /api/v1/invoices</div>
                    </div>
                </div>
                
                <div class="card">
                    <h2>Features</h2>
                    <ul>
                        <li>Multi-tenant architecture with complete data isolation</li>
                        <li>Advanced OCR processing with AI/ML capabilities</li>
                        <li>ERP integration (Dynamics GP, D365 BC, Xero, QuickBooks)</li>
                        <li>Real-time processing with webhook notifications</li>
                        <li>Comprehensive audit trail and logging</li>
                        <li>Advanced security with rate limiting and validation</li>
                        <li>Email-based invoice processing</li>
                        <li>Machine learning model training and improvement</li>
                    </ul>
                </div>
            </div>
        </body>
        </html>
        """)

def add_response_examples():
    """Add comprehensive response examples to OpenAPI schema"""
    return {
        "responses": {
            "200": {
                "description": "Successful response",
                "content": {
                    "application/json": {
                        "example": {
                            "success": True,
                            "message": "Operation completed successfully",
                            "data": {},
                            "timestamp": "2024-01-01T00:00:00Z"
                        }
                    }
                }
            },
            "400": {
                "description": "Bad request",
                "content": {
                    "application/json": {
                        "example": {
                            "error": {
                                "id": "550e8400-e29b-41d4-a716-446655440000",
                                "code": "VALIDATION_ERROR",
                                "message": "Request validation failed",
                                "details": {
                                    "field": "email",
                                    "message": "Invalid email format"
                                },
                                "timestamp": "2024-01-01T00:00:00Z",
                                "path": "/api/v1/users",
                                "method": "POST"
                            }
                        }
                    }
                }
            },
            "401": {
                "description": "Unauthorized",
                "content": {
                    "application/json": {
                        "example": {
                            "error": {
                                "id": "550e8400-e29b-41d4-a716-446655440000",
                                "code": "AUTHENTICATION_ERROR",
                                "message": "Authentication failed",
                                "timestamp": "2024-01-01T00:00:00Z",
                                "path": "/api/v1/invoices",
                                "method": "GET"
                            }
                        }
                    }
                }
            },
            "403": {
                "description": "Forbidden",
                "content": {
                    "application/json": {
                        "example": {
                            "error": {
                                "id": "550e8400-e29b-41d4-a716-446655440000",
                                "code": "AUTHORIZATION_ERROR",
                                "message": "Insufficient permissions",
                                "timestamp": "2024-01-01T00:00:00Z",
                                "path": "/api/v1/companies",
                                "method": "POST"
                            }
                        }
                    }
                }
            },
            "404": {
                "description": "Not found",
                "content": {
                    "application/json": {
                        "example": {
                            "error": {
                                "id": "550e8400-e29b-41d4-a716-446655440000",
                                "code": "NOT_FOUND",
                                "message": "Resource not found",
                                "timestamp": "2024-01-01T00:00:00Z",
                                "path": "/api/v1/invoices/123",
                                "method": "GET"
                            }
                        }
                    }
                }
            },
            "429": {
                "description": "Too many requests",
                "content": {
                    "application/json": {
                        "example": {
                            "error": {
                                "id": "550e8400-e29b-41d4-a716-446655440000",
                                "code": "RATE_LIMIT_EXCEEDED",
                                "message": "Rate limit exceeded",
                                "details": {
                                    "retry_after": 60
                                },
                                "timestamp": "2024-01-01T00:00:00Z",
                                "path": "/api/v1/invoices",
                                "method": "POST"
                            }
                        }
                    }
                }
            },
            "500": {
                "description": "Internal server error",
                "content": {
                    "application/json": {
                        "example": {
                            "error": {
                                "id": "550e8400-e29b-41d4-a716-446655440000",
                                "code": "INTERNAL_ERROR",
                                "message": "An unexpected error occurred",
                                "timestamp": "2024-01-01T00:00:00Z",
                                "path": "/api/v1/invoices",
                                "method": "POST"
                            }
                        }
                    }
                }
            }
        }
    }
