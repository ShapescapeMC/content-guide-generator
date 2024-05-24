'''
This module contains logic used for gathering and presenting the information
about items.
'''
from __future__ import annotations
from collections import defaultdict

from typing import NamedTuple, Literal
from pathlib import Path
from functools import cache
from json import JSONDecodeError
import json

from sqlite_bedrock_packs.better_json_tools import (
    load_jsonc, SKIP_LIST, JSONPath)
from sqlite_bedrock_packs import (
    yield_from_easy_query, Feature, FeatureRule, FeatureRuleFile, FeatureFile,
    FeaturePlacesFeatureField, FeaturePlacesFeatureFieldValue, Left
)

# Local imports
from .utils import filter_paths
from .errors import print_error
from .globals import AppConfig, get_db
from .recipes import (
    load_recipe, InvalidRecipeException, RecipeCrafting, RecipeFurnace,
    RecipeBrewing)

PlayerFacingSelector = Literal['player_facing', 'non_player_facing', 'all']
'''
In the functions that filter items by player facing property it's used to select
player-facing only items, non-player-facing only items or all items.
'''

class FeatureOrFeatureRulesProperties(NamedTuple):
    identifier: str
    description: str
    places_features: list[str]
    type: Literal['feature', 'feature_rule']

    def summary(self):
        '''
        Returns the summary of this feature/feature rule.
        '''
        result: list[str] = [f"### {self.identifier}"]
        if self.description != "":
            result.append(f"{self.description}")

        if len(self.places_features) > 0:
            if self.type == 'feature_rule':
                result.append(
                    f"\n\n**Places feature:** {self.places_features[0]}")
            else:
                result.append("#### **Places features:**")
                for feature in self.places_features:
                    result.append(f"- {feature}")
        return '\n'.join(result) + "\n"

    def table_summary(self):
        '''
        Returns the summary of this feature/feature rule in a table format
        (excluding the header).
        '''
        description = self.description.replace("\n", "<br>")
        places_features = ', '.join(self.places_features)
        return f"| {self.identifier} | {description} | {places_features} |"


@cache
def _list_feature_rules() -> list[FeatureOrFeatureRulesProperties]:
    '''
    Returns the list of available feature rules in the project as easy
    to process objects.
    '''
    db = get_db()
    result: list[FeatureOrFeatureRulesProperties] = []
    for fr_file, fr in yield_from_easy_query(db, FeatureRuleFile, FeatureRule):
        try:
            fr_file = load_jsonc(fr_file.path)
        except JSONDecodeError as e:
            print_error(f"Error while loading {fr_file.path}: {e}")
            continue
        description = (
            fr_file / "minecraft:feature_rules" / "description" /
            "description").data
        if not isinstance(description, str):
            description = ""
            print_error(f"File {fr_file.path} has no description")
        places_features = [fr.placesFeature]
        result.append(FeatureOrFeatureRulesProperties(
            identifier=fr.identifier,
            description=description,
            places_features=places_features,
            type='feature_rule'
        ))
    return result

@cache
def _list_features() -> list[FeatureOrFeatureRulesProperties]:
    '''
    Returns the list of available features in the project as easy to proces
    objects.
    '''

    # READ FROM DATABASE
    db = get_db()
    feature_relations: dict[str, list[str]] = defaultdict(list)
    features: list[tuple[Path, str, str]] = []  # (path, identifier, json_path)
    # Make the places_features list for each feature
    for feature_file, feature, _, placed_feature in yield_from_easy_query(
        db, FeatureFile, Feature, Left(FeaturePlacesFeatureField),
        Left(FeaturePlacesFeatureFieldValue)
    ):
        if placed_feature is not None:  # type: ignore
            feature_relations[feature.identifier].append(placed_feature.identifier)
        features.append((
            feature_file.path, feature.identifier, feature.jsonPath))
    
    # GENERATE THE RESULT
    result: list[FeatureOrFeatureRulesProperties] = []
    for path, identifier, json_path in features:
        try:
            feature_file = load_jsonc(path)
        except JSONDecodeError as e:
            print_error(f"Error while loading {path}: {e}")
            continue
        description = (
            feature_file / JSONPath(json_path) / "description" / "description"
        ).data
        if not isinstance(description, str):
            description = ""
            print_error(f"File {path} has no description")
        result.append(FeatureOrFeatureRulesProperties(
            identifier=identifier,
            description=description,
            places_features=feature_relations[identifier],
            type='feature'
        ))
    return result

def summarize_feature_rules() -> str:
    '''
    Returns the summaries of all feature rules.
    '''
    result: list[str] = []
    feature_rules = _list_feature_rules()
    if len(feature_rules) == 0:
        return "There is no feature rules on this project."
    for feature_rule in feature_rules:
        result.append(feature_rule.summary())

    if len(result) == 0:
        return "There is no feature rules on this project."
    return '\n'.join(result)

def summarize_feature_rules_in_tables() -> str:
    '''
    Returns the summaries of all feature rules in a table format.
    '''
    result: list[str] = []
    feature_rules = _list_feature_rules()
    if len(feature_rules) == 0:
        return "There is no feature rules on this project."
    for feature_rule in feature_rules:
        result.append(feature_rule.table_summary())
    
    if len(result) == 0:
        return "There is no feature rules on this project."
    return '\n'.join(
        [
            "| Item | Description | Places feature |",
            "|------|-------------|----------------|",
            *result
        ]
    )

def list_feature_rules() -> str:
    '''
    Simplified version of summarize_feature_rules that returns only the
    list of feature rule identifiers.
    '''
    result: list[str] = []
    feature_rules = _list_feature_rules()
    if len(feature_rules) == 0:
        return "There is no feature rules on this project."
    for feature_rule in feature_rules:
        result.append(f'- {feature_rule.identifier}')
    return '\n'.join(result)

def summarize_features() -> str:
    '''
    Returns the summaries of all features.
    '''
    result: list[str] = []
    features = _list_features()
    if len(features) == 0:
        return "There is no features on this project."
    for feature in features:
        result.append(feature.summary())

    if len(result) == 0:
        return "There is no features on this project."
    return '\n'.join(result)

def summarize_features_in_tables() -> str:
    '''
    Returns the summaries of all features in a table format.
    '''
    result: list[str] = []
    features = _list_features()
    if len(features) == 0:
        return "There is no features on this project."
    for feature in features:
        result.append(feature.table_summary())
    
    if len(result) == 0:
        return "There is no features on this project."
    return '\n'.join(
        [
            "| Item | Description | Places features |",
            "|------|-------------|-----------------|",
            *result
        ]
    )

def list_features() -> str:
    '''
    Simplified version of summarize_features that returns only the
    list of feature identifiers.
    '''
    result: list[str] = []
    features = _list_features()
    if len(features) == 0:
        return "There is no features on this project."
    for feature in features:
        result.append(f'- {feature.identifier}')
    return '\n'.join(result)

def feature_tree() -> str:
    '''
    Returns a tree that shows which feature and feature rules place which
    features. For better readablity, the most common namespaces are removed
    from the feature identiifers.
    '''
    result: list[str] = [
        'Followin tree shows the relations between features and feature '
        'rules. The feature rule names are written in square brackets. If a '
        'feature is used multiple times, it may be shown in some places with '
        'ellipsis ("...") at the end to avoid redundancy.\n\n']
    features = _list_features() + _list_feature_rules()
    if len(features) == 0:
        return "There is no features or feature rules on this project."

    namespace_ratings: dict[str, int] = defaultdict(int)
    for feature in features:
        if ':' not in feature.identifier:
            raise ValueError(
                f'Feature or feature rule "{feature.identifier}" has no '
                'namespace.')
        namespace = feature.identifier.split(':', 1)[0]
        namespace_ratings[namespace] += 1
    most_common_namespace = max(
        namespace_ratings, key=lambda x: namespace_ratings[x])
    result.append(
        f"For better readablity, the most common namespace - "
        f"{most_common_namespace} - is removed from the feature "
        "identifiers.\n")
    
    # Map the relations
    def strip_namespace(identifier: str) -> str:
        if identifier.startswith(most_common_namespace + ':'):
            return identifier[len(most_common_namespace) + 1:]
        return identifier
    parent_child_map: dict[str, list[str]] = defaultdict(list)
    known_children: set[str] = set()  # Feutres that have parents
    known_parents: set[str] = set()  # Features that have children
    for feature in features:
        identifier = strip_namespace(feature.identifier)
        if feature.type == 'feature_rule':
            identifier = f'[{identifier}]'
        placed_features = [strip_namespace(f) for f in feature.places_features]
        parent_child_map[identifier] = placed_features
        known_children.update(placed_features)
        if len(placed_features) > 0:
            known_parents.add(identifier)
    # Expand the repot
    logged: set[str] = set()
    def log_feature(identifier: str, result: list[str], depth: int = 0):
        if depth == 0 and identifier in known_children:
            # This is a leaf feature that will be logged by its parent(s)
            return
        if identifier in logged and identifier in known_parents:
            # This is not a leaf, but it's already logged somewhere, we can
            # log it as a leaf with "..." at the end.
            result.append(f'{"  " * depth}{identifier}...')
            return
        logged.add(identifier)
        result.append(f'{"  " * depth}{identifier}')
        for child in parent_child_map[identifier]:
            log_feature(child, result, depth + 1)

    for parent in parent_child_map:
        partial_result: list[str] = []
        log_feature(parent, partial_result)
        if len(partial_result) > 0:
            result.append('```')
            result.extend(partial_result)
            result.append('```')

    return '\n'.join(result)
