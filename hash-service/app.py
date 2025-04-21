import hashlib
from flask import Flask, request, jsonify
import logging
import os
from prometheus_flask_exporter import PrometheusMetrics
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure OpenTelemetry
resource = Resource(attributes={
    SERVICE_NAME: "hash-service"
})

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# Configure Jaeger exporter
jaeger_host = os.getenv("JAEGER_HOST", "jaeger")
jaeger_port = int(os.getenv("JAEGER_PORT", "6831"))

jaeger_exporter = JaegerExporter(
    agent_host_name=jaeger_host,
    agent_port=jaeger_port,
)

trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

app = Flask(__name__)

# Initialize Flask instrumentation
FlaskInstrumentor().instrument_app(app)

# Initialize Prometheus metrics
metrics = PrometheusMetrics(app)
metrics.info('hash_service_info', 'Hash service info', version='1.0.0')

# Define custom metrics
request_counter = metrics.counter(
    'hash_request_count', 'Number of hash requests', 
    labels={'status': lambda r: r.status_code}
)
request_duration = metrics.histogram(
    'hash_request_duration_seconds', 'Hash request duration in seconds',
    buckets=(0.1, 0.3, 0.5, 0.7, 1.0, 3.0)
)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Kubernetes probes"""
    return jsonify({"status": "healthy"}), 200

@app.route('/metrics', methods=['GET'])
def metrics_endpoint():
    """Endpoint for Prometheus metrics"""
    return metrics.generate_latest()

@app.route('/hash', methods=['POST'])
@request_counter
@request_duration
def calculate_hash():
    """Calculate SHA256 hash of input string"""
    try:
        with tracer.start_as_current_span("calculate_hash") as span:
            # Get input text from request body
            input_text = request.get_data(as_text=True)
            
            if not input_text:
                logger.warning("Empty input received")
                span.set_attribute("error", True)
                span.set_attribute("error.message", "Empty input received")
                return jsonify({"error": "Input text is required"}), 400
            
            # Add span attributes
            span.set_attribute("input.length", len(input_text))
            
            # Calculate SHA256 hash
            hash_result = hashlib.sha256(input_text.encode()).hexdigest()
            
            logger.info(f"Calculated hash for input of length {len(input_text)}")
            span.set_attribute("hash.length", len(hash_result))
            
            return hash_result, 200
    
    except Exception as e:
        logger.error(f"Error calculating hash: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", "8080"))
    app.run(host='0.0.0.0', port=port)
