import json
import pytest
import os
import pandas as pd


from orchestrator.assets.catalog_report_assets import (
    all_sources_dataframe,
    all_destinations_dataframe,
)
from orchestrator.assets.catalog_assets import (
    oss_destinations_dataframe,
    cloud_destinations_dataframe,
    oss_sources_dataframe,
    cloud_sources_dataframe,
)


@pytest.fixture
def oss_catalog_dict():
    file_path = os.path.join(os.path.dirname(__file__), "fixtures", "oss_catalog.json")
    return json.load(open(file_path))


@pytest.fixture
def cloud_catalog_dict():
    file_path = os.path.join(os.path.dirname(__file__), "fixtures", "cloud_catalog.json")
    return json.load(open(file_path))


def test_merged_catalog_dataframes(oss_catalog_dict, cloud_catalog_dict):
    github_connector_folders = []
    valid_metadata_list = pd.DataFrame([{"definitionId": "test", "is_metadata_valid": True}])
    num_oss_destinations = len(oss_catalog_dict["destinations"])
    num_cloud_destinations = len(cloud_catalog_dict["destinations"])

    num_cloud_sources = len(cloud_catalog_dict["sources"])
    num_oss_sources = len(oss_catalog_dict["sources"])

    cloud_destinations_df = cloud_destinations_dataframe(cloud_catalog_dict).value
    assert len(cloud_destinations_df) == num_cloud_destinations

    cloud_sources_df = cloud_sources_dataframe(cloud_catalog_dict).value
    assert len(cloud_sources_df) == num_cloud_sources

    oss_destinations_df = oss_destinations_dataframe(oss_catalog_dict).value
    assert len(oss_destinations_df) == num_oss_destinations

    oss_sources_df = oss_sources_dataframe(oss_catalog_dict).value
    assert len(oss_sources_df) == num_oss_sources

    all_sources_df = all_sources_dataframe(cloud_sources_df, oss_sources_df, github_connector_folders, valid_metadata_list)
    all_destinations_df = all_destinations_dataframe(cloud_destinations_df, oss_destinations_df, github_connector_folders, valid_metadata_list)

    # assert that all_sources_df has a entry for each sourceDefinitionId in the cloud catalog and oss catalog
    oss_source_definition_ids = set([source["sourceDefinitionId"] for source in oss_catalog_dict["sources"]])
    cloud_source_definition_ids = set([source["sourceDefinitionId"] for source in cloud_catalog_dict["sources"]])
    all_source_definition_ids = set(all_sources_df["sourceDefinitionId"])

    assert all_source_definition_ids == oss_source_definition_ids.union(cloud_source_definition_ids)

    # assert that all_destinations_df has a entry for each sourceDefinitionId in the cloud catalog and oss catalog
    oss_destination_definition_ids = set([destination["destinationDefinitionId"] for destination in oss_catalog_dict["destinations"]])
    cloud_destination_definition_ids = set([destination["destinationDefinitionId"] for destination in cloud_catalog_dict["destinations"]])
    all_destination_definition_ids = set(all_destinations_df["destinationDefinitionId"])

    assert all_destination_definition_ids == oss_destination_definition_ids.union(cloud_destination_definition_ids)
