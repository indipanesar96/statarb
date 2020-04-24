from typing import List

import numpy as np

from src.Cointegrator import CointegratedPair
from src.Portfolio import Portfolio, Position
from src.util.Features import PositionType


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
                 emergency_z: float):
        self.port: Portfolio = port
        self.entry_z: float = entry_z
        self.exit_z: float = exit_z
        self.emergency_z: float = emergency_z

    def make_decision(self, pairs: List[CointegratedPair]):

        positions = self.port.cur_positions
        current_posn_pairs = [(i.asset1, i.asset2) for i in positions]

        decisions = []
        for coint_pair in pairs:

            try:
                # Check to see if we're already invested
                # this will throw an IndexError if coint_pair.pair isn't in current_posn_pairs
                # ie we're not invested in coint_pair.pair

                idx = np.where([x == coint_pair.pair for x in current_posn_pairs])[0][0]
                position = positions[idx]

            except IndexError:
                if coint_pair.recent_dev_scaled > self.entry_z:
                    # l = long pair = long x short y
                    p1, p2 = coint_pair.pair

                    decisions.append(
                        Decision(
                            position=Position(
                                ticker1=p1,
                                ticker2=p2,
                                weight1=coint_pair.scaled_beta,
                                weight2=1 - coint_pair.scaled_beta,
                                investment_type=PositionType.LONG),
                            old_action=PositionType.NOT_INVESTED,
                            new_action=PositionType.LONG
                        )
                    )

                elif coint_pair.recent_dev_scaled < -self.entry_z:
                    # s = short pair = long y short x
                    p1, p2 = coint_pair.pair

                    decisions.append(
                        Decision(
                            position=Position(
                                ticker1=p1,
                                ticker2=p2,
                                weight1=-coint_pair.scaled_beta,
                                weight2=coint_pair.scaled_beta + 1,
                                investment_type=PositionType.SHORT),
                            old_action=PositionType.NOT_INVESTED,
                            new_action=PositionType.SHORT
                        )
                    )

            else:
                if position.position_type is PositionType.LONG:
                    natural_close_required = coint_pair.recent_dev_scaled < self.exit_z
                    emergency_close_required = coint_pair.recent_dev_scaled > self.emergency_z

                    if natural_close_required or emergency_close_required:
                        decisions.append(
                            Decision(
                                position=position,
                                old_action=PositionType.LONG,
                                new_action=PositionType.NOT_INVESTED)
                        )
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
                    emergency_close_required = coint_pair.recent_dev_scaled < -self.emergency_z

                    if natural_close_required or emergency_close_required:
                        decisions.append(
                            Decision(
                                position=position,
                                old_action=PositionType.SHORT,
                                new_action=PositionType.NOT_INVESTED)
                        )
                    else:
                        # no need to close, so keep the position open
                        decisions.append(
                            Decision(
                                position=position,
                                old_action=PositionType.SHORT,
                                new_action=PositionType.SHORT)
                        )

        return decisions
