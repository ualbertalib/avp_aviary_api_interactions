# Experimental Aviary

Purpose:

* contain forays into using the AVP Aviary API and explore what is possible

Details:

* scripts that fail due to limited Aviary API functionality, for example:
  * the lack of pagination and limited list length `media_file_ids` in the resource API
    * `aviary_api_report_media.py`
    * `aviary_api_report_resources_csv.py`
    * `aviary_api_report_resources_json.py`
  * the limited list length `media_file_ids` in the resource API
    * `aviary_api_report_media_csv_by_resource_list.py`
    * `aviary_api_report_transcripts_csv_by_resource_list.py`
* scripts that scrape the data tables in the admin interface
  * `experimental_get_all_media_ids.py`
