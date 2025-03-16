from fastapi import FastAPI
from backend.observability.core import configure_otel_otlp
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from backend.dummy_component.core import print_hello_world


configure_otel_otlp(service_name="fapi_example", endpoint="http://aspire-dashboard.default:4317") # TODO: set endpoint from envshould be different for local and k3d

app = FastAPI()


@app.get("/")
async def root():
    print_hello_world()
    return {"message": "Hello World"}


@app.get("/error")
async def gen_error():
    return 23/0


# https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html
FastAPIInstrumentor.instrument_app(app)
