# JSON Output

A set of scripts based on the CSV output versions of similar names but adapted to output JSON.

Note: Nov. 2023, due to a lack of pagination within the AVP Aviary API documentation (and a limit of the first 100 results with the remainder cutoff), a workaround is used by the script that involves exporting from the admin resource/media/etc. table view in the UI (see comments at the top of the script for details).

## Resources in JSON via the UI-generated resource list

* `aviary_api_report_resources_json_by_resource_list.py`

## Indexes in JSON via the UI-generated media list

* `aviary_api_report_index_json_by_media_list.py`
* requires the UI-generated media list which contains the metadata for the attached index content type (i.e., `index` content type is attached to a specified `media`) content type

## Media in JSON from Resource JSON

* Given input from `aviary_api_report_resources_json_by_resource_list.py`, output the associated Media JSON
* `aviary_api_report_media_by_resource_json.py`

## Indexes in JSON via a Media JSON

* Given input from `aviary_api_report_media_by_resource_json.py`, output the associated Indexes JSON
* `aviary_api_report_index_by_media_json.py`

## Download the attached file to an Index

* Given input from `aviary_api_report_index_by_media_json.py`, output the file attached to the Indexes
* `aviary_api_download_index_by_index_json.py`
