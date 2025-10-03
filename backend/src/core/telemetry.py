import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from .config import settings
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

logger = logging.getLogger(__name__)

def setup_telemetry():
    """Setup OpenTelemetry and Sentry for observability"""
    
    # Setup Sentry if DSN is provided
    if settings.SENTRY_DSN:
        try:
            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                environment=settings.ENVIRONMENT,
                integrations=[FastApiIntegration()],
                traces_sample_rate=1.0 if settings.ENVIRONMENT == "development" else 0.1,
                profiles_sample_rate=1.0 if settings.ENVIRONMENT == "development" else 0.1,
            )
            logger.info("Sentry integration enabled")
        except Exception as e:
            logger.warning(f"Failed to setup Sentry: {e}")
    
    # Setup OpenTelemetry
    try:
        # Create tracer provider
        provider = TracerProvider()
        trace.set_tracer_provider(provider)
        
        # Add console exporter for development
        if settings.ENVIRONMENT == "development":
            console_exporter = ConsoleSpanExporter()
            provider.add_span_processor(BatchSpanProcessor(console_exporter))
            logger.info("OpenTelemetry console exporter enabled")
        
        # Add OTLP exporter if endpoint is provided
        if settings.OTEL_ENDPOINT:
            try:
                from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
                otlp_exporter = OTLPSpanExporter(endpoint=settings.OTEL_ENDPOINT)
                provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
                logger.info("OpenTelemetry OTLP exporter enabled")
            except ImportError:
                logger.warning("OTLP exporter not available, skipping")
            except Exception as e:
                logger.warning(f"Failed to setup OTLP exporter: {e}")
        
        logger.info("OpenTelemetry setup complete")
        
    except Exception as e:
        logger.warning(f"Failed to setup OpenTelemetry: {e}")

def instrument_app(app):
    """Instrument FastAPI app with OpenTelemetry"""
    try:
        FastAPIInstrumentor.instrument_app(app)
        logger.info("FastAPI instrumentation enabled")
    except Exception as e:
        logger.warning(f"Failed to instrument FastAPI: {e}")

def instrument_sqlalchemy():
    """Instrument SQLAlchemy with OpenTelemetry"""
    try:
        SQLAlchemyInstrumentor().instrument()
        logger.info("SQLAlchemy instrumentation enabled")
    except Exception as e:
        logger.warning(f"Failed to instrument SQLAlchemy: {e}")

def instrument_redis():
    """Instrument Redis with OpenTelemetry"""
    try:
        RedisInstrumentor().instrument()
        logger.info("Redis instrumentation enabled")
    except Exception as e:
        logger.warning(f"Failed to instrument Redis: {e}")

def instrument_celery():
    """Instrument Celery with OpenTelemetry"""
    try:
        CeleryInstrumentor().instrument()
        logger.info("Celery instrumentation enabled")
    except Exception as e:
        logger.warning(f"Failed to instrument Celery: {e}")
