# ruff: noqa: PLR2004
from warnings import warn

from ._shaped_perlin import ShapeCreator, ShapeFunction


class OilSimulator:
    # pylint: disable=too-many-public-methods
    """OilSimulator is the builder of the model and the generator of the values.


    Generates oil simulator values based on perlin-noise.

    :param ooip: Oil in place for the entire field at initial conditions.
    :param goip: Gas in place for the entire field at initial conditions.
    :param woip: Water in place for the entire field at initial conditions.

    """

    OPR_SHAPE = ShapeFunction([0.0, 0.2, 0.5, 0.7, 1.0], [0.0, 0.7, 0.2, 0.1, 0.01])
    GPR_SHAPE = ShapeFunction([0.0, 0.2, 0.5, 0.7, 1.0], [0.0, 0.5, 0.7, 0.7, 0.3])
    WPR_SHAPE = ShapeFunction([0.0, 0.2, 0.5, 0.7, 1.0], [0.0, 0.01, 0.3, 0.7, 1])
    BPR_SHAPE = ShapeFunction([0.0, 0.2, 0.5, 0.7, 1.0], [1.0, 0.7, 0.5, 0.3, 0.1])

    O_DIVERGENCE = ShapeFunction([0.0, 0.5, 0.7, 0.9, 1.0], [0.0, 0.5, 0.3, 0.1, 0.01])
    G_DIVERGENCE = ShapeFunction([0.0, 0.5, 0.7, 0.9, 1.0], [0.0, 0.1, 0.3, 0.2, 0.1])
    W_DIVERGENCE = ShapeFunction([0.0, 0.5, 0.7, 0.9, 1.0], [0.0, 0.1, 0.3, 0.2, 0.01])
    B_DIVERGENCE = ShapeFunction([0.0, 0.5, 0.7, 0.9, 1.0], [0.0, 0.1, 0.2, 0.3, 0.5])

    def __init__(self, ooip=2000, goip=2500, woip=2250):
        self._foip = self.ooip = ooip
        self._fgip = self.goip = goip
        self._fwip = self.woip = woip

        self._opr_func = {}  # Oil production rate function for each well
        self._gpr_func = {}  # Gas production rate function for each well
        self._wpr_func = {}  # Water produtcion rate function for each well
        self._bpr_func = {}  # Pressure function for each block
        self._current_step = 0

        self._fopt = 0.0  # Oil production total for entire reservoir
        self._fopr = 0.0  # Oil production rate for entire reservoir
        self._fgpt = 0.0  # Gas production tota for entire reservoir
        self._fgpr = 0.0  # Gas production rate for entire reservoir
        self._fwpt = 0.0  # Water production total for entire reservoir
        self._fwpr = 0.0  # Water production rate for entire reservoir

        self._fgor = 0.0  # Gas oil ratio for entire reservoir
        self._fwct = 0.0  # water cut for entire reservoir

        self._wells = {}
        self._bpr = {}  # Block pressure for each block

    def addWell(self, *args, **kwargs):
        # pylint: disable=invalid-name
        warn(
            "addWell() is deprecated. Use add_well().", DeprecationWarning, stacklevel=2
        )
        self.add_well(*args, **kwargs)

    def add_well(  # noqa: PLR0913
        self, name, seed, persistence=0.2, octaves=8, divergence_scale=1.0, offset=0.0
    ):
        """Add a well to the simulator model."""
        oil_div = OilSimulator.O_DIVERGENCE.scaled_copy(divergence_scale)
        gas_div = OilSimulator.G_DIVERGENCE.scaled_copy(divergence_scale)
        water_div = OilSimulator.W_DIVERGENCE.scaled_copy(divergence_scale)
        self._opr_func[name] = ShapeCreator.create_noise_function(
            OilSimulator.OPR_SHAPE,
            oil_div,
            seed,
            persistence=persistence,
            octaves=octaves,
            cutoff=0.0,
            offset=offset,
        )
        self._gpr_func[name] = ShapeCreator.create_noise_function(
            OilSimulator.GPR_SHAPE,
            gas_div,
            seed * 7,
            persistence=persistence * 3.5,
            octaves=octaves / 2,
            cutoff=0.0,
            offset=offset,
        )
        self._wpr_func[name] = ShapeCreator.create_noise_function(
            OilSimulator.WPR_SHAPE,
            water_div,
            seed * 11,
            persistence=persistence,
            octaves=octaves,
            cutoff=0.0,
            offset=offset,
        )

        self._wells[name] = {
            "opr": 0.0,
            "opt": 0.0,
            "gpr": 0.0,
            "gpt": 0.0,
            "wpr": 0.0,
            "wpt": 0.0,
        }

    def addBlock(self, *args, **kwargs):
        # pylint: disable=invalid-name
        warn(
            "addBlock() is deprecated. Use add_block().",
            DeprecationWarning,
            stacklevel=2,
        )
        self.add_block(*args, **kwargs)

    def add_block(self, name, seed, persistence=0.2):
        """Add a grid block to the model"""
        self._bpr_func[name] = ShapeCreator.create_noise_function(
            OilSimulator.BPR_SHAPE,
            OilSimulator.B_DIVERGENCE,
            seed,
            persistence=persistence,
            cutoff=0.0,
        )
        self._bpr[name] = 0.0

    def step(self, scale=1.0):
        """Step the simulator forward in time.
        :param scale: From 0.0 to 1.0. How far to step, 0.0 means no time. 1.0
            means go from start to finish in one step.
        """
        self._fopr = 0.0
        self._fgpr = 0.0
        self._fwpr = 0.0
        self._fgor = 0.0
        self._fwct = 0.0
        for key, well in self._wells.items():
            opr_function = self._opr_func[key]
            gpr_function = self._gpr_func[key]
            wpr_function = self._wpr_func[key]
            opr_value = opr_function(self._current_step, scale)
            gpr_value = gpr_function(self._current_step, scale)
            wpr_value = wpr_function(self._current_step, scale)

            if self._foip > 0.0:
                well["opr"] = opr_value
                well["opt"] += opr_value
                self._fopr += opr_value

            if self._fgip > 0.0:
                well["gpr"] = gpr_value
                well["gpt"] += gpr_value
                self._fgpr += gpr_value

            if self._fwip > 0.0:
                well["wpr"] = wpr_value
                well["wpt"] += wpr_value
                self._fwpr += wpr_value

            self._fgor += self.gor(key)
            self._fwct += self.wct(key)

        self._foip -= self._fopr
        self._fgip -= self._fgpr
        self._fwip -= self._fwpr

        self._foip = max(
            self._foip, 0.0
        )  # This may lead to the total (FOPT) larger than OOIP
        self._fgip = max(self._fgip, 0.0)
        self._fwip = max(self._fwip, 0.0)

        self._fopt += self._fopr
        self._fgpt += self._fgpr
        self._fwpt += self._fwpr

        self._fgor /= len(self._wells)
        self._fwct /= len(self._wells)

        for key in self._bpr:
            bpr_function = self._bpr_func[key]
            self._bpr[key] = bpr_function(self._current_step, scale)

        self._current_step += 1

    def fopt(self):
        """Get the field oil production total at the current time."""
        return self._fopt

    def fopr(self):
        """Get the field oil production rate at the current time."""
        return self._fopr

    def fgpt(self):
        """Get the field gas production total at the current time."""
        return self._fgpt

    def fgpr(self):
        """Get the field gas production rate at the current time."""
        return self._fgpr

    def fwpt(self):
        """Get the field water production total at the current time."""
        return self._fwpt

    def fwpr(self):
        """Get the field water production rate at the current time."""
        return self._fwpr

    def fgor(self):
        """Get the field gas oil ratio at the current time."""
        return self._fgor

    def fwct(self):
        """Get the field water cut at the current time."""
        return self._fwct

    def foip(self):
        """Get the field oil in place at the current time."""
        return self._foip

    def fgip(self):
        """Get the field gas in place at the current time."""
        return self._fgip

    def fwip(self):
        """Get the field water in place at the current time."""
        return self._fwip

    def opr(self, well_name):
        """Get the oil rate for the given well at the current time."""
        return self._wells[well_name]["opr"]

    def gpr(self, well_name):
        """Get the gas rate for the given well at the current time."""
        return self._wells[well_name]["gpr"]

    def wpr(self, well_name):
        """Get the water rate for the given well at the current time."""
        return self._wells[well_name]["wpr"]

    def wct(self, well_name):
        """Get the water cut for the given well at the current time."""
        opr = self.opr(well_name)
        wpr = self.wpr(well_name)
        opr = max(opr, 0.1)
        return wpr / (wpr + opr) if (wpr + opr) > 0.0 else 0.0

    def gor(self, well_name):
        """Get the gas oil ratio for the given well at the current time."""
        opr = self.opr(well_name)
        gpr = self.gpr(well_name)
        opr = max(opr, 0.1)
        gpr = max(gpr, 0.1)
        return gpr / opr

    def bpr(self, block_name):
        """Get the block pressure for the given block at the current time."""
        return self._bpr[block_name]
