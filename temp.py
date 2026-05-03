# Define a typed scenario subclass with defaults
class EpsteinScenario(Scenario):
    """Scenario parameters for Epstein Civil Violence model."""

    citizen_density: float = 0.7
    cop_density: float = 0.074
    citizen_vision: int = 7
    cop_vision: int = 7
    legitimacy: float = 0.8
    max_jail_term: int = 1000
    active_threshold: float = 0.1
    arrest_prob_constant: float = 2.3
    movement: bool = True
    max_iters: int = 1000
    activation_order: Literal["Random", "Sequential"] = "Random"
    grid_type: Literal["Von Neumann", "Moore"] = "Von Neumann"
    rng: int = 42



model_params = {
    "rng": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "height": 40,
    "width": 40,
    "citizen_density": Slider("Initial Agent Density", 0.7, 0.1, 0.9, 0.1),
    "cop_density": Slider("Initial Cop Density", 0.04, 0.0, 0.1, 0.01),
    "citizen_vision": Slider("Citizen Vision", 7, 1, 10, 1),
    "cop_vision": Slider("Cop Vision", 7, 1, 10, 1),
    "legitimacy": Slider("Government Legitimacy", 0.82, 0.0, 1, 0.01),
    "max_jail_term": Slider("Max Jail Term", 30, 0, 50, 1),
    "activation_order": {
        "type": "Select",
        "value": "Random",
        "values": ["Random", "Sequential"],
        "label": "Activation Order",
    },
    "grid_type": {
        "type": "Select",
        "value": "Von Neumann",
        "values": ["Von Neumann", "Moore"],
        "label": "Grid Type",
    },
}