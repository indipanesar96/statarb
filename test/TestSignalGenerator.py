from copy import deepcopy
from datetime import date, timedelta
from unittest import TestCase

from src.Cointegrator import CointegratedPair
from src.DataRepository import DataRepository
from src.SignalGenerator import SignalGenerator
from src.Portfolio import Portfolio, Position
from src.Window import Window
from src.util.Features import PositionType
from src.util.Tickers import SnpTickers


# Not Invested:
# Long Open
# Short Open
# Invested:
# Long Close
# Short Close
# Emergency close
# Hold


class TestDecisionMaker(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.window = Window(window_start=date(2008, 1, 3),
                            trading_win_len=timedelta(days=90),
                            repository=DataRepository())

        cls.empty_portfolio: Portfolio = Portfolio(100_000, cls.window)

        cls.portfolio_to_be_augmented = Portfolio(100_000, cls.window)

        cls.decision_maker = SignalGenerator(cls.empty_portfolio,
                                             entry_z=0.5,
                                             exit_z=0.1,
                                             emergency_z=0.8)

        cls.pair1 = CointegratedPair(
            pair=(SnpTickers.AAPL, SnpTickers.MSFT),
            mu_x_ann=0.0,
            sigma_x_ann=0.0,
            scaled_beta=1.2,
            hl=0.0,
            ou_mean=0.0,
            ou_std=0.0,
            ou_diffusion_v=0.0,
            recent_dev=0.0,
            recent_dev_scaled=0.1)

        cls.pair2 = CointegratedPair(
            pair=(SnpTickers.AAPL, SnpTickers.TDG),
            mu_x_ann=0.0,
            sigma_x_ann=0.0,
            scaled_beta=0.5,
            hl=0.0,
            ou_mean=0.0,
            ou_std=0.0,
            ou_diffusion_v=0.0,
            recent_dev=0.0,
            recent_dev_scaled=0.2)

    def test_not_invested_long_open(self):
        pair1_copy = deepcopy(self.pair1)
        pair1_copy.recent_dev_scaled = 0.6

        pairs = [pair1_copy, self.pair2]

        actual_decisions = self.decision_maker.make_decision(pairs)

        self.assertEqual(1, len(actual_decisions))
        self.assertEqual(SnpTickers.AAPL, actual_decisions[0].position.asset1)
        self.assertEqual(SnpTickers.MSFT, actual_decisions[0].position.asset2)
        self.assertEqual(pairs[0].scaled_beta, actual_decisions[0].position.weight1)
        self.assertEqual(1 - pairs[0].scaled_beta, actual_decisions[0].position.weight2)
        self.assertEqual(PositionType.LONG, actual_decisions[0].position.position_type)

        for d in actual_decisions:
            self.assertEqual(PositionType.NOT_INVESTED, d.old_action)
            self.assertEqual(PositionType.LONG, d.new_action)

    # number of routes through code = 2 ^ (# if statements)
    def test_not_invested_short_open(self):
        pair2_copy = deepcopy(self.pair2)
        pair2_copy.recent_dev_scaled = -0.7

        pairs = [self.pair1, pair2_copy]

        actual_decisions = self.decision_maker.make_decision(pairs)

        self.assertEqual(1, len(actual_decisions))
        self.assertEqual(SnpTickers.AAPL, actual_decisions[0].position.asset1)
        self.assertEqual(SnpTickers.TDG, actual_decisions[0].position.asset2)
        self.assertEqual(- pairs[1].scaled_beta, actual_decisions[0].position.weight1)
        self.assertEqual(1 + pairs[1].scaled_beta, actual_decisions[0].position.weight2)
        self.assertEqual(PositionType.SHORT, actual_decisions[0].position.position_type)

        for d in actual_decisions:
            self.assertEqual(PositionType.NOT_INVESTED, d.old_action)
            self.assertEqual(PositionType.SHORT, d.new_action)

    def test_not_invested_open_nothing(self):
        pairs = [self.pair1, self.pair2]
        actual_decisions = self.decision_maker.make_decision(pairs)
        self.assertEqual(0, len(actual_decisions))

    def test_not_invested_open_short_and_long(self):
        # 1st pair should be longed, 2nd shorted

        pair1_copy = deepcopy(self.pair1)
        pair1_copy.recent_dev_scaled = 0.7

        pair2_copy = deepcopy(self.pair2)
        pair2_copy.recent_dev_scaled = -0.7

        pairs = [pair1_copy, pair2_copy]

        actual_decisions = self.decision_maker.make_decision(pairs)

        self.assertEqual(2, len(actual_decisions))
        self.assertEqual(SnpTickers.AAPL, actual_decisions[0].position.asset1)
        self.assertEqual(SnpTickers.MSFT, actual_decisions[0].position.asset2)
        self.assertEqual(pairs[0].scaled_beta, actual_decisions[0].position.weight1)
        self.assertEqual(1 - pairs[0].scaled_beta, actual_decisions[0].position.weight2)
        self.assertEqual(PositionType.LONG, actual_decisions[0].position.position_type)

        self.assertEqual(SnpTickers.AAPL, actual_decisions[1].position.asset1)
        self.assertEqual(SnpTickers.TDG, actual_decisions[1].position.asset2)
        self.assertEqual(- pairs[1].scaled_beta, actual_decisions[1].position.weight1)
        self.assertEqual(1 + pairs[1].scaled_beta, actual_decisions[1].position.weight2)
        self.assertEqual(PositionType.SHORT, actual_decisions[1].position.position_type)

        for d in actual_decisions:
            self.assertEqual(PositionType.NOT_INVESTED, d.old_action)

        self.assertEqual(PositionType.LONG, actual_decisions[0].new_action)
        self.assertEqual(PositionType.SHORT, actual_decisions[1].new_action)

    def test_invested_open_nothing(self):

        # shouldn't matter, just need not_invested == False in prod code
        port_copy = deepcopy(self.portfolio_to_be_augmented)
        port_copy.open_position(
            Position(SnpTickers.AAPL,
                     SnpTickers.MSFT,
                     1,
                     -1,
                     PositionType.LONG)
        )

        dm = deepcopy(self.decision_maker)
        dm.port = port_copy

        pairs = [self.pair1, self.pair2]
        actual_decisions = dm.make_decision(pairs)
        self.assertEqual(PositionType.LONG, actual_decisions[0].old_action)
        self.assertEqual(PositionType.LONG, actual_decisions[0].new_action)

    def test_invested_already_long_to_be_closed_naturally(self):
        # self.pair1 is a current position
        port_copy = deepcopy(self.portfolio_to_be_augmented)

        # shouldn't matter, just need not_invested == False in prod code
        port_copy.open_position(
            Position(SnpTickers.AAPL,
                     SnpTickers.MSFT,
                     1,
                     -1,
                     PositionType.LONG)
        )

        dm = deepcopy(self.decision_maker)
        dm.port = port_copy

        # dm = DecisionMaker(portfolio, 0.5, 0.1, 0.8)

        pair1_copy = deepcopy(self.pair1)
        # anything less than exit_z (=0.1 at the time of writing)
        pair1_copy.recent_dev_scaled = 0.05

        pairs = [pair1_copy]
        actual_decisions = dm.make_decision(pairs)

        self.assertEqual(1, len(actual_decisions))
        self.assertEqual(PositionType.LONG, actual_decisions[0].old_action)
        self.assertEqual(PositionType.NOT_INVESTED, actual_decisions[0].new_action)

    def test_invested_already_long_to_be_closed_emergency(self):
        # self.pair1 is a current position

        # shouldn't matter, just need not_invested == False in prod code
        port_copy = deepcopy(self.portfolio_to_be_augmented)

        port_copy.open_position(
            Position(SnpTickers.AAPL,
                     SnpTickers.MSFT,
                     1,
                     -1,
                     PositionType.LONG)
        )

        dm = deepcopy(self.decision_maker)
        dm.port = port_copy

        pair1_copy = deepcopy(self.pair1)
        # anything more than emergency_z (=0.9 at the time of writing)
        pair1_copy.recent_dev_scaled = 0.9

        pairs = [pair1_copy]
        actual_decisions = dm.make_decision(pairs)

        self.assertEqual(1, len(actual_decisions))
        self.assertEqual(PositionType.LONG, actual_decisions[0].old_action)
        self.assertEqual(PositionType.NOT_INVESTED, actual_decisions[0].new_action)

    def test_invested_already_short_to_be_closed_naturally(self):
        # self.pair1 is a current position
        port_copy = deepcopy(self.portfolio_to_be_augmented)

        # shouldn't matter, just need not_invested == False in prod code
        port_copy.open_position(
            Position(SnpTickers.AAPL,
                     SnpTickers.MSFT,
                     1,
                     -1,
                     PositionType.SHORT)
        )

        dm = deepcopy(self.decision_maker)
        dm.port = port_copy

        pair1_copy = deepcopy(self.pair1)
        # anything more than -exit_z (=-0.1 at the time of writing)
        pair1_copy.recent_dev_scaled = -0.01

        pairs = [pair1_copy]
        actual_decisions = dm.make_decision(pairs)

        self.assertEqual(1, len(actual_decisions))
        self.assertEqual(PositionType.SHORT, actual_decisions[0].old_action)
        self.assertEqual(PositionType.NOT_INVESTED, actual_decisions[0].new_action)

    def test_invested_already_short_to_be_closed_emergency(self):
        # self.pair1 is a current position
        port_copy = deepcopy(self.portfolio_to_be_augmented)

        # shouldn't matter, just need not_invested == False in prod code
        port_copy.open_position(
            Position(SnpTickers.AAPL,
                     SnpTickers.MSFT,
                     1,
                     -1,
                     PositionType.SHORT)
        )

        dm = deepcopy(self.decision_maker)
        dm.port = port_copy

        pair1_copy = deepcopy(self.pair1)
        # anything les than -emergency_z (=-0.9 at the time of writing)
        pair1_copy.recent_dev_scaled = -1.0

        pairs = [pair1_copy]
        actual_decisions = dm.make_decision(pairs)

        self.assertEqual(1, len(actual_decisions))
        self.assertEqual(PositionType.SHORT, actual_decisions[0].old_action)
        self.assertEqual(PositionType.NOT_INVESTED, actual_decisions[0].new_action)
