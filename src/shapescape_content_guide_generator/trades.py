'''
This module contains logic used for gathering and presenting the infromation
about the trades in the game.
'''
from __future__ import annotations

from pathlib import Path
from functools import cache
from typing import NamedTuple, Literal

from json import JSONDecodeError

from sqlite_bedrock_packs.better_json_tools import load_jsonc
from sqlite_bedrock_packs.better_json_tools.json_walker import JSONWalker
from sqlite_bedrock_packs import yield_from_easy_query, Entity, TradeTable

# Local imports
from .utils import filter_paths
from .errors import print_error
from .globals import AppConfig, get_db

class TradeProperties(NamedTuple):
    identifier: str  # Always based on the path to the trade
    data: JSONWalker

    @cache
    @staticmethod
    def from_path(path: Path) -> TradeProperties | None:
        '''
        Loads the trade properties from the trade file. The properties are
        later reused by various functions to generate the content guide. If
        file fails to load or is missing some important data, it returns None.

        :param path: The path to the item file.
        '''
        # Load file
        if not path.is_relative_to(AppConfig.get().bp_path / "trading"):
            print_error(
                "The path to the trade file is not relative to the "
                "'BP/trading' folder.\n"
                f"\tPath: {path.as_posix()}"
            )
            return None
        try:
            data = load_jsonc(path)
        except JSONDecodeError:
            print_error(
                f"Unable to load the trade file as JSON\n"
                f"\tPath: {path.as_posix()}")
            return None
        return TradeProperties(
            identifier=path.relative_to(
                AppConfig.get().bp_path
            ).as_posix(),
            data=data
        )

    def trade_summary(self) -> str:
        '''
        Returns the summary of the trade.
        '''
        # the trade IDs always start with 'trading/' so we can remove it
        short_id = self.identifier[8:]
        result: list[str] = [f"## Trade: {short_id}"]
        # TODO - implement additional properties like "Traded by:"
        trading_entities =  list_trade_using_entities(self.identifier)
        if len(trading_entities) > 0:
            result.append("#### Traded by:")
            result.extend([f'- {entity}' for entity in trading_entities])
        result.append("#### Content")
        result.append("```")  # Open block of code
        tiers = self.data / 'tiers'
        if not isinstance(tiers.data, list):
            print_error(
                f"Trade '{short_id}' does not have 'tiers' property.")
            result.append("Trade does not have 'tiers' property.")
            result.append("```")  # Close block of code & return
            return "\n".join(result)
        
        for tier_id, tier in enumerate(tiers // int, start=1):
            # The Header
            total_exp_required = (tier / 'total_exp_required').data
            if not isinstance(total_exp_required, int):
                total_exp_required = 0
            tier_header = (
                f"Tier {tier_id} trades (Total EXP required: "
                f"{total_exp_required}):"
            )
            result.append(tier_header)
            result.append("="*len(tier_header) + "\n")
            # The groups of tiers
            groups = tier / 'groups'
            trades = tier / 'trades'
            if groups.exists:
                if not isinstance(groups.data, list):
                    print_error(
                        f"Trade '{short_id}' does not have 'groups' property.\n"
                        f"\tJOSN Path: {groups.path_str}")
                    result.append("Trade does not have 'groups' property.\n")
                    continue
                for group_id, group in enumerate(groups // int, start=1):
                    result.extend(
                        TradeProperties._trade_summary_group(
                            short_id, group_id, group))
            elif trades.exists:
                if not isinstance(trades.data, list):
                    print_error(
                        f"Trade '{short_id}' does not have 'trades' property.\n"
                        f"\tJOSN Path: {trades.path_str}")
                    result.append("Trade does not have 'trades' property.")
                    continue
                for trade in trades // int:
                    wants = TradeProperties._trade_summary_wants_givs(
                        short_id, 'wants', trade)
                    gives = TradeProperties._trade_summary_wants_givs(
                        short_id, 'gives', trade)
                    result.append(f"- Gives {gives} for {wants}")
            else:
                print_error(
                    f"Trade '{short_id}' does not have 'groups' nor 'trades' "
                    f"property in tier {tier_id}.\n"
                    f"\tJOSN Path: {tier.path_str}")
            result.append("")  # new line


        result.append("```")  # Close block of code & return
        return "\n".join(result)

    @staticmethod
    def _trade_summary_group(
            short_trade_id: str, group_id: int, group: JSONWalker):
            '''
            This is a utility function from trade_summary() method to avoid
            writing the same code multiple times.
            '''
            result: list[str] = []
            num_to_select = (group / 'num_to_select').data
            if not isinstance(num_to_select, int) or num_to_select == 0:
                # If the num_to_select is 0 then all trades are selected
                group_header = (
                    f"Group {group_id}:")
            else:
                group_header = (
                    f"Group {group_id} - Selects "
                    f"{num_to_select} of following trades:")
            result.append(group_header)
            result.append("-"*len(group_header) + "\n")

            # Iterate through the trades in the group
            trades = group / 'trades'
            if not isinstance(trades.data, list):
                print_error(
                    f"Trade '{short_trade_id}' does not have 'trades' property.\n"
                    f"\tJOSN Path: {trades.path_str}")
                result.append("Trade does not have 'trades' property.")
                return result
            for trade in trades // int:
                wants = TradeProperties._trade_summary_wants_givs(
                    short_trade_id, 'wants', trade)
                gives = TradeProperties._trade_summary_wants_givs(
                    short_trade_id, 'gives', trade)
                result.append(f"- Gives {gives} FOR {wants}")
            result.append("")  # new line
            return result

    @staticmethod
    def _trade_summary_wants_givs(
                short_trade_id: str,  # Used for error messages
                key: Literal['wants', 'gives'],
                trade: JSONWalker) -> str:
        '''
        This is a utility function from trade_summary() method to avoid writing
        the same code multiple times.
        '''
        # Wants and gives properties have the same structure so
        # we can reuse the code
        trade_instances = (trade / key)
        if not isinstance(trade_instances.data, list):
            print_error(
                f"Trade {short_trade_id} does not have '{key}' property.\n"
                f"\tJOSN Path: {trade_instances.path_str}"
            )
            trade_instance_text = "NOTHING"
        else:
            trade_instance_text_parts = []
            for trade_instance in trade_instances // int:
                choice = trade_instance / 'choice'
                if choice.exists and isinstance(choice.data, list):
                    choice_text_parts = []
                    for choice_instance in choice // int:
                        ti_text = TradeProperties._trade_summary_wants_gives_trade_instance(
                            short_trade_id, choice_instance
                        )
                        choice_text_parts.append(ti_text)
                    choice_text = "(" + " OR ".join(choice_text_parts) + ")"
                    trade_instance_text_parts.append(choice_text)
                else:
                    ti_text = TradeProperties._trade_summary_wants_gives_trade_instance(
                        short_trade_id, trade_instance
                    )
                    trade_instance_text_parts.append(ti_text)
            trade_instance_text = " & ".join(
                trade_instance_text_parts)
        return trade_instance_text

    @staticmethod
    def _trade_summary_wants_gives_trade_instance(
            short_trade_id: str,  # Used for error messages
            trade_instance: JSONWalker) -> str:
        quantity = (trade_instance / 'quantity').data
        if not isinstance(quantity, int):
            quantity = 1
        trade_instance_data = (trade_instance / 'item').data
        if not isinstance(trade_instance_data, str):
            print_error(
                f"Trade {short_trade_id} does not have 'item' property.\n"
                f"\tJOSN Path: {trade_instance.path_str}")
            trade_instance_data = "UNKNOWN"
        return f"{quantity}⨯{trade_instance_data}"

def summarize_trades(
    search_patterns: str | list[str],
    exclude_patterns: str | list[str] | None = None,
) -> str:
    '''
    Returns the summaries of all trades and the entities that use them.

    :param search_pattern: glob pattern used to find the trade files. The
        pattern must be relative to behavior pack 'trading' folder.
    :param exclude_patterns: the pattern that excludes the files even if they
        matched the search pattern.
    '''
    trades_paths = AppConfig.get().bp_path / 'trading'
    filtered_paths = filter_paths(
        trades_paths, search_patterns, exclude_patterns)

    result: list[str] = []
    for trade_path in filtered_paths:
        if not trade_path.is_file():
            continue
        trade = TradeProperties.from_path(trade_path)
        if trade is None:
            continue
        result.append(trade.trade_summary())
    if len(result) == 0:
        return "No trades found."
    return "\n".join(result)


def list_trade_using_entities(trade_table_id: str) -> list[str]:
    '''
    Lists the identifiers of the entities that use the specified trade
    '''
    db = get_db()
    result: list[str] = []
    for _, entity in yield_from_easy_query(
            db, TradeTable, Entity,
            where=[f"TradeTable.identifier = '{trade_table_id}'"]):
        if entity.identifier is None:  # type: ignore
            continue
        result.append(entity.identifier)
    return result
