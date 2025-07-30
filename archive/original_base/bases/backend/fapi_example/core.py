from fastapi import FastAPI
from backend.observability.core import configure_otel_otlp
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from backend.dummy_component.core import print_hello_world
from opentelemetry import trace
from opentelemetry import metrics
import logging

from random import randint

# Acquire a tracer
tracer = trace.get_tracer("diceroller.tracer")
# Acquire a meter.
meter = metrics.get_meter("diceroller.meter")

# Now create a counter instrument to make measurements with
roll_counter = meter.create_counter(
    "dice.rolls",
    description="The number of rolls by roll value",
)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

configure_otel_otlp(service_name="fapi_example", endpoint="http://aspire-dashboard.default:4317") # TODO: set endpoint from envshould be different for local and k3d

app = FastAPI()


@app.get("/")
async def root():
    print_hello_world()
    return {"message": "Hello World"}


@app.get("/error")
async def gen_error():
    return 23/0


@app.get("/rolldice")
async def roll_dice(player: str | None = None):
    # This creates a new span that's the child of the current one
    with tracer.start_as_current_span("roll") as roll_span:
        result = str(roll())
        roll_span.set_attribute("roll.value", result)
        # This adds 1 to the counter for the given roll value
        roll_counter.add(1, {"roll.value": result})
        if player:
            logger.warn(f"{player} is rolling the dice: {result}")
        else:
            logger.warn("Anonymous player is rolling the dice: %s", result)
        return result

def roll():
    return randint(1, 6)

# https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html
FastAPIInstrumentor.instrument_app(app)
