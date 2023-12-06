# Oil Reservoir Synthesizer

A generator for synthetic oil reservoir simulator results based
on [Perlin noise](https://en.wikipedia.org/wiki/Perlin_noise). The
values generated are pseudo-random but retains the nice properties
of Perlin noise.

The values generated have names (such as fopr) that are derived from oil
simulators such as [opm-flow](opm-project.org).

## Example

The code exposes one class, `OilSimulator` which is a builder of
the oil reservoir model and the generator of the values.

```python

from oil_reservoir_synthesizer import OilSimulator

simulator = OilSimulator()

# Build a model with one well and block
simulator.add_well("wellName", seed=997)
simulator.add_block("5,5,5", seed=31)

# Run simulation
num_steps = 10
fopr_values = []  # oil production rate for each time step
for time_steps in range(num_steps):
    simulator.step(scale=1.0 / num_steps)
    fopr_values.append(simulator.fopr())

```

## Building

```sh
pip install .
```

## Testing

```sh
pip install -e .[dev]
tox test
```

## History

This project was split out of [ERT](https://github.com/equinor/ert) and
[libres](https://github.com/equinor/libres).
