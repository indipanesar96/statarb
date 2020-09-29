from typing import List
from src.Cointegrator import CointegratedPair
from src.Portfolio import Portfolio, Position
from src.util.Features import PositionType
from datetime import date, timedelta
from src.Filters import Filters

class Decision:
    def __init__(self, position: Position, old_action: PositionType, new_action: PositionType):
        self.position: Position = position
        self.new_action: PositionType = new_action
        self.old_action: PositionType = old_action


class SignalGenerator:

    def __init__(self,
                 port: Portfolio,
                 entry_z: float,
                 exit_z: float,
                 emergency_delta_z: float):
        self.port: Portfolio = port
        self.entry_z: float = entry_z
        self.exit_z: float = exit_z
        self.emergency_delta_z: float = emergency_delta_z
        self.time_stop_loss = 30
        self.open_count = 0
        self.natural_close_count = 0
        self.emergency_close_count = 0
        self.time_stop_loss_count = 0
        self.filter = Filters()
        self.volumn_shock_filter = 0

    def make_decision(self, pairs: List[CointegratedPair]) ->List[Decision]:

        positions = self.port.cur_positions
        current_posn_pairs = [(i.asset1, i.asset2) for i in positions]
        coint_pairs = [i.pair for i in pairs]
        today = self.port.current_window.window_end
        decisions = []
        for coint_pair in pairs:
        # if coint_pair not invested, check if we need to open position
            if coint_pair.pair not in current_posn_pairs:
                if coint_pair.recent_dev_scaled > self.entry_z:
                    # l = long pair = long x short y
                    p1, p2 = coint_pair.pair
                    shock = self.filter.run_volume_shock_filter_single_pair(coint_pair.pair,
                                                                            self.port.current_window)
                    if not shock:
                        decisions.append(
                            Decision(
                                position=Position(
                                    ticker1=p1,
                                    ticker2=p2,
                                    weight1=coint_pair.scaled_beta,
                                    weight2=1 - coint_pair.scaled_beta,
                                    investment_type=PositionType.LONG,
                                    init_z=coint_pair.recent_dev_scaled,
                                    init_date=today),
                                old_action=PositionType.NOT_INVESTED,
                                new_action=PositionType.LONG,
                            )
                        )
                        self.open_count += 1
                    else:
                        self.volumn_shock_filter += 1

                elif coint_pair.recent_dev_scaled < - self.entry_z:
                    # s = short pair = long y short x
                    p1, p2 = coint_pair.pair
                    shock = self.filter.run_volume_shock_filter_single_pair(coint_pair.pair,
                                                                            self.port.current_window)
                    if not shock:

                        decisions.append(
                            Decision(
                                position=Position(
                                    ticker1=p1,
                                    ticker2=p2,
                                    weight1=-coint_pair.scaled_beta,
                                    weight2=coint_pair.scaled_beta + 1,
                                    investment_type=PositionType.SHORT,
                                    init_z=coint_pair.recent_dev_scaled,
                                    init_date=today),
                                old_action=PositionType.NOT_INVESTED,
                                new_action=PositionType.SHORT,

                            )
                        )
                        self.open_count += 1
                    else:
                        self.volumn_shock_filter += 1

        # loop through all invested position
        for position in positions:
            position_pair = (position.asset1, position.asset2)
            # if pair not cointegrated, exit position
            if  position_pair not in coint_pairs:
                decisions.append(
                    Decision(
                        position=position,
                        old_action=position.position_type,
                        new_action=PositionType.NOT_INVESTED))
                self.emergency_close_count += 1

            else:
                idx = coint_pairs.index(position_pair)
                coint_pair = pairs[idx]
                # if position passed time limit, exit position
                # if recent_dev is still high, position will be opened again tmr, so don't exit in such situation
                if today > (position.init_date + timedelta(self.time_stop_loss)) and \
                        (abs(coint_pair.recent_dev_scaled) < self.entry_z):
                    decisions.append(
                        Decision(
                            position=position,
                            old_action=position.position_type,
                            new_action=PositionType.NOT_INVESTED))
                    self.time_stop_loss_count += 1
                # else, check if need to exit
                else:
                    if position.position_type is PositionType.LONG:
                        natural_close_required = coint_pair.recent_dev_scaled < self.exit_z
                        emergency_close_required = coint_pair.recent_dev_scaled > \
                                                   (self.emergency_delta_z + position.init_z)

                        if natural_close_required or emergency_close_required:
                            decisions.append(
                                Decision(
                                    position=position,
                                    old_action=PositionType.LONG,
                                    new_action=PositionType.NOT_INVESTED)
                            )
                            if natural_close_required:
                                self.natural_close_count += 1
                            else:
                                self.emergency_close_count += 1
                        else:
                            # no need to close, so keep the position open
                            decisions.append(
                                Decision(
                                    position=position,
                                    old_action=PositionType.LONG,
                                    new_action=PositionType.LONG)
                            )

                    elif position.position_type is PositionType.SHORT:

                        natural_close_required = coint_pair.recent_dev_scaled > -self.exit_z
                        emergency_close_required = coint_pair.recent_dev_scaled < \
                                                   (position.init_z - self.emergency_delta_z)

                        if natural_close_required or emergency_close_required:
                            decisions.append(
                                Decision(
                                    position=position,
                                    old_action=PositionType.SHORT,
                                    new_action=PositionType.NOT_INVESTED)
                            )
                            if natural_close_required:
                                self.natural_close_count += 1
                            else:
                                self.emergency_close_count += 1
                        else:
                            # no need to close, so keep the position open
                            decisions.append(
                                Decision(
                                    position=position,
                                    old_action=PositionType.SHORT,
                                    new_action=PositionType.SHORT)
                            )
        print("open count: ", self.open_count)
        print("natural close count: ", self.natural_close_count)
        print("emergency close count: ", self.emergency_close_count)
        print("time stop-loss close count: ", self.time_stop_loss_count)
        return decisions
