"""Fictional same-day IST inventory. Nothing here is real availability."""

from backend.models import Option, RescueRequest, minutes

ROUTES = {"rail": ("varkala", "kochi"), "flight": ("kochi", "bengaluru"), "weather": ("munnar", "kochi")}


def travel(identifier, kind, title, subtitle, departure, arrival, cost, tags, steps):
    return Option(id=identifier, kind=kind, title=title, subtitle=subtitle,
                  departure=departure, arrival=arrival, duration_minutes=minutes(arrival) - minutes(departure),
                  cost=cost, tags=["Fictional fixture", *tags], steps=steps)


TRANSPORT = {
    "rail": [
        travel("rail-bus-01", "bus", "Coastal express coach", "Varkala → Kochi · illustrative direct service", "15:10", "19:45", 680,
               ["Direct"], ["Use the fictional Varkala coach stop.", "Board the 15:10 coach.", "Arrive at the fictional Kochi terminal at 19:45."]),
        travel("rail-train-01", "train", "Evening relief train", "Varkala → Kochi · illustrative alternate train", "16:20", "20:35", 420,
               ["Alternate service"], ["Use the fictional alternate service, not the cancelled train.", "Depart Varkala at 16:20.", "Arrive in Kochi at 20:35."]),
        travel("rail-taxi-01", "taxi", "Shared coastal cab", "Varkala → Kochi · illustrative shared fare", "15:00", "19:10", 2850,
               ["Shared ride"], ["Use the fictional shared-cab pickup point.", "Leave at 15:00.", "Arrive in Kochi at 19:10."]),
        travel("rail-taxi-02", "taxi", "Private direct cab", "Varkala → Kochi · illustrative private fare", "15:05", "18:55", 4600,
               ["Private ride"], ["Depart the fictional pickup point at 15:05.", "Arrive in Kochi at 18:55."]),
    ],
    # No invented same-evening Kochi–Bengaluru surface transfer: the fixture has no feasible transport.
    "flight": [],
    "weather": [
        travel("weather-bus-01", "bus", "Valley route coach", "Munnar → Kochi · fictional service, verify road conditions first", "16:00", "21:15", 950,
               ["Conditions must be checked"], ["This fictional schedule is not evidence that a road is safe.", "Verify current conditions with a real operator before travel.", "Illustrative departure 16:00; arrival 21:15."]),
    ],
}

STAYS = {
    "flight": [
        travel("flight-stay-01", "stay", "Airport rest house", "Kochi · one fictional night + local transfer; not arrival in Bengaluru", "18:45", "19:05", 2400,
               ["Near airport", "Transfer included"], ["Take the fictional 18:45 local transfer in Kochi.", "Check in at 19:05; one night is included.", "Onward travel to Bengaluru is not included or booked."]),
        travel("flight-stay-02", "stay", "Courtyard guest room", "Kochi · one fictional night + local transfer; not arrival in Bengaluru", "19:00", "19:35", 1650,
               ["Guest room", "Transfer included"], ["Take the fictional 19:00 local transfer in Kochi.", "Check in at 19:35; one night is included.", "Plan onward travel separately; nothing is booked."]),
    ]
}

ADVISORIES = {
    "weather": [
        Option(id="weather-advisory-01", kind="advisory", title="Hill-road disruption bulletin", subtitle="Munnar → Kochi · fictional monsoon report",
               tags=["Fictional fixture", "Verify conditions"], steps=["The scenario assumes a closure on the hill-road segment after heavy rain.", "This is not a current weather report or a road-safety assessment.", "Check official local updates and your operator before departing."]),
        Option(id="weather-advisory-02", kind="advisory", title="Recheck before rerouting", subtitle="Munnar → Kochi · fictional recovery guidance",
               tags=["Fictional fixture", "No arrival guarantee"], steps=["Do not interpret an alternate route as verified safe.", "Confirm any revised route and departure with the operator.", "If travel is suspended, arrange a place to wait; this report does not include a stay or transfer."]),
    ]
}


def run_tool(choice: str, request: RescueRequest) -> list[Option]:
    if (request.origin.casefold(), request.destination.casefold()) != ROUTES[request.scenario]:
        return []
    registries = {"find_transport": TRANSPORT, "find_stay": STAYS, "check_disruptions": ADVISORIES}
    candidates = registries[choice].get(request.scenario, [])
    return [option.model_copy(deep=True) for option in candidates
            if (option.cost is None or option.cost <= request.budget)
            and (option.departure is None or minutes(option.departure) > minutes(request.current_time))
            and (option.arrival is None or minutes(option.arrival) <= minutes(request.arrive_by))]
