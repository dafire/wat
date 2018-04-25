from collections import OrderedDict

from wot_api.models import VehicleStatisticItem


class WN8TankEntry:
    def __init__(self, s: VehicleStatisticItem):
        self.vehicle_id = s.vehicle_id
        self.name = s.vehicle.name
        self.battles = s.all.get("battles")
        self.expected_fragged = s.vehicle.expected.exp_frag
        self.expected_spotted = s.vehicle.expected.exp_spot
        self.expected_damage_done = s.vehicle.expected.exp_damage
        self.expected_deffed = s.vehicle.expected.exp_def
        self.expected_winrate = s.vehicle.expected.exp_win_rate
        self.deffed = s.all.get("dropped_capture_points")
        self.fragged = s.all.get("frags")
        self.spotted = s.all.get("spotted")
        self.damage_done = s.all.get("damage_dealt")
        self.wins = s.all.get("wins")

    @property
    def winrate(self):
        return self.wins / self.battles * 100

    @property
    def average_damage_done(self):
        return self.damage_done / self.battles

    @property
    def average_fragged(self):
        return self.fragged / self.battles

    @property
    def average_spotted(self):
        return self.spotted / self.battles

    @property
    def average_deffed(self):
        return self.deffed / self.battles

    @property
    def expected_wins(self):
        return self.expected_winrate * self.battles

    @property
    def wn8(self):
        ratio_damage_done = self.average_damage_done / self.expected_damage_done
        ratio_spotted = self.average_spotted / self.expected_spotted
        ratio_fragged = self.average_fragged / self.expected_fragged
        ratio_deffed = self.average_deffed / self.expected_deffed
        ratio_wins = self.wins / self.expected_wins

        ratio_wins_calculated = max(0.0, (ratio_wins - 0.71) / (1 - 0.71))
        ratio_damage_done_calculated = max(0.0, (ratio_damage_done - 0.22) / (1 - 0.22))
        ratio_frags_calculated = max(0.0, min(ratio_damage_done_calculated + 0.2, (ratio_fragged - 0.12) / (1 - 0.12)))
        ratio_spots_calculated = max(0.0, min(ratio_damage_done_calculated + 0.1, (ratio_spotted - 0.38) / (1 - 0.38)))
        ratio_deffed_calculated = max(0.0, min(ratio_damage_done_calculated + 0.1, (ratio_deffed - 0.10) / (1 - 0.10)))

        wn8 = 980 * ratio_damage_done_calculated \
              + 210 * ratio_damage_done_calculated * ratio_frags_calculated \
              + 155 * ratio_frags_calculated * ratio_spots_calculated \
              + ratio_spots_calculated \
              + 75 * ratio_deffed_calculated * ratio_frags_calculated \
              + 145 * min(1.8, ratio_wins_calculated)

        return wn8


class WN8Calculation:
    def __init__(self):
        self.expected_fragged = 0
        self.expected_spotted = 0
        self.expected_damage = 0
        self.expected_deffed = 0
        self.expected_wins = 0
        self.deffed = 0
        self.frags = 0
        self.spotted = 0
        self.battles = 0
        self.damage_done = 0
        self.wins = 0
        self.vehicles = OrderedDict()

    def add_vehicle(self, s: VehicleStatisticItem):
        vehicle = WN8TankEntry(s)

        self.battles += vehicle.battles

        self.damage_done += vehicle.damage_done
        self.expected_damage += vehicle.expected_damage_done * vehicle.battles

        self.spotted += vehicle.spotted
        self.expected_spotted += vehicle.expected_spotted * vehicle.battles

        self.frags += vehicle.fragged
        self.expected_fragged += vehicle.expected_fragged * vehicle.battles

        self.deffed += vehicle.deffed
        self.expected_deffed += vehicle.expected_deffed * vehicle.battles

        self.wins += vehicle.wins
        self.expected_wins += vehicle.expected_winrate * vehicle.battles * 0.01

        self.vehicles[vehicle.vehicle_id] = vehicle

    @property
    def wn8(self):
        ratio_damage_done = self.damage_done / self.expected_damage
        ratio_spotted = self.spotted / self.expected_spotted
        ratio_fragged = self.frags / self.expected_fragged
        ratio_deffed = self.deffed / self.expected_deffed
        ratio_wins = self.wins / self.expected_wins

        ratio_wins_calculated = max(0.0, (ratio_wins - 0.71) / (1 - 0.71))
        ratio_damage_done_calculated = max(0.0, (ratio_damage_done - 0.22) / (1 - 0.22))
        ratio_frags_calculated = max(0.0, min(ratio_damage_done_calculated + 0.2, (ratio_fragged - 0.12) / (1 - 0.12)))
        ratio_spots_calculated = max(0.0, min(ratio_damage_done_calculated + 0.1, (ratio_spotted - 0.38) / (1 - 0.38)))
        ratio_deffed_calculated = max(0.0, min(ratio_damage_done_calculated + 0.1, (ratio_deffed - 0.10) / (1 - 0.10)))

        wn8 = 980 * ratio_damage_done_calculated \
              + 210 * ratio_damage_done_calculated * ratio_frags_calculated \
              + 155 * ratio_frags_calculated * ratio_spots_calculated \
              + ratio_spots_calculated \
              + 75 * ratio_deffed_calculated * ratio_frags_calculated \
              + 145 * min(1.8, ratio_wins_calculated)

        return wn8
