# AVP Aviary API Interactions

The repository contains quickly written scripts designed to interact with the [AVP Aviary](https://www.aviaryplatform.com/api/v1/documentation) audio/video repository software. These scripts, as of March 2023 are only proof-of-concept.

Note: March 2024 - the [./json](./json/) directory contains the more recently used scripts (for the SpokenWeb export).

## Requirements

* Python 3
* Ability to work with proof-of-concept level software (e.g., exception handling is basic and involves reading stack traces)
* Elevated user privileges to access the Aviary API (i.e., default privileges on your campus computing id are insufficient)

## Setup

Assumes Python 3 is installed.

* git clone the repository
* Install dependencies:
  * `pip install -r requirements.txt --user`
  * Or python3 setup.py install --user
    * installed required modules in a local user account
  * Or without `--user` to install into the OS's central Python environment (required administrative privileges)

## Aviary

A SaaS vendor audio/video repository solution. Terminology:

* `Resources`: term for the main container of the audio/video object (links together the metadata, `media` files, etc.)
* `Media`: term for the container representing one or more audio/video files, associated file metadata; linked to the `resource`
* `Index`: term for the container representing one or more indexes into the media and associated metadata; linked to a `media` item
* `Transcript`: term for the container representing one or more transcripts of the audio/video; linked to a `media` item
* `Supplemental Files`: term for the container representing one or more supplemental files (JPEG, PDF, etc.) attached to the resource; linked to a `resource` item

**Note:** the vendor rate limits API requests. Each of the following scripts uses a simple wait mechanism between API requests. A more advanced approach could be implemented where the wait time is dynamically computed based on the response latency plus a retry mechanism. As of 2023-05-29, running multiple scripts will cause one to fail with the default wait settings.

**Note:** pagination is not documented (as of 2023-05-29) so workarounds are needed for collections with more than 100 resources (e.g., use Web UI export to gain a list of IDs)

**Note:** as of 2023-06-29, a resource returned by the Aviary API lists the attached media item(s) in the `media_file_id` field. However, `media_file_id` only contains a maximum of 10 IDs (a significant number of resources have over 10 media attached). I also tried via the Web UI, "export Media Files(s) to CSV" but the resulting file doesn't contain media IDs. How to get the entire list of media items is unknown.

**Notes:** 2024-10-06

* Pagination: to be added to documentation on Monday
* Media associated with a Resource: limited to 10: bug fix Monday
* Fields available in UI and CVS export not available via the API: bug fix Monday
* Downloading file marked as "not downloadable": recommendation - use the make downloadable for period of time option and download. Sean: about 9 items, SILR that should be excluded from this approach
* Rate limiting: not currently imposing a specific rate, recommendation exponential back-off if error ( (no present requirement to use a rate limiter on the client side e.g., leaky bucket algorithm).


## Included Scripts

The main types of scripts (the details are in the following subsections):

* Request metadata about a single Aviary item by ID
  * `avairy_api_get_by_id.py`
* Request a CSV report of all items of a specified model. The file naming convention is `aviary_api_report_[model]_[output (CSV)]_[how the IDs are discovered]`. The offering includes:
  * aviary_api_report_index_csv_by_media_list.py
  * aviary_api_report_media_csv_by_media_list.py
  * aviary_api_report_resources_csv_by_list.py
  * aviary_api_report_supplemental_csv_by_list.py
  * aviary_api_report_transcripts_csv_by_media_list.py
* Upload a list of media items
* JSON output (new 2023/2024)
  * ./json/
* [Experimental:](./experimental/) working with the Aviary API in different ways including the use of the collection API to find resource lists without needing the Web UI export.

The details:

### List metadata about an item

The following script authenticates against the Aviary API and prints out the metadata of a specified object

``` bash
python3 aviary_api_get_by_id.py --server ${aviary_server_name} --id ${media_id} --type [c|r|m]
```

Where:

* 'c': collection resources (no pagination so max 100 returned -- as of 2023-05-27 no documentation on pagination nor obvious mechanism in API response header or content)
* 'r': resource (single)
* 'm': media

### Reports

**Note:** for the reports using the CSV export file to gain a list of IDs, some fields are required (fields can be disabled via the UI and thus prevented from being added to the CSV export). The CSV export is required due to the aforementioned lack of pagination (as of May 2023)

#### Resource metadata report (including the `updated_at` field)

Note: the `updated_at` field is unavailable via the web UI as of 2023-03-27

For input, use the Web UI resource table option to export. This obtains a list of resource IDs (required due to lack of pagination in the Aviary API as of 2023-05-26).

* Navigate to `/collection_resources`
* Select `Table Options` --> `Export Resources to CSV`
* Use as the `input` in the following command

``` bash
python3 aviary_api_report_resources_csv_by_list.py --server ${aviary_server_name} --output ${output_path} -input ${input_path}
```

Failed: an attempt to use the Aviary APIs `/api/v1/collections` and `/api/v1/collections/{:collection_id}/resources` to build a list of resources failed (2023-03-27) due to a limit of 100 resources returned per collection and no documentation on how to enable pagination.

``` bash
python3 experimental/aviary_api_report_resources_csv.py --server ${aviary_server_name} --output ${output_path}
```

For a JSON-like output (more for debugging)

[JSON](./json/)

Or

``` bash
python3 experimental/aviary_api_report_resources_json.py --server ${aviary_server_name} --output ${output_path}
```

#### Media metadata report (including the `updated_at` field)

For input, use the Web UI resource table option to export. This obtains a list of resource IDs (required due to lack of pagination in the Aviary API as of 2023-05-26).

* Navigate to `/collection_resource_files` (`Media` in the Web UI)
* Select `Table Options` --> `Export Media file(s) to CSV`
* Use as the `input` in the following command

``` bash
python3 aviary_api_report_media_csv_by_media_list.py --server ${aviary_server_name} --output ${output_path} -input ${input_path}
```

**Note:** the resource API response, when the `media files count` is >10, the `media file IDs` will display only a maximum of 10 IDs in the list (as of May 2023). An example is resource 58924

Failed: an attempt to use the Aviary API `/api/v1/collections` and `/api/v1/collections/{:collection_id}/resources` to build a list of media failed (2023-03-27) due to a limit of 100 resources returned and no documentation on how to enable pagination (similar to the resource report).

``` bash
python3 experimental/aviary_api_report_media_csv.py --server ${aviary_server_name} --output ${output_path}
```

Failed: an attempt to the resource CSV export instead of requiring the user to also export the media CSV failed. The resource CSV export contains a `media_file_ids` field that contains a maximum of 10 items (no documentation nor easily identifiable means to increase). The experiment validates the list length versus the `media_files_count`.

* Navigate to `/collection_resource`
* Select `Table Options` --> `Export resources to CSV`
* Use as the `input` in the following command

``` bash
python3 experimental/aviary_api_report_media_csv_by_list.py --server ${aviary_server_name} --output ${output_path} -input ${input_path}
```

Or [JSON](./json/)

#### Transcripts metadata report

For input, use the Web UI resource table option to export. This obtains a list of resource IDs (required due to lack of pagination in the Aviary API as of 2023-05-26).

* Navigate to `/collection_resource_files` (`Media` in the Web UI)
* Select `Table Options` --> `Export Resources to CSV`
* Use as the `input` in the following command

``` bash
python3 aviary_api_report_transcripts_csv_by_media_list.py --server ${aviary_server_name} --output ${output_path} -input ${input_path}
```

**Note:** As of 2023-05-26, IDs for transcripts are discovered through the contest of the transcripts filed in the media API response -- there is no indication that the list is complete and may have a limit like the `media file IDs` field in the resources API response.

Todo: alter to remove the need for an input file of ID once pagination is available and replace with `/api/v1/collections` and `/api/v1/collections/{:collection_id}/resources` to build a list of media.

Note: `experiemental/aviary_api_report_transcripts_csv_by_list.py` uses the resource CSV export as input.

#### Index metadata report

**Note:** As of 2023-05-26, the Aviary API does not support a direct HTTP GET API request to gather the metadata for the `index` type. The index report is built from the contents of the `indexes` field in the media API response -- there is no indication that the list is complete and may have a limit like the `media file IDs` field in the resources API response.

* Navigate to `/collection_resource_files` (`Media` in the Web UI)
* Select `Table Options` --> `Export Resources to CSV`
* Use as the `input` in the following command

``` bash
python3 aviary_api_report_index_csv_by_media_list.py --server ${aviary_server_name} --output ${output_path} -input ${input_path}
```

Or [JSON](./json/), either JSON metadata or a index download/export of the WebVTT.

**Note:** the resource API response, when the `media files count` is >10, the `media file IDs` will display only a maximum of 10 IDs in the list (as of May 2023). An example is resource 58924

Todo: alter to remove the need for an input file of ID once pagination is available and replace with `/api/v1/collections` and `/api/v1/collections/{:collection_id}/resources` to build a list of media.

Note: `experiemental/aviary_api_report_index_csv_by_list.py` uses the resource CSV export as input.

### Supplemental files metadata report

For input, use the Web UI resource table option to export. This obtains a list of resource IDs (required due to lack of pagination in the Aviary API as of 2023-05-26).

* Navigate to `/supplemental_files`
* Select `Table Options` --> `Export Supplemental Files(s) to CSV`

``` bash
python3 aviary_api_report_supplemental_files_csv_by_list.py --server ${aviary_server_name} --output ${output_path} -input ${input_path}
```

Todo: alter to remove the need for an input file of ID once pagination is available and replace with `/api/v1/collections` and `/api/v1/collections/{:collection_id}/resources` to build a list of media.

### Upload a media file via the API and attach it to an existing resource

The following script authenticates against the Aviary API and via chunking, uploads a media file. This approach only works for media files below 1G (maybe up to 2G at times) due to security and configuration restrictions on the Aviary side (according to Feb. 2023 conversations with AVP)

* Sometime after Aug/Sept 2022 tests and before Feb 2023, the API upload seems to have broken
  * the filename was made a required parameter (not in the release notes)
  * the API upload occurs without error but the media does not appear in the web UI and the resource media listing the Web UI throws an error page after the API upload

``` bash
python3 aviary_media_api_upload_chunked.py --server ${aviary_server_name} --input input.sample.csv
```

### To generate test media objects

The ffmpeg tool can be used to generate test videos in cases where one requires a video of a certain size without copyright or permission encumbrances.

For example, the following creates a video of a testsrc with a 10sec duration at a 30 frames/second rate. By varying the duration, one can increase the storage size of the resulting video.

``` bash
ffmpeg -f lavfi -i testsrc=duration=10:size=1280x720:rate=30 testsrc_10.mpg
```

Another option is to concatenate multiple videos together using ffmpeg and the `concat` feature that takes as input a file listing the video files to concatenate (one-per-line) and the output file.

``` bash
ffmpeg -f concat -safe 0 -i ffmpeg_concat.txt -c copy 3g.mp4
```

## Development

To check style:

``` bash
pycodestyle --show-source --show-pep8 --ignore=E402,W504 --max-line-length=200 .
```

To run tests:

``` bash
python3 tests/unit_tests.py
```

## Spoken Web collection export

Note: uses fragile workarounds as AVP Aviary API does not cover all the required features (e.g., pagination as of March 2024; index API added after Nov 2023).

### SpokenWeb Export Nov. 2023 & Mar. 2024

1. Get the list of resources in the SpokenWeb Collection (ID: 1783)
   * Workaround as the API doesn't have pagination nor a filter by collection
   * Export all resources as CSV from the UI resources table: <https://ualberta.aviaryplatform.com/collection_resources>
     * Verify the "Collection Title" property is enabled in the UI resources table "manage table" otherwise there is no information to determine each resource's collection
   * Filter the CSV by the "Collection Title" property (verify enabled via the "manage table" list of displayed properties)
     * `grep 'SpokenWeb UAlberta' delete2/UniversityofAlbertaLibrary_collection_resources_2024-03-25_1711392929.csv`
     * add back the CSV header
2. Get the resource metadata (JSON)
   * `python3 avp_aviary_api_interactions/json/aviary_api_report_resources_json_by_resource_list.py --server 'https://ualberta.aviaryplatform.com/' --output delete2/aviary_collection_1783_resources_2024-03-25.json --input delete2/UniversityofAlbertaLibrary_collection_resources_2024-03-25_1711392929_collection_1783.csv`
3. Get the media metadata (JSON)
   * Nov. 2023 approach fails as of March 2024 (unable to export the media CSV from the Aviary UI) - `aviary_api_report_index_json_by_media_list.py`.
   * Use the 'media_file_id' in the resource JSON output (truncated to 10 media IDs when last tested in 2022)
   * Check if the media_file_id field in the resource JSON has truncated the ID list at 10 items:
     * `jq '.[].data.media_file_id | length' delete2/aviary_collection_1783_resources_2024-03-25.json`
     * `jq '.[1].data' delete2/aviary_collection_1783_resources_2024-03-25.json`
   * `python3 avp_aviary_api_interactions/json/aviary_api_report_media_by_resource_json.py --server 'https://ualberta.aviaryplatform.com/' --input delete2/aviary_collection_1783_resources_2024-03-25.json --output delete2/aviary_collection_1783_media_2024-03-25.json`
   * These two should match:
     * `jq '. | length' delete2/aviary_collection_1783_media_2024-03-25.json`
     * `jq '.[].data.media_file_id[]' delete2/aviary_collection_1783_resources_2024-03-25.json | wc -l`
4. Get the index metadata
   * `python3 avp_aviary_api_interactions/json/aviary_api_report_index_by_media_json.py --server 'https://ualberta.aviaryplatform.com/' --input delete2/aviary_collection_1783_media_2024-03-25.json --output delete2/aviary_collection_1783_index_2024-03-25.json`
   * These two should match
     * `jq '.[].data.indexes[].id' delete2/aviary_collection_1783_media_2024-03-25.json | wc -l`
     * `jq '. | length' delete2/aviary_collection_1783_index_2024-03-25.json`
5. Download index files
   * using the same script as of November 2023
     * `python3 avp_aviary_api_interactions/experimental/experimental_test_batch_download.py --server 'https://ualberta.aviaryplatform.com/' --input_file delete2/index_id_list_2024-03-25.csv --output_path delete2/index_file_export/ --type i --wait 10`
   * using the new API index endpoint as of March 2024
     * `python3 avp_aviary_api_interactions/json/aviary_api_download_index_by_index_json.py --server 'https://ualberta.aviaryplatform.com/' --input delete2/aviary_collection_1783_index_2024-03-25.json --output delete2/index_file_export__new_api_march_2024 --wait 5`
