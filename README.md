# AVP Aviary API Interactions

The repository contains quickly written scripts designed to interact with the [AVP Aviary](https://www.aviaryplatform.com/api/v1/documentation) audio/video repository software. These scripts, as of March 2023 are only proof-of-concept.

## Requirements

* Python 3
* ability to work with proof-of-concept level software

## Setup

Assumes Python 3 is installed.

* git clone the repository
* Install dependencies:
  * `pip install -r requirements.txt --user`
  * Or python3 setup.py install --user
    * installed required modules in a local user account
  * Or without `--user` to install into the OS's central Python environment (required administrative privleges)

## Aviary

A SaaS vendor audio/video repository solution. Terminology:

* `Resources`: term for the main container of the audio/video object (links together the metadata, `media` files, etc.)
* `Media`: term for the container representing one or more audio/video files, associated file metadata; linked to the `resource`
* `Index`: term for the container representing one or more indexes into the media and associated metadata; linked to a `media` item
* `Transcript`: term for the container representing one or more transcripts of the audio/video; linked to a `media` item
* `Supplemental Files`: term for the container representing one or more supplemental files (JPEG, PDF, etc.) attached to the resource; linked to a `resource` item

**Note:** the vendor rate limits API requests. Each of the following scripts uses a simple wait mechanism between API requests. A more advanced approach could be implemented where the wait time is dynamically computed based on the response latency plus a retry mechanism. As of 2023-05-29, running multiple scripts will cause one to fail with the default wait settings.

**Note:** pagination is not documented (as of 2023-05-29) so workarounds are needed for collections with more than 100 resources (e.g., use Web UI export to gain a list of IDs)

**Note:** as of 2023-06-29, a resource returned by the Aviary API lists the attached media item(s) in the `media_file_id` field. However, `media_ife_id` only contains a maximum of 10 IDs (a significant number of resources have over 10 media attached). I also tried via the Web UI, "export Media Files(s) to CSV" but the resulting file doesn't contain media IDs. How to get the entire list of media items is unknown.

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
