# AVP Aviary API Interactions

The repository contains quickly written scripts designed to interact with the [AVP Aviary](https://www.aviaryplatform.com/api/v1/documentation) audio/video repository software. These scripts, as of March 2023 are only proof-of-concept.

## Requirements

* Python 3
* ability to work with proof-of-concept level software

## Aviary

A SaaS vendor audio/video repository solution. Terminology:

* `Resources`: term for the main container of the audio/video object (links together the metadata, `media` files, etc.)
* `Media`: term for the container representing one or more audio/video files, associated file metadata and linkage to the `resource`

## Included Scripts

### Resource metadata report including the `updated_at` field

Note: the `updated_at` field is unavailable via the web UI as of 2023-03-27

For input, use the Web UI resource table option to export. This obtains a list of resource IDs (required due to lack of pagination in the Aviary API as of 2023-05-26).

* Navigate to `/collection_resources`
* Select `Table Options` --> `Export Resources to CSV`

``` bash
python3 aviary_api_report_resources_csv_by_list.py --server ${aviary_server_name} --output ${output_path} -input ${input_path}
```

An attempt to use the Aviary APIs `/api/v1/collections` and `/api/v1/collections/{:collection_id}/resources` to build a list of resources failed (2023-03-27) due to a limit of 100 resources returned per collection and no documentation on how to enable pagination.

``` bash
python3 aviary_api_report_resources_csv.py --server ${aviary_server_name} --output ${output_path}
```

For a JSON-like output (more for debugging)

``` bash
python3 aviary_api_report_resources_json.py --server ${aviary_server_name} --output ${output_path}
```

### Media metadata report including the `updated_at` field

For input, use the Web UI resource table option to export. This obtains a list of resource IDs (required due to lack of pagination in the Aviary API as of 2023-05-26).

* Navigate to `/collection_resources`
* Select `Table Options` --> `Export Resources to CSV`

``` bash
python3 aviary_api_report_media_csv_by_list.py --server ${aviary_server_name} --output ${output_path} -input ${input_path}
```

An attempt to use the Aviary API `/api/v1/collections` and `/api/v1/collections/{:collection_id}/resources` to build a list of media failed (2023-03-27) due to a limit of 100 resources returned and no documentation on how to enable pagination (similar to the resource report).

``` bash
python3 aviary_api_report_media_csv.py --server ${aviary_server_name} --output ${output_path}
```

### Transcripts metadata report

For input, use the Web UI resource table option to export. This obtains a list of resource IDs (required due to lack of pagination in the Aviary API as of 2023-05-26).

* Navigate to `/collection_resources`
* Select `Table Options` --> `Export Resources to CSV`

``` bash
python3 aviary_api_report_transcripts_csv_by_list.py --server ${aviary_server_name} --output ${output_path} -input ${input_path}
```

Todo: alter to remove the need for an input file of ID once pagination is available and replace with `/api/v1/collections` and `/api/v1/collections/{:collection_id}/resources` to build a list of media.

### Indexes metadata report

As of 2023-05-26, the Aviary API does not support a direct HTTP GET API request to gather the metadata for the `indexes` type.

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

### List metadata about a media item (could be extended to generate reports)

The following script authenticates against the Aviary API and prints out the media metadata of a specified media object

``` bash
python3 aviary_media_api_get.py --server ${aviary_server_name} --media_id ${media_id}
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
